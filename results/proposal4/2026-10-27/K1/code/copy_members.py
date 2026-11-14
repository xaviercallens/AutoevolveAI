"""Copy the dataset members used for the Table 2 materials into K1/data/zenodo_members (CC-BY-4.0 data,
Zenodo 14452152, NIST: McDannald & Siderius) and write their SHA-256."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

NAMES = ["VANNIK_clean", "LETQAE01_ion_b", "BEVQID_clean", "FASJAL_clean", "IFUDAO_charged", "MAXHEA_clean",
         "MAXHOK_clean", "PARFOF_clean_h"]


def rels(n: str) -> list[str]:
    p = n.replace("_clean", "").replace("_h", "_clean_h")
    return [f"Optimized_Intrinsic_Cycle/OptIDC_{n}.json", f"CSD_FEASST_Materials/Results/{n}.results.json",
            f"Results/results_300_N2_{p}.json", f"CV_predictions/Cv_{n}.json", f"Saturation/CO2_sat_200K_{n}.json",
            f"Atmosphere_check/results_300K_1atmN2_{p}.json"]


def main() -> int:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    extra = sys.argv[3:]
    out = {}
    for n in NAMES:
        for r in rels(n):
            s = src / r
            if not s.exists():
                out[r] = "MISSING"
                continue
            d = dst / r
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(s, d)
            out[r] = hashlib.sha256(d.read_bytes()).hexdigest()
    for r in extra:
        s = src / r
        d = dst / r
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(s, d)
        out[r] = hashlib.sha256(d.read_bytes()).hexdigest()
    (dst / "SHA256SUMS.json").write_text(json.dumps(out, indent=1))
    print(len(out), sum(1 for v in out.values() if v == "MISSING"), "missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
