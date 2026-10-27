"""Loaders for the extracted Zenodo 14452152 files (untrusted data; JSON only, parsed with json)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


class Dataset:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)  # .../DAC_data

    def _j(self, rel: str) -> dict:
        return json.loads((self.root / rel).read_text())

    def material(self, name: str) -> dict:
        return self._j(f"CSD_FEASST_Materials/Materials/{name}.json")

    def kh_n2(self, name: str) -> dict:
        p = name.replace("_clean", "").replace("_h", "_clean_h")
        return self._j(f"Results/results_300_N2_{p}.json")

    def kh_co2(self, name: str) -> dict:
        return self._j(f"CSD_FEASST_Materials/Results/{name}.results.json")

    def saturation_mmol_per_kg(self, name: str) -> float:
        d = self._j(f"Saturation/CO2_sat_200K_{name}.json")
        step = d["step_number"]
        loading = d["isotherm"][str(step)]["loading"]
        mass = self.material(name)["cell_mass"]
        return float(loading) * 1e6 / float(mass)

    def cv(self, name: str) -> dict:
        return self._j(f"CV_predictions/Cv_{name}.json")

    def optimized(self, name: str) -> dict:
        return self._j(f"Optimized_Intrinsic_Cycle/OptIDC_{name}.json")

    def optimized_names(self) -> list[str]:
        d = self.root / "Optimized_Intrinsic_Cycle"
        return sorted(p.name[len("OptIDC_"):-len(".json")] for p in d.glob("OptIDC_*.json"))


def arr(x) -> np.ndarray:
    """Julia vectors / 1-column matrices -> flat float array (JSON null -> nan)."""
    a = np.array(x, dtype=object)
    flat = np.array([np.nan if v is None else v for v in np.ravel(np.array(a.tolist(), dtype=object))],
                    dtype=float) if a.size else np.array([], dtype=float)
    return flat
