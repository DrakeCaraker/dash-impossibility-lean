"""
causal_dag_experiment.py
------------------------
Validates the conditional SHAP impossibility and escape condition using a
known causal DAG.

Known DAG:
  X1 -> Y, X2 -> Y, X1 <-> X2 (correlated via shared latent)

Data generating process:
  X1, X2 ~ bivariate Gaussian with correlation rho = 0.8
  Y = beta1 * X1 + beta2 * X2 + epsilon,  epsilon ~ N(0, 0.1)

We sweep Delta_beta = |beta1 - beta2| from 0 to 1 in steps of 0.1, with
  beta1 = 1 + Delta_beta / 2,  beta2 = 1 - Delta_beta / 2
so the average coefficient stays at 1.

For each Delta_beta we:
  1. Generate N=2000 samples
  2. Train 50 XGBoost models (different seeds, subsample=0.8)
  3. Compute marginal SHAP (TreeSHAP, tree_path_dependent) -- expected UNSTABLE
     for small Delta_beta
  4. Compute "conditional-like" SHAP by residualizing X2 on X1:
       X2_resid = X2 - rho * X1
     Then retrain on [X1, X2_resid] and compute TreeSHAP.
     This simulates conditional SHAP's decorrelation effect.
  5. Measure flip rate for the (X1, X2) pair under both methods

Expected results:
  - Marginal SHAP: unstable for Delta_beta < ~0.2, stable for large Delta_beta
  - Conditional SHAP: unstable when Delta_beta = 0 (impossible to escape),
    stable when Delta_beta > 0
  - Sharp transition at Delta_beta ~ 0 for conditional, gradual for marginal
  - Validates: conditional SHAP escapes impossibility ONLY when causal effects
    differ

Output:
  - Table: Delta_beta | marginal_flip_rate | conditional_flip_rate
  - Verdict string summarizing the resolution thresholds
  - Saved to paper/results_causal_dag.json
"""

import os
import sys
import json
import warnings
import itertools

import numpy as np

try:
    import xgboost as xgb
except ImportError:
    print("ERROR: xgboost not installed. Install with: pip install xgboost")
    sys.exit(1)

try:
    import shap
except ImportError:
    print("ERROR: shap not installed. Install with: pip install shap")
    sys.exit(1)

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────────────

N_SAMPLES = 2000
N_MODELS = 50
N_EVAL = 200
RHO = 0.8
SIGMA_NOISE = 0.1
TRAIN_FRAC = 0.8
DELTA_BETAS = [round(d * 0.1, 1) for d in range(11)]  # 0.0, 0.1, ..., 1.0

XGB_PARAMS = dict(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    subsample=0.8,
    n_jobs=1,
    verbosity=0,
)

# Threshold: flip rate below this is considered "stable"
STABLE_THRESHOLD = 0.10

# ── Data generation ───────────────────────────────────────────────────────────

def generate_data(delta_beta: float, rng: np.random.Generator) -> tuple:
    """
    Generate (X, y) from the causal DGP.

    X1, X2 ~ bivariate Gaussian with Corr(X1, X2) = RHO.
    Y = beta1 * X1 + beta2 * X2 + epsilon.
    """
    beta1 = 1.0 + delta_beta / 2.0
    beta2 = 1.0 - delta_beta / 2.0

    # Bivariate Gaussian via latent variable
    Z = rng.standard_normal(N_SAMPLES)
    eps_x = rng.standard_normal(N_SAMPLES)
    X1 = Z
    X2 = RHO * Z + np.sqrt(1.0 - RHO ** 2) * eps_x

    noise = rng.normal(0.0, SIGMA_NOISE, size=N_SAMPLES)
    y = beta1 * X1 + beta2 * X2 + noise

    return X1, X2, y, beta1, beta2


# ── SHAP helpers ──────────────────────────────────────────────────────────────

def mean_abs_shap(model: xgb.XGBRegressor, X_eval: np.ndarray) -> np.ndarray:
    """
    Marginal SHAP via tree_path_dependent perturbation.
    Returns mean |SHAP| per feature.
    """
    explainer = shap.TreeExplainer(
        model,
        feature_perturbation="tree_path_dependent",
    )
    shap_vals = explainer.shap_values(X_eval)
    return np.abs(shap_vals).mean(axis=0)


# ── Flip rate ─────────────────────────────────────────────────────────────────

def compute_flip_rate(rankings: list) -> float:
    """
    Fraction of model pairs where feature 0 vs feature 1 ranking reverses.
    """
    n_pairs = len(rankings) * (len(rankings) - 1) // 2
    if n_pairs == 0:
        return 0.0
    n_flips = sum(1 for a, b in itertools.combinations(rankings, 2) if a != b)
    return n_flips / n_pairs


# ── Main experiment ───────────────────────────────────────────────────────────

