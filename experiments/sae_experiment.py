#!/usr/bin/env python3
"""
SAE Stability Experiment: Do independently trained SAEs on the same frozen
model produce the same interpretable features?

Design:
  - Freeze one GPT-2-small model (seed 0 from the training experiment)
  - Extract residual stream activations at layer 6 (standard MI practice)
  - Train 10 TopK SAEs with different random seeds
  - Measure: feature matching quality, importance ranking stability, dead features

Usage:
    CUDA_VISIBLE_DEVICES=0 python sae_experiment.py --phase collect  # collect activations
    CUDA_VISIBLE_DEVICES=0 python sae_experiment.py --phase train --sae-seed 0
    python sae_experiment.py --phase analyze

Crash recovery: per-seed DONE markers, atomic saves.
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

from config import (GPT2TrainConfig, SAEConfig, StatsConfig,
                    CHECKPOINT_DIR, RESULTS_DIR, EVAL_DIR, DATA_DIR)

GCFG = GPT2TrainConfig()
CFG = SAEConfig()
SCFG = StatsConfig()

SAE_DIR = RESULTS_DIR / "sae"
SAE_DIR.mkdir(parents=True, exist_ok=True)


# ── TopK SAE ──────────────────────────────────────────────────────────────────

class TopKSAE(nn.Module):
    """TopK Sparse Autoencoder (Bricken et al. 2023 / Templeton et al. 2024 style)."""

    def __init__(self, d_in: int, d_sae: int, k: int):
        super().__init__()
        self.d_in = d_in
        self.d_sae = d_sae
        self.k = k

        self.W_enc = nn.Parameter(torch.randn(d_in, d_sae) * (1.0 / d_in ** 0.5))
        self.b_enc = nn.Parameter(torch.zeros(d_sae))
        self.W_dec = nn.Parameter(torch.randn(d_sae, d_in) * (1.0 / d_sae ** 0.5))
        self.b_dec = nn.Parameter(torch.zeros(d_in))

        # Normalize decoder columns at init
        with torch.no_grad():
            self.W_dec.data = F.normalize(self.W_dec.data, dim=1)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to sparse feature activations."""
        h = (x - self.b_dec) @ self.W_enc + self.b_enc
        # TopK: keep only the k largest activations
        topk_vals, topk_idx = h.topk(self.k, dim=-1)
        h_sparse = torch.zeros_like(h)
        h_sparse.scatter_(-1, topk_idx, F.relu(topk_vals))
        return h_sparse

    def decode(self, h: torch.Tensor) -> torch.Tensor:
        """Decode sparse features back to input space."""
        return h @ self.W_dec + self.b_dec

    def forward(self, x: torch.Tensor):
        h = self.encode(x)
        x_hat = self.decode(h)
        return x_hat, h

    def loss(self, x: torch.Tensor) -> dict:
        x_hat, h = self(x)
        recon_loss = F.mse_loss(x_hat, x)
        # L0 = average number of active features (for monitoring)
        l0 = (h > 0).float().sum(dim=-1).mean()
        return {"loss": recon_loss, "recon_loss": recon_loss, "l0": l0}


# ── Activation collection ────────────────────────────────────────────────────

