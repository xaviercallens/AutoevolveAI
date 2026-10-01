"""
anse/laya/trainer.py
====================
CPU-optimized multi-task LoRA trainer for Laya Coding Companion.

Loss function:
  L = w_noul·BCE(noul) + w_choice·CE(choice) + w_score·Huber(score) + w_gate·BCE(gate)
  (only applied to samples that have the respective label)

Training is designed for CPU (no CUDA required) with:
  - AdamW optimizer
  - OneCycleLR schedule with warmup
  - Gradient accumulation (effective batch = batch_size * accumulation_steps)
  - Checkpointing to /mnt/data/

Receipts (JSON) are written after each stage for pipeline gate verification.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from anse.laya.dataset import LayaCodingDataset, stratified_split
from anse.laya.model import LayaCodingCompanion


class LayaTrainer:
    """
    CPU LoRA trainer for LayaCodingCompanion.

    Trains in stages:
      Stage 1: noul=1.0, choice=0.5, score=0.0, gate=0.5
      Stage 2: noul=0.3, choice=0.5, score=1.0, gate=0.3
      Stage 3: noul=0.5, choice=1.0, score=0.3, gate=0.5
    """

    STAGE_WEIGHTS = {
        1: {'noul': 1.0, 'choice': 0.5, 'score': 0.0, 'gate': 0.5},
        2: {'noul': 0.3, 'choice': 0.5, 'score': 1.0, 'gate': 0.3},
        3: {'noul': 0.5, 'choice': 1.0, 'score': 0.3, 'gate': 0.5},
    }

    def __init__(
        self,
        model: LayaCodingCompanion,
        checkpoint_dir: Path,
        learning_rate: float = 2e-4,
        batch_size: int = 16,
        accumulation_steps: int = 4,
        num_epochs: int = 5,
        warmup_ratio: float = 0.1,
        val_split: float = 0.1,
        device: str = "cpu",
        patience: int = 2,
    ) -> None:
        self.model = model
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.accumulation_steps = accumulation_steps
        self.num_epochs = num_epochs
        self.warmup_ratio = warmup_ratio
        self.val_split = val_split
        self.device = device
        self.patience = patience

        # Loss functions
        self.bce_loss = nn.BCELoss(reduction="none")
        self.ce_loss = nn.CrossEntropyLoss(reduction="none")
        self.huber_loss = nn.HuberLoss(reduction="none", delta=1.0)

    def _masked_loss(
        self,
        pred: torch.Tensor,
        target: torch.Tensor,
        mask: torch.Tensor,
        loss_fn: nn.Module,
    ) -> torch.Tensor:
        """Compute loss only on samples where mask=1."""
        if mask.sum() == 0:
            return torch.tensor(0.0)
        per_sample = loss_fn(pred, target)
        return (per_sample * mask).sum() / (mask.sum() + 1e-8)

    def _compute_loss(
        self,
        batch: dict[str, torch.Tensor],
        loss_weights: dict[str, float],
    ) -> tuple[torch.Tensor, dict[str, float]]:
        """Compute multi-task loss for one batch."""
        noul_pred, choice_logits, score_pred, gate_pred = self.model(
            batch["input_ids"].to(self.device),
            batch["attention_mask"].to(self.device),
        )

        noul_target = batch["noul_label"].to(self.device)
        noul_mask = batch["has_noul"].to(self.device)
        choice_target = batch["choice_label"].to(self.device)
        choice_mask = batch["has_choice"].to(self.device)
        score_target = batch["score_label"].to(self.device)
        score_mask = batch["has_score"].to(self.device)

        # BCE loss (noul gate)
        l_noul = self._masked_loss(noul_pred, noul_target, noul_mask, self.bce_loss)

        # CE loss (choice routing)
        l_choice = self._masked_loss(
            choice_logits,
            choice_target,
            choice_mask,
            lambda logits, targets: self.ce_loss(logits, targets),
        )

        # Huber loss (score regression)
        l_score = self._masked_loss(
            score_pred,
            score_target.clamp(0, 100),  # normalize to [0, 100]
            score_mask,
            self.huber_loss,
        )
        
        # BCE loss (gate head)
        l_gate = self._masked_loss(gate_pred, noul_target, noul_mask, self.bce_loss)

        total = (
            loss_weights['noul'] * l_noul +
            loss_weights['choice'] * l_choice +
            loss_weights['score'] * l_score +
            loss_weights['gate'] * l_gate
        )
        return total, {
            "loss": float(total.detach()),
            "l_noul": float(l_noul.detach()) if isinstance(l_noul, torch.Tensor) else float(l_noul),
            "l_choice": float(l_choice.detach()) if isinstance(l_choice, torch.Tensor) else float(l_choice),
            "l_score": float(l_score.detach()) if isinstance(l_score, torch.Tensor) else float(l_score),
            "l_gate": float(l_gate.detach()) if isinstance(l_gate, torch.Tensor) else float(l_gate),
        }

    def _evaluate(
        self,
        val_loader: DataLoader,
        loss_weights: dict[str, float],
    ) -> dict[str, float]:
        """Evaluate model on validation set, compute loss + noul accuracy."""
        self.model.eval()
        total_loss = 0.0
        noul_correct = 0
        noul_total = 0

        with torch.no_grad():
            for batch in val_loader:
                loss, _ = self._compute_loss(batch, loss_weights)
                total_loss += float(loss)

                # Noul accuracy
                noul_pred, _, _, _ = self.model(
                    batch["input_ids"].to(self.device),
                    batch["attention_mask"].to(self.device),
                )
                mask = batch["has_noul"].bool()
                if mask.any():
                    pred_labels = (noul_pred[mask] > 0.5).float()
                    true_labels = batch["noul_label"].to(self.device)[mask]
                    noul_correct += (pred_labels == true_labels).sum().item()
                    noul_total += mask.sum().item()

        avg_loss = total_loss / max(len(val_loader), 1)
        noul_acc = noul_correct / max(noul_total, 1)
        return {"val_loss": avg_loss, "noul_accuracy": noul_acc}

    def train_stage(
        self,
        stage: int,
        dataset: LayaCodingDataset,
        results_json_path: Path | None = None,
        loss_weights: dict[str, float] | None = None,
        epochs: int | None = None,
    ) -> dict[str, Any]:
        """Train one stage of the 3-stage curriculum."""
        if loss_weights is None:
            loss_weights = self.STAGE_WEIGHTS.get(stage, {'noul': 1.0, 'choice': 0.5, 'score': 0.0, 'gate': 0.5})
        if epochs is None:
            epochs = self.num_epochs
            
        t0 = time.time()

        print(f"\n  Training Stage {stage}:")
        print(f"    Loss weights: {loss_weights}")
        print(f"    Records: {len(dataset)}, Epochs: {epochs}")
        print(f"    LR={self.learning_rate}, Batch={self.batch_size}, AccumSteps={self.accumulation_steps}")

        # Train/val split
        train_ds, val_ds = stratified_split(dataset, val_fraction=self.val_split)
        train_size = len(train_ds)
        val_size = len(val_ds)

        train_loader = DataLoader(
            train_ds,
            batch_size=self.batch_size,
            shuffle=True,
            collate_fn=LayaCodingDataset.collate_fn,
        )
        val_loader = DataLoader(
            val_ds,
            batch_size=self.batch_size * 2,
            shuffle=False,
            collate_fn=LayaCodingDataset.collate_fn,
        )

        # Optimizer + scheduler
        optimizer = torch.optim.AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=self.learning_rate,
            weight_decay=0.01,
        )
        
        total_steps = len(train_loader) * epochs // self.accumulation_steps
        if total_steps == 0: total_steps = 1
        
        pct_start = self.warmup_ratio if self.warmup_ratio > 0 else 0.1
        scheduler = torch.optim.lr_scheduler.OneCycleLR(
            optimizer, 
            max_lr=self.learning_rate,
            total_steps=total_steps,
            pct_start=pct_start,
            anneal_strategy='cos'
        )

        history: list[dict] = []
        step = 0
        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(1, epochs + 1):
            self.model.train()
            epoch_loss = 0.0
            optimizer.zero_grad()

            for batch_idx, batch in enumerate(train_loader):
                loss, losses = self._compute_loss(batch, loss_weights)
                (loss / self.accumulation_steps).backward()
                epoch_loss += float(loss)

                if (batch_idx + 1) % self.accumulation_steps == 0 or (batch_idx + 1) == len(train_loader):
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(), max_norm=1.0
                    )
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()
                    step += 1

                if batch_idx % 5 == 0:
                    print(f"    Epoch {epoch}/{epochs} | "
                          f"Batch {batch_idx}/{len(train_loader)} | "
                          f"Loss: {float(loss.detach()):.4f} | "
                          f"noul={losses['l_noul']:.4f} choice={losses['l_choice']:.4f} score={losses['l_score']:.4f} gate={losses['l_gate']:.4f}",
                          flush=True)

            # Validation
            val_metrics = self._evaluate(val_loader, loss_weights)
            avg_train_loss = epoch_loss / max(len(train_loader), 1)
            print(f"    Epoch {epoch} Summary: train_loss={avg_train_loss:.4f} | "
                  f"val_loss={val_metrics['val_loss']:.4f} | "
                  f"noul_acc={val_metrics['noul_accuracy']:.3f}",
                  flush=True)

            epoch_record = {
                "epoch": epoch,
                "train_loss": avg_train_loss,
                **val_metrics,
            }
            history.append(epoch_record)
            
            # Save per-epoch logging to JSON
            if results_json_path:
                with open(results_json_path, 'w') as f:
                    json.dump(history, f, indent=2)
            
            # Early stopping
            if val_metrics["val_loss"] < best_val_loss:
                best_val_loss = val_metrics["val_loss"]
                patience_counter = 0
            else:
                patience_counter += 1
                
            if patience_counter >= self.patience:
                print(f"    Early stopping triggered at epoch {epoch}")
                break

        duration = time.time() - t0
        final_val = history[-1] if history else {}

        # Save stage checkpoint
        ckpt_path = self.checkpoint_dir / f"stage{stage}"
        self.model.save_checkpoint(ckpt_path)

        receipt = {
            "stage": stage,
            "status": "COMPLETED",
            "duration_s": round(duration, 1),
            "train_records": train_size,
            "val_records": val_size,
            "epochs": epochs,
            "final_train_loss": history[-1]["train_loss"] if history else None,
            "final_val_loss": final_val.get("val_loss"),
            "final_noul_accuracy": final_val.get("noul_accuracy"),
            "loss_weights": loss_weights,
            "checkpoint_path": str(ckpt_path),
            "training_history": history,
        }
        print(f"  ✅ Stage {stage} complete in {duration:.1f}s → {ckpt_path}")
        return receipt
