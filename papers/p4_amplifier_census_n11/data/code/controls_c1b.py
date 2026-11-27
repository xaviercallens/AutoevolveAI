"""C1b controls for the fast decision code (run BEFORE any N = 11 census number counts).

Usage: controls_c1b.py <census_fast binary> <out.json>

Positive:
  P1  K_11 and C_11: certified path does not exclude them; exact Fraction N_eff = 11 for both.
  P2  Richter's N = 11 graph J?ouPjI[@i?: not excluded, exact N_eff = 2668552698098/242579025123; its parent: exact 11.
  P3  Enumeration level: every connected graph on 11 vertices with degrees in [3,4] and 21 edges (nauty-geng -c -d3 -D4 11 21:21)
      passes through census_fast; the candidates are solved exactly; at least one has N_eff > 11 and is isomorphic to Richter's
      graph (canonical labels by nauty-labelg).
Negative:
  N1  Corrupted criterion (--corrupt uniform_pi: pi_i = 1/N instead of k_i/2m) on every connected graph with N = 3..10: the
      verdict counts must change relative to the correct criterion; one flipped graph is re-solved exactly with Fractions
      for the corrupted functional to confirm the certified corrupted verdict.
  N2  K_11 and C_11 do NOT pass the strict test N_eff > 11 (tie), and the parent does not.
"""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dbcore as d  # noqa: E402

WT = HERE.parents[4]
SCR_C1 = WT / ".scratchpad" / "C1"
SCR = WT / ".scratchpad" / "C1b"
C1DATA = WT / "results" / "proposal4" / "2026-10-27" / "C1" / "data"
CORE = "2"
R11_NEFF = Fraction(2668552698098, 242579025123)


def fast(binary: str, n: int, src: Path, out: Path, corrupt: bool = False) -> dict:
    cmd = ["taskset", "-c", CORE, binary, str(n), str(out)] + (["--corrupt", "uniform_pi"] if corrupt else [])
    with open(src, "rb") as fin:
        subprocess.run(cmd, stdin=fin, check=True, stderr=subprocess.DEVNULL)
    return json.load(open(out))


def canon(g6s: list[str]) -> list[str]:
    p = subprocess.run(["taskset", "-c", CORE, "nauty-labelg", "-q"], input="\n".join(g6s) + "\n", capture_output=True, text=True,
                       check=True)
    return p.stdout.split()


def neff_uniform_pi(adj: d.Adj) -> Fraction:
    """Corrupted functional (negative control): (1/N) sum_i tau_i, exact."""
    tau = d.coalescence_times(adj)
    ti = d.remeeting_times(adj, tau)
    return sum(ti, Fraction(0)) / len(adj)