def collect_activations(device: torch.device):
    """Extract residual stream activations from the frozen base model."""
    act_path = SAE_DIR / "activations_train.npy"
    act_eval_path = SAE_DIR / "activations_eval.npy"

    if act_path.exists() and act_eval_path.exists():
        print("Activations already collected.")
        return

    print(f"Collecting activations from model seed {CFG.base_model_seed}, layer {CFG.target_layer}...")

    # Load frozen model
    model_path = CHECKPOINT_DIR / f"gpt2_seed{CFG.base_model_seed}" / "model_final.pt"
    config = GPT2Config(
        vocab_size=GCFG.vocab_size, n_positions=GCFG.block_size,
        n_embd=GCFG.n_embd, n_layer=GCFG.n_layer, n_head=GCFG.n_head,
        resid_pdrop=0.0, embd_pdrop=0.0, attn_pdrop=0.0,
    )
    model = GPT2LMHeadModel(config)
    model.load_state_dict(torch.load(model_path, map_location="cpu", weights_only=True))
    model = model.to(device).eval()

    # Load eval sequences
    eval_seqs = np.load(EVAL_DIR / "eval_sequences.npy")

    # Hook to capture residual stream after target layer
    activations = []
    def hook_fn(module, input, output):
        # output[0] is the hidden state after this transformer block
        activations.append(output[0].detach().cpu())

    handle = model.transformer.h[CFG.target_layer].register_forward_hook(hook_fn)

    # Collect training activations
    print("  Collecting training activations...")
    n_needed = CFG.n_activation_batches * CFG.sae_batch_size
    n_seqs_needed = n_needed // GCFG.block_size + 1

    with torch.no_grad():
        for i in tqdm(range(0, min(n_seqs_needed, len(eval_seqs)), 16)):
            batch = torch.from_numpy(eval_seqs[i:i+16]).to(device)
            model(batch)

    all_acts = torch.cat(activations, dim=0)  # [n_seqs, seq_len, d_model]
    all_acts = all_acts.reshape(-1, GCFG.n_embd).numpy()  # flatten to [n_tokens, d_model]

    # Split into train and eval
    n_train = min(len(all_acts), CFG.n_activation_batches * CFG.sae_batch_size)
    n_eval = min(len(all_acts) - n_train, CFG.n_eval_activations)

    np.save(SAE_DIR / "activations_train.npy.tmp", all_acts[:n_train])
    Path(SAE_DIR / "activations_train.npy.tmp").rename(act_path)

    np.save(SAE_DIR / "activations_eval.npy.tmp", all_acts[n_train:n_train + n_eval])
    Path(SAE_DIR / "activations_eval.npy.tmp").rename(act_eval_path)

    handle.remove()
    print(f"  Saved {n_train} train + {n_eval} eval activations")


# ── SAE Training ──────────────────────────────────────────────────────────────

