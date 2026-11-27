"""Revision-stage checks (audit notes N1, N2): sensitivity of the He-4 verdict counts to the post hoc Delta_ds,
and the verdicts under Donnelly-Barenghi's own dataset recommendation (X-ray for Q<1, neutron for Q>1).
Reads data/test_he4.csv (the producer's table: Q, S, key, bound, margin). Tier X; writes revision_checks.json.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I revision_checks.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def verdict(margin: float, delta: float) -> str:
    if margin <= 0:
        return "CONSISTENT"
    return "REFUTED" if margin > delta else "UNDECIDED"


def counts(rows: list[dict[str, float]], delta: float) -> dict[str, int]:
    out = {"CONSISTENT": 0, "UNDECIDED": 0, "REFUTED": 0}
    for r in rows:
        out[verdict(r["margin"], delta)] += 1
    return out


def main() -> int:
    rows: list[dict[str, float]] = []
    with (HERE / "data/test_he4.csv").open() as fh:
        for r in csv.DictReader(fh):
            rows.append({"Q": float(r["Q_invA"]), "S": float(r["S"]), "key": float(r["key"]),
                         "bound": float(r["bound"]), "margin": float(r["margin"])})
    res: dict[str, object] = {"n": len(rows), "tier": "X", "claim_licence": False}
    # N1: sensitivity to the post hoc threshold
    sens = {}
    for d in (0.07, 0.075, 0.082, 0.09, 0.10):
        c = counts(rows, d)
        c["REFUTED_Q_gt_2p4"] = sum(1 for r in rows if r["Q"] > 2.4 and verdict(r["margin"], d) == "REFUTED")
        c["REFUTED_xray"] = sum(1 for r in rows if r["key"] == 1 and verdict(r["margin"], d) == "REFUTED")
        c["REFUTED_roton_1p7_2p4"] = sum(1 for r in rows if 1.7 <= r["Q"] <= 2.4 and verdict(r["margin"], d) == "REFUTED")
        sens[f"{d:g}"] = c
    res["sensitivity_to_delta"] = sens
    near = [(r["Q"], round(r["margin"], 4), int(r["key"])) for r in rows if 0.07 <= r["margin"] <= 0.09]
    res["points_with_margin_0p07_to_0p09"] = near
    q = [r for r in rows if r["Q"] > 2.4 and r["margin"] > 0]
    res["smallest_positive_margins_above_Q2p4"] = sorted((round(r["margin"], 4), r["Q"], int(r["key"])) for r in q)[:6]
    # N2: Donnelly-Barenghi recommendation: X-ray (key 1) for Q<1, neutron (key 2) for Q>1
    rec = [r for r in rows if (r["key"] == 1 and r["Q"] < 1.0) or (r["key"] == 2 and r["Q"] > 1.0)]
    roton = [r for r in rec if 1.7 <= r["Q"] <= 2.4]
    res["recommended_subset"] = {
        "n": len(rec), "n_xray_Q_lt_1": sum(1 for r in rec if r["key"] == 1),
        "n_neutron_Q_gt_1": sum(1 for r in rec if r["key"] == 2),
        "verdicts_delta_0.082": counts(rec, 0.082),
        "roton_n": len(roton),
        "roton_all_refuted": all(verdict(r["margin"], 0.082) == "REFUTED" for r in roton),
        "roton_min_margin": min(r["margin"] for r in roton),
        "roton_ratio_range": [min(r["S"] / r["bound"] for r in roton), max(r["S"] / r["bound"] for r in roton)],
        "roton_refuted_even_if_delta_0": all(r["margin"] > 0 for r in roton),
    }
    allroton = [r for r in rows if 1.7 <= r["Q"] <= 2.4]
    res["roton_min_margin_all_points"] = min(r["margin"] for r in allroton)
    res["roton_min_margin_over_delta"] = min(r["margin"] for r in allroton) / 0.082
    # N3: the hand-checkable peak inequality
    pk = max(allroton, key=lambda r: r["S"])
    res["peak_point"] = {"Q": pk["Q"], "S": pk["S"], "bound": pk["bound"], "ratio": pk["S"] / pk["bound"], "key": pk["key"]}
    (HERE / "revision_checks.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
