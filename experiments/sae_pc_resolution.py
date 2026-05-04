#!/usr/bin/env python3
"""
SAE PC Resolution: test whether projecting feature importance onto data PCs
produces reproducible importance rankings across SAE training seeds.

Theory predicts: the reproducible subspace has dim ≤ d = 768.
Data PCs provide a seed-invariant 768-dim basis for this subspace.
If correct, per-PC importance should be reproducible (ρ >> 0.5).

Usage: CUDA_VISIBLE_DEVICES=0 python3 sae_pc_resolution.py
"""
import os
import sys
import json
import torch
import numpy as np
from pathlib import Path
from itertools import combinations
from scipy.stats import spearmanr

EXPERIMENT_DIR = Path(os.environ.get("EXPERIMENT_DIR", os.path.expanduser("~/SageMaker/experiments")))
RESULTS_DIR = EXPERIMENT_DIR / "results" / "sae_pc_resolution"
SAE_DIR = EXPERIMENT_DIR / "results" / "sae"
HF_HOME = os.environ.get("HF_HOME", os.path.expanduser("~/SageMaker/.cache/huggingface"))
os.environ["HF_HOME"] = HF_HOME

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")


def load_model(seed: int):
    """Load a trained GPT-2-small model."""
    from transformers import GPT2LMHeadModel, GPT2Config
    config = GPT2Config()
    model = GPT2LMHeadModel(config).to(device).eval()
    ckpt_path = EXPERIMENT_DIR / f"checkpoints/seed_{seed}/model_final.pt"
    if not ckpt_path.exists():
        ckpt_path = EXPERIMENT_DIR / f"checkpoints/seed_{seed}/checkpoint_step_50000.pt"
    state = torch.load(ckpt_path, map_location=device)
    if "model_state_dict" in state:
        model.load_state_dict(state["model_state_dict"])
    else:
        model.load_state_dict(state)
    return model


def compute_data_pcs(model, n_batches=50, batch_size=8, seq_len=256, target_layer=6):
    """
    Compute PCA of layer-6 activations on the model's own data.
    Returns: U (768 × 768 orthogonal matrix of PCs), S (singular values)
    """
    from transformers import GPT2Tokenizer
    from datasets import load_dataset

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    # Use a fixed eval set for seed-invariance
    ds = load_dataset("openwebtext", split="train", streaming=True, trust_remote_code=True)

    activations = []
    hook_output = {}

    def hook_fn(module, input, output):
        hook_output["act"] = output[0].detach()  # (batch, seq, 768)

    # Hook on layer 6 output
    handle = model.transformer.h[target_layer].register_forward_hook(hook_fn)

    n_collected = 0
    for i, example in enumerate(ds):
        if n_collected >= n_batches * batch_size:
            break
        tokens = tokenizer(example["text"], return_tensors="pt", max_length=seq_len,
                           truncation=True, padding="max_length")["input_ids"].to(device)
        if tokens.shape[1] < seq_len:
            continue
        with torch.no_grad():
            model(tokens)
        # Take mean over sequence positions
        act = hook_output["act"].mean(dim=1).cpu().numpy()  # (1, 768)
        activations.append(act[0])
        n_collected += 1

    handle.remove()

    # PCA via SVD
    X = np.array(activations)  # (n_samples, 768)
    X_centered = X - X.mean(axis=0)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    # Vt rows are PCs (768 × 768)
    return Vt.T, S  # Return as columns: (768, 768)


