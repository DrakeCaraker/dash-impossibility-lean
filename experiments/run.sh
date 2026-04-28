#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# Master experiment orchestrator for ml.g5.12xlarge (4x A100-80GB)
#
# Total estimated wall time: ~18-22 hours
#   Phase 1: Data prep          ~30 min
#   Phase 2: GPT-2 training     ~12 hours (3 rounds of 4 GPUs)
#   Phase 3: Activation patch   ~3 hours  (3 rounds of 4 GPUs)
#   Phase 4: SAE collection     ~15 min
#   Phase 5: SAE training       ~2 hours  (3 rounds of 4 GPUs)
#   Phase 6: Analysis           ~30 min   (CPU)
#
# Crash recovery: all phases check for DONE markers. Safe to re-run after crash.
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

export EXPERIMENT_DIR="${EXPERIMENT_DIR:-/home/ec2-user/experiments}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

N_GPUS=$(python3 -c "import torch; print(torch.cuda.device_count())" 2>/dev/null || echo 1)
echo "══════════════════════════════════════════════════════════════════════"
echo "Attribution Impossibility: GPT-2-from-Scratch + SAE Stability"
echo "GPUs detected: $N_GPUS"
echo "Experiment dir: $EXPERIMENT_DIR"
echo "══════════════════════════════════════════════════════════════════════"

# ── Phase 0: Setup ────────────────────────────────────────────────────────────
echo ""
echo "Phase 0: Installing dependencies..."
pip install -q -r requirements.txt

# ── Phase 1: Data preparation (single-threaded, must complete before training) ─
echo ""
echo "Phase 1: Preparing data (will skip if already done)..."
python3 -c "from gpt2_train import prepare_data; prepare_data()"
echo "  Data ready."

