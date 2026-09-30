"""
export_laya_onnx.py
===================
Merge the Laya LoRA adapter into ModernBERT-base, export to ONNX INT8,
and verify that cold-start inference latency < 500 ms (System 1 paradox fix).

Usage:
  uv run python scripts/export_laya_onnx.py \
    --checkpoint /mnt/data/home/xavkal/laya_coding_checkpoints/stage3 \
    --output_dir /mnt/data/home/xavkal/laya_onnx

Requirements (added to pyproject.toml [project.optional-dependencies.onnx]):
  optimum[onnxruntime]>=1.17
  onnxruntime>=1.17
  onnx>=1.15
"""

import argparse
import time
import subprocess
import sys
import json
import hashlib
from pathlib import Path

import numpy as np


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--output_dir", default="/mnt/data/home/xavkal/laya_onnx")
    p.add_argument("--max_seq_len", type=int, default=512)
    p.add_argument("--target_cold_ms", type=float, default=500.0,
                   help="Cold-start latency target in ms (System 1 paradox fix)")
    return p.parse_args()


def merge_and_save_backbone(checkpoint: str, merged_dir: str) -> None:
    """Merge LoRA adapter into the backbone weights and save a standard HF model."""
    print(f"[1/4] Loading PEFT checkpoint from {checkpoint} …")
    from peft import PeftModel
    from transformers import AutoTokenizer
    from anse.laya.model import LayaCodingCompanion

    model = LayaCodingCompanion.from_pretrained(checkpoint)
    # Merge LoRA adapter weights into the base model
    base = model.backbone
    if hasattr(base, "merge_and_unload"):
        base = base.merge_and_unload()
        print("  LoRA adapter merged into backbone.")
    else:
        print("  WARNING: merge_and_unload() not available; base model used as-is.")

    Path(merged_dir).mkdir(parents=True, exist_ok=True)
    base.save_pretrained(merged_dir)
    tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
    tokenizer.save_pretrained(merged_dir)
    print(f"  Merged model saved to {merged_dir}")


def export_onnx(merged_dir: str, onnx_dir: str, max_seq_len: int) -> None:
    """Export merged model to ONNX using optimum-cli."""
    print(f"[2/4] Exporting to ONNX ({onnx_dir}) …")
    cmd = [
        sys.executable, "-m", "optimum.exporters.onnx.main",
        "--model", merged_dir,
        "--task", "feature-extraction",
        "--opset", "17",
        "--sequence_length", str(max_seq_len),
        onnx_dir,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ONNX export failed:\n{result.stderr}")
    print(f"  ONNX export complete. Files: {list(Path(onnx_dir).glob('*.onnx'))}")


def quantize_int8(onnx_dir: str, quantized_dir: str) -> None:
    """INT8 static quantization using onnxruntime.quantization."""
    print(f"[3/4] Quantizing to INT8 ({quantized_dir}) …")
    from onnxruntime.quantization import quantize_dynamic, QuantType

    input_model = Path(onnx_dir) / "model.onnx"
    Path(quantized_dir).mkdir(parents=True, exist_ok=True)
    output_model = Path(quantized_dir) / "model_int8.onnx"

    quantize_dynamic(
        str(input_model),
        str(output_model),
        weight_type=QuantType.QInt8,
    )
    size_mb = output_model.stat().st_size / 1e6
    sha = hashlib.sha256(output_model.read_bytes()).hexdigest()
    print(f"  INT8 model: {output_model} ({size_mb:.1f} MB), SHA-256: {sha}")
    return str(output_model), sha


def benchmark_cold_start(model_path: str, target_ms: float) -> dict:
    """Simulate cold-start: load session + run a single forward pass."""
    print(f"[4/4] Benchmarking cold-start latency (target < {target_ms} ms) …")
    import onnxruntime as ort

    input_ids = np.ones((1, 24), dtype=np.int64)
    attention_mask = np.ones((1, 24), dtype=np.int64)

    t0 = time.perf_counter()
    # Full cold-start: session creation + first inference
    session = ort.InferenceSession(
        model_path,
        providers=["CPUExecutionProvider"],
        sess_options=ort.SessionOptions(),
    )
    outputs = session.run(
        None,
        {"input_ids": input_ids, "attention_mask": attention_mask},
    )
    cold_ms = (time.perf_counter() - t0) * 1000

    # Warm path: 5 consecutive runs
    warm_times = []
    for _ in range(5):
        t = time.perf_counter()
        session.run(None, {"input_ids": input_ids, "attention_mask": attention_mask})
        warm_times.append((time.perf_counter() - t) * 1000)

    warm_p50 = float(np.median(warm_times))
    status = "PASS" if cold_ms < target_ms else "FAIL"

    result = {
        "cold_start_ms": round(cold_ms, 1),
        "warm_p50_ms": round(warm_p50, 2),
        "target_cold_ms": target_ms,
        "system1_latency_paradox_resolved": cold_ms < target_ms,
        "status": status,
    }
    print(f"  Cold-start: {cold_ms:.1f} ms  |  Warm P50: {warm_p50:.2f} ms  |  {status}")
    if status == "FAIL":
        print(f"  ⚠ System 1 latency paradox NOT resolved — cold start {cold_ms:.0f}ms > {target_ms}ms")
    else:
        print(f"  ✓ System 1 latency paradox RESOLVED — cold start {cold_ms:.0f}ms < {target_ms}ms")
    return result


def main():
    args = parse_args()
    merged_dir = str(Path(args.output_dir) / "merged")
    onnx_dir = str(Path(args.output_dir) / "onnx_fp32")
    quantized_dir = str(Path(args.output_dir) / "onnx_int8")

    merge_and_save_backbone(args.checkpoint, merged_dir)
    export_onnx(merged_dir, onnx_dir, args.max_seq_len)
    model_path, model_sha = quantize_int8(onnx_dir, quantized_dir)
    bench = benchmark_cold_start(model_path, args.target_cold_ms)

    receipt = {
        "script": "scripts/export_laya_onnx.py",
        "checkpoint": args.checkpoint,
        "onnx_int8_path": model_path,
        "onnx_int8_sha256": model_sha,
        **bench,
    }

    receipt_path = Path(args.output_dir) / "onnx_export_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2))
    print(f"\nReceipt written to {receipt_path}")

    # Energy = E = 10^6 if cold-start paradox unresolved
    if not bench["system1_latency_paradox_resolved"]:
        print("ENERGY = 1e6 (MAXIMUM PAIN) — ONNX cold-start target not met.")
        sys.exit(1)
    print("ENERGY = OK — ONNX export successful, System 1 paradox resolved.")


if __name__ == "__main__":
    main()