def load_sae_decoder(seed: int):
    """Load a trained SAE decoder matrix."""
    # Check multiple possible locations
    for pattern in [
        SAE_DIR / f"sae_seed_{seed}" / "decoder.npy",
        SAE_DIR / f"sae_seed_{seed}" / "model.pt",
        SAE_DIR / f"seed_{seed}" / "decoder.npy",
        SAE_DIR / f"seed_{seed}" / "model.pt",
    ]:
        if pattern.exists():
            if pattern.suffix == ".npy":
                return np.load(pattern)
            else:
                state = torch.load(pattern, map_location="cpu")
                # TopK SAE: decoder is normalized
                if "decoder.weight" in state:
                    D = state["decoder.weight"].numpy()  # (d_sae, d_model) or (d_model, d_sae)
                    if D.shape[0] == 768:
                        return D.T  # Want (d_sae, d_model) = (6144, 768)
                    return D
                elif "W_dec" in state:
                    return state["W_dec"].numpy()
                else:
                    # Try to find any decoder-like tensor
                    for k, v in state.items():
                        if "dec" in k.lower() and v.ndim == 2:
                            D = v.numpy()
                            if D.shape == (6144, 768):
                                return D
                            elif D.shape == (768, 6144):
                                return D.T
                    raise ValueError(f"Cannot find decoder in {pattern}: keys={list(state.keys())}")

    # Try loading full model state
    for seed_dir in [SAE_DIR / f"sae_seed_{seed}", SAE_DIR / f"seed_{seed}"]:
        if seed_dir.exists():
            for f in seed_dir.iterdir():
                if f.suffix in [".pt", ".pth"]:
                    state = torch.load(f, map_location="cpu")
                    if isinstance(state, dict):
                        for k, v in state.items():
                            if hasattr(v, 'shape') and v.ndim == 2:
                                if v.shape == (6144, 768) or v.shape == (768, 6144):
                                    D = v.numpy() if hasattr(v, 'numpy') else np.array(v)
                                    return D if D.shape == (6144, 768) else D.T

    raise FileNotFoundError(f"Cannot find SAE decoder for seed {seed} in {SAE_DIR}")


def compute_feature_importance(decoder, activations_for_importance=None):
    """
    Compute feature importance as decoder column L2 norm (proxy for
    reconstruction contribution). This is seed-specific but doesn't
    require running the SAE encoder.
    """
    # Simple importance: L2 norm of each decoder column
    # decoder shape: (6144, 768)
    return np.linalg.norm(decoder, axis=1)  # (6144,)


def pc_importance(decoder, importance, pcs):
    """
    Project feature importance onto data PCs.

    For each PC direction u_j, compute how much total importance is
    aligned with that direction:
      w[j] = sum_i importance[i] * (decoder[i] · u_j)²

    Args:
        decoder: (6144, 768) decoder matrix
        importance: (6144,) per-feature importance
        pcs: (768, 768) PC matrix (columns are PCs)

    Returns:
        (768,) PC-projected importance (seed-invariant basis)
    """
    # decoder @ pcs gives (6144, 768) alignment of each feature with each PC
    alignment = decoder @ pcs  # (6144, 768)
    # Squared alignment = fraction of feature pointing in PC direction
    alignment_sq = alignment ** 2  # (6144, 768)
    # Normalize rows (each feature's alignments should sum to 1 if decoder is unit-norm)
    row_norms = alignment_sq.sum(axis=1, keepdims=True)
    row_norms = np.maximum(row_norms, 1e-10)
    alignment_frac = alignment_sq / row_norms  # (6144, 768)
    # Weighted sum: importance of PC-j = sum of feature importances weighted by alignment
    w = (importance[:, None] * alignment_frac).sum(axis=0)  # (768,)
    return w


