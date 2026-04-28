#!/usr/bin/env python3
"""
Activation patching + full statistical analysis for GPT-2-from-scratch models.

Usage:
    CUDA_VISIBLE_DEVICES=0 python gpt2_evaluate.py --seed 0
    python gpt2_evaluate.py --analyze   # run analysis after all seeds patched

Two phases:
  1. Patching: for each model, zero out each of 156 components and measure loss change.
  2. Analysis: compute all statistics, compare with predictions, generate results JSON.

Crash recovery: checks for per-seed DONE markers before running.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F
from scipy import stats
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm
from transformers import GPT2Config, GPT2LMHeadModel

from config import (GPT2TrainConfig, PatchConfig, StatsConfig,
                    CHECKPOINT_DIR, RESULTS_DIR, EVAL_DIR, DATA_DIR)

CFG = GPT2TrainConfig()
PCFG = PatchConfig()
SCFG = StatsConfig()


# ── Eval data ─────────────────────────────────────────────────────────────────

def prepare_eval_set():
    """Create a fixed evaluation set shared across all models. Saved to disk."""
    eval_path = EVAL_DIR / "eval_sequences.npy"
    if eval_path.exists():
        return np.load(eval_path)

    print("Preparing fixed evaluation set...")
    val_path = DATA_DIR / "openwebtext_val.bin"
    data = np.memmap(str(val_path), dtype=np.uint16, mode='r')

    n = PCFG.n_eval_sequences
    sl = PCFG.eval_seq_length
    sequences = np.zeros((n, sl), dtype=np.int64)

    # Deterministic, evenly-spaced sampling from validation set
    stride = max(1, (len(data) - sl) // n)
    for i in range(n):
        start = i * stride
        sequences[i] = data[start:start + sl].astype(np.int64)

    np.save(eval_path, sequences)
    print(f"  Saved {n} sequences of length {sl} to {eval_path}")
    return sequences


# ── Activation patching ──────────────────────────────────────────────────────

def get_component_name(layer: int, component_type: str, head_idx: Optional[int] = None) -> str:
    if component_type == "head":
        return f"L{layer}H{head_idx}"
    return f"L{layer}MLP"


def patch_single_model(seed: int, device: torch.device):
    """Run weight zeroing and mean ablation for all 156 components of one model."""
    patch_dir = RESULTS_DIR / f"patch_seed{seed}"
    patch_dir.mkdir(parents=True, exist_ok=True)

    done_marker = patch_dir / "DONE"
    if done_marker.exists():
        print(f"Seed {seed}: patching already complete")
        return

    # Load model
    model_path = CHECKPOINT_DIR / f"gpt2_seed{seed}" / "model_final.pt"
    config = GPT2Config(
        vocab_size=CFG.vocab_size, n_positions=CFG.block_size,
        n_embd=CFG.n_embd, n_layer=CFG.n_layer, n_head=CFG.n_head,
        resid_pdrop=0.0, embd_pdrop=0.0, attn_pdrop=0.0,
    )
    model = GPT2LMHeadModel(config)
    model.load_state_dict(torch.load(model_path, map_location="cpu", weights_only=True))
    model = model.to(device).eval()

    # Load eval sequences
    sequences = prepare_eval_set()
    eval_tokens = torch.from_numpy(sequences).to(device)

    # ── Per-sequence baseline loss (needed for split-half) ──────────────
    print(f"Seed {seed}: computing per-sequence baseline loss...")
    with torch.no_grad(), torch.amp.autocast("cuda", dtype=torch.bfloat16):
        per_seq_baseline = []
        for i in range(0, len(eval_tokens), 32):
            batch = eval_tokens[i:i+32]
            logits = model(batch).logits[:, :-1, :]
            targets = batch[:, 1:]
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)),
                                   targets.reshape(-1), reduction='none')
            per_seq_baseline.append(loss.reshape(targets.shape).mean(dim=1).cpu())
        per_seq_baseline = torch.cat(per_seq_baseline)  # [n_eval]
        baseline_loss = per_seq_baseline.mean().item()
    print(f"  Baseline loss: {baseline_loss:.4f} (PPL {math.exp(baseline_loss):.1f})")

    # ── Collect mean activations for mean ablation ──────────────────────
    # IMPORTANT: Hook c_proj INPUT (= concatenated head outputs BEFORE projection)
    # NOT the attn module output (which is AFTER c_proj mixing).
    print(f"Seed {seed}: collecting mean activations for mean ablation...")
    mean_head_outputs = {}  # {(layer, head): tensor of shape [d_head]}
    mean_mlp_outputs = {}   # {layer: tensor of shape [n_embd]}

    hooks = []
    head_accum = {}
    mlp_accum = {}

    def make_cproj_input_hook(layer_idx):
        """Hook c_proj to capture its INPUT = concatenated head outputs BEFORE projection."""
        def hook(module, input, output):
            pre_proj = input[0]  # [batch, seq, n_embd] — heads concatenated, before projection
            d_head = CFG.n_embd // CFG.n_head
            for h in range(CFG.n_head):
                head_out = pre_proj[:, :, h*d_head:(h+1)*d_head]
                key = (layer_idx, h)
                if key not in head_accum:
                    head_accum[key] = {"sum": torch.zeros(d_head, device=head_out.device,
                                                          dtype=torch.float32), "n": 0}
                head_accum[key]["sum"] += head_out.float().sum(dim=(0, 1))
                head_accum[key]["n"] += head_out.shape[0] * head_out.shape[1]
        return hook

    def make_mlp_hook(layer_idx):
        def hook(module, input, output):
            key = layer_idx
            if key not in mlp_accum:
                mlp_accum[key] = {"sum": torch.zeros(CFG.n_embd, device=output.device,
                                                     dtype=torch.float32), "n": 0}
            mlp_accum[key]["sum"] += output.float().sum(dim=(0, 1))
            mlp_accum[key]["n"] += output.shape[0] * output.shape[1]
        return hook

    for layer in range(CFG.n_layer):
        # Hook c_proj INPUT for heads (not attn module output!)
        hooks.append(model.transformer.h[layer].attn.c_proj.register_forward_hook(
            make_cproj_input_hook(layer)))
        hooks.append(model.transformer.h[layer].mlp.register_forward_hook(
            make_mlp_hook(layer)))

    with torch.no_grad(), torch.amp.autocast("cuda", dtype=torch.bfloat16):
        for i in range(0, len(eval_tokens), 32):  # use ALL eval tokens for stable means
            model(eval_tokens[i:i+32])

    for h in hooks:
        h.remove()

    for key, val in head_accum.items():
        mean_head_outputs[key] = val["sum"] / val["n"]
    for key, val in mlp_accum.items():
        mean_mlp_outputs[key] = val["sum"] / val["n"]

    # ── Helper: run patched forward pass, return per-sequence losses ───
    def patched_forward(model, eval_tokens):
        """Run forward pass, return per-sequence mean loss tensor."""
        per_seq = []
        with torch.no_grad(), torch.amp.autocast("cuda", dtype=torch.bfloat16):
            for i in range(0, len(eval_tokens), 32):
                batch = eval_tokens[i:i+32]
                logits = model(batch).logits[:, :-1, :]
                targets = batch[:, 1:]
                loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)),
                                       targets.reshape(-1), reduction='none')
                per_seq.append(loss.reshape(targets.shape).mean(dim=1).cpu())
        return torch.cat(per_seq)

    # ── Patching (both methods, with per-sequence losses for split-half) ─
    results = {
        "seed": seed,
        "baseline_loss": baseline_loss,
        "baseline_ppl": math.exp(baseline_loss),
        "components": {},
        "split_half_reliability": {},
    }
    half = len(eval_tokens) // 2

    for method in PCFG.methods:
        print(f"Seed {seed}: patching with {method}...")
        importance = {}
        # Accumulate per-sequence importance for split-half (not saved to JSON)
        per_seq_imp_a = {}  # first half of eval sequences
        per_seq_imp_b = {}  # second half

        for layer in range(CFG.n_layer):
            d_head = CFG.n_embd // CFG.n_head
            attn = model.transformer.h[layer].attn

            for head in range(CFG.n_head):
                name = get_component_name(layer, "head", head)
                orig_c_attn_w = attn.c_attn.weight.data.clone()
                orig_c_attn_b = attn.c_attn.bias.data.clone()
                orig_c_proj_w = attn.c_proj.weight.data.clone()
                orig_c_proj_b = attn.c_proj.bias.data.clone()  # MUST clone bias too

                if method == "weight_zeroing":
                    for qkv_offset in [0, CFG.n_embd, 2 * CFG.n_embd]:
                        s = qkv_offset + head * d_head
                        e = s + d_head
                        attn.c_attn.weight.data[:, s:e] = 0
                        attn.c_attn.bias.data[s:e] = 0
                    attn.c_proj.weight.data[head * d_head:(head + 1) * d_head, :] = 0

                elif method == "mean_ablation":
                    for qkv_offset in [0, CFG.n_embd, 2 * CFG.n_embd]:
                        s = qkv_offset + head * d_head
                        e = s + d_head
                        attn.c_attn.weight.data[:, s:e] = 0
                        attn.c_attn.bias.data[s:e] = 0
                    attn.c_proj.weight.data[head * d_head:(head + 1) * d_head, :] = 0
                    # Add mean head contribution to residual via c_proj bias.
                    # mean_out is head h's mean output BEFORE c_proj (from c_proj input hook).
                    # Contribution = mean_out @ c_proj.weight[h*d_head:(h+1)*d_head, :]
                    mean_out = mean_head_outputs[(layer, head)].to(attn.c_proj.bias.device)
                    mean_contrib = mean_out @ orig_c_proj_w[head * d_head:(head + 1) * d_head, :]
                    attn.c_proj.bias.data += mean_contrib

                per_seq_patched = patched_forward(model, eval_tokens)
                per_seq_diff = (per_seq_patched - per_seq_baseline).numpy()
                importance[name] = float(per_seq_diff.mean())
                per_seq_imp_a[name] = float(per_seq_diff[:half].mean())
                per_seq_imp_b[name] = float(per_seq_diff[half:].mean())

                # Restore ALL weights + bias
                attn.c_attn.weight.data = orig_c_attn_w
                attn.c_attn.bias.data = orig_c_attn_b
                attn.c_proj.weight.data = orig_c_proj_w
                attn.c_proj.bias.data = orig_c_proj_b

            # ── MLP ───────────────────────────────────────────────────────
            name = get_component_name(layer, "mlp")
            mlp = model.transformer.h[layer].mlp
            orig_fc_w = mlp.c_fc.weight.data.clone()
            orig_fc_b = mlp.c_fc.bias.data.clone()
            orig_proj_w = mlp.c_proj.weight.data.clone()
            orig_proj_b = mlp.c_proj.bias.data.clone()

            if method == "weight_zeroing":
                mlp.c_fc.weight.data.zero_()
                mlp.c_fc.bias.data.zero_()
                mlp.c_proj.weight.data.zero_()
                mlp.c_proj.bias.data.zero_()
            elif method == "mean_ablation":
                mlp.c_fc.weight.data.zero_()
                mlp.c_fc.bias.data.zero_()
                mlp.c_proj.weight.data.zero_()
                # Replace MLP output with its mean via bias
                mlp.c_proj.bias.data = mean_mlp_outputs[layer].to(mlp.c_proj.bias.device)

            per_seq_patched = patched_forward(model, eval_tokens)
            per_seq_diff = (per_seq_patched - per_seq_baseline).numpy()
            importance[name] = float(per_seq_diff.mean())
            per_seq_imp_a[name] = float(per_seq_diff[:half].mean())
            per_seq_imp_b[name] = float(per_seq_diff[half:].mean())

            mlp.c_fc.weight.data = orig_fc_w
            mlp.c_fc.bias.data = orig_fc_b
            mlp.c_proj.weight.data = orig_proj_w
            mlp.c_proj.bias.data = orig_proj_b

            if (layer + 1) % 3 == 0:
                print(f"    Layer {layer+1}/12 complete")

        results["components"][method] = importance
        print(f"  {method}: top = {max(importance, key=importance.get)} "
              f"({max(importance.values()):.4f})")

        # ── Split-half reliability (computed inline, not persisted) ────
        imp_a = [per_seq_imp_a[n] for n in importance]
        imp_b = [per_seq_imp_b[n] for n in importance]
        rho_sh, _ = stats.spearmanr(imp_a, imp_b)
        rho_p, _ = stats.pearsonr(imp_a, imp_b)
        results["split_half_reliability"][method] = {
            "spearman": float(rho_sh), "pearson": float(rho_p)
        }
        print(f"  {method} split-half: Spearman={rho_sh:.3f}, Pearson={rho_p:.4f}")

    # ── Save results ──────────────────────────────────────────────────────
    tmp = patch_dir / "results.json.tmp"
    with open(tmp, "w") as f:
        json.dump(results, f, indent=2)
    tmp.rename(patch_dir / "results.json")
    done_marker.write_text("complete")
    print(f"Seed {seed}: patching complete. Results saved to {patch_dir / 'results.json'}")


# ── Analysis ──────────────────────────────────────────────────────────────────

def load_all_results():
    """Load patching results for all seeds."""
    results = {}
    for seed in range(CFG.n_seeds):
        path = RESULTS_DIR / f"patch_seed{seed}" / "results.json"
        if not path.exists():
            print(f"WARNING: results missing for seed {seed}")
            continue
        with open(path) as f:
            results[seed] = json.load(f)
    return results


def importance_vector(result: dict, method: str = "weight_zeroing") -> np.ndarray:
    """Extract importance vector in canonical order: L0H0..L0H11, L0MLP, L1H0..."""
    components = result["components"][method]
    vec = []
    for layer in range(CFG.n_layer):
        for head in range(CFG.n_head):
            vec.append(components[f"L{layer}H{head}"])
        vec.append(components[f"L{layer}MLP"])
    return np.array(vec)


def g_invariant_projection(vec: np.ndarray) -> np.ndarray:
    """Project importance vector to G-invariant subspace.
    For S_12^12: average heads within each layer, keep MLPs as-is.
    Input: 156-dim vector (12 layers * 13 components each).
    Output: 24-dim vector (12 head-averages + 12 MLPs).
    """
    proj = []
    for layer in range(12):
        base = layer * 13
        head_avg = vec[base:base + 12].mean()
        mlp = vec[base + 12]
        proj.append(head_avg)
        proj.append(mlp)
    return np.array(proj)


def compute_flip_rates(vectors: list[np.ndarray]) -> dict:
    """Compute within-layer and between-group flip rates across all model pairs.

    Bootstrap CIs resample at the MODEL level (cluster bootstrap) to account
    for non-independence of pairs sharing a model.
    """
    n_models = len(vectors)

    # Compute per-pair flip rates (for Cohen's d and cluster bootstrap)
    pair_within = []   # one value per model pair
    pair_between = []
    all_within = []    # all individual flip indicators (for point estimate)
    all_between = []

    for i in range(n_models):
        for j in range(i + 1, n_models):
            vi, vj = vectors[i], vectors[j]
            w_flips, b_flips = [], []

            for layer in range(12):
                base = layer * 13
                heads_i = vi[base:base + 12]
                heads_j = vj[base:base + 12]
                for h1 in range(12):
                    for h2 in range(h1 + 1, 12):
                        flip = float((heads_i[h1] > heads_i[h2]) != (heads_j[h1] > heads_j[h2]))
                        w_flips.append(flip)
                        all_within.append(flip)

                mlp_i = vi[base + 12]
                mlp_j = vj[base + 12]
                for h in range(12):
                    flip = float((vi[base + h] > mlp_i) != (vj[base + h] > mlp_j))
                    b_flips.append(flip)
                    all_between.append(flip)

            pair_within.append(np.mean(w_flips))
            pair_between.append(np.mean(b_flips))

    # Point estimates from all indicators
    within_mean = float(np.mean(all_within))
    between_mean = float(np.mean(all_between))

    # Cluster bootstrap: resample MODELS, recompute all pairs within resample
    rng = np.random.RandomState(42)
    boot_within, boot_between = [], []
    for _ in range(SCFG.n_bootstrap):
        model_idx = rng.choice(n_models, size=n_models, replace=True)
        # Recompute pairs within the resampled model set
        w_vals, b_vals = [], []
        for ii in range(n_models):
            for jj in range(ii + 1, n_models):
                mi, mj = model_idx[ii], model_idx[jj]
                if mi == mj:
                    continue  # skip self-pairs
                vi, vj = vectors[mi], vectors[mj]
                for layer in range(12):
                    base = layer * 13
                    hi, hj = vi[base:base+12], vj[base:base+12]
                    for h1 in range(12):
                        for h2 in range(h1+1, 12):
                            w_vals.append(float((hi[h1]>hi[h2]) != (hj[h1]>hj[h2])))
                    mi_mlp, mj_mlp = vi[base+12], vj[base+12]
                    for h in range(12):
                        b_vals.append(float((vi[base+h]>mi_mlp) != (vj[base+h]>mj_mlp)))
        boot_within.append(np.mean(w_vals) if w_vals else within_mean)
        boot_between.append(np.mean(b_vals) if b_vals else between_mean)

    within_ci = [float(np.percentile(boot_within, q)) for q in [2.5, 97.5]]
    between_ci = [float(np.percentile(boot_between, q)) for q in [2.5, 97.5]]

    # Cohen's d from per-pair rates (the right unit of analysis)
    pair_w = np.array(pair_within)
    pair_b = np.array(pair_between)
    pooled_sd = math.sqrt((pair_w.var() + pair_b.var()) / 2)
    cohens_d = float(abs(pair_w.mean() - pair_b.mean()) / pooled_sd) if pooled_sd > 0 else float('inf')

    # Mann-Whitney test on per-pair rates
    if pair_b.std() > 0:
        mw_stat, mw_p = stats.mannwhitneyu(pair_w, pair_b, alternative='two-sided')
    else:
        mw_p = 0.0  # between is constant (all zeros)

    return {
        "within_layer": within_mean,
        "within_ci_95": within_ci,
        "head_vs_mlp": between_mean,
        "between_ci_95": between_ci,
        "cohens_d": cohens_d,
        "mann_whitney_p": float(mw_p),
        "per_pair_within": [float(x) for x in pair_within],
        "per_pair_between": [float(x) for x in pair_between],
    }


def random_projection_test(vectors: list[np.ndarray], actual_ginv_rho: float) -> dict:
    """Test whether G-invariant rho is significantly above random projections."""
    n_components = len(vectors[0])
    n_invariant = PCFG.n_invariant
    null_rhos = []

    for _ in range(SCFG.n_random_projections):
        proj_matrix = np.random.randn(n_components, n_invariant)
        proj_matrix /= np.linalg.norm(proj_matrix, axis=0, keepdims=True)
        projected = [v @ proj_matrix for v in vectors]
        rhos = []
        for i in range(len(projected)):
            for j in range(i + 1, len(projected)):
                rho, _ = stats.spearmanr(projected[i], projected[j])
                rhos.append(rho)
        null_rhos.append(np.mean(rhos))

    null_arr = np.array(null_rhos)
    p_value = float(np.mean(null_arr >= actual_ginv_rho))

    return {
        "test_type": "random_projection",
        "actual": actual_ginv_rho,
        "null_mean": float(null_arr.mean()),
        "null_std": float(null_arr.std()),
        "p_value": max(p_value, 1.0 / SCFG.n_random_projections),
        "percentile": float(stats.percentileofscore(null_arr, actual_ginv_rho)),
    }


def random_grouping_test(vectors: list[np.ndarray], actual_ginv_rho: float) -> dict:
    """Test whether LAYER grouping is better than random groupings of same size.

    Null: randomly assign 144 heads to 12 equal-size groups, average within groups,
    keep 12 MLPs as-is, compute mean pairwise Spearman. This tests whether the
    layer structure specifically matters, not just any grouping.
    """
    null_rhos = []
    n_heads = 144  # 12 layers * 12 heads
    group_size = 12

    for _ in range(SCFG.n_random_projections):
        # Random assignment of 144 heads to 12 groups of 12
        perm = np.random.permutation(n_heads)
        groups = perm.reshape(12, group_size)

        projected = []
        for v in vectors:
            # Extract heads only (skip MLPs)
            heads = []
            mlps = []
            for layer in range(12):
                base = layer * 13
                heads.extend(v[base:base + 12])
                mlps.append(v[base + 12])
            heads = np.array(heads)

            # Average within random groups
            group_avgs = [heads[g].mean() for g in groups]
            proj = group_avgs + mlps
            projected.append(np.array(proj))

        rhos = []
        for i in range(len(projected)):
            for j in range(i + 1, len(projected)):
                rho, _ = stats.spearmanr(projected[i], projected[j])
                rhos.append(rho)
        null_rhos.append(np.mean(rhos))

    null_arr = np.array(null_rhos)
    p_value = float(np.mean(null_arr >= actual_ginv_rho))

    return {
        "test_type": "random_grouping",
        "actual": actual_ginv_rho,
        "null_mean": float(null_arr.mean()),
        "null_std": float(null_arr.std()),
        "p_value": max(p_value, 1.0 / SCFG.n_random_projections),
        "percentile": float(stats.percentileofscore(null_arr, actual_ginv_rho)),
    }


def run_full_analysis():
    """Run complete statistical analysis across all seeds."""
    print("=" * 70)
    print("FULL ANALYSIS: GPT-2-small from scratch")
    print("=" * 70)

    all_results = load_all_results()
    if len(all_results) < CFG.n_seeds:
        print(f"WARNING: only {len(all_results)}/{CFG.n_seeds} seeds available")

    seeds = sorted(all_results.keys())
    output = {"n_seeds": len(seeds), "seeds": seeds}

    for method in PCFG.methods:
        print(f"\n{'='*40} {method} {'='*40}")

        # ── Extract importance vectors ────────────────────────────────────
        vectors = [importance_vector(all_results[s], method) for s in seeds]
        ginv_vectors = [g_invariant_projection(v) for v in vectors]

        # ── Perplexity ────────────────────────────────────────────────────
        ppls = [all_results[s]["baseline_ppl"] for s in seeds]
        ppl_mean = np.mean(ppls)
        ppl_cv = np.std(ppls) / ppl_mean * 100
        output["perplexity"] = {
            "mean": float(ppl_mean), "cv_pct": float(ppl_cv),
            "per_model": [float(p) for p in ppls]
        }
        print(f"PPL: mean={ppl_mean:.1f}, CV={ppl_cv:.2f}%")

        # ── Full pairwise Spearman ────────────────────────────────────────
        full_rhos = []
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                rho, _ = stats.spearmanr(vectors[i], vectors[j])
                full_rhos.append(rho)
        full_rho_mean = np.mean(full_rhos)
        full_rho_range = [float(min(full_rhos)), float(max(full_rhos))]
        print(f"Full rho: {full_rho_mean:.3f} [range: {full_rho_range[0]:.3f}-{full_rho_range[1]:.3f}]")

        # ── G-invariant Spearman ──────────────────────────────────────────
        ginv_rhos = []
        for i in range(len(ginv_vectors)):
            for j in range(i + 1, len(ginv_vectors)):
                rho, _ = stats.spearmanr(ginv_vectors[i], ginv_vectors[j])
                ginv_rhos.append(rho)
        ginv_rho_mean = np.mean(ginv_rhos)
        ginv_rho_range = [float(min(ginv_rhos)), float(max(ginv_rhos))]
        print(f"G-inv rho: {ginv_rho_mean:.3f} [range: {ginv_rho_range[0]:.3f}-{ginv_rho_range[1]:.3f}]")

        # ── Heads-only analysis ───────────────────────────────────────────
        heads_only = []
        heads_avg = []
        for v in vectors:
            h = []
            ha = []
            for layer in range(12):
                base = layer * 13
                h.extend(v[base:base + 12])
                ha.append(v[base:base + 12].mean())
            heads_only.append(np.array(h))
            heads_avg.append(np.array(ha))

        heads_raw_rhos = []
        heads_avg_rhos = []
        for i in range(len(heads_only)):
            for j in range(i + 1, len(heads_only)):
                r1, _ = stats.spearmanr(heads_only[i], heads_only[j])
                r2, _ = stats.spearmanr(heads_avg[i], heads_avg[j])
                heads_raw_rhos.append(r1)
                heads_avg_rhos.append(r2)

        head_lift = np.mean(heads_avg_rhos) - np.mean(heads_raw_rhos)
        print(f"Heads raw rho: {np.mean(heads_raw_rhos):.3f}, "
              f"avg rho: {np.mean(heads_avg_rhos):.3f}, lift: {head_lift:.3f}")

        # ── Flip rates (with cluster bootstrap CIs and Cohen's d) ─────────
        flips = compute_flip_rates(vectors)
        print(f"Within-layer flip: {flips['within_layer']:.3f} "
              f"[{flips['within_ci_95'][0]:.3f}, {flips['within_ci_95'][1]:.3f}]")
        print(f"Head-vs-MLP flip: {flips['head_vs_mlp']:.3f} "
              f"[{flips['between_ci_95'][0]:.3f}, {flips['between_ci_95'][1]:.3f}]")
        print(f"Cohen's d (within vs between, per-pair rates): {flips['cohens_d']:.1f}")
        print(f"Mann-Whitney p: {flips['mann_whitney_p']:.2e}")

        # ── Null distribution tests ───────────────────────────────────────
        rp_test = random_projection_test(vectors, ginv_rho_mean)
        print(f"Random projection test: p={rp_test['p_value']:.4f}, "
              f"actual={rp_test['actual']:.3f}, null_mean={rp_test['null_mean']:.3f}")
        rg_test = random_grouping_test(vectors, ginv_rho_mean)
        print(f"Random grouping test: p={rg_test['p_value']:.4f}, "
              f"actual={rg_test['actual']:.3f}, null_mean={rg_test['null_mean']:.3f}")

        # ── Per-seed top component (S_12 realization check) ───────────────
        top_heads_per_seed = {}
        for idx, s in enumerate(seeds):
            v = vectors[idx]
            # Find top head (excluding MLPs) in each layer
            for layer in range(12):
                base = layer * 13
                heads = v[base:base + 12]
                top_h = int(np.argmax(heads))
                top_heads_per_seed.setdefault(layer, []).append(
                    {"seed": s, "head": top_h, "importance": float(heads[top_h]),
                     "name": f"L{layer}H{top_h}"})

        # Count distinct top heads per layer
        distinct_per_layer = {}
        for layer in range(12):
            tops = set(entry["head"] for entry in top_heads_per_seed[layer])
            distinct_per_layer[layer] = len(tops)
        print(f"Distinct top heads per layer: {distinct_per_layer}")

        # ── Assemble method results ───────────────────────────────────────
        output[method] = {
            "full_agreement": {
                "mean_spearman": float(full_rho_mean),
                "range": full_rho_range,
                "all_spearman": [float(r) for r in full_rhos],
            },
            "g_invariant": {
                "mean_spearman": float(ginv_rho_mean),
                "range": ginv_rho_range,
            },
            "excl_mlp": {
                "heads_raw_rho": float(np.mean(heads_raw_rhos)),
                "heads_avg_rho": float(np.mean(heads_avg_rhos)),
                "head_lift": float(head_lift),
            },
            "flip_rates": flips,
            "random_projection_test": rp_test,
            "random_grouping_test": rg_test,
            "top_heads_per_seed": top_heads_per_seed,
            "distinct_top_heads_per_layer": distinct_per_layer,
            "importance_vectors": [v.tolist() for v in vectors],
        }

    # ── Compare with predictions ──────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PREDICTION COMPARISON")
    print("=" * 70)

    pred_path = Path(__file__).parent / "predictions.json"
    pred_hash = hashlib.sha256(pred_path.read_bytes()).hexdigest()
    print(f"  predictions.json SHA-256: {pred_hash}")
    output["predictions_hash"] = pred_hash

    with open(pred_path) as f:
        predictions = json.load(f)["gpt2_from_scratch"]

    method = "weight_zeroing"  # primary method for prediction comparison
    comparison = {}
    n_pass = 0

    field_map = {
        "perplexity.cv_pct": output["perplexity"]["cv_pct"],
        "full_agreement.mean_spearman": output[method]["full_agreement"]["mean_spearman"],
        "g_invariant.mean_spearman": output[method]["g_invariant"]["mean_spearman"],
        "excl_mlp.head_lift": output[method]["excl_mlp"]["head_lift"],
        "flip_rates.within_layer": output[method]["flip_rates"]["within_layer"],
        "flip_rates.head_vs_mlp": output[method]["flip_rates"]["head_vs_mlp"],
        "permutation_test.p_value": output[method]["random_grouping_test"]["p_value"],
    }

    for pred_key, pred in predictions.items():
        observed = field_map.get(pred["field"])
        if observed is None:
            comparison[pred_key] = {"status": "MISSING", "observed": None}
            continue

        if pred["direction"] == "less_than":
            passed = observed < pred["threshold"]
        else:
            passed = observed > pred["threshold"]

        n_pass += int(passed)
        status = "PASS" if passed else "FAIL"
        comparison[pred_key] = {
            "name": pred["name"],
            "predicted": pred["predicted"],
            "observed": float(observed),
            "threshold": pred["threshold"],
            "status": status,
        }
        marker = "PASS" if passed else "** FAIL **"
        print(f"  {pred_key}: {pred['name']}")
        print(f"    Predicted: {pred['predicted']}  |  Observed: {observed:.4f}  |  {marker}")

    output["predictions"] = comparison
    output["predictions_summary"] = f"{n_pass}/{len(predictions)} PASS"
    print(f"\n  TOTAL: {n_pass}/{len(predictions)} predictions PASS")

    # ── Save final results ────────────────────────────────────────────────
    out_path = RESULTS_DIR / "gpt2_from_scratch_results.json"
    tmp = out_path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(output, f, indent=2)
    tmp.rename(out_path)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None, help="Run patching for one seed")
    parser.add_argument("--analyze", action="store_true", help="Run full analysis")
    args = parser.parse_args()

    if args.seed is not None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        patch_single_model(args.seed, device)
    elif args.analyze:
        run_full_analysis()
    else:
        print("Usage: --seed N (for patching) or --analyze (for analysis)")
