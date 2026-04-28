"""
Shared configuration for GPT-2-from-scratch and SAE stability experiments.

Hardware assumption: ml.g5.12xlarge (4x A100-80GB)
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(os.environ.get("EXPERIMENT_DIR", "/home/ec2-user/experiments"))
DATA_DIR = BASE_DIR / "data"
CHECKPOINT_DIR = BASE_DIR / "checkpoints"
RESULTS_DIR = BASE_DIR / "results"
EVAL_DIR = BASE_DIR / "eval_data"

for d in [DATA_DIR, CHECKPOINT_DIR, RESULTS_DIR, EVAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── GPT-2 Training ────────────────────────────────────────────────────────────

@dataclass
class GPT2TrainConfig:
    # Architecture (matches GPT-2-small exactly)
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    vocab_size: int = 50257
    block_size: int = 1024
    dropout: float = 0.0   # 0 for eval reproducibility; original used 0.1

    # Training
    n_seeds: int = 10
    max_steps: int = 50_000        # ~3B tokens at batch 60K (fits 100GB volume)
    batch_size: int = 12           # per-GPU micro-batch
    gradient_accumulation: int = 5 # effective batch = 12*5*1024 = 61,440 tokens
    learning_rate: float = 6e-4
    min_lr: float = 6e-5
    warmup_steps: int = 2000
    weight_decay: float = 0.1
    beta1: float = 0.9
    beta2: float = 0.95
    grad_clip: float = 1.0
    dtype: str = "bfloat16"

    # Checkpointing
    save_every: int = 5_000        # save checkpoint every N steps
    eval_every: int = 1_000        # evaluate perplexity every N steps
    log_every: int = 100           # log loss every N steps

    # Data
    dataset_name: str = "Skylion007/openwebtext"
    eval_tokens: int = 10_485_760  # 10M tokens for validation


# ── Activation Patching ───────────────────────────────────────────────────────

@dataclass
class PatchConfig:
    n_eval_sequences: int = 2000   # fixed eval set for all models
    eval_seq_length: int = 1024
    methods: tuple = ("weight_zeroing", "mean_ablation")

    @property
    def n_components(self) -> int:
        """12 layers * (12 heads + 1 MLP) = 156 components."""
        return 12 * (12 + 1)

    @property
    def n_invariant(self) -> int:
        """12 head-averages + 12 MLPs = 24 invariant components."""
        return 12 + 12


# ── SAE ───────────────────────────────────────────────────────────────────────

@dataclass
class SAEConfig:
    base_model_seed: int = 0       # use model seed 0 as the frozen base
    n_sae_seeds: int = 10
    target_layer: int = 6          # middle layer (standard in MI literature)
    target_hook: str = "resid_post"  # residual stream after layer 6
    d_sae: int = 768 * 8           # 6144 features (8x overcomplete)
    k: int = 48                    # TopK sparsity
    sae_lr: float = 3e-4
    sae_steps: int = 50_000        # training steps
    sae_batch_size: int = 4096     # activation vectors per batch
    n_activation_batches: int = 200  # total training activations: 200*4096 = 819,200
    n_eval_activations: int = 50_000  # for feature importance evaluation


# ── Statistical Analysis ──────────────────────────────────────────────────────

@dataclass
class StatsConfig:
    n_bootstrap: int = 10_000      # bootstrap resamples for CIs
    n_permutations: int = 1_000    # permutation test iterations
    n_random_projections: int = 1_000  # random projection null
    alpha: float = 0.05            # significance level
    bonferroni_tests: int = 10     # number of tests for Bonferroni correction
    ci_level: float = 0.95

    @property
    def bonferroni_alpha(self) -> float:
        return self.alpha / self.bonferroni_tests
