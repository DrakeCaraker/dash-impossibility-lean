#!/usr/bin/env python3
"""
SAE Follow-up Experiments: ReLU SAE + Pretrained SAE + Resolution Test

Addresses three open questions from the vet:
  OQ1: Do ReLU SAEs (Bricken et al. style) show the same instability as TopK?
  OQ2: Are SAEs on pretrained GPT-2 more stable than from-scratch?
  OQ3: Does averaging matched features across SAE seeds help?

Usage:
    CUDA_VISIBLE_DEVICES=0,1 python sae_followup.py --phase relu      # 10 ReLU SAEs on from-scratch model
    CUDA_VISIBLE_DEVICES=2,3 python sae_followup.py --phase pretrained # 10 TopK SAEs on pretrained GPT-2
    python sae_followup.py --phase resolve                             # Average matched features (CPU only)
    python sae_followup.py --phase analyze                             # Compare all conditions
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import stats
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm
from transformers import GPT2Config, GPT2LMHeadModel

from config import GPT2TrainConfig, SAEConfig, CHECKPOINT_DIR, RESULTS_DIR, EVAL_DIR

GCFG = GPT2TrainConfig()
CFG = SAEConfig()
FOLLOWUP_DIR = RESULTS_DIR / "sae_followup"
FOLLOWUP_DIR.mkdir(parents=True, exist_ok=True)


# ── ReLU SAE (Bricken et al. style) ──────────────────────────────────────────

class ReLUSAE(nn.Module):
    def __init__(self, d_in, d_sae):
        super().__init__()
        self.W_enc = nn.Parameter(torch.randn(d_in, d_sae) * (1.0 / d_in ** 0.5))
        self.b_enc = nn.Parameter(torch.zeros(d_sae))
        self.W_dec = nn.Parameter(torch.randn(d_sae, d_in) * (1.0 / d_sae ** 0.5))
        self.b_dec = nn.Parameter(torch.zeros(d_in))
        with torch.no_grad():
            self.W_dec.data = F.normalize(self.W_dec.data, dim=1)

    def forward(self, x):
        h = F.relu((x - self.b_dec) @ self.W_enc + self.b_enc)
        x_hat = h @ self.W_dec + self.b_dec
        return x_hat, h

    def loss(self, x, l1_coeff=5e-4):
        x_hat, h = self(x)
        recon = F.mse_loss(x_hat, x)
        sparsity = h.abs().mean()
        return {"loss": recon + l1_coeff * sparsity, "recon_loss": recon,
                "l0": (h > 0).float().sum(dim=-1).mean(), "l1": sparsity}


# ── Activation collection ────────────────────────────────────────────────────

def collect_activations(model, eval_seqs, layer, device):
    """Extract residual stream activations from a model."""
    activations = []
    def hook_fn(module, input, output):
        activations.append(output[0].detach().cpu())
    handle = model.transformer.h[layer].register_forward_hook(hook_fn)
    with torch.no_grad():
        for i in tqdm(range(0, min(800, len(eval_seqs)), 16), desc="Collecting"):
            batch = torch.from_numpy(eval_seqs[i:i+16]).to(device)
            model(batch)
    handle.remove()
    all_acts = torch.cat(activations, dim=0).reshape(-1, GCFG.n_embd).numpy()
    n_eval = min(len(all_acts) // 5, CFG.n_eval_activations)
    n_train = len(all_acts) - n_eval
    return all_acts[:n_train], all_acts[n_train:]


def train_sae(sae, train_acts, device, steps=50000, lr=3e-4, batch_size=4096, is_relu=False):
    """Train one SAE."""
    optimizer = torch.optim.Adam(sae.parameters(), lr=lr)
    acts_tensor = torch.from_numpy(train_acts).float()
    n = len(acts_tensor)
    for step in range(steps):
        idx = torch.randint(0, n, (batch_size,))
        batch = acts_tensor[idx].to(device)
        loss_dict = sae.loss(batch) if not is_relu else sae.loss(batch)
        optimizer.zero_grad()
        loss_dict["loss"].backward()
        optimizer.step()
        with torch.no_grad():
            sae.W_dec.data = F.normalize(sae.W_dec.data, dim=1)
        if step % 10000 == 0:
            print(f"    step {step}: loss={loss_dict['loss'].item():.4f} "
                  f"L0={loss_dict['l0'].item():.1f}")
    return sae


def eval_sae(sae, eval_acts, device):
    """Get feature stats from eval activations."""
    sae.eval()
    all_h = []
    acts = torch.from_numpy(eval_acts).float().to(device)
    with torch.no_grad():
        for i in range(0, len(acts), 1024):
            _, h = sae(acts[i:i+1024])
            all_h.append(h.cpu())
    features = torch.cat(all_h, dim=0)
    freq = (features > 0).float().mean(dim=0).numpy()
    dec = sae.W_dec.data.cpu().numpy()
    n_dead = int((freq == 0).sum())
    return freq, dec, n_dead


# ── Comparison analysis ──────────────────────────────────────────────────────

def compare_saes(label, decoders, freqs, n_seeds):
    """Compute pairwise cosine, matched rho, etc."""
    pairs = []
    raw_rhos = []
    for i in range(n_seeds):
        for j in range(i+1, n_seeds):
            di = decoders[i] / (np.linalg.norm(decoders[i], axis=1, keepdims=True) + 1e-8)
            dj = decoders[j] / (np.linalg.norm(decoders[j], axis=1, keepdims=True) + 1e-8)
            cos = di @ dj.T
            alive_i = freqs[i] > 0
            max_cos = float(cos.max(axis=1)[alive_i].mean()) if alive_i.any() else 0.0

            # Hungarian on top 500
            k = min(500, len(freqs[i]))
            top_i = np.argsort(-freqs[i])[:k]
            top_j = np.argsort(-freqs[j])[:k]
            sub = cos[np.ix_(top_i, top_j)]
            ri, ci = linear_sum_assignment(-sub)
            matched_cos = float(sub[ri, ci].mean())
            freq_i_m = freqs[i][top_i[ri]]
            freq_j_m = freqs[j][top_j[ci]]
            rho_m, _ = stats.spearmanr(freq_i_m, freq_j_m)

            rho_raw, _ = stats.spearmanr(freqs[i], freqs[j])
            raw_rhos.append(rho_raw)

            pairs.append({"i": i, "j": j, "max_cos": max_cos,
                          "matched_cos": matched_cos, "rho_matched": float(rho_m)})

    max_cosines = [p["max_cos"] for p in pairs]
    matched_cosines = [p["matched_cos"] for p in pairs]
    matched_rhos = [p["rho_matched"] for p in pairs]

    result = {
        "label": label,
        "n_seeds": n_seeds,
        "mean_max_cosine": float(np.mean(max_cosines)),
        "std_max_cosine": float(np.std(max_cosines)),
        "mean_matched_cosine": float(np.mean(matched_cosines)),
        "mean_matched_rho": float(np.mean(matched_rhos)),
        "mean_raw_rho": float(np.mean(raw_rhos)),
        "pairs": pairs,
    }
    print(f"\n  {label}:")
    print(f"    Max cosine (greedy): {result['mean_max_cosine']:.3f}")
    print(f"    Matched cosine (Hungarian): {result['mean_matched_cosine']:.3f}")
    print(f"    Matched importance rho: {result['mean_matched_rho']:.3f}")
    print(f"    Raw importance rho: {result['mean_raw_rho']:.3f}")
    return result


# ── Phase: ReLU SAE ──────────────────────────────────────────────────────────

def run_relu_phase(device):
    """Train 10 ReLU SAEs on from-scratch model, compare with TopK."""
    print("=" * 60)
    print("PHASE: ReLU SAE (Bricken et al. style)")
    print("=" * 60)

    relu_dir = FOLLOWUP_DIR / "relu"
    relu_dir.mkdir(exist_ok=True)

    # Load from-scratch model and collect activations
    model_path = CHECKPOINT_DIR / f"gpt2_seed{CFG.base_model_seed}" / "model_final.pt"
    config = GPT2Config(vocab_size=GCFG.vocab_size, n_positions=GCFG.block_size,
                        n_embd=GCFG.n_embd, n_layer=GCFG.n_layer, n_head=GCFG.n_head,
                        resid_pdrop=0.0, embd_pdrop=0.0, attn_pdrop=0.0)
    model = GPT2LMHeadModel(config)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model = model.to(device).eval()

    eval_seqs = np.load(EVAL_DIR / "eval_sequences.npy")
    train_acts, eval_acts = collect_activations(model, eval_seqs, CFG.target_layer, device)
    del model; torch.cuda.empty_cache()

    decoders, freqs = [], []
    for seed in range(10):
        print(f"\n  ReLU SAE seed {seed}:")
        torch.manual_seed(seed)
        sae = ReLUSAE(GCFG.n_embd, CFG.d_sae).to(device)
        sae = train_sae(sae, train_acts, device, steps=CFG.sae_steps, is_relu=True)
        freq, dec, n_dead = eval_sae(sae, eval_acts, device)
        decoders.append(dec); freqs.append(freq)
        print(f"    Dead: {n_dead} ({n_dead/CFG.d_sae*100:.1f}%), "
              f"L0={float((freq>0).sum()):.0f}")
        del sae; torch.cuda.empty_cache()

    result = compare_saes("ReLU SAE (from-scratch model)", decoders, freqs, 10)
    with open(relu_dir / "results.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {relu_dir / 'results.json'}")


# ── Phase: Pretrained SAE ────────────────────────────────────────────────────

def run_pretrained_phase(device):
    """Train 10 TopK SAEs on pretrained GPT-2."""
    print("=" * 60)
    print("PHASE: TopK SAE on PRETRAINED GPT-2")
    print("=" * 60)

    pre_dir = FOLLOWUP_DIR / "pretrained"
    pre_dir.mkdir(exist_ok=True)

    model = GPT2LMHeadModel.from_pretrained("gpt2").to(device).eval()
    eval_seqs = np.load(EVAL_DIR / "eval_sequences.npy")
    train_acts, eval_acts = collect_activations(model, eval_seqs, CFG.target_layer, device)
    del model; torch.cuda.empty_cache()

    # Import TopK SAE from the original experiment
    from sae_experiment import TopKSAE

    decoders, freqs = [], []
    for seed in range(10):
        print(f"\n  Pretrained TopK SAE seed {seed}:")
        torch.manual_seed(seed)
        sae = TopKSAE(GCFG.n_embd, CFG.d_sae, CFG.k).to(device)
        sae = train_sae(sae, train_acts, device, steps=CFG.sae_steps)
        freq, dec, n_dead = eval_sae(sae, eval_acts, device)
        decoders.append(dec); freqs.append(freq)
        print(f"    Dead: {n_dead} ({n_dead/CFG.d_sae*100:.1f}%)")
        del sae; torch.cuda.empty_cache()

    result = compare_saes("TopK SAE (pretrained GPT-2)", decoders, freqs, 10)
    with open(pre_dir / "results.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {pre_dir / 'results.json'}")


# ── Phase: Resolution test ───────────────────────────────────────────────────

def run_resolve_phase():
    """Average matched features across SAE seeds, measure improvement."""
    print("=" * 60)
    print("PHASE: SAE Resolution (average matched features)")
    print("=" * 60)

    sae_dir = RESULTS_DIR / "sae"
    decoders, freqs = [], []
    for seed in range(10):
        dec_path = sae_dir / f"sae_seed{seed}" / "decoder_weights.npy"
        stats_path = sae_dir / f"sae_seed{seed}" / "feature_stats.json"
        if not dec_path.exists():
            print(f"  Seed {seed}: missing decoder weights")
            continue
        decoders.append(np.load(dec_path))
        with open(stats_path) as f:
            freqs.append(np.array(json.load(f)["activation_freq"]))

    if len(decoders) < 2:
        print("Need at least 2 SAEs for resolution test")
        return

    # Take seed 0 as reference, match all others to it
    ref_dec = decoders[0] / (np.linalg.norm(decoders[0], axis=1, keepdims=True) + 1e-8)
    k = 500  # top features

    averaged_decs = [decoders[0].copy()]  # start with reference
    for seed in range(1, len(decoders)):
        other_dec = decoders[seed] / (np.linalg.norm(decoders[seed], axis=1, keepdims=True) + 1e-8)
        cos = ref_dec @ other_dec.T
        top_ref = np.argsort(-freqs[0])[:k]
        top_other = np.argsort(-freqs[seed])[:k]
        sub = cos[np.ix_(top_ref, top_other)]
        ri, ci = linear_sum_assignment(-sub)

        # Create aligned decoder: reorder other's features to match reference
        aligned = np.zeros_like(decoders[seed])
        for r, c in zip(ri, ci):
            aligned[top_ref[r]] = decoders[seed][top_other[c]]
        averaged_decs.append(aligned)

    # Average the aligned decoders
    avg_dec = np.mean(averaged_decs, axis=0)
    avg_dec_norm = avg_dec / (np.linalg.norm(avg_dec, axis=1, keepdims=True) + 1e-8)

    # Compare averaged decoder to each individual
    cosines_to_avg = []
    for seed in range(len(decoders)):
        d = decoders[seed] / (np.linalg.norm(decoders[seed], axis=1, keepdims=True) + 1e-8)
        cos = d @ avg_dec_norm.T
        alive = freqs[seed] > 0
        max_cos = float(cos.max(axis=1)[alive].mean()) if alive.any() else 0.0
        cosines_to_avg.append(max_cos)
        print(f"  Seed {seed} → averaged: max_cos={max_cos:.3f}")

    result = {
        "method": "Hungarian matching + averaging (top 500 features)",
        "n_seeds_averaged": len(averaged_decs),
        "individual_mean_max_cosine": 0.394,  # from original experiment
        "cosine_to_averaged": cosines_to_avg,
        "mean_cosine_to_averaged": float(np.mean(cosines_to_avg)),
        "improvement": float(np.mean(cosines_to_avg) - 0.394),
    }
    print(f"\n  Individual pairwise cosine: 0.394")
    print(f"  Cosine to averaged decoder: {result['mean_cosine_to_averaged']:.3f}")
    print(f"  Improvement: {result['improvement']:+.3f}")

    with open(FOLLOWUP_DIR / "resolution_results.json", "w") as f:
        json.dump(result, f, indent=2)


# ── Phase: Compare all ───────────────────────────────────────────────────────

def run_analyze_phase():
    """Compare TopK/from-scratch, ReLU/from-scratch, TopK/pretrained."""
    print("=" * 60)
    print("SAE FOLLOW-UP: COMPARISON")
    print("=" * 60)

    results = {}
    for name, path in [
        ("TopK_from_scratch", RESULTS_DIR / "sae_stability_results.json"),
        ("ReLU_from_scratch", FOLLOWUP_DIR / "relu" / "results.json"),
        ("TopK_pretrained", FOLLOWUP_DIR / "pretrained" / "results.json"),
        ("Resolution", FOLLOWUP_DIR / "resolution_results.json"),
    ]:
        if path.exists():
            with open(path) as f:
                results[name] = json.load(f)

    print("\n  Condition                  | Max Cosine | Matched Cos | Matched ρ")
    print("  " + "-" * 72)
    for name, r in results.items():
        if name == "Resolution":
            print(f"  {name:28s} | {r['mean_cosine_to_averaged']:.3f}      | —           | —")
        else:
            mc = r.get("mean_max_cosine", r.get("feature_matching", {}).get("mean_max_cosine", "?"))
            mmc = r.get("mean_matched_cosine", r.get("feature_matching", {}).get("mean_matched_cosine_top500", "?"))
            mr = r.get("mean_matched_rho", r.get("importance_stability", {}).get("mean_spearman_matched", "?"))
            print(f"  {name:28s} | {mc:.3f}      | {mmc:.3f}       | {mr:.3f}")

    out = FOLLOWUP_DIR / "comparison.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Saved to {out}")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["relu", "pretrained", "resolve", "analyze"],
                        required=True)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.phase == "relu":
        run_relu_phase(device)
    elif args.phase == "pretrained":
        run_pretrained_phase(device)
    elif args.phase == "resolve":
        run_resolve_phase()
    elif args.phase == "analyze":
        run_analyze_phase()