def train_single_sae(sae_seed: int, device: torch.device):
    """Train one SAE with the given seed."""
    sae_dir = SAE_DIR / f"sae_seed{sae_seed}"
    sae_dir.mkdir(parents=True, exist_ok=True)

    done_marker = sae_dir / "DONE"
    if done_marker.exists():
        print(f"SAE seed {sae_seed}: already complete")
        return

    torch.manual_seed(sae_seed)
    np.random.seed(sae_seed)

    # Load activations
    acts = np.load(SAE_DIR / "activations_train.npy")
    acts_tensor = torch.from_numpy(acts).float()

    # Create SAE
    sae = TopKSAE(GCFG.n_embd, CFG.d_sae, CFG.k).to(device)
    optimizer = torch.optim.Adam(sae.parameters(), lr=CFG.sae_lr)

    # Resume from checkpoint
    ckpt_path = sae_dir / "checkpoint.pt"
    start_step = 0
    if ckpt_path.exists():
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        sae.load_state_dict(ckpt["sae"])
        optimizer.load_state_dict(ckpt["optimizer"])
        start_step = ckpt["step"]
        print(f"SAE seed {sae_seed}: resumed from step {start_step}")

    # Training loop
    n_acts = len(acts_tensor)
    log_path = sae_dir / "training_log.jsonl"

    for step in range(start_step, CFG.sae_steps):
        # Random batch of activations
        idx = torch.randint(0, n_acts, (CFG.sae_batch_size,))
        batch = acts_tensor[idx].to(device)

        loss_dict = sae.loss(batch)
        loss = loss_dict["loss"]

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Normalize decoder columns (standard SAE practice)
        with torch.no_grad():
            sae.W_dec.data = F.normalize(sae.W_dec.data, dim=1)

        if step % 1000 == 0:
            entry = {"step": step, "loss": loss.item(),
                     "recon_loss": loss_dict["recon_loss"].item(),
                     "l0": loss_dict["l0"].item()}
            with open(log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            if step % 5000 == 0:
                print(f"  SAE seed {sae_seed} step {step}: "
                      f"loss={loss.item():.6f} L0={loss_dict['l0'].item():.1f}")

        # Checkpoint every 10K steps
        if step % 10_000 == 0 and step > 0:
            tmp = sae_dir / "checkpoint.tmp"
            torch.save({"sae": sae.state_dict(), "optimizer": optimizer.state_dict(),
                        "step": step}, tmp)
            tmp.rename(ckpt_path)

    # Save final model
    tmp = sae_dir / "sae_final.pt.tmp"
    torch.save(sae.state_dict(), tmp)
    tmp.rename(sae_dir / "sae_final.pt")

    # Compute feature statistics on eval set
    print(f"SAE seed {sae_seed}: computing feature statistics...")
    eval_acts = torch.from_numpy(np.load(SAE_DIR / "activations_eval.npy")).float().to(device)
    sae.eval()

    all_features = []
    with torch.no_grad():
        for i in range(0, len(eval_acts), 1024):
            batch = eval_acts[i:i+1024]
            _, h = sae(batch)
            all_features.append(h.cpu())

    features = torch.cat(all_features, dim=0)  # [n_eval, d_sae]

    # Feature importance: activation frequency (fraction of tokens where feature > 0)
    activation_freq = (features > 0).float().mean(dim=0).numpy()
    # Mean activation magnitude (when active)
    active_mask = features > 0
    mean_activation = torch.where(active_mask, features, torch.zeros_like(features)).sum(dim=0)
    mean_activation = (mean_activation / active_mask.sum(dim=0).clamp(min=1)).numpy()
    # Dead features
    dead = (activation_freq == 0)
    n_dead = int(dead.sum())

    feature_stats = {
        "activation_freq": activation_freq.tolist(),
        "mean_activation": mean_activation.tolist(),
        "n_dead": n_dead,
        "dead_fraction": float(n_dead / CFG.d_sae),
    }

    # Save decoder weights for feature matching
    decoder_weights = sae.W_dec.data.cpu().numpy()  # [d_sae, d_in]
    np.save(sae_dir / "decoder_weights.npy.tmp", decoder_weights)
    Path(sae_dir / "decoder_weights.npy.tmp").rename(sae_dir / "decoder_weights.npy")

    with open(sae_dir / "feature_stats.json", "w") as f:
        json.dump(feature_stats, f)

    done_marker.write_text("complete")
    print(f"SAE seed {sae_seed}: DONE. {n_dead} dead features ({n_dead/CFG.d_sae*100:.1f}%)")


# ── SAE Analysis ──────────────────────────────────────────────────────────────

def analyze_sae_stability():
    """Full stability analysis across all SAE seeds."""
    print("=" * 70)
    print("SAE STABILITY ANALYSIS")
    print("=" * 70)

    # Load all decoder weights and feature stats
    decoders = {}
    freq_vectors = {}
    dead_fractions = {}

    for sae_seed in range(CFG.n_sae_seeds):
        sae_dir = SAE_DIR / f"sae_seed{sae_seed}"
        if not (sae_dir / "DONE").exists():
            print(f"WARNING: SAE seed {sae_seed} not complete")
            continue
        decoders[sae_seed] = np.load(sae_dir / "decoder_weights.npy")
        with open(sae_dir / "feature_stats.json") as f:
            stats_data = json.load(f)
        freq_vectors[sae_seed] = np.array(stats_data["activation_freq"])
        dead_fractions[sae_seed] = stats_data["dead_fraction"]

    seeds = sorted(decoders.keys())
    n = len(seeds)
    print(f"Loaded {n} SAEs")

    # ── Feature matching ──────────────────────────────────────────────────
    # For each pair of SAEs, find optimal feature matching via cosine similarity
    print("\nComputing pairwise feature matching...")

    pair_results = []
    for i_idx, si in enumerate(seeds):
        for j_idx, sj in enumerate(seeds):
            if si >= sj:
                continue

            dec_i = decoders[si]  # [d_sae, d_in]
            dec_j = decoders[sj]

            # Normalize for cosine similarity
            dec_i_norm = dec_i / (np.linalg.norm(dec_i, axis=1, keepdims=True) + 1e-8)
            dec_j_norm = dec_j / (np.linalg.norm(dec_j, axis=1, keepdims=True) + 1e-8)

            # Cosine similarity matrix [d_sae, d_sae]
            cos_sim = dec_i_norm @ dec_j_norm.T

            # Greedy matching: for each feature in SAE_i, find best match in SAE_j
            max_cosine_per_feature_i = cos_sim.max(axis=1)
            max_cosine_per_feature_j = cos_sim.max(axis=0)

            # Exclude dead features from matching quality
            alive_i = freq_vectors[si] > 0
            alive_j = freq_vectors[sj] > 0

            mean_max_cosine_alive = float(max_cosine_per_feature_i[alive_i].mean())

            # Hungarian (optimal) matching for top-k features
            k_match = min(500, CFG.d_sae)
            # Use top-k most frequent features for optimal matching
            top_i = np.argsort(-freq_vectors[si])[:k_match]
            top_j = np.argsort(-freq_vectors[sj])[:k_match]
            sub_cos = cos_sim[np.ix_(top_i, top_j)]
            row_ind, col_ind = linear_sum_assignment(-sub_cos)  # maximize
            matched_cosines = sub_cos[row_ind, col_ind]
            mean_matched_cosine = float(matched_cosines.mean())

            # Importance ranking after matching
            freq_i_matched = freq_vectors[si][top_i[row_ind]]
            freq_j_matched = freq_vectors[sj][top_j[col_ind]]
            rho_matched, _ = stats.spearmanr(freq_i_matched, freq_j_matched)

            # Raw importance ranking (no matching — pure ranking comparison)
            # Sort both by frequency, compare: is the k-th most important feature similar?
            sorted_i = np.argsort(-freq_vectors[si])
            sorted_j = np.argsort(-freq_vectors[sj])
            # Cosine similarity of k-th most important features
            rank_cosines = [float(cos_sim[sorted_i[k], sorted_j[k]])
                            for k in range(min(100, CFG.d_sae))]

            pair_results.append({
                "seed_i": si, "seed_j": sj,
                "mean_max_cosine_alive": mean_max_cosine_alive,
                "mean_matched_cosine_top500": mean_matched_cosine,
                "spearman_matched": float(rho_matched),
                "rank_cosines_top100": rank_cosines,
            })

            print(f"  Pair ({si},{sj}): max_cos={mean_max_cosine_alive:.3f}, "
                  f"matched_cos={mean_matched_cosine:.3f}, "
                  f"rho_matched={rho_matched:.3f}")

    # ── Aggregate statistics ──────────────────────────────────────────────
    mean_max_cosines = [p["mean_max_cosine_alive"] for p in pair_results]
    mean_matched_cosines = [p["mean_matched_cosine_top500"] for p in pair_results]
    spearman_matched = [p["spearman_matched"] for p in pair_results]

    dead_frac_values = [dead_fractions[s] for s in seeds]
    dead_cv = float(np.std(dead_frac_values) / max(np.mean(dead_frac_values), 1e-8) * 100)

    # ── Raw importance Spearman (no matching) ─────────────────────────────
    raw_rhos = []
    for i_idx, si in enumerate(seeds):
        for j_idx, sj in enumerate(seeds):
            if si >= sj:
                continue
            rho, _ = stats.spearmanr(freq_vectors[si], freq_vectors[sj])
            raw_rhos.append(rho)

    # ── Compare with predictions ──────────────────────────────────────────
    pred_path = Path(__file__).parent / "predictions.json"
    with open(pred_path) as f:
        predictions = json.load(f)["sae_stability"]

    comparison = {}
    observed_map = {
        "feature_matching.mean_max_cosine": np.mean(mean_max_cosines),
        "importance_stability.mean_spearman_matched": np.mean(spearman_matched),
        "dead_features.cv_pct": dead_cv,
    }

    n_pass = 0
    for pred_key, pred in predictions.items():
        observed = observed_map.get(pred["field"])
        if pred["direction"] == "less_than":
            passed = observed < pred["threshold"]
        else:
            passed = observed > pred["threshold"]
        n_pass += int(passed)
        comparison[pred_key] = {
            "name": pred["name"],
            "predicted": pred["predicted"],
            "observed": float(observed),
            "status": "PASS" if passed else "FAIL",
        }
        print(f"\n  {pred_key}: {pred['name']}")
        print(f"    Predicted: {pred['predicted']}  |  Observed: {observed:.4f}  |  "
              f"{'PASS' if passed else '** FAIL **'}")

    # ── Assemble results ──────────────────────────────────────────────────
    output = {
        "n_sae_seeds": len(seeds),
        "base_model_seed": CFG.base_model_seed,
        "target_layer": CFG.target_layer,
        "d_sae": CFG.d_sae,
        "k": CFG.k,
        "feature_matching": {
            "mean_max_cosine": float(np.mean(mean_max_cosines)),
            "std_max_cosine": float(np.std(mean_max_cosines)),
            "all_max_cosines": [float(x) for x in mean_max_cosines],
            "mean_matched_cosine_top500": float(np.mean(mean_matched_cosines)),
        },
        "importance_stability": {
            "mean_spearman_matched": float(np.mean(spearman_matched)),
            "all_spearman_matched": [float(x) for x in spearman_matched],
            "mean_spearman_raw": float(np.mean(raw_rhos)),
            "all_spearman_raw": [float(x) for x in raw_rhos],
        },
        "dead_features": {
            "per_seed": {str(s): float(dead_fractions[s]) for s in seeds},
            "mean": float(np.mean(dead_frac_values)),
            "cv_pct": dead_cv,
        },
        "pair_results": pair_results,
        "predictions": comparison,
        "predictions_summary": f"{n_pass}/{len(predictions)} PASS",
    }

    out_path = RESULTS_DIR / "sae_stability_results.json"
    tmp = out_path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(output, f, indent=2)
    tmp.rename(out_path)
    print(f"\nResults saved to {out_path}")

    # ── Interpretation ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    mmx = np.mean(mean_max_cosines)
    if mmx > 0.80:
        print(f"Mean max cosine = {mmx:.3f} > 0.80: SAE features are STABLE across seeds.")
        print("SAE-based attribution likely ESCAPES the Rashomon property.")
        print("Implication: SAEs provide an escape hatch from the impossibility for")
        print("component-level attribution — the decomposition is determined by the")
        print("frozen model's activation structure, not by the SAE seed.")
    elif mmx < 0.60:
        print(f"Mean max cosine = {mmx:.3f} < 0.60: SAE features are UNSTABLE across seeds.")
        print("The impossibility EXTENDS to SAE-based attribution.")
        print("Implication: even the dominant MI paradigm (SAE features) is subject to")
        print("the attribution impossibility — different SAE seeds produce different features.")
    else:
        print(f"Mean max cosine = {mmx:.3f}: MIXED result.")
        print("Some features are stable (universal), others are seed-dependent.")
        print("The Rashomon property holds partially for SAE features.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["collect", "train", "analyze"], required=True)
    parser.add_argument("--sae-seed", type=int, default=None)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.phase == "collect":
        collect_activations(device)
    elif args.phase == "train":
        if args.sae_seed is None:
            print("--sae-seed required for train phase")
        else:
            train_single_sae(args.sae_seed, device)
    elif args.phase == "analyze":
        analyze_sae_stability()
