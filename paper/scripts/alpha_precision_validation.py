#!/usr/bin/env python3
"""
Validate whether alpha = 2/pi is a precise theoretical prediction for the
split-count ratio in boosted stumps under collinearity.

Theory predicts: ratio = 1 / (1 - (2/pi) * rho^2)

Setup:
  - N = 50,000 samples, P = 2 correlated Gaussian features
  - XGBClassifier: 100 depth-1 stumps, learning_rate=1.0
  - 200 seeds per rho value
  - Binary classification: Y = sign(X1 + X2 + eps), eps ~ N(0, 0.5)

For each seed, compute ratio = n_first / n_second (first = feature with
more splits). Report mean ratio per rho, compare to theoretical prediction,
and compute R^2.
"""

import numpy as np
from xgboost import XGBClassifier
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings("ignore")

# --- Configuration ---
N_SAMPLES = 50_000
N_ESTIMATORS = 100
MAX_DEPTH = 1
LEARNING_RATE = 1.0
N_SEEDS = 200
ALPHA = 2.0 / np.pi
RHO_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
NOISE_STD = 0.5

FIGURES_DIR = "/Users/drake.caraker/ds_projects/dash-impossibility-lean/paper/figures"

# --- Run experiment ---
print(f"alpha = 2/pi = {ALPHA:.6f}")
print(f"N={N_SAMPLES}, T={N_ESTIMATORS}, depth={MAX_DEPTH}, lr={LEARNING_RATE}")
print(f"seeds={N_SEEDS}, noise_std={NOISE_STD}")
print("-" * 72)

empirical_ratios = []

for rho in RHO_VALUES:
    seed_ratios = []
    for seed in range(N_SEEDS):
        rng = np.random.RandomState(seed)

        # Generate correlated features
        X1 = rng.randn(N_SAMPLES)
        Z = rng.randn(N_SAMPLES)
        X2 = rho * X1 + np.sqrt(1.0 - rho**2) * Z

        X = np.column_stack([X1, X2])

        # Binary classification target
        linear = X1 + X2 + NOISE_STD * rng.randn(N_SAMPLES)
        Y = (linear > 0).astype(int)

        # Train single-stump boosted model
        model = XGBClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            learning_rate=LEARNING_RATE,
            use_label_encoder=False,
            eval_metric="logloss",
            verbosity=0,
            random_state=seed,
        )
        model.fit(X, Y)

        # Get split counts
        score = model.get_booster().get_score(importance_type="weight")
        counts = {}
        for feat, count in score.items():
            # Feature names are f0, f1
            idx = int(feat[1:])
            counts[idx] = count

        c0 = counts.get(0, 0)
        c1 = counts.get(1, 0)

        if c0 == 0 and c1 == 0:
            continue  # skip degenerate case

        n_first = max(c0, c1)
        n_second = min(c0, c1)

        if n_second == 0:
            # All splits on one feature — ratio is effectively infinite;
            # use n_estimators / 0.5 as a large but finite stand-in
            seed_ratios.append(float(N_ESTIMATORS) / 0.5)
        else:
            seed_ratios.append(n_first / n_second)

    mean_ratio = np.mean(seed_ratios)
    empirical_ratios.append(mean_ratio)
    predicted = 1.0 / (1.0 - ALPHA * rho**2)
    rel_err = abs(mean_ratio - predicted) / predicted * 100
    print(f"rho={rho:.2f}  empirical={mean_ratio:.4f}  predicted={predicted:.4f}  rel_err={rel_err:.1f}%")

# --- Compute R^2 ---
predicted_ratios = [1.0 / (1.0 - ALPHA * r**2) for r in RHO_VALUES]
r2 = r2_score(empirical_ratios, predicted_ratios)
print("-" * 72)
print(f"R^2 = {r2:.6f}")

# --- Generate figure ---
rho_fine = np.linspace(0.0, 0.96, 200)
theory_fine = 1.0 / (1.0 - ALPHA * rho_fine**2)

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(rho_fine, theory_fine, "b-", linewidth=2, label=r"Theory: $1/(1 - \frac{2}{\pi}\rho^2)$")
ax.scatter(RHO_VALUES, empirical_ratios, c="red", s=60, zorder=5, label="Empirical (200 seeds)")
ax.set_xlabel(r"Correlation $\rho$", fontsize=13)
ax.set_ylabel("Split-count ratio (first / second)", fontsize=13)
ax.set_title(r"Validation of $\alpha = 2/\pi$ prediction", fontsize=14)
ax.annotate(
    f"$R^2 = {r2:.4f}$",
    xy=(0.05, 0.90),
    xycoords="axes fraction",
    fontsize=14,
    bbox=dict(boxstyle="round,pad=0.3", fc="wheat", alpha=0.8),
)
ax.legend(fontsize=11, loc="lower right")
ax.set_xlim(-0.02, 1.0)
ax.grid(True, alpha=0.3)
fig.tight_layout()

outpath = f"{FIGURES_DIR}/alpha_precision.pdf"
fig.savefig(outpath, dpi=150)
print(f"Figure saved: {outpath}")
