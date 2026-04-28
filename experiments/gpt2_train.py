#!/usr/bin/env python3
"""
Train a single GPT-2-small model from scratch on OpenWebText.

Usage:
    CUDA_VISIBLE_DEVICES=0 python gpt2_train.py --seed 0
    CUDA_VISIBLE_DEVICES=1 python gpt2_train.py --seed 1

Crash recovery: automatically resumes from the latest checkpoint.
Completion marker: writes {CHECKPOINT_DIR}/gpt2_seed{N}/DONE on completion.
"""
import argparse
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import tiktoken
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import GPT2Config, GPT2LMHeadModel

from config import GPT2TrainConfig, DATA_DIR, CHECKPOINT_DIR, RESULTS_DIR

CFG = GPT2TrainConfig()


# ── Data ──────────────────────────────────────────────────────────────────────

class TokenDataset(Dataset):
    """Memory-mapped token dataset. Tokens stored as uint16 in a flat binary file."""

    def __init__(self, path: Path, block_size: int):
        self.block_size = block_size
        self.data = np.memmap(str(path), dtype=np.uint16, mode='r')
        self.n_tokens = len(self.data)

    def __len__(self):
        return (self.n_tokens - 1) // self.block_size

    def __getitem__(self, idx):
        # Random offset for each access (stochastic data augmentation)
        start = np.random.randint(0, self.n_tokens - self.block_size - 1)
        chunk = self.data[start:start + self.block_size + 1].astype(np.int64)
        x = torch.from_numpy(chunk[:-1])
        y = torch.from_numpy(chunk[1:])
        return x, y


MAX_TRAIN_TOKENS = 3_000_000_000   # 3B tokens = 6GB on disk, enough for 50K steps
MAX_VAL_TOKENS = 10_000_000        # 10M tokens for validation


def prepare_data():
    """Download and tokenize OpenWebText using streaming (no disk cache)."""
    train_path = DATA_DIR / "openwebtext_train.bin"
    val_path = DATA_DIR / "openwebtext_val.bin"

    if train_path.exists() and val_path.exists():
        print(f"Data already prepared: {train_path} ({train_path.stat().st_size / 1e9:.1f} GB)")
        return train_path, val_path

    # Clean any failed partial files
    for p in [train_path.with_suffix(".tmp"), val_path.with_suffix(".tmp")]:
        p.unlink(missing_ok=True)

    print("Preparing OpenWebText data via streaming (no full download cache)...")
    from datasets import load_dataset

    enc = tiktoken.get_encoding("gpt2")

    # Stream to avoid caching the full arrow dataset on disk (~24GB)
    dataset = load_dataset(CFG.dataset_name, split="train", streaming=True)

    for split_name, max_tokens, out_path in [
        ("train", MAX_TRAIN_TOKENS, train_path),
        ("val", MAX_VAL_TOKENS, val_path),
    ]:
        print(f"Tokenizing {split_name} (up to {max_tokens/1e9:.1f}B tokens)...")
        tmp_path = out_path.with_suffix(".tmp")
        total_tokens = 0
        with open(tmp_path, "wb") as f:
            chunk = []
            for doc in dataset:
                tokens = enc.encode_ordinary(doc["text"])
                chunk.extend(tokens)
                if len(chunk) >= 10_000_000:
                    arr = np.array(chunk, dtype=np.uint16)
                    arr.tofile(f)
                    total_tokens += len(chunk)
                    chunk = []
                    if total_tokens % 100_000_000 < 10_000_000:
                        print(f"    {total_tokens/1e9:.1f}B tokens...")
                    if total_tokens >= max_tokens:
                        break
            if chunk and total_tokens < max_tokens:
                arr = np.array(chunk, dtype=np.uint16)
                arr.tofile(f)
                total_tokens += len(chunk)
        tmp_path.rename(out_path)
        print(f"  Saved {total_tokens:,} tokens to {out_path}")

        # Re-create iterator for val split (streaming iterators are single-pass)
        if split_name == "train":
            dataset = load_dataset(CFG.dataset_name, split="train", streaming=True)
            # Skip the documents we already used for training
            dataset = dataset.skip(total_tokens // 200)  # ~200 tokens/doc avg

    return train_path, val_path


# ── Training ──────────────────────────────────────────────────────────────────

def get_lr(step: int) -> float:
    """Cosine learning rate schedule with warmup."""
    if step < CFG.warmup_steps:
        return CFG.learning_rate * step / CFG.warmup_steps
    if step >= CFG.max_steps:
        return CFG.min_lr
    decay_ratio = (step - CFG.warmup_steps) / (CFG.max_steps - CFG.warmup_steps)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return CFG.min_lr + coeff * (CFG.learning_rate - CFG.min_lr)


def save_checkpoint(model, optimizer, step, loss, ckpt_dir: Path):
    """Atomic checkpoint save."""
    ckpt = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "step": step,
        "loss": loss,
    }
    tmp = ckpt_dir / "checkpoint.tmp"
    torch.save(ckpt, tmp)
    tmp.rename(ckpt_dir / "checkpoint.pt")  # atomic
    print(f"  Checkpoint saved at step {step}")


