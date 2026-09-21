"""
Code Critic Module: local SLM evaluation against stubs, cheats, and poor complexity.
Interfaces with a local Ollama daemon or OpenAI-compatible endpoint.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx

from anse.config import CriticConfig, get_config

logger = logging.getLogger(__name__)


class CriticDecision(str, Enum):  # noqa: UP042
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    SKIPPED = "SKIPPED"


@dataclass
class CriticResult:
    decision: CriticDecision
    reason: str
    energy_penalty: float
    raw_response: str = ""
    duration_ms: float = 0.0

    @property
    def is_accepted(self) -> bool:
        return self.decision == CriticDecision.ACCEPT


class CodeCritic:
    """
    Evaluates candidate code using a quantized local SLM (e.g. Qwen2.5-Coder-3B via Ollama).
    Acts as a pre-execution System 2 critic before entering the sandbox or Lean 4 prover.
    """

    def __init__(self, config: CriticConfig | None = None) -> None:
        self.config = config or get_config().critic

    def evaluate(self, code: str, prompt_context: str = "") -> CriticResult:
        """
        Synchronously evaluate the candidate code.
        """
        if not self.config.enabled:
            return CriticResult(
                decision=CriticDecision.SKIPPED,
                reason="Critic evaluation is disabled in configuration.",
                energy_penalty=0.0,
            )

        import time

        start_t = time.perf_counter()
        raw_text = ""

        try:
            raw_text = self._call_ollama(code, prompt_context)
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            return self._parse_verdict(raw_text, duration_ms)
        except Exception as e:
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            logger.warning(
                "Critic model query failed (%s). Policy: %s", e, self.config.fallback_policy
            )
            if self.config.fallback_policy == "deny":
                return CriticResult(
                    decision=CriticDecision.REJECT,
                    reason=f"CRITIC_UNAVAILABLE: {e}",
                    energy_penalty=self.config.rejection_penalty,
                    raw_response=raw_text,
                    duration_ms=duration_ms,
                )
            return CriticResult(
                decision=CriticDecision.SKIPPED,
                reason=f"CRITIC_FALLBACK_OPEN: {e}",
                energy_penalty=0.0,
                raw_response=raw_text,
                duration_ms=duration_ms,
            )

    def _call_ollama(self, code: str, prompt_context: str) -> str:
        """Call Ollama /api/generate endpoint."""
        user_prompt = (
            f"Context / Task:\n{prompt_context}\n\n"
            f"Candidate Code to evaluate:\n```python\n{code}\n```\n\n"
            "Evaluate strictly. Return valid JSON only."
        )

        payload = {
            "model": self.config.model_name,
            "prompt": user_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": self.config.temperature,
            },
        }

        url = f"{self.config.ollama_base_url.rstrip('/')}/api/generate"
        with httpx.Client(timeout=self.config.timeout_seconds) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return str(data.get("response", ""))

    def _parse_verdict(self, raw_text: str, duration_ms: float) -> CriticResult:
        """Parse JSON status and reason from the critic model's output."""
        clean_text = raw_text.strip()
        # Strip potential markdown backticks if returned despite format=json
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?", "", clean_text)
            clean_text = re.sub(r"```$", "", clean_text).strip()

        try:
            parsed: dict[str, Any] = json.loads(clean_text)
        except json.JSONDecodeError:
            # Fallback regex if imperfect JSON
            if '"status": "ACCEPT"' in clean_text or '"status":"ACCEPT"' in clean_text:
                return CriticResult(
                    decision=CriticDecision.ACCEPT,
                    reason="Parsed ACCEPT via regex recovery.",
                    energy_penalty=0.0,
                    raw_response=raw_text,
                    duration_ms=duration_ms,
                )
            return CriticResult(
                decision=CriticDecision.REJECT,
                reason=f"Malformed critic output: {clean_text[:200]}",
                energy_penalty=self.config.rejection_penalty,
                raw_response=raw_text,
                duration_ms=duration_ms,
            )

        status = str(parsed.get("status", "")).upper()
        reason = str(parsed.get("reason", ""))

        if status == "ACCEPT":
            return CriticResult(
                decision=CriticDecision.ACCEPT,
                reason="Code passed critic review.",
                energy_penalty=0.0,
                raw_response=raw_text,
                duration_ms=duration_ms,
            )
        elif status == "REJECT":
            return CriticResult(
                decision=CriticDecision.REJECT,
                reason=reason or "Rejected by Critic Model.",
                energy_penalty=self.config.rejection_penalty,
                raw_response=raw_text,
                duration_ms=duration_ms,
            )
        else:
            return CriticResult(
                decision=CriticDecision.REJECT,
                reason=f"Unexpected status '{status}': {reason}",
                energy_penalty=self.config.rejection_penalty,
                raw_response=raw_text,
                duration_ms=duration_ms,
            )
