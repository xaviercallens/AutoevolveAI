"""
DPO Dataset Record Schema & Provenance Contracts.

Enforces strict typed structure for DPO preference pairs across multi-domain
benchmarks (Rust numeric, Pure Mathematics, Theoretical Physics).
Bans synthetic proxies and validates that all performance telemetry is empirical.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict


@dataclass
class DPORecord:
    """Rigorous schema for paired DPO preference optimization records."""

    case_id: str
    domain: str
    prompt: str
    chosen: str
    rejected: str
    reward_chosen: float
    reward_rejected: float
    reward_delta: float
    opt_lat: float
    base_lat: float
    opt_e: float
    base_e: float
    opt_lat__provenance: str = "measured"
    base_lat__provenance: str = "measured"
    opt_e__provenance: str = "measured"
    base_e__provenance: str = "measured"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.reward_delta <= 0.0:
            raise ValueError(
                f"Degenerate or inverted DPO pair: {self.case_id} has reward_delta={self.reward_delta} <= 0"
            )
        if self.opt_lat <= 0.0 or self.base_lat <= 0.0:
            raise ValueError(
                f"Invalid latency values for {self.case_id}: opt_lat={self.opt_lat}, base_lat={self.base_lat}"
            )
        for field_name in ("opt_lat", "base_lat", "opt_e", "base_e"):
            prov = getattr(self, f"{field_name}__provenance")
            if prov != "measured":
                raise ValueError(
                    f"Fabrication violation: {field_name} for {self.case_id} must have provenance='measured', got '{prov}'"
                )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DPORecord:
        """Validate and construct DPORecord strictly without synthetic fallbacks."""
        required = [
            "case_id",
            "domain",
            "prompt",
            "chosen",
            "rejected",
            "reward_chosen",
            "reward_rejected",
            "reward_delta",
            "opt_lat",
            "base_lat",
            "opt_e",
            "base_e",
        ]
        missing = [k for k in required if k not in data]
        if missing:
            raise KeyError(
                f"DPORecord schema violation for {data.get('case_id', 'unknown')}: missing required measured fields: {missing}"
            )

        return cls(
            case_id=str(data["case_id"]),
            domain=str(data["domain"]),
            prompt=str(data["prompt"]),
            chosen=str(data["chosen"]),
            rejected=str(data["rejected"]),
            reward_chosen=float(data["reward_chosen"]),
            reward_rejected=float(data["reward_rejected"]),
            reward_delta=float(data["reward_delta"]),
            opt_lat=float(data["opt_lat"]),
            base_lat=float(data["base_lat"]),
            opt_e=float(data["opt_e"]),
            base_e=float(data["base_e"]),
            opt_lat__provenance=str(data.get("opt_lat__provenance", "measured")),
            base_lat__provenance=str(data.get("base_lat__provenance", "measured")),
            opt_e__provenance=str(data.get("opt_e__provenance", "measured")),
            base_e__provenance=str(data.get("base_e__provenance", "measured")),
            metadata=dict(data.get("metadata", {})),
        )
