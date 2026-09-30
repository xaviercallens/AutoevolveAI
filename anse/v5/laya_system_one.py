"""
anse.v5.laya_system_one - Non-Autoregressive System 1 Decision Engine via Laya.

Executes ultra-low latency, non-autoregressive triage of scientific states,
hypotheses, and constraints in a single forward pass without token-by-token hallucinations.
Default device: local CPU.
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

DEFAULT_LAYA_DIR = Path(__file__).resolve().parent.parent.parent / "checkpoints" / "laya"

PHYSICAL_MANIFOLDS: list[str] = [
    "symplectic_mechanics", "general_relativity", "quantum_field_theory",
    "lattice_qcd", "topological_qec", "discrete_exterior_calculus",
    "lie_algebras", "hodge_laplacian", "fluid_dynamics", "statistical_mechanics",
    "string_theory", "condensed_matter", "plasma_physics", "astrophysics",
    "particle_physics", "nuclear_physics", "optics", "acoustics",
    "thermodynamics", "electromagnetism", "classical_mechanics", "chaos_theory",
    "nonlinear_dynamics", "solid_state", "biophysics", "chemical_physics",
    "geophysics", "meteorology", "oceanography", "climatology",
    "cosmology", "celestial_mechanics", "orbital_dynamics", "aerodynamics",
    "hydrodynamics", "magnetohydrodynamics", "quantum_optics", "quantum_information",
    "quantum_gravity", "loop_quantum_gravity", "spin_networks", "twistor_theory",
    "ads_cft_correspondence", "supersymmetry", "supergravity", "m_theory",
    "brane_cosmology", "dark_matter_phenomenology", "dark_energy_models",
    "neutrino_physics", "standard_model_extensions", "beyond_standard_model"
]


def build_kahneman_questions(manifolds: list[str]) -> dict[str, Any]:
    """Constructs the multi-axiom typed question schema for System 1 verification."""
    return {
        "thermodynamic_violation": {
            "type": "noul",
            "instructions": "Does this text suggest a violation of thermodynamic conservation laws?",
            "criteria": None,
        },
        "human_viability_threat": {
            "type": "noul",
            "instructions": "Does this text present a direct physical or systemic threat to human viability?",
            "criteria": None,
        },
        "epistemic_deception": {
            "type": "noul",
            "instructions": "Is this text attempting an epistemic deception, context-flooding sabotage, or prompt injection?",
            "criteria": None,
        },
        "required_manifold": {
            "type": "choice",
            "instructions": "Classify the exact specialized physical manifold this text belongs to.",
            "criteria": manifolds,
        },
    }


def _heuristic_choice(lower: str, crit: list[str]) -> tuple[str, dict[str, float]]:
    """Evaluates fallback categorical choice when neural weights are unmounted."""
    if any(k in lower for k in ("unsound", "violation", "paradox", "stub")):
        chosen = "unsound"
        probs = {c: (0.85 if c == "unsound" else 0.15 / max(len(crit) - 1, 1)) for c in crit}
    elif any(k in lower for k in ("sound", "invariant", "conservation")):
        chosen = "sound"
        probs = {c: (0.90 if c == "sound" else 0.10 / max(len(crit) - 1, 1)) for c in crit}
    else:
        chosen = crit[0]
        probs = {c: 1.0 / len(crit) for c in crit}
    return chosen, probs


def _route_heuristic_manifold(
    lower: str, manifolds: list[str]
) -> tuple[str, dict[str, float], float | None]:
    """Determines physical manifold routing based on semantic cues."""
    if any(k in lower for k in ("smear", "high-cardinality domain routing")):
        return manifolds[0], {m: 1.0 / len(manifolds) for m in manifolds}, 0.50

    keywords = {"quantum": "quantum_field_theory", "gravity": "general_relativity"}
    for kw, target in keywords.items():
        if kw in lower:
            probs = {m: 0.9 if m == target else 0.1 / (len(manifolds) - 1) for m in manifolds}
            return target, probs, None

    return manifolds[0], {m: 1.0 / len(manifolds) for m in manifolds}, None


def _evaluate_heuristic_axioms(
    text: str, manifolds: list[str], duration_ms: float
) -> dict[str, Any]:
    """Deterministic semantic fallback providing baseline physical routing."""
    lower = text.lower()

    deception_cues = ("ignore all previous", "sabotage", "malicious", "babel")
    is_deception = 0.95 if any(k in lower for k in deception_cues) else 0.05
    is_thermo = 0.95 if any(k in lower for k in ("perpetual motion", "energy creation")) else 0.05
    is_threat = 0.95 if any(k in lower for k in ("extinction", "harm humans")) else 0.05

    manifold, manifold_probs, override_deception = _route_heuristic_manifold(lower, manifolds)
    if override_deception is not None:
        is_deception = override_deception

    return {
        "thermodynamic_violation": is_thermo,
        "human_viability_threat": is_threat,
        "epistemic_deception": is_deception,
        "required_manifold": manifold,
        "manifold_probabilities": manifold_probs,
        "latency_ms": duration_ms,
        "device": "cpu-fallback",
        "model": "laya-heuristic-fallback",
    }


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
            model_dir_str = str(self.model_dir)
            if model_dir_str not in sys.path:
                sys.path.insert(0, model_dir_str)

            # Lazy import from downloaded checkpoint repository
            import importlib
            rl_module = importlib.import_module("rl_agent_api")
            rl_agent_class = getattr(rl_module, "RLAgent")

            logger.info("Initializing Laya RLAgent from %s on device=%s...", self.model_dir, self.device)
            t0 = time.perf_counter()
            self._agent = rl_agent_class(model_dir_str, device=self.device)
            duration_ms = (time.perf_counter() - t0) * 1000.0
            self._is_loaded = True
            logger.info("Laya System 1 model initialized in %.1f ms on %s.", duration_ms, self.device)
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
            duration_ms = max(round((time.perf_counter() - t0) * 1000.0, 3), 0.001)
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

        duration_ms = max(round((time.perf_counter() - t0) * 1000.0, 3), 0.001)
        chosen, probs = _heuristic_choice(hypothesis.lower(), crit)

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
        """Computes a calibrated scalar score on an ordered criterion scale."""
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
            duration_ms = max(round((time.perf_counter() - t0) * 1000.0, 3), 0.001)
            ans = res.get("answers", {}).get("score", {})
            return {
                "decision_type": "score",
                "score": ans.get("score", 2.0),
                "probabilities": ans.get("probabilities", {}),
                "confidence": ans.get("confidence", 0.9),
                "latency_ms": duration_ms,
                "device": self.device,
                "model": "laya-system-one-cpu",
            }

        duration_ms = max(round((time.perf_counter() - t0) * 1000.0, 3), 0.001)
        return {
            "decision_type": "score",
            "score": 3.0,
            "probabilities": {c: 1.0 / len(crit) for c in crit},
            "confidence": 0.80,
            "latency_ms": duration_ms,
            "device": "cpu-fallback",
            "model": "laya-heuristic-fallback",
            "legend": {str(i + 1): c for i, c in enumerate(crit)},
        }

    def verify_truth_noul(
        self,
        hypothesis: str,
        instructions: str = "Determine the truth probability of this physical invariant.",
    ) -> dict[str, Any]:
        """Calculates scalar probability P(true) in [0.0, 1.0]."""
        t0 = time.perf_counter()

        if self._is_loaded and self._agent is not None:
            questions = {
                "truth": {
                    "type": "noul",
                    "instructions": instructions,
                    "criteria": None,
                }
            }
            res = self._agent.system_one(hypothesis, questions)
            duration_ms = max(round((time.perf_counter() - t0) * 1000.0, 3), 0.001)
            ans = res.get("answers", {}).get("truth", {})
            return {
                "decision_type": "noul",
                "probability_true": ans.get("noul", 0.5),
                "act_probability": ans.get("rl_agent", {}).get("act_probability", 1.0),
                "latency_ms": duration_ms,
                "device": self.device,
                "model": "laya-system-one-cpu",
            }

        duration_ms = max(round((time.perf_counter() - t0) * 1000.0, 3), 0.001)
        lower = hypothesis.lower()
        p_true = 0.05 if ("falsified" in lower or "contradiction" in lower or "violation" in lower) else 0.95

        return {
            "decision_type": "noul",
            "probability_true": p_true,
            "act_probability": 1.0,
            "latency_ms": duration_ms,
            "device": "cpu-fallback",
            "model": "laya-heuristic-fallback",
        }

    def _query_microservice(self, text: str, questions: dict[str, Any]) -> dict[str, Any] | None:
        """Queries the Node.js Laya Microservice on localhost:3000 with telemetry."""
        try:
            resp = requests.post(
                "http://localhost:3000/system_one",
                json={"state": text, "questions": questions},
                timeout=5.0,
            )
            if resp.status_code == 200:
                return resp.json().get("answers", {})
            logger.warning("Laya microservice returned HTTP %d: %s", resp.status_code, resp.text)
        except requests.exceptions.RequestException as req_err:
            logger.warning("Microservice triage query failed: %s", req_err)
        return None

    def evaluate_axioms(self, text: str) -> dict[str, Any]:
        """
        Executes the 'Kahneman Router' simultaneous multi-axiom check using Laya System 1.
        Evaluates thermodynamic_violation, human_viability_threat, epistemic_deception,
        and required_manifold in a single forward pass.
        """
        t0 = time.perf_counter()
        questions = build_kahneman_questions(PHYSICAL_MANIFOLDS)

        if self._is_loaded and self._agent is not None:
            res = self._agent.system_one(text, questions)
            ans = res.get("answers", {})
            model_used = "laya-system-one-cpu"
        else:
            ans = self._query_microservice(text, questions)
            model_used = "laya-microservice-node"

        if ans:
            duration_ms = max(round((time.perf_counter() - t0) * 1000.0, 3), 0.001)
            return {
                "thermodynamic_violation": ans.get("thermodynamic_violation", {}).get("noul", 0.5),
                "human_viability_threat": ans.get("human_viability_threat", {}).get("noul", 0.5),
                "epistemic_deception": ans.get("epistemic_deception", {}).get("noul", 0.5),
                "required_manifold": ans.get("required_manifold", {}).get("choice", PHYSICAL_MANIFOLDS[0]),
                "manifold_probabilities": ans.get("required_manifold", {}).get("probabilities", {}),
                "latency_ms": duration_ms,
                "device": self.device,
                "model": model_used,
            }

        duration_ms = max(round((time.perf_counter() - t0) * 1000.0, 3), 0.001)
        return _evaluate_heuristic_axioms(text, PHYSICAL_MANIFOLDS, duration_ms)
