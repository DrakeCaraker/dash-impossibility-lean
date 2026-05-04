#!/bin/bash
# SAE Follow-up: ReLU + Pretrained + Resolution + Analysis
# Run after the main experiments are done. ~3-4 hours on 4x A10G.
#
# Usage: bash run_sae_followup.sh
set -eo pipefail

export EXPERIMENT_DIR="${EXPERIMENT_DIR:-$HOME/SageMaker/experiments}"
export HF_HOME="${HF_HOME:-$HOME/SageMaker/.cache/huggingface}"
cd "$(dirname "$0")"

echo "=== SAE Follow-up Experiments ==="

# Phase 1: Resolution test (CPU only, fast)
echo ""
echo "=== Phase 1: Resolution (averaging matched features) ==="
python3 sae_followup.py --phase resolve

# Phase 2: ReLU + Pretrained in parallel (2 GPUs each)
echo ""
echo "=== Phase 2: ReLU SAE (GPUs 0-1) + Pretrained SAE (GPUs 2-3) ==="
CUDA_VISIBLE_DEVICES=0 python3 sae_followup.py --phase relu &
PID_RELU=$!
CUDA_VISIBLE_DEVICES=2 python3 sae_followup.py --phase pretrained &
PID_PRE=$!
wait $PID_RELU || echo "ReLU phase failed"
wait $PID_PRE || echo "Pretrained phase failed"

# Phase 3: Compare all conditions
echo ""
echo "=== Phase 3: Comparison ==="
python3 sae_followup.py --phase analyze

# Phase 4: Copy results to repo and push
echo ""
echo "=== Phase 4: Push results ==="
REPO_DIR="$(cd .. && pwd)"
DEST="$REPO_DIR/docs/gpt2-experiment-results/sae_followup"
mkdir -p "$DEST"
cp "$EXPERIMENT_DIR/results/sae_followup/"*.json "$DEST/" 2>/dev/null || true
cp "$EXPERIMENT_DIR/results/sae_followup/relu/results.json" "$DEST/relu_results.json" 2>/dev/null || true
cp "$EXPERIMENT_DIR/results/sae_followup/pretrained/results.json" "$DEST/pretrained_results.json" 2>/dev/null || true

cd "$REPO_DIR"
git add docs/gpt2-experiment-results/sae_followup/
git commit -m "data: SAE follow-up — ReLU, pretrained, resolution (auto-pushed)" || echo "Nothing to commit"
git push origin main || echo "Push failed — results saved locally"

echo ""
echo "=== DONE ==="
