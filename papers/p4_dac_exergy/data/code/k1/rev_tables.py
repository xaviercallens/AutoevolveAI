"""Revision 2026-10-27: write the two LaTeX table bodies of the v2 paper from the JSON outputs (no hand transcription).

Usage: python -I rev_tables.py <exergy_table2_right.json> <scenario_summary.json> <out_base.tex> <out_air.tex>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def f(v: float | None, fmt: str) -> str:
    return "--" if v is None else format(v, fmt)


def ratio_fmt(v: float | None) -> str:
    if v is None:
        return "--"
    return f"{v:.1f}" if v >= 10 else f"{v:.2f}"


def main() -> int:
    ex = json.loads(Path(sys.argv[1]).read_text())
    sm = json.loads(Path(sys.argv[2]).read_text())
    base_lines = []
    air_lines = []
    for e, s in zip(ex["rows"], sm["rows"]):
        name = e["row"][0].split(" ")[0]
        xpub = e["row"][1]
        assert s["row"].split(" ")[-1] == xpub, (s["row"], xpub)
        t = e["eval"]["T0=298.15"]
        br = s["base_ratio_v1"]
        base_lines.append(" & ".join([
            name, xpub, f(e["eval"]["xi_fv_umol_per_J"], ".2f"), f(t["r=0.0"]["xi_umol_per_J"], ".1f"),
            f(t["r=1.0"]["xi_umol_per_J"], ".1f"), f(t["refrigeration_share_of_B_NC"], ".2f"),
            f(s["base_T1star_U_298_r0"], ".1f"), ratio_fmt(br["fv"]), ratio_fmt(br["r0"]), ratio_fmt(br["r1"]),
            f(s["best_warm_purity_298"], ".2f") + "/" + f(s["purity_min"], ".3f")]) + r"\\")
        a = s["air_eps0"]
        oc = {"cold": "C", "near-ambient": "N", "warm": "W"}

        def cell(r: str) -> str:
            v = a[r]['T1star']
            txt = f"{v:.0f}" if abs(v - round(v)) < 1e-6 else f"{v:.2f}"
            return f"{txt} {oc[a[r]['outcome']]}"
        es = s["eps_star_d10"]["1.0"]
        ea = s["eps_star_aud"]["1.0"]
        air_lines.append(" & ".join([
            name, xpub, cell("0.0"), ratio_fmt(a["0.0"]["ratio_d10"]), cell("0.5"), ratio_fmt(a["0.5"]["ratio_d10"]),
            cell("1.0"), f(a["1.0"]["ratio_v1"], ".4f"), ratio_fmt(a["1.0"]["ratio_d10"]),
            "none" if es is None else f"{es:.2f}", "none" if ea is None else f"{ea:.2f}",
            f(s["eta_noair_R_r1_d10"], ".2f")]) + r"\\")
    Path(sys.argv[3]).write_text("\n".join(base_lines) + "\n")
    Path(sys.argv[4]).write_text("\n".join(air_lines) + "\n")
    print("\n".join(base_lines))
    print("\n".join(air_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
