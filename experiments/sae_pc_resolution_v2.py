#!/usr/bin/env python3
"""
SAE PC Resolution v2: tests BOTH decoder geometry AND activation-weighted importance.

Addresses /vet findings:
1. Test activation-weighted importance (mean |z_i| across inputs) — the standard metric
2. Increase PCA samples to 2000 (get close to full 768 PCs)
3. Report both L2-norm (geometric coverage) and activation-weighted (behavioral) metrics
4. Clarify what is reproducible: geometry only, or also behavior?

Usage: CUDA_VISIBLE_DEVICES=0 python3 sae_pc_resolution_v2.py
"""
import os
import json
import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from itertools import combinations
from scipy.stats import spearmanr

EXPERIMENT_DIR = Path(os.environ.get("EXPERIMENT_DIR", os.path.expanduser("~/SageMaker/experiments")))
RESULTS_DIR = EXPERIMENT_DIR / "results" / "sae_pc_resolution"
SAE_DIR = EXPERIMENT_DIR / "results" / "sae"
CKPT_DIR = EXPERIMENT_DIR / "checkpoints"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

N_PCA_SAMPLES = 2000  # More samples → more PCs (up to 768)
N_ACT_SAMPLES = 500   # Samples for activation-weighted importance
SEQ_LEN = 256
D_MODEL = 768
D_SAE = 6144
K = 48


class TopKSAE(torch.nn.Module):
    """Minimal TopK SAE for inference."""
    def __init__(self, state_dict):
        super().__init__()
        self.W_enc = torch.nn.Parameter(state_dict["W_enc"])  # (768, 6144)
        self.b_enc = torch.nn.Parameter(state_dict["b_enc"])  # (6144,)
        self.W_dec = torch.nn.Parameter(state_dict["W_dec"])  # (6144, 768)
        self.b_dec = torch.nn.Parameter(state_dict["b_dec"])  # (768,)

    def encode(self, x):
        """Encode with TopK activation."""
        z = x @ self.W_enc + self.b_enc  # (batch, 6144)
        topk_vals, topk_idx = torch.topk(z, K, dim=-1)
        z_sparse = torch.zeros_like(z)
        z_sparse.scatter_(-1, topk_idx, F.relu(topk_vals))
        return z_sparse

    def forward(self, x):
        z = self.encode(x)
        x_hat = z @ self.W_dec + self.b_dec
        return x_hat, z


def load_model(seed: int):
    from transformers import GPT2LMHeadModel, GPT2Config
    config = GPT2Config()
    model = GPT2LMHeadModel(config).to(device).eval()
    ckpt_path = CKPT_DIR / f"gpt2_seed{seed}" / "model_final.pt"
    state = torch.load(ckpt_path, map_location=device)
    if "model_state_dict" in state:
        model.load_state_dict(state["model_state_dict"])
    else:
        model.load_state_dict(state)
    return model


def collect_activations(model, n_samples, target_layer=6):
    """Collect layer-6 activations using random tokens."""
    activations = []
    hook_output = {}

    def hook_fn(module, input, output):
        out = output[0] if isinstance(output, tuple) else output
        hook_output["act"] = out.detach()

    handle = model.transformer.h[target_layer].register_forward_hook(hook_fn)

    vocab_size = 50257
    for i in range(n_samples):
        toks = torch.randint(0, vocab_size, (1, SEQ_LEN), device=device)
        with torch.no_grad():
            model(toks)
        act = hook_output["act"].mean(dim=1).squeeze().cpu().numpy()
        assert act.shape == (D_MODEL,), f"Expected ({D_MODEL},), got {act.shape}"
        activations.append(act)
        if i == 0:
            print(f"  First activation shape: {act.shape}")

    handle.remove()
    return np.stack(activations)


def compute_pcs(X):
    """PCA on activation matrix. Returns (d, min(n,d)) PCs as columns."""
    X_c = X - X.mean(axis=0)
    _, S, Vt = np.linalg.svd(X_c, full_matrices=False)
    return Vt.T, S  # (768, n_components)


def compute_activation_importance(model, sae, n_samples, target_layer=6):
    """
    Compute activation-weighted importance: mean |z_i| across inputs.
    This is the standard behavioral importance metric for SAE features.
    """
    hook_output = {}

    def hook_fn(module, input, output):
        out = output[0] if isinstance(output, tuple) else output
        hook_output["act"] = out.detach()

    handle = model.transformer.h[target_layer].register_forward_hook(hook_fn)

    total_activation = torch.zeros(D_SAE, device=device)
    vocab_size = 50257

    for i in range(n_samples):
        toks = torch.randint(0, vocab_size, (1, SEQ_LEN), device=device)
        with torch.no_grad():
            model(toks)
        # Get layer-6 activations, mean over sequence
        layer_act = hook_output["act"].mean(dim=1)  # (1, 768)
        # Encode through SAE
        with torch.no_grad():
            z = sae.encode(layer_act)  # (1, 6144)
        total_activation += z.abs().squeeze()

    handle.remove()
    importance = (total_activation / n_samples).cpu().numpy()
    return importance


def pc_projection(decoder, importance, pcs):
    """Project importance onto PC basis."""
    alignment = decoder @ pcs  # (6144, n_pcs)
    alignment_sq = alignment ** 2
    row_norms = alignment_sq.sum(axis=1, keepdims=True)
    row_norms = np.maximum(row_norms, 1e-10)
    alignment_frac = alignment_sq / row_norms
    w = (importance[:, None] * alignment_frac).sum(axis=0)
    return w


