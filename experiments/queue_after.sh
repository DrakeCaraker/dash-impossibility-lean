#!/bin/bash
# Queue IOI + SAE + analysis to run automatically after the current run.sh finishes.
#
# Usage (one line from SageMaker):
#   cd ~/SageMaker/datascience/dash-impossibility-lean/experiments && bash queue_after.sh
#
# What it does:
#   1. Finds the running run.sh process
#   2. Waits for it to finish (polls every 60s)
#   3. Runs IOI analysis on all 10 trained models (4 GPUs parallel)
#   4. Runs SAE stability experiment (4 GPUs parallel)
#   5. Runs full statistical analysis
#   6. Prints summary of all results
#
# Safe to run while run.sh is still training. Logs to ~/SageMaker/queue_after.log

set -euo pipefail

export EXPERIMENT_DIR="${EXPERIMENT_DIR:-$HOME/SageMaker/experiments}"
export HF_HOME="${HF_HOME:-$HOME/SageMaker/.cache/huggingface}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$HOME/SageMaker/queue_after.log"
N_GPUS=$(python3 -c "import torch; print(torch.cuda.device_count())" 2>/dev/null || echo 1)

# Find the running run.sh
RUN_PID=$(pgrep -f "bash run.sh" | head -1 || true)

if [ -z "$RUN_PID" ]; then
    echo "No run.sh process found. Will start immediately."
else
    echo "Found run.sh (PID $RUN_PID). Will queue after it finishes."
    echo "Log: $LOG"
fi

# Run everything in background via nohup
nohup bash -c "
set -euo pipefail
export EXPERIMENT_DIR='$EXPERIMENT_DIR'
export HF_HOME='$HF_HOME'
cd '$SCRIPT_DIR'

# ── Wait for run.sh to finish ─────────────────────────────────────
if [ -n '${RUN_PID:-}' ]; then
    echo '[\$(date)] Waiting for run.sh (PID $RUN_PID) to finish...'
    while kill -0 $RUN_PID 2>/dev/null; do
        sleep 60
    done
    echo '[\$(date)] run.sh finished. Starting follow-up experiments.'
fi

# ── Verify training completed ─────────────────────────────────────
DONE_COUNT=\$(ls \$EXPERIMENT_DIR/checkpoints/gpt2_seed*/DONE 2>/dev/null | wc -l)
echo \"[\$(date)] \$DONE_COUNT/10 models trained.\"
if [ \"\$DONE_COUNT\" -lt 10 ]; then
    echo 'ERROR: Not all models trained. Aborting.'
    exit 1
fi

# ── IOI circuit analysis (4 GPUs parallel) ────────────────────────
echo ''
echo '[\$(date)] === IOI Circuit Analysis ==='
for seed in \$(seq 0 9); do
    if [ -f \"\$EXPERIMENT_DIR/results/ioi/patch_seed\${seed}/DONE\" ]; then
        echo \"  IOI seed \$seed: already done, skipping.\"
        continue
    fi
    gpu=\$((seed % $N_GPUS))
    echo \"  IOI seed \$seed on GPU \$gpu...\"
    CUDA_VISIBLE_DEVICES=\$gpu python3 ioi_analysis.py --seed \$seed &
    if (( (seed + 1) % $N_GPUS == 0 )); then wait; fi
done
wait
echo '[\$(date)] IOI patching complete. Running analysis...'
python3 ioi_analysis.py --analyze

# ── SAE stability (4 GPUs parallel) ──────────────────────────────
echo ''
echo '[\$(date)] === SAE Stability Experiment ==='
echo '  Collecting activations...'
CUDA_VISIBLE_DEVICES=0 python3 sae_experiment.py --phase collect

for sae_seed in \$(seq 0 9); do
    if [ -f \"\$EXPERIMENT_DIR/results/sae/sae_seed\${sae_seed}/DONE\" ]; then
        echo \"  SAE seed \$sae_seed: already done, skipping.\"
        continue
    fi
    gpu=\$((sae_seed % $N_GPUS))
    echo \"  SAE seed \$sae_seed on GPU \$gpu...\"
    CUDA_VISIBLE_DEVICES=\$gpu python3 sae_experiment.py --phase train --sae-seed \$sae_seed &
    if (( (sae_seed + 1) % $N_GPUS == 0 )); then wait; fi
done
wait
echo '[\$(date)] SAE training complete. Running analysis...'
python3 sae_experiment.py --phase analyze

# ── Full GPT-2 analysis (if not already done) ────────────────────
echo ''
echo '[\$(date)] === Full GPT-2 Analysis ==='
python3 gpt2_evaluate.py --analyze

# ── Summary ───────────────────────────────────────────────────────
echo ''
echo '══════════════════════════════════════════════════════════════'
echo 'ALL EXPERIMENTS COMPLETE'
echo '══════════════════════════════════════════════════════════════'
echo ''
echo 'Results:'
ls -lh \$EXPERIMENT_DIR/results/gpt2_from_scratch_results.json 2>/dev/null
ls -lh \$EXPERIMENT_DIR/results/ioi/ioi_results.json 2>/dev/null
ls -lh \$EXPERIMENT_DIR/results/sae_stability_results.json 2>/dev/null
echo ''
python3 -c \"
import json
for name, path in [('GPT-2', 'results/gpt2_from_scratch_results.json'),
                   ('IOI', 'results/ioi/ioi_results.json'),
                   ('SAE', 'results/sae_stability_results.json')]:
    try:
        with open('\$EXPERIMENT_DIR/' + path) as f:
            d = json.load(f)
        summary = d.get('predictions_summary', 'N/A')
        print(f'{name}: {summary}')
        if 'flip_rates' in d:
            fr = d['flip_rates']
            print(f'  within_layer_flip={fr[\"within_layer\"]:.3f}  head_vs_mlp={fr[\"head_vs_mlp\"]:.3f}')
        if 'raw_agreement' in d:
            print(f'  raw_rho={d[\"raw_agreement\"][\"mean_spearman\"]:.3f}  ginv_rho={d[\"g_invariant_agreement\"][\"mean_spearman\"]:.3f}')
        if 'feature_matching' in d:
            print(f'  mean_max_cosine={d[\"feature_matching\"][\"mean_max_cosine\"]:.3f}')
    except Exception as e:
        print(f'{name}: not available ({e})')
\"
echo ''
echo '[\$(date)] Done.'
" > "$LOG" 2>&1 &

QUEUE_PID=$!
echo "Queued as PID $QUEUE_PID"
echo "Monitor: tail -f $LOG"
echo "Check status: ps aux | grep queue_after"
