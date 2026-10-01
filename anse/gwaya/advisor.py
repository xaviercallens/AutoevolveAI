"""
anse/gwaya/advisor.py
=====================
GWAYA: The Qwen (Gwen) + Laya Asymmetric Dual-Process Advisor AI Companion.

Operates in parallel with primary Antigravity agents (Gemini 3.1 Pro & Gemini 3.8 Flash)
as a zero-trust code quality verifier, anti-hallucination shield, and architectural advisor.

Key Capabilities:
1. Fast Reflex Verification (<50 ms CPU):
   - Laya-LoRA (149M ModernBERT) runs non-autoregressive AST and safety screening.
   - Detects stubs (pass, ..., NotImplementedError, # TODO, sorry, unimplemented!()).
   - Flags security vulnerabilities (CWEs, eval(), os.system(), shell=True).
   - Assigns maximum pain barrier penalty E = 10^6 if quality score < 0.3.
2. Deliberative Advisory (Qwen 3.8 / Gemini System 2):
   - When issues or performance bottlenecks are detected, provides immediate,
     formally grounded refactoring recommendations across Python, Rust, and Lean 4.
3. Live Parallel Shielding for Antigravity:
   - Intercepts generated code before tool execution.
   - Prevents hallucination cascades from degrading the user workspace.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from anse.laya.assistant import (
    CodeAuditReport,
    DualProcessResponse,
    LayaDualProcessAssistant,
    SpecialistPillar,
)

logger = logging.getLogger("GwayaAdvisor")


class VerificationVerdict(str, Enum):
    APPROVED = "APPROVED"
    BLOCKED_STUB = "BLOCKED_STUB"
    BLOCKED_SECURITY = "BLOCKED_SECURITY"
    BLOCKED_HALLUCINATION = "BLOCKED_HALLUCINATION"
    NEEDS_OPTIMIZATION = "NEEDS_OPTIMIZATION"


@dataclass
class GwayaVerificationResult:
    verdict: VerificationVerdict
    passed: bool
    confidence: float
    physical_energy: float
    stubs_detected: List[str] = field(default_factory=list)
    security_flags: List[str] = field(default_factory=list)
    recommendation: str = ""
    specialist_pillar: SpecialistPillar = SpecialistPillar.GENERAL
    latency_ms: float = 0.0

    @property
    def should_reject(self) -> bool:
        return not self.passed or self.physical_energy >= 1e6


@dataclass
class GwayaAdvice:
    task: str
    verdict: VerificationVerdict
    specialist_pillar: SpecialistPillar
    suggested_code: str
    explanation: str
    energy_estimate: float
    latency_ms: float
    verified_by_laya: bool


class GwayaAdvisor:
    """The master Qwen + Laya (GWAYA) advisor companion."""

    def __init__(
        self,
        checkpoint_path: Optional[Path | str] = None,
        noul_threshold: float = 0.30,
        qwen_synthesizer: Optional[Callable[[str, str], str]] = None,
        mock: bool = False,
    ) -> None:
        self.noul_threshold = noul_threshold
        self.qwen_synthesizer = qwen_synthesizer
        self.mock = mock

        # Underlying Laya dual-process engine
        self.assistant = LayaDualProcessAssistant(
            checkpoint_path=checkpoint_path,
            noul_threshold=noul_threshold,
            system2_caller=qwen_synthesizer,
            mock=mock,
        )
        logger.info(f"Initialized GWAYA Advisor (threshold={noul_threshold}, mock={mock})")

    def verify_generation(
        self,
        candidate_code: str,
        language: str = "python",
        prompt: Optional[str] = None,
    ) -> GwayaVerificationResult:
        """
        Parallel verifier for code produced by Gemini 3.1 Pro or Gemini 3.8 Flash.
        Runs in ~45 ms on CPU without incurring extra generative token costs.
        """
        t0 = time.perf_counter()
        audit = self.assistant.audit_code_safety_and_stubs(candidate_code)
        pillar = self.assistant.route_specialist_pillar(f"{candidate_code}\n{prompt or ''}")
        latency = (time.perf_counter() - t0) * 1000

        # Determine verdict
        if audit.security_flags:
            verdict = VerificationVerdict.BLOCKED_SECURITY
            passed = False
            rec = f"Critical security issue: {'; '.join(audit.security_flags)}. Remove dynamic execution/subprocess."
        elif audit.detected_stubs:
            verdict = VerificationVerdict.BLOCKED_STUB
            passed = False
            rec = f"Incomplete implementation with stubs: {'; '.join(audit.detected_stubs)}. Implement full logic."
        elif audit.blocked:
            verdict = VerificationVerdict.BLOCKED_HALLUCINATION
            passed = False
            rec = f"Laya gate blocked: noul={audit.noul_score:.3f} < {self.noul_threshold}. Possible hallucination."
        elif audit.energy > 50.0:
            verdict = VerificationVerdict.NEEDS_OPTIMIZATION
            passed = True
            rec = f"Code is valid but has high energy (E={audit.energy:.2f}). Consider vectorization or zero-alloc."
        else:
            verdict = VerificationVerdict.APPROVED
            passed = True
            rec = f"Code verified clean and safe. Low energy footprint (E={audit.energy:.2f})."

        return GwayaVerificationResult(
            verdict=verdict,
            passed=passed,
            confidence=round(audit.noul_score, 4),
            physical_energy=audit.energy,
            stubs_detected=audit.detected_stubs,
            security_flags=audit.security_flags,
            recommendation=rec,
            specialist_pillar=pillar,
            latency_ms=round(latency, 2),
        )

    def advise(
        self,
        task_prompt: str,
        code_context: Optional[str] = None,
        force_deliberation: bool = False,
    ) -> GwayaAdvice:
        """
        Advises on an engineering task, pairing Laya System 1 pre-filtering
        with Qwen System 2 deliberative synthesis.
        """
        t0 = time.perf_counter()
        resp: DualProcessResponse = self.assistant.assist(
            prompt=task_prompt,
            code_context=code_context,
            force_system2=force_deliberation,
        )
        latency = (time.perf_counter() - t0) * 1000

        if resp.audit.blocked:
            verdict = VerificationVerdict.BLOCKED_STUB if resp.audit.detected_stubs else VerificationVerdict.BLOCKED_SECURITY
        else:
            verdict = VerificationVerdict.APPROVED

        return GwayaAdvice(
            task=task_prompt,
            verdict=verdict,
            specialist_pillar=resp.specialist_pillar,
            suggested_code=resp.content,
            explanation=resp.audit.reasoning,
            energy_estimate=resp.audit.energy,
            latency_ms=round(latency, 2),
            verified_by_laya=True,
        )