def main() -> None:
    binary, out_path = sys.argv[1], sys.argv[2]
    res: dict = {"controls": []}

    def record(name: str, kind: str, passed: bool, detail: object) -> None:
        res["controls"].append({"name": name, "kind": kind, "passed": bool(passed), "detail": detail})
        print(("PASS " if passed else "FAIL ") + name, json.dumps(detail)[:400], flush=True)

    r11 = (C1DATA / "richter_n11_amplifier.g6").read_text().strip()
    p11 = (C1DATA / "richter_n11_parent.g6").read_text().strip()
    k11 = d.to_graph6(d.graph_complete(11))
    c11 = d.to_graph6(d.graph_cycle(11))
    src = SCR / "ctl_four.g6"
    src.write_text("\n".join([k11, c11, r11, p11]) + "\n")
    out = fast(binary, 11, src, SCR / "ctl_four.json")
    cand = {c["graph6"] for c in out["candidates"]}
    exact = {g: d.neff_exact(d.parse_graph6(g))[0] for g in (k11, c11, r11, p11)}
    record("P1_K11_C11_tie", "positive", k11 in cand and c11 in cand and exact[k11] == 11 and exact[c11] == 11,
           {"K11": [k11, str(exact[k11])], "C11": [c11, str(exact[c11])], "not_excluded": [k11 in cand, c11 in cand]})
    record("P2_richter_exact", "positive", r11 in cand and exact[r11] == R11_NEFF and exact[p11] == 11,
           {"R11": [r11, str(exact[r11]), float(exact[r11])], "parent": [p11, str(exact[p11])], "R11_not_excluded": r11 in cand})
    record("N2_ties_and_parent_not_amplifiers", "negative", not (exact[k11] > 11 or exact[c11] > 11 or exact[p11] > 11),
           {"K11_gt_11": exact[k11] > 11, "C11_gt_11": exact[c11] > 11, "parent_gt_11": exact[p11] > 11})

    # P3 enumeration-level Richter control
    sub = SCR / "geng11_d3D4_e21.g6"
    with open(sub, "w") as fo:
        gp = subprocess.run(["taskset", "-c", CORE, "nauty-geng", "-c", "-d3", "-D4", "11", "21:21"], stdout=fo, stderr=subprocess.PIPE,
                            text=True, check=True)
    geng_msg = gp.stderr.strip().splitlines()[-1]
    out3 = fast(binary, 11, sub, SCR / "ctl_d3D4_e21.json")
    rows = []
    for c in out3["candidates"]:
        ne = d.neff_exact(d.parse_graph6(c["graph6"]))[0]
        rows.append({"graph6": c["graph6"], "regular": c["regular"], "N_eff": str(ne), "gt": ne > 11})
    amps = [r["graph6"] for r in rows if r["gt"]]
    cr = canon([r11])[0]
    ca = canon(amps) if amps else []
    record("P3_richter_found_by_enumeration", "positive", cr in ca,
           {"geng": geng_msg, "graphs": out3["graphs"], "excluded": out3["excluded_certified"], "candidates": len(rows),
            "amplifiers": amps, "amplifier_canonical": ca, "richter_canonical": cr,
            "amplifier_neff": [r["N_eff"] for r in rows if r["gt"]]})

    # N1 corrupted criterion
    per_n = {}
    flipped_example = None
    changed_any = False
    for n in range(3, 11):
        g6 = SCR_C1 / f"geng_c{n}.g6"
        good = fast(binary, n, g6, SCR / f"ctl_good_n{n}.json")
        bad = fast(binary, n, g6, SCR / f"ctl_bad_n{n}.json", corrupt=True)
        gs = {c["graph6"] for c in good["candidates"]}
        bs = {c["graph6"] for c in bad["candidates"]}
        newly = sorted(bs - gs)
        per_n[n] = {"graphs": good["graphs"], "candidates_correct": len(gs), "candidates_corrupted": len(bs),
                    "excluded_correct": good["excluded_certified"], "excluded_corrupted": bad["excluded_certified"],
                    "new_candidates_under_corruption": len(newly), "lost_candidates_under_corruption": len(gs - bs),
                    "top_corrupted": bad["top_by_float_neff"][:3]}
        if newly:
            changed_any = True
            if flipped_example is None:
                g = newly[0]
                ce = neff_uniform_pi(d.parse_graph6(g))
                cc = d.neff_exact(d.parse_graph6(g))[0]
                flipped_example = {"N": n, "graph6": g, "corrupted_exact": str(ce), "corrupted_float": float(ce),
                                   "corrupted_ge_N": ce >= n, "correct_exact": str(cc), "correct_float": float(cc)}
    record("N1_corrupted_criterion_changes_verdicts", "negative", changed_any and flipped_example is not None
           and flipped_example["corrupted_ge_N"], {"per_N": per_n, "flipped_example": flipped_example})
    # corrupted functional on R11: certified interval must contain the exact corrupted value
    outb = fast(binary, 11, src, SCR / "ctl_four_bad.json", corrupt=True)
    ce_r11 = neff_uniform_pi(d.parse_graph6(r11))
    res["corrupted_R11"] = {"exact": str(ce_r11), "float": float(ce_r11),
                            "certified_excluded": r11 not in {c["graph6"] for c in outb["candidates"]}}
    res["all_passed"] = all(c["passed"] for c in res["controls"])
    json.dump(res, open(out_path, "w"), indent=1)
    print("ALL_PASSED" if res["all_passed"] else "SOME_FAILED", flush=True)


if __name__ == "__main__":
    main()
