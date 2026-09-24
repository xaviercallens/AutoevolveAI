"""
anse.v5.laya_system_one - Non-Autoregressive System 1 Decision Engine via Laya.

Executes ultra-low latency, non-autoregressive triage of scientific states,
hypotheses, and constraints in a single forward pass without token-by-token hallucinations.
Default device: local CPU.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_LAYA_DIR = Path(__file__).resolve().parent.parent.parent / "checkpoints" / "laya"


class LayaSystemOneDecisionEngine:
    """Non-autoregressive System 1 decision engine wrapping Laya on local CPU."""

    def __init__(self, model_dir: str | Path | None = None, device: str = "cpu") -> None:
        self.model_dir = Path(model_dir) if model_dir else DEFAULT_LAYA_DIR
        self.device = device
        self._agent: Any = None
        self._is_loaded = False
        self._init_error: str | None = None
        self._load_agent()

    def _load_agent(self) -> None:
        """Loads RLAgent from local checkpoint directory if available."""
        if not self.model_dir.exists() or not (self.model_dir / "model.safetensors").exists():
            self._init_error = f"Laya model weights not found at {self.model_dir}"
            logger.warning("%s. Fallback heuristics will be used.", self._init_error)
            return

        try:
            # Insert model_dir into sys.path to resolve rl_common and rl_agent_api
            model_dir_str = str(self.model_dir)
            if model_dir_str not in sys.path:
                sys.path.insert(0, model_dir_str)

            from rl_agent_api import RLAgent  # type: ignore[import-not-found]

            logger.info("Initializing Laya RLAgent from %s on device=%s...", self.model_dir, self.device)
            t0 = time.perf_counter()
            self._agent = RLAgent(model_dir_str, device=self.device)
            duration_ms = (time.perf_counter() - t0) * 1000.0
            self._is_loaded = True
            logger.info("Laya System 1 model initialized successfully in %.1f ms on %s.", duration_ms, self.device)
        except Exception as exc:
            self._init_error = str(exc)
            logger.exception("Failed to load Laya model on %s: %s", self.device, exc)

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def triage_hypothesis(
        self,
        hypothesis: str,
        choices: list[str] | None = None,
        instructions: str = "Evaluate whether this scientific hypothesis is mathematically sound.",
    ) -> dict[str, Any]:
        """Classifies a hypothesis among typed categorical choices in a single forward pass."""
        crit = choices or ["sound", "unsound", "needs_investigation"]
        t0 = time.perf_counter()

        if self._is_loaded and self._agent is not None:
            questions = {
                "triage": {
                    "type": "choice",
                    "instructions": instructions,
                    "criteria": crit,
                }
            }
            res = self._agent.system_one(hypothesis, questions)
            duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            ans = res.get("answers", {}).get("triage", {})
            return {
                "decision_type": "choice",
                "choice": ans.get("choice", crit[0]),
                "probabilities": ans.get("probabilities", {}),
                "confidence": ans.get("confidence", 0.9),
                "act_probability": ans.get("rl_agent", {}).get("act_probability", 1.0),
                "latency_ms": duration_ms,
                "device": self.device,
                "model": "laya-system-one-cpu",
                "tokens": res.get("usage", {}).get("input_tokens", 0),
            }

        # Deterministic semantic fallback
        duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        lower = hypothesis.lower()
        if "unsound" in lower or "violation" in lower or "paradox" in lower or "stub" in lower:
            chosen = "unsound"
            probs = {c: (0.85 if c == "unsound" else 0.15 / (len(crit) - 1)) for c in crit}
        elif "sound" in lower or "invariant" in lower or "conservation" in lower:
            chosen = "sound"
            probs = {c: (0.90 if c == "sound" else 0.10 / (len(crit) - 1)) for c in crit}
        else:
            chosen = crit[0]
            probs = {c: 1.0 / len(crit) for c in crit}

        return {
            "decision_type": "choice",
            "choice": chosen,
            "probabilities": probs,
            "confidence": 0.85,
            "act_probability": 1.0,
            "latency_ms": duration_ms,
            "device": "cpu-fallback",
            "model": "laya-heuristic-fallback",
            "tokens": len(hypothesis.split()),
        }

    def score_hypothesis(
        self,
        hypothesis: str,
        scale: list[str] | None = None,
        instructions: str = "Rate the thermodynamic feasibility and energy efficiency score.",
    ) -> dict[str, Any]:
        """Computes a calibrated scalar score [0..K-1] on an ordered criterion scale."""
        crit = scale or ["critical_inefficiency", "suboptimal", "acceptable", "optimized", "pareto_optimal"]
        t0 = time.perf_counter()

        if self._is_loaded and self._agent is not None:
            questions = {
                "score": {
                    "type": "score",
                    "instructions": instructions,
                    "criteria": crit,
                }
            }
            res = self._agent.system_one(hypothesis, questions)
            duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            ans = res.get("answers", {}).get("score", {})
            return {
                "decision_type": "score",
                "score": ans.get("score", 3.0),
                "probabilities": ans.get("probabilities", {}),
                "confidence": ans.get("confidence", 0.85),
                "legend": ans.get("legend", {str(i): c for i, c in enumerate(crit)}),
                "latency_ms": duration_ms,
                "device": self.device,
                "model": "laya-system-one-cpu",
            }

        duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        score_val = 4.2 if ("simd" in hypothesis.lower() or "vectorized" in hypothesis.lower()) else 2.1
        return {
            "decision_type": "score",
            "score": score_val,
            "probabilities": {str(i): 0.2 for i in range(len(crit))},
            "confidence": 0.80,
            "legend": {str(i): c for i, c in enumerate(crit)},
            "latency_ms": duration_ms,
            "device": "cpu-fallback",
            "model": "laya-heuristic-fallback",
        }

    def verify_truth_noul(
        self,
        hypothesis: str,
        statement: str,
    ) -> dict[str, Any]:
        """Evaluates statement probability (No / Yes / Unsure calibrated probability)."""
        t0 = time.perf_counter()

        if self._is_loaded and self._agent is not None:
            questions = {
                "truth": {
                    "type": "noul",
                    "instructions": f"Is this statement strictly verified: {statement}?",
                    "criteria": None,
                }
            }
            res = self._agent.system_one(hypothesis, questions)
            duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            ans = res.get("answers", {}).get("truth", {})
            return {
                "decision_type": "noul",
                "probability_true": ans.get("noul", 0.5),
                "act_probability": ans.get("rl_agent", {}).get("act_probability", 1.0),
                "latency_ms": duration_ms,
                "device": self.device,
                "model": "laya-system-one-cpu",
            }

        duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        p_true = 0.95 if ("sound" in hypothesis.lower() or "invariant" in statement.lower()) else 0.40
        return {
            "decision_type": "noul",
            "probability_true": p_true,
            "act_probability": 1.0,
            "latency_ms": duration_ms,
            "device": "cpu-fallback",
            "model": "laya-heuristic-fallback",
        }
