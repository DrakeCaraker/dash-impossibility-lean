#!/usr/bin/env python3
"""
IOI (Indirect Object Identification) circuit analysis across 10 GPT-2-small models.

Tests whether IOI component importance exhibits the same within-layer instability
as general importance — the theorem's prediction applied to a task-specific circuit.
If within-layer flip ≈ 0.50 and G-invariant rho > 0.80, the IOI circuit's importance
structure is seed-dependent within layers but stable between layers.

Runs AFTER gpt2_train.py completes. Uses the same 10 trained models.

Usage:
    python ioi_analysis.py              # full pipeline: generate prompts, patch, analyze
    python ioi_analysis.py --seed 0     # patch one model only
    python ioi_analysis.py --analyze    # analyze after all seeds patched

Reference: Wang et al. 2022, "Interpretability in the Wild: a Circuit for Indirect
Object Identification in GPT-2 small"
"""
import argparse
import itertools
import json
import math
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from scipy import stats
from transformers import GPT2Config, GPT2LMHeadModel, GPT2Tokenizer

from config import GPT2TrainConfig, CHECKPOINT_DIR, RESULTS_DIR, EVAL_DIR

CFG = GPT2TrainConfig()
IOI_DIR = RESULTS_DIR / "ioi"
IOI_DIR.mkdir(parents=True, exist_ok=True)


# ── IOI prompt generation ─────────────────────────────────────────────────────

NAMES = ["John", "Mary", "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona",
         "George", "Helen", "James", "Kate", "Luke", "Nancy", "Oscar", "Paula"]
PLACES = ["store", "park", "school", "office", "restaurant", "library", "gym", "beach"]
OBJECTS = ["drink", "book", "letter", "gift", "key", "phone", "bag", "hat"]
TEMPLATES = [
    "When {A} and {B} went to the {place}, {B} gave a {object} to",
    "Then, {A} and {B} had a meeting. {B} decided to give a {object} to",
    "After {A} and {B} arrived at the {place}, {B} handed the {object} to",
]


def generate_ioi_prompts(n: int = 200, seed: int = 42) -> list[dict]:
    """Generate IOI prompts with IO (indirect object) and S (subject) labels."""
    rng = random.Random(seed)
    prompts = []
    name_pairs = list(itertools.permutations(NAMES, 2))

    for i in range(n):
        a, b = rng.choice(name_pairs)  # A = IO (indirect object), B = S (subject)
        place = rng.choice(PLACES)
        obj = rng.choice(OBJECTS)
        template = rng.choice(TEMPLATES)
        text = template.format(A=a, B=b, place=place, object=obj)
        prompts.append({
            "text": text,
            "io_name": a,    # correct completion (indirect object)
            "s_name": b,     # incorrect completion (subject)
            "idx": i,
        })
    return prompts


def save_prompts():
    """Save fixed IOI prompts to disk."""
    path = IOI_DIR / "prompts.json"
    if path.exists():
        return json.loads(path.read_text())
    prompts = generate_ioi_prompts(200)
    path.write_text(json.dumps(prompts, indent=2))
    return prompts


# ── IOI metrics ───────────────────────────────────────────────────────────────

def compute_logit_diff(model, tokenizer, prompts: list[dict], device) -> dict:
    """Compute logit difference: logit(IO name) - logit(S name) at last position.

    Positive logit diff = model correctly predicts the indirect object.
    """
    logit_diffs = []
    model.eval()

    with torch.no_grad(), torch.amp.autocast("cuda", dtype=torch.bfloat16):
        for p in prompts:
            tokens = tokenizer(p["text"], return_tensors="pt")["input_ids"].to(device)
            logits = model(tokens).logits[0, -1, :]  # logits at last position

            io_token = tokenizer.encode(" " + p["io_name"])[0]
            s_token = tokenizer.encode(" " + p["s_name"])[0]

            diff = (logits[io_token] - logits[s_token]).float().item()
            logit_diffs.append(diff)

    diffs = np.array(logit_diffs)
    return {
        "mean_logit_diff": float(diffs.mean()),
        "std_logit_diff": float(diffs.std()),
        "accuracy": float((diffs > 0).mean()),  # fraction where IO is preferred
        "per_prompt": diffs.tolist(),
    }


# ── IOI patching ──────────────────────────────────────────────────────────────

