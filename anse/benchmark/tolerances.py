"""
Domain-Specific Invariant Tolerances & Normalization Engine.
Defines acceptable error bounds for numerical, theoretical, and stochastic benchmarks.
Backed by declarative invariant_registry.yaml with high-performance in-memory fallback.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path(__file__).resolve().parent / "invariant_registry.yaml"

# Static Fallbacks for ultra-fast lookup
TOLERANCES: Dict[str, float] = {
    # Rust Numeric (30 Cases)
    "RUST-01": 1e-12, "RUST-02": 1e-12, "RUST-03": 1e-05, "RUST-04": 1e-12,
    "RUST-05": 0.05,  "RUST-06": 1e-12, "RUST-07": 1e-12, "RUST-08": 1e-08,
    "RUST-09": 1e-12, "RUST-10": 1e-06, "RUST-11": 1e-12, "RUST-12": 1e-12,
    "RUST-13": 1e-04, "RUST-14": 1e-12, "RUST-15": 1e-10, "RUST-16": 1e-12,
    "RUST-17": 1e-06, "RUST-18": 1e-12, "RUST-19": 1e-12, "RUST-20": 0.05,
    "RUST-21": 1e-12, "RUST-22": 1e-10, "RUST-23": 1e-08, "RUST-24": 1e-05,
    "RUST-25": 1e-09, "RUST-26": 1e-08, "RUST-27": 1e-09, "RUST-28": 1e-08,
    "RUST-29": 1e-06, "RUST-30": 1e-08,
    # Pure Mathematics (30 Cases)
    "MATH-01": 1e-12, "MATH-02": 1e-12, "MATH-03": 1e-08, "MATH-04": 1e-12,
    "MATH-05": 1e-08, "MATH-06": 1e-08, "MATH-07": 1e-12, "MATH-08": 1e-12,
    "MATH-09": 1e-06, "MATH-10": 1e-12, "MATH-11": 1e-12, "MATH-12": 1e-12,
    "MATH-13": 1e-12, "MATH-14": 1e-12, "MATH-15": 1e-08, "MATH-16": 1e-08,
    "MATH-17": 1e-12, "MATH-18": 1e-12, "MATH-19": 1e-12, "MATH-20": 1e-12,
    "MATH-21": 1e-12, "MATH-22": 1e-12, "MATH-23": 1e-08, "MATH-24": 1e-12,
    "MATH-25": 1e-08, "MATH-26": 1e-12, "MATH-27": 1e-08, "MATH-28": 1e-12,
    "MATH-29": 1e-12, "MATH-30": 1e-08,
    # Theoretical Physics (30 Cases)
    "PHYS-01": 1e-12, "PHYS-02": 1e-12, "PHYS-03": 1e-12, "PHYS-04": 1e-06,
    "PHYS-05": 1e-12, "PHYS-06": 1e-12, "PHYS-07": 1e-08, "PHYS-08": 1e-12,
    "PHYS-09": 1e-12, "PHYS-10": 1e-12, "PHYS-11": 1e-12, "PHYS-12": 1e-12,
    "PHYS-13": 1e-12, "PHYS-14": 1e-12, "PHYS-15": 1e-12, "PHYS-16": 1e-12,
    "PHYS-17": 1e-12, "PHYS-18": 1e-12, "PHYS-19": 1e-12, "PHYS-20": 1e-12,
    "PHYS-21": 1e-12, "PHYS-22": 1e-12, "PHYS-23": 1e-08, "PHYS-24": 1e-08,
    "PHYS-25": 1e-12, "PHYS-26": 1e-12, "PHYS-27": 1e-12, "PHYS-28": 1e-08,
    "PHYS-29": 1e-12, "PHYS-30": 1e-12,
    # Complex Python Applied Physics & Math (30 Cases)
    "PYTHON-01": 1e-08, "PYTHON-02": 1e-06, "PYTHON-03": 1e-08, "PYTHON-04": 1e-12,
    "PYTHON-05": 1e-10, "PYTHON-06": 1e-12, "PYTHON-07": 1e-06, "PYTHON-08": 1e-08,
    "PYTHON-09": 1e-08, "PYTHON-10": 1e-10, "PYTHON-11": 1e-08, "PYTHON-12": 1e-06,
    "PYTHON-13": 1e-06, "PYTHON-14": 1e-09, "PYTHON-15": 1e-06, "PYTHON-16": 1e-04,
    "PYTHON-17": 1e-08, "PYTHON-18": 1e-06, "PYTHON-19": 1e-04, "PYTHON-20": 1e-12,
    "PYTHON-21": 1e-06, "PYTHON-22": 1e-06, "PYTHON-23": 1e-06, "PYTHON-24": 1e-06,
    "PYTHON-25": 1e-12, "PYTHON-26": 1e-08, "PYTHON-27": 1e-08, "PYTHON-28": 1e-06,
    "PYTHON-29": 1e-08, "PYTHON-30": 1e-08,
}

_REGISTRY_CACHE: Dict[str, Dict[str, Any]] | None = None


def get_registry() -> Dict[str, Dict[str, Any]]:
    """Loads and caches invariant_registry.yaml."""
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE

    if REGISTRY_PATH.exists():
        try:
            import yaml

            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                _REGISTRY_CACHE = yaml.safe_load(f) or {}
                return _REGISTRY_CACHE
        except Exception as exc:
            logger.warning("Failed loading invariant registry %s: %s", REGISTRY_PATH, exc)

    _REGISTRY_CACHE = {}
    return _REGISTRY_CACHE


def normalize_error(case_id: str, error: float) -> float:
    """
    Normalize the raw invariant error into a [0, 1] penalty score.
    Applies linear or quadratic normalization based on domain registry.
    """
    if error <= 0.0:
        return 0.0

    registry = get_registry()
    entry = registry.get(case_id, {})
    tol = float(entry.get("tolerance", TOLERANCES.get(case_id, 1e-12)))
    norm_type = entry.get("normalization", "linear")

    ratio = error / tol

    if norm_type == "quadratic":
        # Stochastic variance: gentle inside tolerance, quadratic penalty when exceeding
        normalized = ratio * ratio
    else:
        # Standard linear normalization
        normalized = ratio

    return float(min(1.0, max(0.0, normalized)))
