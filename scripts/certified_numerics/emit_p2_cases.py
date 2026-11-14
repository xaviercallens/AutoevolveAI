#!/usr/bin/env python3
"""Untrusted emitter for the P2 data module and case files (certified DESI DR2 BAO likelihood).

  data [--tamper-row J --tamper-sigma X --name N]   BAOCert.P2.Data (or Data_<N>): exact data vector, full covariance,
                                                    sparse exact inverse P (P*C = I kernel-checked), xsOf, chi2DESI
  fit [--data N]                                    BAOCert.P2.Fit(_N): chi2 interval at the fit point (H6, C6)
  slabs                                             BAOCert.P2.Slab_<a>_<b>: for all Om in [a,b], all K: chi2 >= L (H8, C5)
  eds                                               BAOCert.P2.EdS: for all K: chi2(1, K) >= X (H7)

Python mirrors Lean's interval evaluator exactly (Fractions) so that the rounded bounds stated in the theorems can be
closed by `decide +kernel`. K0 (centring of the K-profile) comes from an untrusted mpmath fit and only affects
tightness, never soundness.
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import mpmath as mp

REPO = Path(__file__).resolve().parents[2]
LEAN_DIR = REPO / "formal_cert" / "BAOCert" / "P2"
RES = REPO / "results" / "certified_numerics" / "P2_likelihood"
DR2 = Path("/mnt/disks/disk-socrateai-local-1/dualscale-data-r3/desi_sdss_bao/desi_bao_dr2")
Z2000 = [590, 1020, 1412, 1868, 2642, 2968, 4660]
ZLAB = {n: f"z{n * 1000 // 2000:04d}" for n in Z2000}
# rows in file order: (kind, z index)
ROWS = [("w", 590), ("chi", 1020), ("invE", 1020), ("chi", 1412), ("invE", 1412), ("chi", 1868), ("invE", 1868),
        ("chi", 2642), ("invE", 2642), ("chi", 2968), ("invE", 2968), ("invE", 4660), ("chi", 4660)]
mp.mp.dps = 30


def load_data() -> tuple[list[Fraction], list[list[Fraction]], list[str]]:
    mean = [l.split() for l in (DR2 / "desi_gaussian_bao_ALL_GCcomb_mean.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    d = [Fraction(Decimal(r[1])) for r in mean]
    C = [[Fraction(Decimal(x)) for x in l.split()] for l in (DR2 / "desi_gaussian_bao_ALL_GCcomb_cov.txt").read_text().splitlines() if l.strip()]
    kinds = [r[2] for r in mean]
    expect = {"w": "DV_over_rs", "chi": "DM_over_rs", "invE": "DH_over_rs"}
    for (k, n), r in zip(ROWS, mean):
        assert expect[k] == r[2] and Fraction(Decimal(r[0])) == Fraction(n, 2000), (k, n, r)
    return d, C, kinds


def inverse_sparse(C: list[list[Fraction]]) -> list[tuple[int, int, Fraction]]:
    n = len(C)
    blocks: list[list[int]] = []
    seen: set[int] = set()
    for i in range(n):
        if i in seen:
            continue
        blk = [j for j in range(n) if C[i][j] != 0 or C[j][i] != 0]
        blocks.append(blk)
        seen.update(blk)
    ent: list[tuple[int, int, Fraction]] = []
    for blk in blocks:
        if len(blk) == 1:
            ent.append((blk[0], blk[0], 1 / C[blk[0]][blk[0]]))
        else:
            a, b = blk
            det = C[a][a] * C[b][b] - C[a][b] * C[b][a]
            ent += [(a, a, C[b][b] / det), (a, b, -C[a][b] / det), (b, a, -C[b][a] / det), (b, b, C[a][a] / det)]
    for i in range(n):  # exact check P C = I
        for k in range(n):
            s = sum(p * C[j][k] for (ii, j, p) in ent if ii == i)
            assert s == (1 if i == k else 0)
    return ent


def q(x: Fraction) -> str:
    return f"({x.numerator} / {x.denominator} : ℚ)" if x.denominator != 1 else f"({x.numerator} : ℚ)"


# --- exact mirror of Lean's Ex / ieval -------------------------------------------------------------------------
def iv_add(I, J):
    return (I[0] + J[0], I[1] + J[1])


def iv_mul(I, J):
    a, b, c, d = I[0] * J[0], I[0] * J[1], I[1] * J[0], I[1] * J[1]
    return (min(min(a, b), min(c, d)), max(max(a, b), max(c, d)))


def r_iv(dj, K0, xj):
    return iv_add((dj, dj), iv_mul((-K0, -K0), xj))


def sum_iv(terms):
    acc = (Fraction(0), Fraction(0))
    for t in reversed(terms):  # sumEx = add e (sumEx t), ending in c 0
        acc = iv_add(t, acc)
    return acc


def c_iv(P, d, K0, env):
    return sum_iv([iv_mul((p, p), iv_mul(r_iv(d[j], K0, env[j]), r_iv(d[k], K0, env[k]))) for j, k, p in P])


def b_iv(P, d, K0, env):
    return sum_iv([iv_mul((p, p), iv_add(iv_mul(r_iv(d[j], K0, env[j]), env[k]), iv_mul(env[j], r_iv(d[k], K0, env[k])))) for j, k, p in P])


def a_iv(P, env):
    return sum_iv([iv_mul((p, p), iv_mul(env[j], env[k])) for j, k, p in P])


# --- float model (untrusted, for K0) ---------------------------------------------------------------------------
def x_float(Om: float) -> list[float]:
    E = lambda z: mp.sqrt(Om * (1 + z) ** 3 + 1 - Om)
    out = []
    for kind, n in ROWS:
        z = mp.mpf(n) / 2000
        chi = mp.quad(lambda t: 1 / E(t), [0, z])
        out.append(float({"chi": chi, "invE": 1 / E(z), "w": mp.cbrt(z * chi**2 / E(z))}[kind]))
    return out


def best_K(P, d, x) -> float:
    A = sum(float(p) * x[j] * x[k] for j, k, p in P)
    B = sum(float(p) * (float(d[j]) * x[k] + x[j] * float(d[k])) for j, k, p in P)
    return B / (2 * A)


def tables() -> dict[str, dict]:
    out = {}
    for f in RES.glob("table_*.json"):
        t = json.loads(f.read_text())
        out[t["name"]] = t
    return out


class RF(Fraction):
    """A Fraction that remembers the unreduced 'num/den' text it was read from, so that the Lean literal written into
    a case file is syntactically the one stated by the table theorem (reduced and unreduced literals are equal
    rationals but do not unify syntactically)."""

    raw: str

    def __new__(cls, s: str) -> "RF":
        n, d = s.split("/")
        obj = super().__new__(cls, int(n), int(d))
        obj.raw = s
        return obj


def iv_from(t: dict, kind: str, n: int) -> tuple[RF, RF]:
    if kind == "w":
        a, b = t["wV"]
    else:
        a, b = t["z"][ZLAB[n]][kind]
    return RF(a), RF(b)


def lit(x: Fraction) -> str:
    raw = getattr(x, "raw", None)
    if raw is not None:
        n, d = raw.split("/")
        return f"({n} : ℚ) / ({d} : ℚ)"
    return q(x)


def iv_lean(I) -> str:
    return f"⟨{lit(I[0])}, {lit(I[1])}⟩"


def round_down(x: Fraction, digits: int = 4) -> Fraction:
    s = 10**digits
    return Fraction((x.numerator * s) // x.denominator, s)


def round_up(x: Fraction, digits: int = 4) -> Fraction:
    s = 10**digits
    return Fraction(-((-x.numerator * s) // x.denominator), s)


# --- writers ---------------------------------------------------------------------------------------------------
def write_data(name: str | None, tamper_row: int | None, tamper_sigma: float) -> None:
    d, C, kinds = load_data()
    if tamper_row is not None:
        sig = Fraction(Decimal(str(float(C[tamper_row][tamper_row]) ** 0.5)))
        d[tamper_row] = d[tamper_row] + Fraction(Decimal(str(tamper_sigma))) * sig
    P = inverse_sparse(C)
    mod = "Data" if name is None else f"Data_{name}"
    zc = lambda n: f"((({n} : ℕ) : ℝ) / ((2000 : ℕ) : ℝ))"
    xs = []
    for kind, n in ROWS:
        f = {"w": "wV", "chi": "chi", "invE": "invE"}[kind]
        xs.append(f"{f} Om {zc(n)}")
    lines = ["import BAOCert.Likelihood", "",
             f"/-! Generated by scripts/certified_numerics/emit_p2_cases.py (untrusted; re-checked here by the kernel).",
             "DESI DR2 BAO, desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt, decimals read as exact rationals." +
             ("" if tamper_row is None else f" NEGATIVE CONTROL C6: row {tamper_row} shifted by {tamper_sigma} sigma.") + " -/", "",
             f"namespace BAOCert.P2.{mod}", "open BAOCert", "",
             "/-- Data vector in file order: D_V/r_d (0.295); D_M, D_H at 0.51, 0.706, 0.934, 1.321, 1.484; D_H, D_M at 2.33. -/",
             "def dR : List ℚ := [" + ", ".join(q(x) for x in d) + "]", "",
             "/-- Full 13 × 13 covariance, file order. -/",
             "def Cfull : List (List ℚ) := [" + ", ".join("[" + ", ".join(q(x) for x in row) + "]" for row in C) + "]", "",
             "/-- Non-zero entries `(j, k, P_jk)` of `P = C⁻¹` (block diagonal). -/",
             "def Pent : List (ℕ × ℕ × ℚ) := [" + ", ".join(f"({j}, {k}, {q(p)})" for j, k, p in P) + "]", "",
             "/-- Dense view of a sparse matrix. -/",
             "def dense (L : List (ℕ × ℕ × ℚ)) (j k : ℕ) : ℚ := ((L.filter fun e => e.1 = j ∧ e.2.1 = k).map fun e => e.2.2).sum", "",
             "/-- `P · C = I` entrywise over the full 13 × 13 matrices. -/",
             "def inverseCheck : Bool := (List.range 13).all fun j => (List.range 13).all fun k =>",
             "  ((List.range 13).map fun l => dense Pent j l * ((Cfull.getD l []).getD k 0)).sum == (if j = k then 1 else 0)", "",
             "theorem P_is_inverse : inverseCheck = true := by decide +kernel", "",
             "/-- Base quantities in data order: `w` (D_V row), `χ` (D_M rows), `1/E` (D_H rows). -/",
             "noncomputable def xsOf (Om : ℝ) : List ℝ := [" + ", ".join(xs) + "]", "",
             "/-- Gaussian `χ²` of DESI DR2 BAO for flat ΛCDM (radiation off) at `Om` and `K = c/(100 h r_d)`. -/",
             "noncomputable def chi2DESI (Om K : ℝ) : ℝ := chi2Of Pent dR (valOf (xsOf Om)) K", "",
             f"end BAOCert.P2.{mod}"]
    LEAN_DIR.mkdir(parents=True, exist_ok=True)
    (LEAN_DIR / f"{mod}.lean").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (RES / f"{mod.lower()}.json").write_text(json.dumps({"d": [str(x) for x in d], "P": [[j, k, str(p)] for j, k, p in P],
                                                         "tamper_row": tamper_row, "tamper_sigma": tamper_sigma}, indent=1) + "\n")
    print(f"wrote {mod}")


def load_PD(mod: str):
    j = json.loads((RES / f"{mod.lower()}.json").read_text())
    d = [Fraction(x) for x in j["d"]]
    P = [(a, b, Fraction(c)) for a, b, c in j["P"]]
    return d, P


def mem_lines_point(tmod: str) -> list[str]:
    out = []
    for i, (kind, n) in enumerate(ROWS):
        th = {"w": f"wV_{ZLAB[n]}", "chi": f"chi_{ZLAB[n]}", "invE": f"invE_{ZLAB[n]}"}[kind]
        out.append(f"  have h{i} := BAOCert.P2.T_{tmod}.{th}")
    return out


def forall2(n: int) -> str:
    s = "List.Forall₂.nil"
    for i in reversed(range(n)):
        s = f"(List.Forall₂.cons h{i} {s})"
    return s


def write_fit(data_name: str | None) -> None:
    mod = "Data" if data_name is None else f"Data_{data_name}"
    d, P = load_PD(mod)
    t = tables()["FitFine"]
    env = [iv_from(t, kind, n) for kind, n in ROWS]
    K0 = Fraction(299792458, 10154300)
    I = c_iv(P, d, K0, env)
    lo, hi = round_down(I[0]), round_up(I[1])
    name = "Fit" if data_name is None else f"Fit_{data_name}"
    Om = "((29743 : ℕ) : ℝ) / ((100000 : ℕ) : ℝ)"
    lines = ["import BAOCert.P2.T_FitFine", f"import BAOCert.P2.{mod}", "",
             f"namespace BAOCert.P2.{name}", "open BAOCert BAOCert.P2", "",
             "def envs : List Iv := [" + ", ".join(iv_lean(I_) for I_ in env) + "]", "",
             f"/-- χ² of DESI DR2 at Om = 0.29743, h r_d = 101.543 Mpc (K = 299792458/10154300) lies in [{float(lo)}, {float(hi)}]. -/",
             f"theorem chi2_fit : ({q(lo)} : ℝ) ≤ {mod}.chi2DESI ({Om}) (((299792458 / 10154300 : ℚ)) : ℝ) ∧",
             f"    {mod}.chi2DESI ({Om}) (((299792458 / 10154300 : ℚ)) : ℝ) ≤ ({q(hi)} : ℝ) := by",
             *mem_lines_point("FitFine"),
             f"  have henv := env_ok envs ({mod}.xsOf ({Om})) {forall2(13)}",
             f"  have hm := chi2_mem_at_K0 {mod}.Pent {mod}.dR (299792458 / 10154300) _ _ henv",
             f"  have hlo : {q(lo)} ≤ ((cEx {mod}.Pent {mod}.dR (299792458 / 10154300)).ieval (envOf envs)).lo := by decide +kernel",
             f"  have hhi : ((cEx {mod}.Pent {mod}.dR (299792458 / 10154300)).ieval (envOf envs)).hi ≤ {q(hi)} := by decide +kernel",
             "  have hlo' := (Rat.cast_le (K := ℝ)).2 hlo",
             "  have hhi' := (Rat.cast_le (K := ℝ)).2 hhi",
             "  exact ⟨hlo'.trans hm.1, hm.2.trans hhi'⟩", "",
             f"end BAOCert.P2.{name}"]
    (LEAN_DIR / f"{name}.lean").write_text("\n".join(lines) + "\n", encoding="utf-8")
    rep = {"case": name, "interval_exact": [str(I[0]), str(I[1])], "stated": [str(lo), str(hi)], "stated_float": [float(lo), float(hi)]}
    (RES / f"case_{name}.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep["stated_float"]))


def slab_case(name: str, ta: str, tb: str, a: tuple[int, int], b: tuple[int, int], d, P) -> dict:
    T = tables()
    env = [(iv_from(T[tb], kind, n)[0], iv_from(T[ta], kind, n)[1]) for kind, n in ROWS]
    mid = (a[0] / a[1] + b[0] / b[1]) / 2
    K0 = Fraction(best_K(P, d, x_float(mid))).limit_denominator(10**9)
    A = a_iv(P, env)
    B = b_iv(P, d, K0, env)
    Cc = c_iv(P, d, K0, env)
    Bm = max(abs(B[0]), abs(B[1]))
    ok = A[0] > 0
    bound = Cc[0] - Bm * Bm / (4 * A[0]) if ok else None
    L = round_down(bound, 2) if ok else None
    return {"name": name, "a": f"{a[0]}/{a[1]}", "b": f"{b[0]}/{b[1]}", "K0": str(K0), "A_lo_positive": ok,
            "bound_exact": str(bound) if ok else None, "L": str(L) if ok else None, "L_float": float(L) if ok else None, "env": env}


def write_slab_file(rep: dict, ta: str, tb: str, a: tuple[int, int], b: tuple[int, int], mod: str = "Data") -> str:
    name = rep["name"]
    K0 = Fraction(rep["K0"])
    L = Fraction(rep["L"])
    ar, br = f"((({a[0]} : ℕ) : ℝ) / (({a[1]} : ℕ) : ℝ))", f"((({b[0]} : ℕ) : ℝ) / (({b[1]} : ℕ) : ℝ))"
    imports = sorted({f"import BAOCert.P2.T_{ta}", f"import BAOCert.P2.T_{tb}"})
    lines = [*imports, f"import BAOCert.P2.{mod}", "", f"namespace BAOCert.P2.{name}", "open BAOCert BAOCert.P2", "",
             "def envs : List Iv := [" + ", ".join(iv_lean(I_) for I_ in rep["env"]) + "]", "",
             f"/-- For every Om in [{a[0]}/{a[1]}, {b[0]}/{b[1]}] and every real K, χ²_DESI DR2(Om, K) ≥ {float(L)}. -/",
             f"theorem chi2_slab : ∀ Om : ℝ, {ar} ≤ Om → Om ≤ {br} → ∀ K : ℝ, ({q(L)} : ℝ) ≤ {mod}.chi2DESI Om K := by",
             "  intro Om hOa hOb",
             f"  have ha0 : (0 : ℝ) ≤ {ar} := by positivity",
             f"  have hb1 : {br} ≤ 1 := by norm_num",
             "  have hO0 : 0 ≤ Om := ha0.trans hOa",
             "  have hO1 : Om ≤ 1 := hOb.trans hb1"]
    for i, (kind, n) in enumerate(ROWS):
        th = {"w": f"wV_{ZLAB[n]}", "chi": f"chi_{ZLAB[n]}", "invE": f"invE_{ZLAB[n]}"}[kind]
        anti = {"w": "wV_anti_Om", "chi": "chi_anti_Om", "invE": "invE_anti_Om"}[kind]
        z = f"((({n} : ℕ) : ℝ) / ((2000 : ℕ) : ℝ))"
        lines += [f"  have hz{i} : (0 : ℝ) ≤ {z} := by positivity",
                  f"  have h{i} : ({iv_lean(rep['env'][i])} : Iv).mem _ :=",
                  f"    ⟨(BAOCert.P2.T_{tb}.{th}).1.trans ({anti} hO0 hOb hb1 hz{i}),",
                  f"     ({anti} ha0 hOa hO1 hz{i}).trans (BAOCert.P2.T_{ta}.{th}).2⟩"]
    lines += [f"  have henv := env_ok envs ({mod}.xsOf Om) {forall2(13)}",
              f"  exact chi2_lower_of_env {mod}.Pent {mod}.dR {q(K0)} _ _ henv {q(L)} (by decide +kernel) (by decide +kernel)", "",
              f"end BAOCert.P2.{name}"]
    (LEAN_DIR / f"{name}.lean").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return name


def refine() -> int:
    """Amendment A2: recursive bisection of the non-excluded preregistered slabs (min width 1/400)."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from emit_p2 import lean_table  # noqa: E402

    prereg = json.loads((RES / "preregistration.json").read_text())
    U_fit = Fraction(json.loads((RES / "case_Fit.json").read_text())["stated"][1])
    T = U_fit + 25
    elist = json.loads((REPO / "scripts/certified_numerics/p2_edges.json").read_text())["edges"]
    edges = {Fraction(p, q_): n for n, p, q_ in elist}
    raw = {n: (p, q_) for n, p, q_ in elist}
    d, P = load_PD("Data")

    def edge(x: Fraction) -> str:
        if x not in edges:
            name = f"R{x.numerator}_{x.denominator}"
            if not (LEAN_DIR / f"T_{name}.lean").exists():
                lean_table(name, x.numerator, x.denominator, 2000, False)
            edges[x] = name
            raw[name] = (x.numerator, x.denominator)
        return edges[x]

    leaves, new_edges = [], set()
    stack = [(Fraction(str(a)), Fraction(str(b))) for a, b in prereg["hypotheses"]["slabs"]]
    while stack:
        a, b = stack.pop()
        known = a in edges and b in edges
        ta, tb = edge(a), edge(b)
        if not known:
            new_edges.update({ta, tb} - {n for n, _, _ in json.loads((REPO / "scripts/certified_numerics/p2_edges.json").read_text())["edges"]})
        name = f"Ref_{ta}_{tb}"
        rep = slab_case(name, ta, tb, raw[ta], raw[tb], d, P)
        excluded = rep["A_lo_positive"] and Fraction(rep["L"]) > T
        if excluded or b - a <= Fraction(1, 400):
            if excluded:
                write_slab_file(rep, ta, tb, raw[ta], raw[tb])
            rep.pop("env")
            rep["excluded"] = bool(excluded)
            leaves.append(rep)
        else:
            m = (a + b) / 2
            stack += [(a, m), (m, b)]
    leaves.sort(key=lambda r: Fraction(r["a"]))
    (RES / "refine_plan.json").write_text(json.dumps({"threshold": str(T), "U_fit": str(U_fit), "leaves": leaves,
                                                      "new_edges": sorted(new_edges)}, indent=1) + "\n")
    exc = [r for r in leaves if r["excluded"]]
    print(json.dumps({"threshold": float(T), "leaves": len(leaves), "excluded": len(exc), "new_edges": len(new_edges),
                      "not_excluded": [[r["a"], r["b"], r["L_float"]] for r in leaves if not r["excluded"]]}, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    dd = sub.add_parser("data")
    dd.add_argument("--name")
    dd.add_argument("--tamper-row", type=int)
    dd.add_argument("--tamper-sigma", type=float, default=10.0)
    ff = sub.add_parser("fit")
    ff.add_argument("--data")
    sub.add_parser("slabs")
    sub.add_parser("refine")
    args = ap.parse_args()
    if args.cmd == "refine":
        return refine()
    if args.cmd == "data":
        write_data(args.name, args.tamper_row, args.tamper_sigma)
    elif args.cmd == "fit":
        write_fit(args.data)
    elif args.cmd == "slabs":
        prereg = json.loads((RES / "preregistration.json").read_text())
        elist = json.loads((REPO / "scripts/certified_numerics/p2_edges.json").read_text())["edges"]
        edges = {Fraction(p, q_): n for n, p, q_ in elist}
        raw = {n: (p, q_) for n, p, q_ in elist}
        d, P = load_PD("Data")
        slabs = [[Fraction(str(a)), Fraction(str(b))] for a, b in prereg["hypotheses"]["slabs"]] + [[Fraction(29, 100), Fraction(30, 100)], [Fraction(1), Fraction(1)]]
        out = []
        for a, b in slabs:
            ta, tb = edges[a], edges[b]
            name = "EdS" if a == b == 1 else f"Slab_{ta}_{tb}"
            rep = slab_case(name, ta, tb, raw[ta], raw[tb], d, P)
            if rep["A_lo_positive"]:
                write_slab_file(rep, ta, tb, raw[ta], raw[tb])
            rep.pop("env")
            out.append(rep)
            print(name, rep["L_float"])
        (RES / "slabs_plan.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
