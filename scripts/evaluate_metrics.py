import json
import os
from pathlib import Path

def evaluate():
    state_file = "results/qwen-simpo-reddit-audience/trainer_state.json"
    if not os.path.exists(state_file):
        print(f"Trainer state not found at {state_file}. Make sure the DPO training has progressed sufficiently to save logs.")
        return

    with open(state_file, "r") as f:
        data = json.load(f)

    log_history = data.get("log_history", [])
    
    print("=== DPO Training Metrics (Offline Evaluation) ===")
    
    metrics_to_track = [
        "loss",
        "rewards/chosen",
        "rewards/rejected",
        "rewards/accuracies",
        "rewards/margins"
    ]
    
    print(f"{'Step':<10} | {'Loss':<10} | {'Accuracy':<10} | {'Margin':<10} | {'Chosen R':<10} | {'Rejected R':<10}")
    print("-" * 75)
    
    for entry in log_history:
        if "loss" in entry:
            step = entry.get("step", 0)
            loss = entry.get("loss", 0.0)
            acc = entry.get("rewards/accuracies", 0.0)
            margin = entry.get("rewards/margins", 0.0)
            ch_r = entry.get("rewards/chosen", 0.0)
            rj_r = entry.get("rewards/rejected", 0.0)
            
            print(f"{step:<10} | {loss:<10.4f} | {acc:<10.4f} | {margin:<10.4f} | {ch_r:<10.4f} | {rj_r:<10.4f}")

if __name__ == "__main__":
    evaluate()