def run_experiment() -> list:
    """
    Sweep Delta_beta and compute marginal and conditional flip rates.
    Returns list of row dicts.
    """
    rows = []

    print(f"\n{'Delta_beta':>10}  {'beta1':>6}  {'beta2':>6}  "
          f"{'Marginal flip':>14}  {'Conditional flip':>17}")
    print(f"  {'-' * 63}")

    for delta_beta in DELTA_BETAS:
        beta1 = 1.0 + delta_beta / 2.0
        beta2 = 1.0 - delta_beta / 2.0

        marginal_rankings = []
        conditional_rankings = []

        for seed in range(N_MODELS):
            rng = np.random.default_rng(seed * 1000 + int(delta_beta * 100))
            X1, X2, y, _, _ = generate_data(delta_beta, rng)

            n_train = int(TRAIN_FRAC * N_SAMPLES)

            # ── Marginal SHAP: train on [X1, X2] ─────────────────────────
            X_marginal = np.column_stack([X1, X2])
            X_train_m = X_marginal[:n_train]
            y_train = y[:n_train]
            X_eval_m = X_marginal[n_train : n_train + N_EVAL]

            model_m = xgb.XGBRegressor(random_state=seed, **XGB_PARAMS)
            model_m.fit(X_train_m, y_train)

            ms_m = mean_abs_shap(model_m, X_eval_m)
            marginal_rankings.append(ms_m[0] > ms_m[1])

            # ── Conditional-like SHAP: residualize X2 on X1 ──────────────
            X2_resid = X2 - RHO * X1
            X_cond = np.column_stack([X1, X2_resid])
            X_train_c = X_cond[:n_train]
            X_eval_c = X_cond[n_train : n_train + N_EVAL]

            model_c = xgb.XGBRegressor(random_state=seed, **XGB_PARAMS)
            model_c.fit(X_train_c, y_train)

            ms_c = mean_abs_shap(model_c, X_eval_c)
            conditional_rankings.append(ms_c[0] > ms_c[1])

        marg_flip = compute_flip_rate(marginal_rankings)
        cond_flip = compute_flip_rate(conditional_rankings)

        print(f"  {delta_beta:>8.1f}  {beta1:>6.2f}  {beta2:>6.2f}  "
              f"{marg_flip:>14.3f}  {cond_flip:>17.3f}")

        rows.append(dict(
            delta_beta=delta_beta,
            beta1=beta1,
            beta2=beta2,
            marginal_flip_rate=round(marg_flip, 4),
            conditional_flip_rate=round(cond_flip, 4),
        ))

    return rows


# ── Verdict ───────────────────────────────────────────────────────────────────

def compute_verdict(rows: list) -> str:
    """
    Summarize the resolution thresholds for marginal and conditional SHAP.
    """
    cond_stable = [r for r in rows
                   if r["conditional_flip_rate"] < STABLE_THRESHOLD
                   and r["delta_beta"] > 0]
    marg_stable = [r for r in rows
                   if r["marginal_flip_rate"] < STABLE_THRESHOLD]

    if cond_stable:
        cond_threshold = min(r["delta_beta"] for r in cond_stable)
    else:
        cond_threshold = None

    if marg_stable:
        marg_threshold = min(r["delta_beta"] for r in marg_stable)
    else:
        marg_threshold = None

    parts = []
    if cond_threshold is not None:
        parts.append(f"Conditional SHAP resolves at Delta_beta > {cond_threshold:.1f}")
    else:
        parts.append("Conditional SHAP does not resolve at any tested Delta_beta")

    if marg_threshold is not None:
        parts.append(f"marginal requires Delta_beta > {marg_threshold:.1f}")
    else:
        parts.append("marginal does not resolve at any tested Delta_beta")

    return ", ".join(parts)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PAPER_DIR = os.path.dirname(SCRIPT_DIR)
    OUTPUT_PATH = os.path.join(PAPER_DIR, "results_causal_dag.json")

    print("=== Causal DAG Experiment — Conditional SHAP Impossibility Validation ===")
    print(f"N_SAMPLES={N_SAMPLES}, N_MODELS={N_MODELS}, N_EVAL={N_EVAL}, rho={RHO}")
    print(f"sigma_noise={SIGMA_NOISE}, n_jobs=1")
    print(f"Marginal: TreeSHAP (tree_path_dependent)")
    print(f"Conditional: residualized X2|X1 then TreeSHAP")

    rows = run_experiment()

    verdict = compute_verdict(rows)
    print(f"\n=== Verdict ===")
    print(f"  {verdict}")

    # ── Check Delta_beta = 0 specifically ─────────────────────────────────────
    zero_row = [r for r in rows if r["delta_beta"] == 0.0]
    if zero_row:
        r = zero_row[0]
        print(f"\n  At Delta_beta = 0 (equal effects):")
        print(f"    Marginal flip rate:     {r['marginal_flip_rate']:.4f}")
        print(f"    Conditional flip rate:  {r['conditional_flip_rate']:.4f}")
        if r["conditional_flip_rate"] >= STABLE_THRESHOLD:
            print(f"    -> Impossibility holds: conditional SHAP cannot escape when "
                  f"causal effects are equal")

    # ── Save results ──────────────────────────────────────────────────────────
    output = dict(
        config=dict(
            n_samples=N_SAMPLES,
            n_models=N_MODELS,
            n_eval=N_EVAL,
            rho=RHO,
            sigma_noise=SIGMA_NOISE,
            stable_threshold=STABLE_THRESHOLD,
        ),
        rows=rows,
        verdict=verdict,
    )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")
