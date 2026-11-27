"""Generate Lean certificates (witnesses for NOT_PD entries, LDL^T identities for PD entries) for a small deterministic sample.

Usage: python gen_lean.py <jdft_json> <per_entry_jsonl> <out_lean> <out_manifest_json>
Sample: 12 NOT_PD entries (first by jid order in each stratum: linear-pass-but-NOT_PD x4, cubic x2, hexagonal x2,
tetragonal_I x2, orthorhombic x1, monoclinic x1) and 6 PD entries (seeded random). Entries with huge rational size are skipped.
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction

import born_exact as be


def q(v: Fraction) -> str:
    if v.denominator == 1:
        return f"({v.numerator} : ℚ)"
    return f"({v.numerator} / {v.denominator} : ℚ)"


def mat(s: be.Matrix) -> str:
    return "![" + ", ".join("![" + ", ".join(q(v) for v in r) + "]" for r in s) + "]"


def vec(x: list[Fraction]) -> str:
    return "![" + ", ".join(q(v) for v in x) + "]"


def ldl_full(s: be.Matrix) -> tuple[list[list[Fraction]], list[Fraction]]:
    n = 6
    L = [[Fraction(0)] * n for _ in range(n)]
    d = [Fraction(0)] * n
    for j in range(n):
        d[j] = s[j][j] - sum((L[j][k] ** 2 * d[k] for k in range(j)), Fraction(0))
        L[j][j] = Fraction(1)
        for i in range(j + 1, n):
            L[i][j] = (s[i][j] - sum((L[i][k] * L[j][k] * d[k] for k in range(j)), Fraction(0))) / d[j]
    return L, d


def main(src: str, per_entry: str, out: str, manifest: str) -> int:
    data = {d["jid"]: d for d in json.load(open(src))}
    rs = [json.loads(line) for line in open(per_entry)]
    rs.sort(key=lambda r: r["jid"])

    def size(r: dict) -> int:
        s = be.symmetrize(be.to_matrix(data[r["jid"]]["elastic_tensor"]))
        return max(len(str(v.numerator)) + len(str(v.denominator)) for row in s for v in row)

    def ok(r: dict) -> bool:
        t = data[r["jid"]]["elastic_tensor"]
        return r["max_places"] <= 1 and max(abs(v) for row in t for v in row) < 1e4 and max(abs(v) for row in t for v in row) > 1e-6

    neg = [r for r in rs if (not r["pd_exact"]) and r["interval"] == "ROBUST_NOT_PD" and ok(r)]
    pick: list[dict] = []
    pick += [r for r in neg if r["linear_pass"]][:4]
    for cls, k in (("cubic", 2), ("hexagonal", 2), ("tetragonal_I", 2), ("orthorhombic", 1), ("monoclinic", 1)):
        pick += [r for r in neg if r["cls"] == cls and not r["linear_pass"] and len(r["witness"]) == 6][:k]
    pos = [r for r in rs if r["pd_exact"] and r["interval"] == "ROBUST_PD" and ok(r) and r["symmetric"]]
    random.Random(11).shuffle(pos)
    posp = pos[:6]

    lines = ["import Mathlib.Tactic", "", "namespace BornM2W", "",
             "/-- Quadratic form x^T C x for a 6x6 rational matrix. -/",
             "def quad (C : Fin 6 → Fin 6 → ℚ) (x : Fin 6 → ℚ) : ℚ := ∑ i, ∑ j, x i * C i j * x j", ""]
    man: list[dict] = []
    for n, r in enumerate(pick):
        s = be.symmetrize(be.to_matrix(data[r["jid"]]["elastic_tensor"]))
        x = [Fraction(t) for t in r["witness"]]
        lines += [f"-- {r['jid']} ({r['cls']}, spg {r['spg']}): symmetrised stored decimals, witness from exact LDL^T",
                  f"def S{n} : Fin 6 → Fin 6 → ℚ := fun i j => (({mat(s)}) : Matrix (Fin 6) (Fin 6) ℚ) i j",
                  f"theorem notpd_{n} : ∃ x : Fin 6 → ℚ, x ≠ 0 ∧ quad S{n} x ≤ 0 := by",
                  f"  refine ⟨{vec(x)}, ?_, ?_⟩",
                  f"  · intro h", f"    have := congrFun h {r['pivot_idx']}", "    norm_num at this",
                  f"  · norm_num [quad, S{n}, Fin.sum_univ_succ]", ""]
        man.append({"theorem": f"notpd_{n}", "jid": r["jid"], "kind": "NOT_PD_witness", "cls": r["cls"], "linear_pass": r["linear_pass"]})
    for n, r in enumerate(posp):
        s = be.symmetrize(be.to_matrix(data[r["jid"]]["elastic_tensor"]))
        L, d = ldl_full(s)
        assert all(v > 0 for v in d)

        def lin(k: int) -> str:
            return " + ".join(f"({q(L[i][k])}) * x {i}" for i in range(k, 6))
        rhs = " + ".join(f"({q(d[k])}) * ({lin(k)}) ^ 2" for k in range(6))
        lines += [f"-- {r['jid']} ({r['cls']}, spg {r['spg']}): LDL^T identity with positive pivots (unit lower-triangular L)",
                  f"def P{n} : Fin 6 → Fin 6 → ℚ := fun i j => (({mat(s)}) : Matrix (Fin 6) (Fin 6) ℚ) i j",
                  f"theorem pd_{n} (x : Fin 6 → ℚ) : quad P{n} x = {rhs} := by",
                  f"  simp only [quad, P{n}, Fin.sum_univ_succ, Fin.sum_univ_zero]", "  norm_num", "  ring", ""]
        pivots = " ∧ ".join(f"(0 : ℚ) < {q(dk)}" for dk in d)
        lines += [f"theorem pd_{n}_pivots : {pivots} := by norm_num", ""]
        man.append({"theorem": f"pd_{n}", "jid": r["jid"], "kind": "PD_LDL_identity", "cls": r["cls"]})
    lines += ["end BornM2W", ""]
    for n in range(len(pick)):
        lines.append(f"#print axioms BornM2W.notpd_{n}")
    for n in range(len(posp)):
        lines.append(f"#print axioms BornM2W.pd_{n}")
        lines.append(f"#print axioms BornM2W.pd_{n}_pivots")
    open(out, "w").write("\n".join(lines) + "\n")
    json.dump(man, open(manifest, "w"), indent=1)
    print(len(pick), len(posp))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
