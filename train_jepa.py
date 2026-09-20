#!/usr/bin/env python3
"""
CLI entry point for training the JEPA World Model.

Usage:
    python train_jepa.py --data data/interactions.jsonl --epochs 100
    python train_jepa.py --validate --checkpoint checkpoints/jepa_best.pt
    python train_jepa.py --data data/interactions.jsonl --device cuda --epochs 200
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import torch

from anse.config import get_config
from anse.jepa.dataset import JEPADataset
from anse.jepa.trainer import JEPATrainer
from anse.jepa.world_model import JEPAWorldModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("train_jepa")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train the JEPA World Model on Phase 1 traces.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Data
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Path to interactions.jsonl from Phase 1 Harvester.",
    )

    # Training
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs.")
    parser.add_argument("--batch-size", type=int, default=32, help="Mini-batch size.")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate.")
    parser.add_argument(
        "--val-fraction", type=float, default=0.2, help="Validation split fraction."
    )  # noqa: E501
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")

    # Model
    parser.add_argument(
        "--hidden-dim", type=int, default=4096, help="Input hidden state dimension."
    )  # noqa: E501
    parser.add_argument("--latent-dim", type=int, default=512, help="JEPA latent dimension.")
    parser.add_argument("--device", type=str, default="cpu", help="Device: cpu, cuda, auto.")

    # Checkpoint
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=Path("checkpoints"),
        help="Directory for saving model checkpoints.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Load model from checkpoint (for --validate or resume).",
    )

    # Mode
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation only (requires --checkpoint).",
    )

    return parser.parse_args()


def main() -> int:
    """Main training entry point."""
    args = parse_args()
    config = get_config()

    # Resolve device
    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Using device: %s", device)

    # Load dataset
    logger.info("Loading dataset from %s", args.data)
    dataset = JEPADataset(
        jsonl_path=args.data,
        hidden_dim=args.hidden_dim,
    )
    logger.info("Dataset size: %d samples", len(dataset))

    if len(dataset) == 0:
        logger.error("Dataset is empty — nothing to train on.")
        return 1

    # Create model
    model = JEPAWorldModel(
        d_input=args.hidden_dim,
        d_hidden=config.jepa.hidden_dim,
        d_latent=args.latent_dim,
    )

    # Load checkpoint if specified
    if args.checkpoint:
        logger.info("Loading checkpoint from %s", args.checkpoint)
        model.load(args.checkpoint)

    # Create trainer
    trainer = JEPATrainer(
        model=model,
        config=config.jepa,
        lr=args.lr,
        checkpoint_dir=args.checkpoint_dir,
        device=device,
    )

    if args.validate:
        # Validation-only mode
        if not args.checkpoint:
            logger.error("--validate requires --checkpoint")
            return 1

        from torch.utils.data import DataLoader

        from anse.jepa.dataset import train_val_split

        _, val_ds = train_val_split(dataset, args.val_fraction, args.seed)
        val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False)
        metrics = trainer.validate(val_loader)

        logger.info("Validation Results:")
        logger.info("  Val Loss:              %.4f", metrics.val_loss)
        logger.info("  Prediction Loss:       %.4f", metrics.prediction_loss)
        logger.info("  VICReg Loss:           %.4f", metrics.vicreg_loss)
        logger.info("  Energy Head Loss:      %.4f", metrics.energy_head_loss)
        logger.info("  Energy Accuracy:       %.1f%%", metrics.energy_prediction_accuracy * 100)
        return 0

    # Train
    summary = trainer.train(
        dataset=dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        val_fraction=args.val_fraction,
        seed=args.seed,
    )

    logger.info("Training Summary:")
    logger.info("  Epochs:       %d", summary.epochs_completed)
    logger.info("  Best Val Loss: %.4f", summary.best_val_loss)
    logger.info("  Final Train:   %.4f", summary.final_train_loss)
    logger.info("  Final Val:     %.4f", summary.final_val_loss)
    logger.info("  Total Steps:   %d", summary.total_steps)
    logger.info("  Duration:      %.1fs", summary.training_time_seconds)
    if summary.checkpoint_path:
        logger.info("  Checkpoint:    %s", summary.checkpoint_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
