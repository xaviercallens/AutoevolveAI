"""Positive and negative controls for C1 (exact rationals). Writes data/controls.json; exit 1 if any control misbehaves."""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbcore as d  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data" / "controls.json"
results: list[dict[str, object]] = []


def record(name: str, kind: str, passed: bool, detail: object) -> None:
    results.append({"control": name, "kind": kind, "expected_outcome_met": bool(passed), "detail": detail})
    print(("OK   " if passed else "FAIL ") + kind + " " + name, flush=True)


def geng(n: int, extra: list[str]) -> list[str]:
    res = subprocess.run(["/usr/bin/nauty-geng", "-cq", *extra, str(n)], capture_output=True, text=True, check=True)
    return [x for x in res.stdout.splitlines() if x]


R_VALUES = [Fraction(3, 4), Fraction(5, 4), Fraction(3, 2), Fraction(7, 4), Fraction(1001, 1000)]

# P1: complete graphs and cycles have N_eff = N exactly (weak-selection isothermal theorem).
ok = True
for n in range(3, 11):
    ok &= d.neff_exact(d.graph_complete(n))[0] == n
    ok &= d.neff_exact(d.graph_cycle(n))[0] == n
record("K_N and C_N give N_eff = N exactly, N=3..10", "positive", ok, None)

# P2: star N_eff = 4n/(n+1) (Allen p. 9) and edge-average identity.
ok = True
det = {}
for nl in range(2, 10):
    g = d.graph_star(nl)
    ne, ti, tau = d.neff_exact(g)
    ok &= ne == Fraction(4 * nl, nl + 1)
    ok &= d.neff_edge_identity(g, tau) == ne
    det[nl] = str(ne)
record("star S_n: N_eff = 4n/(n+1), n=2..9; edge identity", "positive", ok, det)

# P3: edge-average identity N_eff = 1 + mean_{edges} tau_ij on every connected graph N <= 7.
ok = True
cnt = 0
for n in range(3, 8):
    for s in geng(n, []):
        g = d.parse_graph6(s)
        ne, ti, tau = d.neff_exact(g)
        ok &= d.neff_edge_identity(g, tau) == ne
        two_m = sum(len(a) for a in g)
        ok &= sum((Fraction(len(g[i]), two_m) ** 2 * ti[i] for i in range(n)), Fraction(0)) == 1  # Allen eq. (7)
        cnt += 1
record("edge identity + Allen eq.(7) sum pi_i^2 tau_i = 1 on all connected graphs N=3..7", "positive", ok, {"graphs": cnt})

# P4: independent slope check, d rho/dr at r=1 from the exact chain == (N_eff - 2)/(2N) (Allen eq. 8).
ok = True
cnt = 0
for n in range(3, 7):
    for s in geng(n, []):
        g = d.parse_graph6(s)
        ne = d.neff_exact(g)[0]
        ok &= d.fixation_slope_at_neutral(g) == (ne - 2) / (2 * n)
        cnt += 1
for s in geng(7, [])[::40]:
    g = d.parse_graph6(s)
    ok &= d.fixation_slope_at_neutral(g) == (d.neff_exact(g)[0] - 2) / 14
    cnt += 1
record("exact-chain slope d rho/dr|_{r=1} = (N_eff-2)/(2N): all connected N=3..6 + every 40th N=7", "positive", ok, {"graphs": cnt})

# P5: closed forms vs exact chain at rational r.
ok_k = ok_c = ok_s = True
allen3_mismatch = 0
for n in range(3, 8):
    for r in R_VALUES:
        ok_k &= d.fixation_exact(d.graph_complete(n), r, "dB") == d.rho_complete_db(n, r)
        ok_k &= d.fixation_exact(d.graph_complete(n), r, "Bd") == d.rho_complete_bd(n, r)
        ex = d.fixation_exact(d.graph_cycle(n), r, "dB")
        ok_c &= ex == d.rho_cycle_db_kaveh(n, r)
        if ex != d.rho_cycle_db_allen_eq3_as_printed(n, r):
            allen3_mismatch += 1
        ok_s &= d.fixation_exact(d.graph_star(n - 1), r, "dB") == d.rho_star_db(n - 1, r)
