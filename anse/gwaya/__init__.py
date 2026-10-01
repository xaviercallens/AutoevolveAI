"""
anse/gwaya — Qwen + Laya (GWAYA) Dual-Process Advisor & Verifier AI Companion.
=============================================================================
Combines:
  - Laya (NAR System 1, 149M ModernBERT): ~45 ms parallel code verification & anti-hallucination shielding
  - Qwen (System 2 deliberative synthesis): Grounded coding advice for Python, Rust, and Lean 4
"""
from anse.gwaya.advisor import (
    GwayaAdvisor,
    GwayaVerificationResult,
    GwayaAdvice,
    VerificationVerdict,
)
from anse.gwaya.verifier import (
    verify_gemini_output,
    assert_zero_hallucination,
    get_gwaya_advisor,
)

__all__ = [
    "GwayaAdvisor",
    "GwayaVerificationResult",
    "GwayaAdvice",
    "VerificationVerdict",
    "verify_gemini_output",
    "assert_zero_hallucination",
    "get_gwaya_advisor",
]