def patch_ioi_single_model(seed: int, device: torch.device):
    """Activation patching on IOI prompts for one model."""
    patch_dir = IOI_DIR / f"patch_seed{seed}"
    patch_dir.mkdir(parents=True, exist_ok=True)

    done_marker = patch_dir / "DONE"
    if done_marker.exists():
        print(f"IOI seed {seed}: already complete")
        return

    # Load model
    model_path = CHECKPOINT_DIR / f"gpt2_seed{seed}" / "model_final.pt"
    if not model_path.exists():
        print(f"IOI seed {seed}: model not found at {model_path}")
        return

    config = GPT2Config(
        vocab_size=CFG.vocab_size, n_positions=CFG.block_size,
        n_embd=CFG.n_embd, n_layer=CFG.n_layer, n_head=CFG.n_head,
        resid_pdrop=0.0, embd_pdrop=0.0, attn_pdrop=0.0,
    )
    model = GPT2LMHeadModel(config)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model = model.to(device).eval()

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    prompts = save_prompts()

    # ── Baseline IOI performance ──────────────────────────────────────
    print(f"IOI seed {seed}: computing baseline...")
    baseline = compute_logit_diff(model, tokenizer, prompts, device)
    print(f"  Logit diff: {baseline['mean_logit_diff']:.2f} "
          f"(acc={baseline['accuracy']:.1%})")

    if baseline["accuracy"] < 0.60:
        print(f"  SKIPPING: model cannot do IOI (acc={baseline['accuracy']:.1%} < 60%). "
              f"Circuit analysis not meaningful.")
        results = {"seed": seed, "baseline": baseline, "importance": {}, "skipped": True}
        with open(patch_dir / "results.json", "w") as f:
            json.dump(results, f, indent=2)
        done_marker.write_text("skipped")
        return

    # ── Patch each component, measure change in logit diff ────────────
    print(f"IOI seed {seed}: patching 156 components...")
    importance = {}
    baseline_diffs = np.array(baseline["per_prompt"])

    for layer in range(CFG.n_layer):
        d_head = CFG.n_embd // CFG.n_head
        attn = model.transformer.h[layer].attn

        # ── Heads ─────────────────────────────────────────────────────
        for head in range(CFG.n_head):
            name = f"L{layer}H{head}"
            orig_w = attn.c_attn.weight.data.clone()
            orig_b = attn.c_attn.bias.data.clone()
            orig_pw = attn.c_proj.weight.data.clone()

            # Zero out this head
            for qkv_offset in [0, CFG.n_embd, 2 * CFG.n_embd]:
                s = qkv_offset + head * d_head
                e = s + d_head
                attn.c_attn.weight.data[:, s:e] = 0
                attn.c_attn.bias.data[s:e] = 0
            attn.c_proj.weight.data[head * d_head:(head + 1) * d_head, :] = 0

            patched = compute_logit_diff(model, tokenizer, prompts, device)
            patched_diffs = np.array(patched["per_prompt"])

            # Importance = reduction in logit diff when component is removed
            importance[name] = float((baseline_diffs - patched_diffs).mean())

            # Restore
            attn.c_attn.weight.data = orig_w
            attn.c_attn.bias.data = orig_b
            attn.c_proj.weight.data = orig_pw

        # ── MLP ───────────────────────────────────────────────────────
        name = f"L{layer}MLP"
        mlp = model.transformer.h[layer].mlp
        orig_fc_w = mlp.c_fc.weight.data.clone()
        orig_fc_b = mlp.c_fc.bias.data.clone()
        orig_proj_w = mlp.c_proj.weight.data.clone()
        orig_proj_b = mlp.c_proj.bias.data.clone()

        mlp.c_fc.weight.data.zero_()
        mlp.c_fc.bias.data.zero_()
        mlp.c_proj.weight.data.zero_()
        mlp.c_proj.bias.data.zero_()

        patched = compute_logit_diff(model, tokenizer, prompts, device)
        patched_diffs = np.array(patched["per_prompt"])
        importance[name] = float((baseline_diffs - patched_diffs).mean())

        mlp.c_fc.weight.data = orig_fc_w
        mlp.c_fc.bias.data = orig_fc_b
        mlp.c_proj.weight.data = orig_proj_w
        mlp.c_proj.bias.data = orig_proj_b

        if (layer + 1) % 4 == 0:
            print(f"    Layer {layer+1}/12 complete")

    # ── Save ──────────────────────────────────────────────────────────
    results = {
        "seed": seed,
        "baseline": baseline,
        "importance": importance,
    }
    tmp = patch_dir / "results.json.tmp"
    with open(tmp, "w") as f:
        json.dump(results, f, indent=2)
    tmp.rename(patch_dir / "results.json")
    done_marker.write_text("complete")
    print(f"IOI seed {seed}: done. Top component: "
          f"{max(importance, key=importance.get)} ({max(importance.values()):.4f})")


