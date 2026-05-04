#!/usr/bin/env python3
"""
SAE PC Resolution: test whether projecting feature importance onto data PCs
produces reproducible importance rankings across SAE training seeds.

Theory predicts: the reproducible subspace has dim <= d = 768.
Data PCs provide a seed-invariant 768-dim basis for this subspace.
If correct, per-PC importance should be reproducible (rho >> 0.5).

Usage: CUDA_VISIBLE_DEVICES=0 python3 sae_pc_resolution.py
"""
import os
import json
import torch
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


def load_model(seed: int):
    """Load a trained GPT-2-small model."""
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


def compute_data_pcs(model, n_samples=400, seq_len=256, target_layer=6):
    """
    Compute PCA of layer-6 activations on streaming OpenWebText.
    Returns: pcs (768 x 768, columns are PCs), singular_values
    """
    from transformers import GPT2Tokenizer
    from datasets import load_dataset

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    ds = load_dataset("openwebtext", split="train", streaming=True)

    activations = []
    hook_output = {}

    def hook_fn(module, input, output):
        hook_output["act"] = output[0].detach()

    handle = model.transformer.h[target_layer].register_forward_hook(hook_fn)

    for example in ds:
        if len(activations) >= n_samples:
            break
        tokens = tokenizer(example["text"], return_tensors="pt", max_length=seq_len,
                           truncation=True)["input_ids"].to(device)
        if tokens.shape[1] < 64:
            continue
        with torch.no_grad():
            model(tokens)
        act = hook_output["act"].mean(dim=1).cpu().numpy()[0]  # (768,)
        activations.append(act)

    handle.remove()

    X = np.array(activations)  # (n_samples, 768)
    X_centered = X - X.mean(axis=0)
    _, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    return Vt.T, S  # pcs: (768, 768) columns; S: singular values


def load_sae_decoder(seed: int):
    """Load SAE decoder matrix. Returns (6144, 768) numpy array."""
    path = SAE_DIR / f"sae_seed{seed}" / "sae_final.pt"
    state = torch.load(path, map_location="cpu")
    D = state["W_dec"].numpy()  # (6144, 768)
    return D


def pc_importance(decoder, importance, pcs):
    """
    Project feature importance onto data PCs.

    For each PC direction u_j:
      w[j] = sum_i importance[i] * (decoder[i] . u_j)^2 / ||decoder[i]||^2

    This measures how much total importance is allocated to each PC direction,
    regardless of which specific features carry it.

    Args:
        decoder: (6144, 768) decoder matrix
        importance: (6144,) per-feature importance
        pcs: (768, 768) PC matrix (columns are PCs)

    Returns:
        (768,) PC-projected importance
    """
    alignment = decoder @ pcs  # (6144, 768)
    alignment_sq = alignment ** 2
    row_norms = alignment_sq.sum(axis=1, keepdims=True)
    row_norms = np.maximum(row_norms, 1e-10)
    alignment_frac = alignment_sq / row_norms
    w = (importance[:, None] * alignment_frac).sum(axis=0)  # (768,)
    return w


def main():
    print("=" * 60)
    print("SAE PC RESOLUTION TEST")
    print("=" * 60)

    # Step 1: Compute data PCs (seed-invariant)
    print("\nStep 1: Computing data PCs from layer-6 activations...")
    model = load_model(seed=0)
    pcs, S = compute_data_pcs(model, n_samples=400)
    print(f"  PCs shape: {pcs.shape}")
    var_explained = S ** 2 / (S ** 2).sum()
    print(f"  Top-5 variance explained: {(var_explained[:5] * 100).round(1)}")
    del model
    torch.cuda.empty_cache()

    # Step 2: Load SAE decoders and compute importance
    print("\nStep 2: Loading SAE decoders...")
    importances = []
    pc_importances = []

    for seed in range(10):
        D = load_sae_decoder(seed)
        print(f"  Seed {seed}: decoder {D.shape}")

        imp = np.linalg.norm(D, axis=1)  # L2 norm as importance proxy
        importances.append(imp)

        w = pc_importance(D, imp, pcs)
        pc_importances.append(w)

    # Step 3: Compute reproducibility
    print("\nStep 3: Computing Spearman correlations...")

    raw_rhos = [spearmanr(importances[i], importances[j])[0]
                for i, j in combinations(range(10), 2)]
    pc_rhos = [spearmanr(pc_importances[i], pc_importances[j])[0]
               for i, j in combinations(range(10), 2)]

    pc_by_k = {}
    for k in [10, 50, 100, 200, 400, 768]:
        rhos_k = [spearmanr(pc_importances[i][:k], pc_importances[j][:k])[0]
                  for i, j in combinations(range(10), 2)]
        pc_by_k[k] = float(np.mean(rhos_k))

    # Results
    print(f"\n{'=' * 60}")
    print("RESULTS")
    print(f"{'=' * 60}")
    print(f"\n  Raw feature importance (6144-dim): rho = {np.mean(raw_rhos):.3f}")
    print(f"  PC-projected importance (768-dim): rho = {np.mean(pc_rhos):.3f}")
    print(f"\n  By dimensionality:")
    for k, rho in sorted(pc_by_k.items()):
        print(f"    Top-{k:>3} PCs: rho = {rho:.3f}")
    print(f"\n  Improvement over raw: {np.mean(pc_rhos) - np.mean(raw_rhos):+.3f}")
    print(f"\n  Reference comparisons:")
    print(f"    Matched Hungarian (prior):  rho = 0.500")
    print(f"    G-invariant (heads):        rho = 0.873")
    print(f"    Theoretical capacity:       C = 768/6144 = 12.5%")

    # Save
    results = {
        "method": "PC projection of SAE feature importance",
        "n_seeds": 10,
        "d_model": 768,
        "d_sae": 6144,
        "n_pca_samples": 400,
        "target_layer": 6,
        "raw_importance": {
            "mean_spearman": float(np.mean(raw_rhos)),
            "std_spearman": float(np.std(raw_rhos)),
            "all_spearman": [float(r) for r in raw_rhos],
        },
        "pc_projected": {
            "mean_spearman": float(np.mean(pc_rhos)),
            "std_spearman": float(np.std(pc_rhos)),
            "all_spearman": [float(r) for r in pc_rhos],
        },
        "pc_by_dimensionality": pc_by_k,
        "improvement": float(np.mean(pc_rhos) - np.mean(raw_rhos)),
        "variance_explained_top10": var_explained[:10].tolist(),
    }

    out_path = RESULTS_DIR / "pc_resolution_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Saved to {out_path}")

    # Copy to repo
    repo_dest = Path(__file__).resolve().parent.parent / "docs" / "gpt2-experiment-results" / "sae_followup"
    repo_dest.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(out_path, repo_dest / "pc_resolution_results.json")
    print(f"  Copied to {repo_dest / 'pc_resolution_results.json'}")


if __name__ == "__main__":
    main()