def main():
    print("=" * 60)
    print("SAE PC RESOLUTION TEST")
    print("=" * 60)
    print()

    # Step 1: Compute data PCs (seed-invariant)
    print("Step 1: Computing data PCs from model activations...")
    model = load_model(seed=0)
    pcs, singular_values = compute_data_pcs(model, n_batches=200)
    print(f"  PCs shape: {pcs.shape}")
    print(f"  Top 10 singular values: {singular_values[:10].round(2)}")
    var_explained = singular_values**2 / (singular_values**2).sum()
    print(f"  Variance explained (top 10): {var_explained[:10].round(3)}")
    del model
    torch.cuda.empty_cache()

    # Step 2: Load all SAE decoders and compute importance
    print("\nStep 2: Loading SAE decoders and computing importance...")
    n_seeds = 10
    decoders = []
    importances = []
    pc_importances = []

    for seed in range(n_seeds):
        try:
            D = load_sae_decoder(seed)
            print(f"  Seed {seed}: decoder shape {D.shape}")
            decoders.append(D)

            # Feature importance (L2 norm of decoder columns)
            imp = compute_feature_importance(D)
            importances.append(imp)

            # PC-projected importance
            w = pc_importance(D, imp, pcs)
            pc_importances.append(w)
            print(f"    PC-importance: top-5 PCs account for {w[:5].sum()/w.sum()*100:.1f}% of total")
        except (FileNotFoundError, ValueError) as e:
            print(f"  Seed {seed}: FAILED - {e}")
            continue

    if len(pc_importances) < 2:
        print("\nERROR: Need at least 2 SAE decoders. Check SAE_DIR paths.")
        print(f"  Searched in: {SAE_DIR}")
        print(f"  Available: {list(SAE_DIR.iterdir()) if SAE_DIR.exists() else 'DIR NOT FOUND'}")
        sys.exit(1)

    # Step 3: Compute reproducibility
    print(f"\nStep 3: Computing reproducibility ({len(pc_importances)} seeds)...")
    n_loaded = len(pc_importances)

    # Raw importance Spearman (6144-dim)
    raw_rhos = [spearmanr(importances[i], importances[j])[0]
                for i, j in combinations(range(n_loaded), 2)]

    # PC-projected importance Spearman (768-dim)
    pc_rhos = [spearmanr(pc_importances[i], pc_importances[j])[0]
               for i, j in combinations(range(n_loaded), 2)]

    # Top-k PC subsets
    pc_rhos_by_k = {}
    for k in [10, 50, 100, 200, 400, 768]:
        rhos_k = [spearmanr(pc_importances[i][:k], pc_importances[j][:k])[0]
                  for i, j in combinations(range(n_loaded), 2)]
        pc_rhos_by_k[k] = np.mean(rhos_k)

    print(f"\n{'=' * 60}")
    print(f"RESULTS")
    print(f"{'=' * 60}")
    print(f"\n  Raw feature importance (6144-dim):")
    print(f"    Mean Spearman: {np.mean(raw_rhos):.3f} [{np.min(raw_rhos):.3f}, {np.max(raw_rhos):.3f}]")
    print(f"\n  PC-projected importance (768-dim):")
    print(f"    Mean Spearman: {np.mean(pc_rhos):.3f} [{np.min(pc_rhos):.3f}, {np.max(pc_rhos):.3f}]")
    print(f"\n  PC-projected by dimensionality:")
    for k, rho in sorted(pc_rhos_by_k.items()):
        print(f"    Top-{k:>3} PCs: ρ = {rho:.3f}")

    # Compute improvement
    improvement = np.mean(pc_rhos) - np.mean(raw_rhos)
    print(f"\n  Improvement (PC over raw): {improvement:+.3f}")
    print(f"  Ratio: {np.mean(pc_rhos)/max(np.mean(raw_rhos), 0.001):.2f}x")

    # For comparison with known results
    print(f"\n  Reference (from prior experiments):")
    print(f"    Matched importance (Hungarian): ρ ≈ 0.500")
    print(f"    G-invariant (attention heads): ρ ≈ 0.873")
    print(f"    Theoretical ceiling: C = 768/6144 = 12.5%")

    # Save results
    results = {
        "method": "PC projection of SAE feature importance",
        "n_seeds": n_loaded,
        "d_model": 768,
        "d_sae": 6144,
        "raw_importance": {
            "mean_spearman": float(np.mean(raw_rhos)),
            "all_spearman": [float(r) for r in raw_rhos],
        },
        "pc_projected_importance": {
            "mean_spearman": float(np.mean(pc_rhos)),
            "all_spearman": [float(r) for r in pc_rhos],
        },
        "pc_by_dimensionality": {str(k): float(v) for k, v in pc_rhos_by_k.items()},
        "improvement_over_raw": float(improvement),
        "pcs_variance_explained_top10": var_explained[:10].tolist(),
    }

    out_path = RESULTS_DIR / "pc_resolution_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Saved to {out_path}")

    # Copy to repo
    repo_dir = Path(__file__).parent.parent
    dest = repo_dir / "docs" / "gpt2-experiment-results" / "sae_followup"
    dest.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(out_path, dest / "pc_resolution_results.json")
    print(f"  Copied to {dest / 'pc_resolution_results.json'}")


if __name__ == "__main__":
    main()
