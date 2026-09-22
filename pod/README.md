# 🚀 RunPod GPU Pod Training Runbook (Post-Processing LoRA)

This runbook guides you through post-processing LoRA distillation on a rented GPU pod (e.g., RunPod, Lambda Labs, Vast.ai) for **$0.25 to $0.40 per training cycle**.

---

## 🎯 Architecture: Teacher-to-Student Distillation

```
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│     Local Dev Machine / IDE     │           │        Remote RunPod GPU        │
├─────────────────────────────────┤           ├─────────────────────────────────┤
│ 1. Active Day:                  │           │ 3. Post-Processing / Nightly:   │
│    • Junior Cluster (Inference) │           │    • 1x RTX 3090 / 4090 ($0.30) │
│    • Frontier Models (Teachers) │           │    • High-speed Unsloth / TRL   │
│    • Redis LTM Streams          │           │    • 10-minute LoRA fine-tuning │
│                                 │           │                                 │
│ 2. Export & Sync:               │──rsync───>│ 4. Train LoRA on Distilled Data │
│    • frontier_distillation.jsonl│           │                                 │
│                                 │<──rsync───│ 5. Export Final Adapter Weights │
│ 6. Hot-Reload 'antigravity-local│           │    • adapters/checkpoint_v...   │
└─────────────────────────────────┘           └─────────────────────────────────┘
```

---

## 1. Select Pod on RunPod

1. Create an account on [runpod.io](https://www.runpod.io).
2. Add \$5 to \$10 balance (sufficient for dozens of training runs).
3. Click **Deploy > GPU Pod**:
   - **GPU Class:** 1x **RTX 3090** (24GB) or **RTX 4090** (24GB) or **A40** (48GB).
   - **Cloud Type:** *Secure Cloud* (recommended) or *Community Cloud*.
   - **Template:** `RunPod PyTorch 2.4.0` (or any Ubuntu 22.04 + CUDA 12.x).
   - **Storage:** 20 GB Disk / 20 GB Volume.
   - **Ports:** Expose port 22 (SSH).
4. Connect via SSH:
   ```bash
   ssh root@<POD_IP> -p <PORT> -i ~/.ssh/id_ed25519
   ```

---

## 2. One-Click Bootstrap on Pod

Inside the pod terminal:
```bash
# Clone the repository
git clone https://github.com/xaviercallens/AutoevolveAI.git
cd AutoevolveAI

# Run automated bootstrap
chmod +x pod/bootstrap_pod.sh
./pod/bootstrap_pod.sh
```

---

## 3. Launch Post-Processing Distillation Training

```bash
# Supervised Fine-Tuning (SFT) from Frontier demonstrations:
python3 pod/train_lora_pod.py \
  --mode sft \
  --dataset results/frontier_distillation_sft.jsonl \
  --model_name "Qwen/Qwen2.5-Coder-7B-Instruct" \
  --epochs 3

# Or Direct Preference Optimization (DPO) on Chosen vs Rejected:
python3 pod/train_lora_pod.py \
  --mode dpo \
  --dataset results/frontier_distillation_dpo.jsonl \
  --model_name "Qwen/Qwen2.5-Coder-7B-Instruct"
```

---

## 4. Retrieve Trained Adapter & Hot-Reload Locally

From your local machine:
```bash
# Pull the newly trained adapter back to your tower:
./scripts/dispatch_gpupod.sh pull root@<POD_IP>:<PORT>

# Terminate the pod on RunPod dashboard to stop billing!
```
The adapter is automatically deployed to `adapters/checkpoint_frontier_<timestamp>` and hot-reloaded into your local vLLM instance.