record("dB and Bd K_N closed forms == exact chain, N=3..7, 5 r values", "positive", ok_k, None)
record("dB cycle Kaveh eq.(20)/Hindersin SI(18)/Richter(12) == exact chain", "positive", ok_c, None)
record("dB star Allen eq.(2) == exact chain", "positive", ok_s, None)
record("Allen eq.(3) as printed (r^{-(N-1)}) must DISAGREE with exact chain", "negative", allen3_mismatch == 25,
       {"mismatches_of_25": allen3_mismatch})

# P6: Hindersin N=4 cycle eq. (13), (14).
ok = True
for r in R_VALUES:
    ex = d.fixation_exact(d.graph_cycle(4), r, "dB")
    ok &= ex == 2 * r * r / (3 * r * r + 2 * r + 3)
    ok &= ex - d.rho_complete_db(4, r) == -r * r * (r - 1) ** 2 / (4 * (r * r + r + 1) * (3 * r * r + 2 * r + 3))
record("Hindersin eq.(13),(14): C_4 dB", "positive", ok, None)

# P7: Hindersin N=4 classification (r = 0.75, 1.25, 1.5, 1.75; uniform init).
cls = {}
for s in geng(4, []):
    g = d.parse_graph6(s)
    lab = {}
    for rule, ref in (("dB", d.rho_complete_db), ("Bd", d.rho_complete_bd)):
        lo = d.fixation_exact(g, Fraction(3, 4), rule) - ref(4, Fraction(3, 4))
        hi = [d.fixation_exact(g, r, rule) - ref(4, r) for r in (Fraction(5, 4), Fraction(3, 2), Fraction(7, 4))]
        if lo < 0 and all(h > 0 for h in hi):
            lab[rule] = "amplifier"
        elif lo > 0 and all(h < 0 for h in hi):
            lab[rule] = "suppressor"
        elif lo == 0 and all(h == 0 for h in hi):
            lab[rule] = "equal_to_well_mixed"
        else:
            lab[rule] = "unclassified"
    lab["degrees"] = sorted(len(a) for a in g)
    lab["N_eff"] = str(d.neff_exact(g)[0])
    cls[s] = lab
bd_amp = sum(1 for v in cls.values() if v["Bd"] == "amplifier")
db_sup = sum(1 for v in cls.values() if v["dB"] == "suppressor")
db_uncl = [k for k, v in cls.items() if v["dB"] == "unclassified"]
ok = bd_amp == 4 and db_sup == 4 and len(db_uncl) == 1 and cls[db_uncl[0]]["degrees"] == [2, 2, 2, 2]
record("Hindersin N=4: 4 heterogeneous graphs Bd amplifiers & dB suppressors; C_4 only dB-unclassified", "positive", ok, cls)

# P8: star is a Bd amplifier and a dB suppressor (N = 5..7, r grid).
ok = True
for nl in (4, 5, 6):
    g = d.graph_star(nl)
    for r in R_VALUES:
        sgn = 1 if r > 1 else -1
        ok &= sgn * (d.fixation_exact(g, r, "Bd") - d.rho_complete_bd(nl + 1, r)) > 0
        ok &= sgn * (d.fixation_exact(g, r, "dB") - d.rho_complete_db(nl + 1, r)) < 0
record("star S_4..S_6: Bd amplifier and dB suppressor on r grid", "positive", ok, None)

# N1: transposed step probabilities p_ij = 1/k_j must break the star value.
bad = d.neff_exact(d.graph_star(5), step="transposed")[0]
record("planted wrong walk (p_ij=1/k_j) must break star N_eff=10/3", "negative", bad != Fraction(20, 6), {"wrong_value": str(bad)})

# N2: K_N never an amplifier of itself under the strict test.
record("K_N never passes strict N_eff > N", "negative", all(not (d.neff_exact(d.graph_complete(n))[0] > n) for n in range(3, 11)), None)

# N3: Antal approximation always <= N on all connected graphs N <= 7 (so it can never find an amplifier).
record("Antal N mu1^2/mu2 <= N on all connected N<=7", "negative",
       all(d.antal_neff(d.parse_graph6(s)) <= n for n in range(3, 8) for s in geng(n, [])), None)

OUT.write_text(json.dumps(results, indent=1))
bad_ctrl = [x["control"] for x in results if not x["expected_outcome_met"]]
print("controls_failed:", bad_ctrl)
sys.exit(1 if bad_ctrl else 0)