# ── Phase 2: Train 10 GPT-2-small models ─────────────────────────────────────
echo ""
echo "Phase 2: Training 10 GPT-2-small models ($N_GPUS GPUs parallel)..."
run_batch() {
    local start=$1
    local end=$2
    local pids=()

    for seed in $(seq $start $end); do
        # Check if already done
        if [ -f "$EXPERIMENT_DIR/checkpoints/gpt2_seed${seed}/DONE" ]; then
            echo "  Seed $seed: already complete, skipping."
            continue
        fi

        gpu=$(( (seed - start) % N_GPUS ))
        echo "  Starting seed $seed on GPU $gpu..."
        CUDA_VISIBLE_DEVICES=$gpu python3 gpt2_train.py --seed $seed &
        pids+=($!)

        # If we've filled all GPUs, wait for this batch
        if [ ${#pids[@]} -ge $N_GPUS ]; then
            for pid in "${pids[@]}"; do wait $pid || true; done
            pids=()
        fi
    done

    # Wait for remaining
    for pid in "${pids[@]}"; do wait $pid || true; done
}

# Train all 10 seeds in batches of N_GPUS
run_batch 0 9

# Verify all 10 models completed
echo "  Verifying all models..."
ALL_DONE=true
for seed in $(seq 0 9); do
    if [ ! -f "$EXPERIMENT_DIR/checkpoints/gpt2_seed${seed}/DONE" ]; then
        echo "  WARNING: seed $seed did not complete!"
        ALL_DONE=false
    fi
done
if [ "$ALL_DONE" = true ]; then
    echo "  All 10 models trained successfully."
else
    echo "  Some models failed. Re-run this script to retry."
    exit 1
fi

# ── Phase 3: Activation patching ──────────────────────────────────────────────
echo ""
echo "Phase 3: Activation patching (weight zeroing + mean ablation)..."

# Prepare fixed eval set first (single-threaded)
python3 -c "from gpt2_evaluate import prepare_eval_set; prepare_eval_set()"

run_patch_batch() {
    local start=$1
    local end=$2
    local pids=()

    for seed in $(seq $start $end); do
        if [ -f "$EXPERIMENT_DIR/results/patch_seed${seed}/DONE" ]; then
            echo "  Seed $seed: already patched, skipping."
            continue
        fi

        gpu=$(( (seed - start) % N_GPUS ))
        echo "  Patching seed $seed on GPU $gpu..."
        CUDA_VISIBLE_DEVICES=$gpu python3 gpt2_evaluate.py --seed $seed &
        pids+=($!)

        if [ ${#pids[@]} -ge $N_GPUS ]; then
            for pid in "${pids[@]}"; do wait $pid || true; done
            pids=()
        fi
    done

    for pid in "${pids[@]}"; do wait $pid || true; done
}

run_patch_batch 0 9

# ── Phase 4: SAE activation collection ───────────────────────────────────────
echo ""
echo "Phase 4: Collecting activations for SAE training..."
CUDA_VISIBLE_DEVICES=0 python3 sae_experiment.py --phase collect

# ── Phase 5: Train 10 SAEs ───────────────────────────────────────────────────
echo ""
echo "Phase 5: Training 10 SAEs on frozen model..."

run_sae_batch() {
    local start=$1
    local end=$2
    local pids=()

    for sae_seed in $(seq $start $end); do
        if [ -f "$EXPERIMENT_DIR/results/sae/sae_seed${sae_seed}/DONE" ]; then
            echo "  SAE seed $sae_seed: already trained, skipping."
            continue
        fi

        gpu=$(( (sae_seed - start) % N_GPUS ))
        echo "  Training SAE seed $sae_seed on GPU $gpu..."
        CUDA_VISIBLE_DEVICES=$gpu python3 sae_experiment.py --phase train --sae-seed $sae_seed &
        pids+=($!)

        if [ ${#pids[@]} -ge $N_GPUS ]; then
            for pid in "${pids[@]}"; do wait $pid || true; done
            pids=()
        fi
    done

    for pid in "${pids[@]}"; do wait $pid || true; done
}

run_sae_batch 0 9

# ── Phase 6: IOI circuit analysis (uses same trained models) ──────────────────
echo ""
echo "Phase 6: IOI circuit analysis across 10 seeds..."

run_ioi_batch() {
    local start=$1
    local end=$2
    local pids=()

    for seed in $(seq $start $end); do
        if [ -f "$EXPERIMENT_DIR/results/ioi/patch_seed${seed}/DONE" ]; then
            echo "  IOI seed $seed: already complete, skipping."
            continue
        fi

        gpu=$(( (seed - start) % N_GPUS ))
        echo "  IOI patching seed $seed on GPU $gpu..."
        CUDA_VISIBLE_DEVICES=$gpu python3 ioi_analysis.py --seed $seed &
        pids+=($!)

        if [ ${#pids[@]} -ge $N_GPUS ]; then
            for pid in "${pids[@]}"; do wait $pid || true; done
            pids=()
        fi
    done

    for pid in "${pids[@]}"; do wait $pid || true; done
}

run_ioi_batch 0 9

# ── Phase 7: Analysis ─────────────────────────────────────────────────────────
echo ""
echo "Phase 7: Running all analyses..."

echo "  GPT-2 general analysis..."
python3 gpt2_evaluate.py --analyze

echo "  IOI analysis..."
python3 ioi_analysis.py --analyze

echo "  SAE analysis..."
python3 sae_experiment.py --phase analyze

# ── Phase 8: Summary ──────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo "ALL EXPERIMENTS COMPLETE"
echo "══════════════════════════════════════════════════════════════════════"
echo ""
echo "Results:"
echo "  GPT-2 from scratch: $EXPERIMENT_DIR/results/gpt2_from_scratch_results.json"
echo "  IOI circuit:        $EXPERIMENT_DIR/results/ioi/ioi_results.json"
echo "  SAE stability:      $EXPERIMENT_DIR/results/sae_stability_results.json"
echo ""
echo "Copy results to your local machine:"
echo "  scp -r ec2-user@\$HOST:$EXPERIMENT_DIR/results/ ."
echo ""

# Print prediction summary
python3 -c "
import json
for name, path in [('GPT-2', 'results/gpt2_from_scratch_results.json'),
                   ('IOI', 'results/ioi/ioi_results.json'),
                   ('SAE', 'results/sae_stability_results.json')]:
    try:
        with open('$EXPERIMENT_DIR/' + path) as f:
            d = json.load(f)
        print(f'{name}: {d[\"predictions_summary\"]}')
    except:
        print(f'{name}: results not found')
"
