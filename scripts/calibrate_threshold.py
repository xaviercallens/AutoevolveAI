#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anse.laya.dataset import LayaCodingDataset, stratified_split
from anse.laya.model import LayaCodingCompanion
from scripts.train_laya_coding import load_tokenizer, STAGE_DATASETS

def main():
    parser = argparse.ArgumentParser(description="Calibrate Laya quality gate threshold")
    parser.add_argument("--checkpoint_dir", type=str, required=True, help="Path to checkpoint directory (e.g. .../v2/stage3)")
    args = parser.parse_args()
    
    ckpt_path = Path(args.checkpoint_dir)
    if not (ckpt_path / "laya_heads.pt").exists():
        print(f"Error: No checkpoint found at {ckpt_path}")
        return
        
    print(f"Loading checkpoint from {ckpt_path}...")
    model = LayaCodingCompanion.load_checkpoint(ckpt_path)
    model.eval()
    tokenizer = load_tokenizer(model.base_model_name)
    
    # Load all datasets and get validation splits
    all_val_datasets = []
    for stage, paths in STAGE_DATASETS.items():
        existing_paths = [p for p in paths if p.exists()]
        if not existing_paths: continue
        
        dataset = LayaCodingDataset(
            jsonl_paths=existing_paths,
            tokenizer=tokenizer,
            choice_classes=model.choice_classes,
        )
        if len(dataset) > 0:
            _, val_ds = stratified_split(dataset, val_fraction=0.1)
            all_val_datasets.append(val_ds)
            
    if not all_val_datasets:
        print("No datasets found for validation.")
        return
        
    from torch.utils.data import ConcatDataset
    full_val_ds = ConcatDataset(all_val_datasets)
    val_loader = DataLoader(
        full_val_ds, 
        batch_size=32, 
        shuffle=False, 
        collate_fn=LayaCodingDataset.collate_fn
    )
    
    print(f"Running inference on validation set ({len(full_val_ds)} samples)...")
    true_labels = []
    pred_scores = []
    
    with torch.no_grad():
        for batch in val_loader:
            mask = batch["has_noul"].bool()
            if not mask.any(): continue
            
            # Forward pass
            input_ids = batch["input_ids"]
            attention_mask = batch["attention_mask"]
            noul_pred, _, _, gate_pred = model(input_ids, attention_mask)
            
            # Using gate_pred for calibration
            gate_probs = gate_pred[mask].cpu().numpy()
            labels = batch["noul_label"][mask].cpu().numpy()
            
            pred_scores.extend(gate_probs)
            true_labels.extend(labels)
            
    true_labels = np.array(true_labels)
    pred_scores = np.array(pred_scores)
    
    print("Sweeping thresholds...")
    thresholds = np.arange(0.05, 0.96, 0.01)
    best_f1 = -1
    best_tau = 0.5
    
    for tau in thresholds:
        preds = (pred_scores >= tau).astype(float)
        tp = np.sum((preds == 1) & (true_labels == 1))
        fp = np.sum((preds == 1) & (true_labels == 0))
        fn = np.sum((preds == 0) & (true_labels == 1))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        if f1 > best_f1:
            best_f1 = f1
            best_tau = tau
            
    print(f"Optimal threshold found: tau* = {best_tau:.2f} (F1 = {best_f1:.4f})")
    
    # Compute confusion matrix at optimal threshold
    preds = (pred_scores >= best_tau).astype(float)
    tp = np.sum((preds == 1) & (true_labels == 1))
    fp = np.sum((preds == 1) & (true_labels == 0))
    tn = np.sum((preds == 0) & (true_labels == 0))
    fn = np.sum((preds == 0) & (true_labels == 1))
    
    print("\nConfusion Matrix at optimal threshold:")
    print(f"TP: {tp} | FP: {fp}")
    print(f"FN: {fn} | TN: {tn}")
    
    calib_data = {
        "optimal_threshold": float(best_tau),
        "f1_score": float(best_f1),
        "confusion_matrix": {
            "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)
        }
    }
    
    out_file = ckpt_path.parent / "calibration.json"
    out_file.write_text(json.dumps(calib_data, indent=2))
    print(f"\nCalibration saved to {out_file}")

if __name__ == "__main__":
    main()