def load_checkpoint(model, optimizer, ckpt_dir: Path, device: torch.device):
    """Load checkpoint if it exists. Returns step number."""
    ckpt_path = ckpt_dir / "checkpoint.pt"
    if not ckpt_path.exists():
        return 0
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model"])
    optimizer.load_state_dict(ckpt["optimizer"])
    print(f"  Resumed from step {ckpt['step']}")
    return ckpt["step"]


@torch.no_grad()
def evaluate(model, val_dataset, device, n_batches=50):
    """Evaluate perplexity on validation set."""
    model.eval()
    losses = []
    for i, (x, y) in enumerate(DataLoader(val_dataset, batch_size=CFG.batch_size, shuffle=True)):
        if i >= n_batches:
            break
        x, y = x.to(device), y.to(device)
        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            logits = model(x).logits
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))
        losses.append(loss.item())
    model.train()
    mean_loss = sum(losses) / len(losses)
    return {"loss": mean_loss, "ppl": math.exp(mean_loss)}


def train_single_model(seed: int):
    """Train one GPT-2-small model with the given seed."""
    ckpt_dir = CHECKPOINT_DIR / f"gpt2_seed{seed}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    done_marker = ckpt_dir / "DONE"
    if done_marker.exists():
        print(f"Seed {seed}: already complete (DONE marker exists)")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Seed {seed}: training on {device}")

    # ── Reproducibility ───────────────────────────────────────────────────
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)

    # ── Model ─────────────────────────────────────────────────────────────
    config = GPT2Config(
        vocab_size=CFG.vocab_size,
        n_positions=CFG.block_size,
        n_embd=CFG.n_embd,
        n_layer=CFG.n_layer,
        n_head=CFG.n_head,
        resid_pdrop=CFG.dropout,
        embd_pdrop=CFG.dropout,
        attn_pdrop=CFG.dropout,
    )
    model = GPT2LMHeadModel(config).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  Model: {n_params/1e6:.1f}M parameters")

    # ── Optimizer ─────────────────────────────────────────────────────────
    param_groups = [
        {"params": [p for n, p in model.named_parameters() if p.dim() >= 2],
         "weight_decay": CFG.weight_decay},
        {"params": [p for n, p in model.named_parameters() if p.dim() < 2],
         "weight_decay": 0.0},
    ]
    optimizer = torch.optim.AdamW(
        param_groups, lr=CFG.learning_rate, betas=(CFG.beta1, CFG.beta2),
        fused=torch.cuda.is_available()
    )

    # ── Data ──────────────────────────────────────────────────────────────
    train_path, val_path = prepare_data()
    train_dataset = TokenDataset(train_path, CFG.block_size)
    val_dataset = TokenDataset(val_path, CFG.block_size)
    train_loader = DataLoader(train_dataset, batch_size=CFG.batch_size, shuffle=True,
                              num_workers=2, pin_memory=True, drop_last=True)

    # ── Resume ────────────────────────────────────────────────────────────
    start_step = load_checkpoint(model, optimizer, ckpt_dir, device)

    # ── Training loop ─────────────────────────────────────────────────────
    model.train()
    # NOTE: No GradScaler with bfloat16 — bf16 has sufficient dynamic range on A100.
    # GradScaler is only needed for float16.
    use_amp = CFG.dtype == "bfloat16"
    train_iter = iter(train_loader)
    log_path = ckpt_dir / "training_log.jsonl"
    eval_log_path = ckpt_dir / "eval_log.jsonl"

    t0 = time.time()

    for step in range(start_step, CFG.max_steps):
        lr = get_lr(step)
        for pg in optimizer.param_groups:
            pg["lr"] = lr

        # Gradient accumulation
        optimizer.zero_grad()
        accum_loss = 0.0
        for micro_step in range(CFG.gradient_accumulation):
            try:
                x, y = next(train_iter)
            except StopIteration:
                train_iter = iter(train_loader)
                x, y = next(train_iter)

            x, y = x.to(device), y.to(device)
            with torch.amp.autocast("cuda", dtype=torch.bfloat16, enabled=use_amp):
                logits = model(x).logits
                loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))
                loss = loss / CFG.gradient_accumulation

            loss.backward()
            accum_loss += loss.item()

        torch.nn.utils.clip_grad_norm_(model.parameters(), CFG.grad_clip)
        optimizer.step()

        # ── Logging ───────────────────────────────────────────────────────
        if step % CFG.log_every == 0:
            dt = time.time() - t0
            tokens_per_sec = (CFG.batch_size * CFG.gradient_accumulation *
                              CFG.block_size * CFG.log_every) / max(dt, 1e-6)
            entry = {"step": step, "loss": accum_loss, "lr": lr,
                     "tokens_per_sec": tokens_per_sec}
            with open(log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            if step % (CFG.log_every * 10) == 0:
                print(f"  Seed {seed} step {step}/{CFG.max_steps}: "
                      f"loss={accum_loss:.4f} lr={lr:.2e} "
                      f"tok/s={tokens_per_sec:.0f}")
            t0 = time.time()

        # ── Evaluation ────────────────────────────────────────────────────
        if step % CFG.eval_every == 0 and step > 0:
            metrics = evaluate(model, val_dataset, device)
            metrics["step"] = step
            with open(eval_log_path, "a") as f:
                f.write(json.dumps(metrics) + "\n")
            print(f"  Seed {seed} step {step}: val_loss={metrics['loss']:.4f} "
                  f"ppl={metrics['ppl']:.1f}")

        # ── Checkpoint ────────────────────────────────────────────────────
        if step % CFG.save_every == 0 and step > 0:
            save_checkpoint(model, optimizer, step, accum_loss, ckpt_dir)

    # ── Final save ────────────────────────────────────────────────────────
    final_metrics = evaluate(model, val_dataset, device, n_batches=200)
    final_metrics["step"] = CFG.max_steps

    # Save final model weights (not optimizer — saves space)
    tmp = ckpt_dir / "model_final.tmp"
    torch.save(model.state_dict(), tmp)
    tmp.rename(ckpt_dir / "model_final.pt")

    # Save final metrics
    with open(ckpt_dir / "final_metrics.json", "w") as f:
        json.dump(final_metrics, f, indent=2)

    # Mark complete
    done_marker.write_text(json.dumps(final_metrics, indent=2))
    print(f"Seed {seed}: DONE. Final PPL = {final_metrics['ppl']:.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    train_single_model(args.seed)
