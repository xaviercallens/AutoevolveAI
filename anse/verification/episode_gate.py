"""Second, independent verdict for harvested episodes, from the GWAYA fail-closed gate.

The harvester's own sandbox verdict (`converged`) stays the primary label. This module adds the GWAYA
verdict on top and applies one rule: **fail closed on REJECT, never upgrade on BLOCKED**.

  ACCEPT   confirmed; labels unchanged.
  REJECT   a converged episode is demoted (converged=False, energy raised): a candidate with a stub body, or one
           that fails when GWAYA runs it, is not a real success even if the other verifier passed it.
  BLOCKED  (no bwrap isolation, timeout) or UNAVAILABLE (gwaya not installed): labels unchanged, `confirmed=False`.
           Training can require confirmation with `ltm_learning_mix.py --require-gate`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

DEMOTION_ENERGY = 100.0  # same weight as one failed hidden assertion in harvest_episodes.energy_of


@dataclass(frozen=True)
class GatedLabels:
    converged: bool
    energy: float
    meta: dict[str, Any]


def _default_gate() -> Callable[..., Any] | None:
    try:
        from anse.verification.gwaya_gate import verify_python
    except ImportError:
        return None
    return verify_python


def apply_gate(
    code: str,
    hidden_test: str,
    converged: bool,
    energy: float,
    gate: Callable[..., Any] | None = None,
) -> GatedLabels:
    fn = gate if gate is not None else _default_gate()
    if fn is None:
        return GatedLabels(converged, energy, {"status": "UNAVAILABLE", "confirmed": False,
                                               "reasons": ["gwaya not installed"]})
    verdict = fn(code, hidden_test)
    meta: dict[str, Any] = {"status": verdict.status, "reasons": list(verdict.reasons),
                            "confirmed": verdict.status == "ACCEPT" and converged}
    if verdict.status == "REJECT" and converged:
        meta["demoted"] = True
        return GatedLabels(False, max(energy, DEMOTION_ENERGY), meta)
    if verdict.status == "ACCEPT" and not converged:
        meta["disagreement"] = "gate accepted a candidate the harvest sandbox failed"
    return GatedLabels(converged, energy, meta)