# ── IOI analysis ──────────────────────────────────────────────────────────────

def g_invariant(vec):
    """Average heads within each layer, keep MLPs."""
    proj = []
    for layer in range(12):
        base = layer * 13
        proj.append(vec[base:base + 12].mean())
        proj.append(vec[base + 12])
    return np.array(proj)


def run_ioi_analysis():
    """Compare IOI importance across all 10 seeds."""
    print("=" * 70)
    print("IOI CIRCUIT ANALYSIS: Cross-seed comparison")
    print("=" * 70)

    # Load all results
    all_results = {}
    skipped = []
    for seed in range(CFG.n_seeds):
        path = IOI_DIR / f"patch_seed{seed}" / "results.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            if data.get("skipped"):
                skipped.append(seed)
                continue
            if not data.get("importance"):
                skipped.append(seed)
                continue
            all_results[seed] = data
    if skipped:
        print(f"Skipped seeds (IOI acc < 60%): {skipped}")

    seeds = sorted(all_results.keys())
    n = len(seeds)
    print(f"Loaded {n} seeds")

    if n < 2:
        print("Need at least 2 seeds for comparison")
        return

    # ── IOI performance across seeds ──────────────────────────────────
    accs = [all_results[s]["baseline"]["accuracy"] for s in seeds]
    diffs = [all_results[s]["baseline"]["mean_logit_diff"] for s in seeds]
    print(f"\nIOI accuracy: {np.mean(accs):.1%} (range {min(accs):.1%}-{max(accs):.1%})")
    print(f"Logit diff: {np.mean(diffs):.2f} (range {min(diffs):.2f}-{max(diffs):.2f})")

    # ── Extract importance vectors ────────────────────────────────────
    vectors = []
    for s in seeds:
        imp = all_results[s]["importance"]
        vec = []
        for layer in range(12):
            for head in range(12):
                vec.append(imp[f"L{layer}H{head}"])
            vec.append(imp[f"L{layer}MLP"])
        vectors.append(np.array(vec))

    ginv_vectors = [g_invariant(v) for v in vectors]

    # ── Pairwise Spearman (raw and G-invariant) ───────────────────────
    raw_rhos, ginv_rhos = [], []
    for i in range(n):
        for j in range(i + 1, n):
            r, _ = stats.spearmanr(vectors[i], vectors[j])
            raw_rhos.append(r)
            r2, _ = stats.spearmanr(ginv_vectors[i], ginv_vectors[j])
            ginv_rhos.append(r2)

    print(f"\nRaw Spearman: {np.mean(raw_rhos):.3f} (range {min(raw_rhos):.3f}-{max(raw_rhos):.3f})")
    print(f"G-inv Spearman: {np.mean(ginv_rhos):.3f} (range {min(ginv_rhos):.3f}-{max(ginv_rhos):.3f})")

    # ── Within-layer flip rate ────────────────────────────────────────
    within_flips = []
    between_flips = []
    for i in range(n):
        for j in range(i + 1, n):
            vi, vj = vectors[i], vectors[j]
            for layer in range(12):
                base = layer * 13
                hi, hj = vi[base:base+12], vj[base:base+12]
                for h1 in range(12):
                    for h2 in range(h1+1, 12):
                        within_flips.append(float((hi[h1]>hi[h2]) != (hj[h1]>hj[h2])))
                mi, mj = vi[base+12], vj[base+12]
                for h in range(12):
                    between_flips.append(float((vi[base+h]>mi) != (vj[base+h]>mj)))

    print(f"Within-layer flip: {np.mean(within_flips):.3f}")
    print(f"Head-vs-MLP flip: {np.mean(between_flips):.3f}")

    # ── Top-5 components per seed (the money table) ───────────────────
    print(f"\n{'='*60}")
    print("TOP-5 IOI COMPONENTS PER SEED")
    print(f"{'='*60}")
    print(f"{'Seed':>4} | {'#1':>8} | {'#2':>8} | {'#3':>8} | {'#4':>8} | {'#5':>8}")
    print("-" * 60)

    top5_per_seed = {}
    for idx, s in enumerate(seeds):
        imp = all_results[s]["importance"]
        sorted_components = sorted(imp.items(), key=lambda x: -x[1])[:5]
        names = [c[0] for c in sorted_components]
        top5_per_seed[s] = names
        print(f"{s:>4} | {names[0]:>8} | {names[1]:>8} | {names[2]:>8} | "
              f"{names[3]:>8} | {names[4]:>8}")

    # Count distinct components appearing in top-5 across all seeds
    all_top5 = set()
    for names in top5_per_seed.values():
        all_top5.update(names)
    print(f"\nDistinct components in top-5 across {n} seeds: {len(all_top5)}")
    print(f"Components: {sorted(all_top5)}")

    # ── Layer-level importance (G-invariant) ──────────────────────────
    print(f"\n{'='*60}")
    print("LAYER-LEVEL IMPORTANCE (G-invariant, averaged across seeds)")
    print(f"{'='*60}")
    mean_ginv = np.mean([g_invariant(v) for v in vectors], axis=0)
    for layer in range(12):
        head_avg = mean_ginv[layer * 2]
        mlp_imp = mean_ginv[layer * 2 + 1]
        bar = "#" * int(max(head_avg, mlp_imp) * 50 / max(mean_ginv))
        print(f"  Layer {layer:2d}: heads={head_avg:.4f}  MLP={mlp_imp:.4f}  {bar}")

    # ── Save results ──────────────────────────────────────────────────
    output = {
        "n_seeds": n,
        "ioi_performance": {
            "mean_accuracy": float(np.mean(accs)),
            "mean_logit_diff": float(np.mean(diffs)),
            "per_seed_accuracy": {str(s): float(all_results[s]["baseline"]["accuracy"])
                                  for s in seeds},
        },
        "raw_agreement": {
            "mean_spearman": float(np.mean(raw_rhos)),
            "all_spearman": [float(r) for r in raw_rhos],
        },
        "g_invariant_agreement": {
            "mean_spearman": float(np.mean(ginv_rhos)),
            "all_spearman": [float(r) for r in ginv_rhos],
        },
        "flip_rates": {
            "within_layer": float(np.mean(within_flips)),
            "head_vs_mlp": float(np.mean(between_flips)),
        },
        "top5_per_seed": {str(s): v for s, v in top5_per_seed.items()},
        "distinct_top5_count": len(all_top5),
        "distinct_top5_components": sorted(all_top5),
        "importance_vectors": {str(s): vectors[i].tolist() for i, s in enumerate(seeds)},
    }

    out_path = IOI_DIR / "ioi_results.json"
    tmp = out_path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(output, f, indent=2)
    tmp.rename(out_path)
    print(f"\nResults saved to {out_path}")

    # ── Interpretation ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("INTERPRETATION")
    print(f"{'='*60}")
    wr = np.mean(within_flips)
    gr = np.mean(ginv_rhos)
    if wr > 0.40 and gr > 0.80:
        print(f"Within-layer flip = {wr:.3f} ≈ 0.50: IOI importance rankings are SEED-DEPENDENT within layers.")
        print(f"G-invariant rho = {gr:.3f}: layer-level IOI importance is STABLE across seeds.")
        print(f"Which head is most important for IOI depends on the training seed;")
        print(f"which LAYER is most important does not — exactly as the theorem predicts.")
        print(f"NOTE: This measures importance instability, not functional role assignment.")
        print(f"Whether the same computational function (e.g., 'name mover') permutes")
        print(f"across heads requires attention pattern analysis (not tested here).")
    elif wr < 0.20:
        print(f"Within-layer flip = {wr:.3f} << 0.50: IOI importance rankings are STABLE.")
        print(f"The IOI task does NOT show the predicted permutation instability.")
        print(f"Possible explanations: (a) IOI creates strong specialization pressure that")
        print(f"breaks S_12 symmetry, (b) 50K training steps is insufficient for full")
        print(f"circuit formation, (c) heads contribute unequally to IOI in a way that")
        print(f"is consistent across seeds.")
    else:
        print(f"Within-layer flip = {wr:.3f}: INTERMEDIATE result.")
        print(f"Some layers show importance permutation for IOI, others are stable.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--analyze", action="store_true")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.seed is not None:
        save_prompts()
        patch_ioi_single_model(args.seed, device)
    elif args.analyze:
        run_ioi_analysis()
    else:
        # Full pipeline
        save_prompts()
        for s in range(CFG.n_seeds):
            patch_ioi_single_model(s, device)
        run_ioi_analysis()
