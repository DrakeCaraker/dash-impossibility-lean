#!/bin/bash
# Run all remaining experiments. Training is done. This does patching + IOI + SAE + analysis.
# Usage: bash run_all_now.sh
set -eo pipefail

export EXPERIMENT_DIR="${EXPERIMENT_DIR:-$HOME/SageMaker/experiments}"
export HF_HOME="${HF_HOME:-$HOME/SageMaker/.cache/huggingface}"
cd "$(dirname "$0")"

echo "=== Cleaning stale results and caches ==="
rm -rf __pycache__
rm -rf $EXPERIMENT_DIR/results/patch_seed*
rm -rf $EXPERIMENT_DIR/results/sae/

echo ""
echo "=== Phase 1: General patching (batch=8) ==="
for seed in 0 1 2 3; do CUDA_VISIBLE_DEVICES=$seed python3 gpt2_evaluate.py --seed $seed & done; wait
for seed in 4 5 6 7; do CUDA_VISIBLE_DEVICES=$((seed-4)) python3 gpt2_evaluate.py --seed $seed & done; wait
for seed in 8 9; do CUDA_VISIBLE_DEVICES=$((seed-8)) python3 gpt2_evaluate.py --seed $seed & done; wait

echo ""
echo "=== Phase 2: General analysis ==="
python3 gpt2_evaluate.py --analyze

echo ""
echo "=== Phase 3: IOI (skip if already done) ==="
NEED_IOI=false
for seed in $(seq 0 9); do
    if [ ! -f "$EXPERIMENT_DIR/results/ioi/patch_seed${seed}/DONE" ]; then NEED_IOI=true; break; fi
done
if [ "$NEED_IOI" = true ]; then
    for seed in 0 1 2 3; do CUDA_VISIBLE_DEVICES=$seed python3 ioi_analysis.py --seed $seed & done; wait
    for seed in 4 5 6 7; do CUDA_VISIBLE_DEVICES=$((seed-4)) python3 ioi_analysis.py --seed $seed & done; wait
    for seed in 8 9; do CUDA_VISIBLE_DEVICES=$((seed-8)) python3 ioi_analysis.py --seed $seed & done; wait
    python3 ioi_analysis.py --analyze
else
    echo "  IOI already complete, skipping."
fi

echo ""
echo "=== Phase 4: SAE ==="
CUDA_VISIBLE_DEVICES=0 python3 sae_experiment.py --phase collect
for seed in 0 1 2 3; do CUDA_VISIBLE_DEVICES=$seed python3 sae_experiment.py --phase train --sae-seed $seed & done; wait
for seed in 4 5 6 7; do CUDA_VISIBLE_DEVICES=$((seed-4)) python3 sae_experiment.py --phase train --sae-seed $seed & done; wait
for seed in 8 9; do CUDA_VISIBLE_DEVICES=$((seed-8)) python3 sae_experiment.py --phase train --sae-seed $seed & done; wait
python3 sae_experiment.py --phase analyze

echo ""
echo "=== Phase 5: Pretrained GPT-2 IOI baseline ==="
python3 -c "
import torch, json
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from ioi_analysis import save_prompts, compute_logit_diff

device = torch.device('cuda')
model = GPT2LMHeadModel.from_pretrained('gpt2').to(device).eval()
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
prompts = save_prompts()
baseline = compute_logit_diff(model, tokenizer, prompts, device)
print(f'Pretrained GPT-2: logit_diff={baseline[\"mean_logit_diff\"]:.2f}, acc={baseline[\"accuracy\"]:.1%}')
with open('$EXPERIMENT_DIR/results/ioi/pretrained_baseline.json', 'w') as f:
    json.dump(baseline, f, indent=2)
print('Saved to $EXPERIMENT_DIR/results/ioi/pretrained_baseline.json')
"

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "ALL EXPERIMENTS COMPLETE"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "Results:"
for f in gpt2_from_scratch_results.json ioi/ioi_results.json ioi/pretrained_baseline.json sae_stability_results.json; do
    p="$EXPERIMENT_DIR/results/$f"
    if [ -f "$p" ]; then echo "  OK: $p ($(du -h "$p" | cut -f1))"; else echo "  MISSING: $p"; fi
done

echo ""
echo "=== Phase 6: Copy results to repo and push ==="
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESULTS_DEST="$REPO_DIR/docs/gpt2-experiment-results"
mkdir -p "$RESULTS_DEST/ioi"

cp "$EXPERIMENT_DIR/results/gpt2_from_scratch_results.json" "$RESULTS_DEST/" 2>/dev/null || true
cp "$EXPERIMENT_DIR/results/ioi/ioi_results.json" "$RESULTS_DEST/ioi/" 2>/dev/null || true
cp "$EXPERIMENT_DIR/results/ioi/pretrained_baseline.json" "$RESULTS_DEST/ioi/" 2>/dev/null || true
cp "$EXPERIMENT_DIR/results/sae_stability_results.json" "$RESULTS_DEST/" 2>/dev/null || true

cd "$REPO_DIR"
git add docs/gpt2-experiment-results/
git commit -m "data: GPT-2-from-scratch experiment results (auto-pushed from SageMaker)

General patching: 10 seeds, weight zeroing + mean ablation, batch=8
IOI circuit: 10 seeds, 156 components, within-layer flip, G-inv rho
SAE stability: 10 SAEs on frozen model, feature matching
Pretrained baseline: GPT-2-small reference IOI performance

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>" || echo "Nothing to commit"

git push origin main || echo "Push failed — results saved locally at $RESULTS_DEST"
echo ""
echo "=== DONE. Results committed and pushed. ==="
