"""
Domain-Specific Invariant Tolerances & Normalization Engine.
Defines acceptable error bounds for numerical, theoretical, and stochastic benchmarks.
Backed by declarative invariant_registry.yaml with high-performance in-memory fallback.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

REGISTRY_PATH = Path(__file__).resolve().parent / "invariant_registry.yaml"

# Static Fallbacks for ultra-fast lookup
TOLERANCES: Dict[str, float] = {
    # Deterministic Exact
    "RUST-01": 1e-12,
    "RUST-02": 1e-12,
    "RUST-03": 1e-12,
    "RUST-04": 1e-12,
    "RUST-06": 1e-12,
    "RUST-07": 1e-12,
    "RUST-09": 1e-12,
    "RUST-11": 1e-12,
    "RUST-12": 1e-12,
    "RUST-14": 1e-12,
    "RUST-16": 1e-12,
    "RUST-18": 1e-12,
    "RUST-19": 1e-12,
    # Adaptive Numerical
    "RUST-08": 1e-08,
    "RUST-10": 1e-06,
    "RUST-13": 1e-04,
    "RUST-15": 1e-10,
    "RUST-17": 1e-06,
    # Stochastic (variance tolerance)
    "RUST-05": 0.05,
    "RUST-20": 0.05,
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
        except Exception:
            pass

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