def main():
    print("=" * 60)
    print("SAE PC RESOLUTION v2 (Geometric + Behavioral)")
    print("=" * 60)

    # Step 1: Load model and compute PCs with more samples
    print(f"\nStep 1: Computing PCs from {N_PCA_SAMPLES} random-token activations...")
    model = load_model(seed=0)
    X_pca = collect_activations(model, N_PCA_SAMPLES)
    pcs, S = compute_pcs(X_pca)
    n_pcs = pcs.shape[1]
    var_exp = S ** 2 / (S ** 2).sum()
    print(f"  PCs: {pcs.shape} ({n_pcs} components)")
    print(f"  Variance explained top-5: {(var_exp[:5]*100).round(1)}")

    # Step 2: Load SAEs and compute BOTH importance metrics
    print(f"\nStep 2: Loading SAEs, computing geometric + activation importance...")
    n_seeds = 10

    l2_importances = []
    act_importances = []
    pc_l2 = []
    pc_act = []

    for seed in range(n_seeds):
        # Load decoder
        path = SAE_DIR / f"sae_seed{seed}" / "sae_final.pt"
        state = torch.load(path, map_location="cpu")
        D = state["W_dec"].numpy()  # (6144, 768)

        # L2 norm importance (geometric)
        l2_imp = np.linalg.norm(D, axis=1)
        l2_importances.append(l2_imp)
        pc_l2.append(pc_projection(D, l2_imp, pcs))

        # Activation-weighted importance (behavioral)
        sae = TopKSAE(state).to(device).eval()
        act_imp = compute_activation_importance(model, sae, N_ACT_SAMPLES)
        act_importances.append(act_imp)
        pc_act.append(pc_projection(D, act_imp, pcs))

        # Report
        n_active = (act_imp > 0).sum()
        print(f"  Seed {seed}: L2 range [{l2_imp.min():.3f}, {l2_imp.max():.3f}], "
              f"active features: {n_active}/{D_SAE} ({n_active/D_SAE*100:.1f}%)")

    del model, sae
    torch.cuda.empty_cache()

    # Step 3: Compute all Spearman correlations
    print(f"\nStep 3: Computing correlations...")
    pairs = list(combinations(range(n_seeds), 2))

    # Raw
    raw_l2 = [spearmanr(l2_importances[i], l2_importances[j])[0] for i, j in pairs]
    raw_act = [spearmanr(act_importances[i], act_importances[j])[0] for i, j in pairs]

    # PC-projected
    pc_l2_rhos = [spearmanr(pc_l2[i], pc_l2[j])[0] for i, j in pairs]
    pc_act_rhos = [spearmanr(pc_act[i], pc_act[j])[0] for i, j in pairs]

    # By dimensionality
    dims_to_test = [10, 50, 100, 200, 400, min(n_pcs, 768)]
    pc_l2_by_k = {}
    pc_act_by_k = {}
    for k in dims_to_test:
        if k > n_pcs:
            continue
        pc_l2_by_k[k] = np.mean([spearmanr(pc_l2[i][:k], pc_l2[j][:k])[0] for i, j in pairs])
        pc_act_by_k[k] = np.mean([spearmanr(pc_act[i][:k], pc_act[j][:k])[0] for i, j in pairs])

    # Results
    print(f"\n{'=' * 60}")
    print("RESULTS")
    print(f"{'=' * 60}")
    print(f"\n  {'Metric':<35} | {'Raw rho':>8} | {'PC-proj rho':>11}")
    print(f"  {'-'*35}-+-{'-'*8}-+-{'-'*11}")
    print(f"  {'L2 norm (geometric coverage)':<35} | {np.mean(raw_l2):>8.3f} | {np.mean(pc_l2_rhos):>11.3f}")
    print(f"  {'Mean |activation| (behavioral)':<35} | {np.mean(raw_act):>8.3f} | {np.mean(pc_act_rhos):>11.3f}")

    print(f"\n  By dimensionality (activation-weighted):")
    for k, rho in sorted(pc_act_by_k.items()):
        print(f"    Top-{k:>4} PCs: rho = {rho:.3f}")

    print(f"\n  By dimensionality (L2 geometric):")
    for k, rho in sorted(pc_l2_by_k.items()):
        print(f"    Top-{k:>4} PCs: rho = {rho:.3f}")

    print(f"\n  Reference: Hungarian matched = 0.500, G-inv heads = 0.873")

    # Save
    results = {
        "method": "PC projection v2 (geometric + behavioral)",
        "n_seeds": n_seeds,
        "n_pca_samples": N_PCA_SAMPLES,
        "n_act_samples": N_ACT_SAMPLES,
        "n_pcs_available": n_pcs,
        "l2_geometric": {
            "raw_rho": float(np.mean(raw_l2)),
            "pc_rho": float(np.mean(pc_l2_rhos)),
            "pc_by_k": {str(k): float(v) for k, v in pc_l2_by_k.items()},
        },
        "activation_weighted": {
            "raw_rho": float(np.mean(raw_act)),
            "pc_rho": float(np.mean(pc_act_rhos)),
            "pc_by_k": {str(k): float(v) for k, v in pc_act_by_k.items()},
        },
        "variance_explained_top10": var_exp[:10].tolist(),
    }

    out_path = RESULTS_DIR / "pc_resolution_v2_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Saved to {out_path}")

    repo_dest = Path(__file__).resolve().parent.parent / "docs" / "gpt2-experiment-results" / "sae_followup"
    repo_dest.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(out_path, repo_dest / "pc_resolution_v2_results.json")
    print(f"  Copied to repo")


if __name__ == "__main__":
    main()
