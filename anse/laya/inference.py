"""
anse/laya/inference.py
======================
LayaInference — production CPU inference engine for Laya Coding Companion.

Target: <50ms per query on commodity CPU (ModernBERT-base [CLS] pooling).
Benchmarks latency over N warmup + K measured calls and returns p50/p95/p99.
"""
from __future__ import annotations

import json
import statistics
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import torch


class LayaInference:
    """
    Production inference engine for LayaCodingCompanion.

    Loads model from checkpoint, tokenizes code/prompt input, runs
    forward pass, and returns a LayaDecision with latency measurement.

    Design principle: all numeric values come from actual forward passes,
    never from hardcoded estimates (zero-hallucination protocol).
    """

    LATENCY_TARGET_MS = 50.0  # ANSE deployment invariant

    def __init__(
        self,
        checkpoint_path: Path | None = None,
        device: str = "cpu",
        max_length: int = 256,
    ) -> None:
        from anse.laya.model import LayaCodingCompanion, DEFAULT_BASE_MODEL
        self.device = device
        self.max_length = max_length

        if checkpoint_path and Path(checkpoint_path).exists():
            print(f"  Loading Laya from checkpoint: {checkpoint_path}")
            self.model = LayaCodingCompanion.load_checkpoint(Path(checkpoint_path))
        else:
            print(f"  No checkpoint found — using untrained Laya (base model only)")
            self.model = LayaCodingCompanion(
                base_model_name=DEFAULT_BASE_MODEL,
                load_pretrained=True,
            )

        self.model.eval()
        self.model.to(device)

        # Load tokenizer matching the base model
        self._load_tokenizer()

    def _load_tokenizer(self) -> None:
        from transformers import AutoTokenizer  # type: ignore
        base_name = self.model.base_model_name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                base_name,
                trust_remote_code=True,
                cache_dir="/mnt/data/home/xavkal/.cache/huggingface",
            )
        except Exception:
            # Fallback to BERT tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                "bert-base-uncased",
                cache_dir="/mnt/data/home/xavkal/.cache/huggingface",
            )

    def predict(self, text: str) -> "LayaDecision":  # noqa: F821
        """Run single-sample inference. Returns LayaDecision with real latency."""
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)
        return self.model.predict(input_ids, attention_mask)

    def benchmark(
        self,
        texts: list[str] | None = None,
        n_warmup: int = 3,
        n_measure: int = 10,
    ) -> dict[str, Any]:
        """
        Benchmark inference latency over multiple calls.

        Returns p50, p95, p99 latency in ms, and whether target is met.
        All numbers are from real timing (time.perf_counter()), not estimates.
        """
        if texts is None:
            texts = [
                "def foo(): pass  # stub",
                "def binary_search(arr, x):\n    lo, hi = 0, len(arr)-1\n    while lo<=hi:\n        mid=(lo+hi)//2\n        if arr[mid]==x: return mid\n        elif arr[mid]<x: lo=mid+1\n        else: hi=mid-1\n    return -1",
                "import subprocess; subprocess.run(user_input, shell=True)",
                "theorem add_comm (a b : Nat) : a + b = b + a := by omega",
            ]

        # Warmup (not measured)
        for _ in range(n_warmup):
            self.predict(texts[0])

        # Measured calls
        latencies = []
        for i in range(n_measure):
            text = texts[i % len(texts)]
            t0 = time.perf_counter()
            self.predict(text)
            latencies.append((time.perf_counter() - t0) * 1000)

        result = {
            "n_warmup": n_warmup,
            "n_measure": n_measure,
            "p50_ms": statistics.median(latencies),
            "p95_ms": sorted(latencies)[int(0.95 * len(latencies))],
            "p99_ms": sorted(latencies)[int(0.99 * len(latencies))],
            "mean_ms": statistics.mean(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "target_ms": self.LATENCY_TARGET_MS,
            "target_met": statistics.median(latencies) < self.LATENCY_TARGET_MS,
            "raw_latencies_ms": [round(x, 2) for x in latencies],
        }
        print(f"  Latency: p50={result['p50_ms']:.1f}ms p95={result['p95_ms']:.1f}ms "
              f"target={'✅' if result['target_met'] else '⚠️'} (<{self.LATENCY_TARGET_MS}ms)")
        return result

    def predict_batch(self, texts: list[str]) -> list["LayaDecision"]:  # noqa: F821
        """Predict a batch of code snippets."""
        return [self.predict(text) for text in texts]

    def decision_to_json(self, decision: "LayaDecision") -> str:  # noqa: F821
        """Serialize a LayaDecision to JSON string."""
        return json.dumps(asdict(decision), indent=2)
