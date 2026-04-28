# GPT-2-from-Scratch + SAE Stability Experiments

## Overview

Two experiments testing the Attribution Impossibility at GPT-2-small scale:

1. **GPT-2-from-scratch**: Train 10 GPT-2-small models (124M params) from independent random seeds on OpenWebText. Measure circuit importance instability via activation patching. Test whether the G-invariant projection resolves it. This is the same experiment as TinyStories Configs A/B but at the scale used by foundational MI papers (Wang et al. 2022, Olsson et al. 2022, Conmy et al. 2023).

2. **SAE stability**: Train 10 sparse autoencoders on the same frozen GPT-2-small model with different seeds. Measure whether independently trained SAEs produce the same interpretable features. This tests whether SAE-based attribution escapes the Rashomon property.

## Hardware

**ml.g5.12xlarge** (4x A100-80GB, 48 vCPU, 192GB RAM)

Estimated wall time: ~18-22 hours total.

## Usage

```bash
# Full run (all phases, crash-safe)
bash run.sh

# Or run phases individually:
python gpt2_train.py --seed 0          # train one model
python gpt2_evaluate.py --seed 0       # patch one model
python gpt2_evaluate.py --analyze      # analyze all models
python sae_experiment.py --phase collect
python sae_experiment.py --phase train --sae-seed 0
python sae_experiment.py --phase analyze
```

## Predictions

Written to `predictions.json` BEFORE any evaluation. 7 predictions for GPT-2, 3 for SAE. The analysis scripts load and compare against these automatically.

### GPT-2 predictions (from theory + TinyStories trend)

| ID | Prediction | Threshold | Justification |
|----|-----------|-----------|---------------|
| P1 | PPL CV < 5% | 5% | Functional equivalence |
| P2 | Raw Spearman < 0.70 | 0.70 | S_12^12 symmetry creates Rashomon |
| P3 | G-invariant Spearman > 0.80 | 0.80 | Stable between-orbit structure |
| P4 | Head lift > 0.15 | 0.15 | G-inv captures non-trivial structure |
| P5 | Within-layer flip > 0.40 | 0.40 | Near coin-flip (theory: 0.50) |
| P6 | Head-vs-MLP flip < 0.15 | 0.15 | Stable between-group |
| P7 | Permutation p < 0.01 | 0.01 | G-inv not random |

### SAE predictions (genuinely open)

| ID | Prediction | Threshold | Justification |
|----|-----------|-----------|---------------|
| S1 | Mean max cosine > 0.80 | 0.80 | SAEs decompose fixed activations |
| S2 | Matched importance Spearman > 0.70 | 0.70 | Importance from frozen model |
| S3 | Dead feature CV < 20% | 20% | Architecture-determined |

## Methodological Controls

### For GPT-2-from-scratch

1. **Functional equivalence**: All 10 models must have PPL CV < 5%. If models converge to different quality levels, importance differences could reflect model quality, not permutation symmetry.

2. **Fixed eval set**: 2000 sequences sampled deterministically from validation split. Saved to disk before any patching. Same sequences for all 10 models.

3. **Two ablation methods**: Weight zeroing (primary) and mean ablation (robustness check). Cross-method agreement tests whether the results are method-specific.

4. **Split-half reliability**: Random split of eval sequences. Within-model reliability should greatly exceed between-model agreement (confirms instability is structural, not measurement noise).

5. **Random projection null**: 1000 random projections to the same dimensionality as G-invariant (24-dim). Tests whether ANY low-dimensional projection gives high agreement, or whether the G-invariant projection is specifically effective.

6. **Permutation test**: 1000 random permutations of head labels. Tests whether the G-invariant grouping (by layer) is significantly better than random groupings.

7. **S_12 realization check**: For each layer, count how many distinct heads appear as "most important" across 10 seeds. Under perfect symmetry, all 12 should appear (though 10 draws from 12 categories won't cover all 12 with certainty).

8. **Bonferroni correction**: 10 statistical tests reported; significance threshold adjusted to 0.005.

### For SAE stability

1. **Frozen model**: All 10 SAEs train on activations from the same frozen GPT-2-small (seed 0). This ensures the only source of variation is the SAE seed.

2. **Optimal matching**: Hungarian algorithm on cosine similarity matrix for top-500 features. This is the fairest comparison — it doesn't penalize for arbitrary feature ordering.

3. **Greedy matching**: For computational efficiency, also report greedy (per-feature max cosine). Comparison between greedy and optimal matching reveals matching quality.

4. **Dead feature stability**: Dead features (activation frequency = 0) are excluded from matching quality. Dead feature fraction CV measures whether optimization dynamics are consistent across seeds.

5. **Raw importance Spearman**: Without matching — compares importance vectors directly. This is a lower bound (features are in different coordinate systems).

## Crash Recovery

Every phase writes atomic DONE markers. On re-run:
- Models with DONE markers are skipped
- Models with checkpoints resume from latest checkpoint
- Models with no checkpoint start from scratch

Checkpointing frequency:
- GPT-2 training: every 5,000 steps (~30 min intervals)
- SAE training: every 10,000 steps
- All writes use tmp+rename pattern for atomicity

## Output

```
$EXPERIMENT_DIR/
  data/                          # Tokenized OpenWebText
  eval_data/                     # Fixed eval sequences
  checkpoints/gpt2_seed{0-9}/    # Model checkpoints + DONE markers
  results/
    patch_seed{0-9}/             # Per-model patching results
    sae/
      activations_{train,eval}.npy
      sae_seed{0-9}/             # Per-SAE checkpoints + results
    gpt2_from_scratch_results.json   # Final GPT-2 analysis
    sae_stability_results.json       # Final SAE analysis
```
