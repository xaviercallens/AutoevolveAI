"""Generator for the L1 port of stage `cs()` (lattice coefficients c_1..c_38, core.hpp:150-172).

1. Brute-force Python mirror of cs() exactly as written in the C++ (grouping by norm), compared with the C++ co[m]
   from the dump (must be bit-equal, else abort).
2. The band formulation used by Lean: the norms are split into bands [N0, N1); in each band the points of the box with
   norm in the band are enumerated row by row through two k-intervals (from integer square roots), grouped by norm,
   and Σ_N rat(S_N, base_N^m) is formed. Since IV addition is exact, the band sums add up to the C++ result. The
   Python band computation is compared with the brute force.
3. Emits Lean: Cs/Core.lean (definitions), one chunk file per band and mode (theorem: band value = literal, plus the
   point count), Cs/Assemble.lean (the bands tile the norm range, the counts add up to the box size, and the final
   scaling of the band sums gives exactly the C++ co[1..38] = coList of Bcons.lean), and planted false chunks.
   Writes chunks.json entries for the scheduler.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from l1common import (CONT, L1DIR, OLD_DUMP, ONE, ZERO, add, div, inv, isqrt, lit, load_scalars, mul, ofint,  # noqa: E402
                      pow_, rat, sha256)

M = 38
B0, B1 = 256, 48


def re_im6(n: int, k: int) -> tuple[int, int]:
    ar, bi = 2 * n + k, k
    ar2, bi2 = ar * ar, bi * bi
    re6 = ar2 * ar2 * ar2 - 45 * ar2 * ar2 * bi2 + 135 * ar2 * bi2 * bi2 - 27 * bi2 * bi2 * bi2
    im6 = 6 * ar * ar2 * ar2 * bi - 60 * ar * ar2 * bi * bi2 + 54 * ar * bi * bi2 * bi2
    return re6, im6


def m1vals(re6: int, im6: int) -> list[int]:
    """[2 Re(z^m) for m = 2..38] in the C++ recurrence."""
    out, re, im = [], re6, im6
    for _ in range(M - 1):
        nr = re * re6 - 3 * im * im6
        im = re * im6 + im * re6
        re = nr
        out.append(2 * re)
    return out


def brute(a: tuple[int, int]) -> tuple[list[tuple[int, int]], dict[int, int], dict[int, list[int]]]:
    result = [ZERO] * M
    sums0: dict[int, int] = {}
    sums1: dict[int, list[int]] = {}
    for mode, B in ((0, B0), (1, B1)):
        for n in range(B + 1):
            for k in range(1 if n == 0 else -B, B + 1):
                norm = n * n + n * k + k * k
                re6, im6 = re_im6(n, k)
                if mode == 0:
                    sums0[norm] = sums0.get(norm, 0) + 2 * re6
                else:
                    vs = m1vals(re6, im6)
                    cur = sums1.setdefault(norm, [0] * (M - 1))
                    for i, x in enumerate(vs):
                        cur[i] += x
    for N, s in sums0.items():
        result[0] = add(result[0], rat(s, 64 * N**6))
    for N, vs in sums1.items():
        base = 64 * N**6
        den = base
        for m in range(2, M + 1):
            den *= base
            result[m - 1] = add(result[m - 1], rat(vs[m - 2], den))
    return finalize(result, a), sums0, sums1


def finalize(result: list[tuple[int, int]], a: tuple[int, int]) -> list[tuple[int, int]]:
    out = []
    for m in range(1, M + 1):
        B = 256 if m == 1 else 48
        h = 6 * m
        extra = div(mul(mul(ofint(8), pow_(rat(4, 3), 3 * m)), pow_(ofint(B), 2 - h)), ofint(h - 2))
        r = add(result[m - 1], (-extra[1], extra[1]))
        out.append(mul(mul(r, pow_(a, -h)), inv(ofint(h))))
    return out


def kiv(B: int, n: int, N: int) -> tuple[int, int]:
    klo = 1 if n == 0 else -B
    D = 4 * N - 3 * n * n
    if D <= 0:
        return (1, 0)
    s = isqrt(D - 1)
    a = -((s + n) // 2)
    b = (s - n) // 2
    return (max(a, klo), min(b, B))


def ranges(B: int, n: int, N0: int, N1: int) -> list[tuple[int, int]]:
    a1, b1 = kiv(B, n, N1)
    a0, b0 = kiv(B, n, N0)
    if a1 > b1:
        return []
    if a0 > b0:
        return [(a1, b1)]
    return [r for r in ((a1, a0 - 1), (b0 + 1, b1)) if r[0] <= r[1]]


def band(mode: int, N0: int, N1: int) -> tuple[int, object]:
    B = B0 if mode == 0 else B1
    cnt = 0
    s0: dict[int, int] = {}
    s1: dict[int, list[int]] = {}
    for n in range(B + 1):
        for (ka, kb) in ranges(B, n, N0, N1):
            for k in range(ka, kb + 1):
                cnt += 1
                norm = n * n + n * k + k * k
                assert N0 <= norm < N1
                re6, im6 = re_im6(n, k)
                if mode == 0:
                    s0[norm] = s0.get(norm, 0) + 2 * re6
                else:
                    vs = m1vals(re6, im6)
                    cur = s1.setdefault(norm, [0] * (M - 1))
                    for i, x in enumerate(vs):
                        cur[i] += x
    if mode == 0:
        acc = ZERO
        for N, s in s0.items():
            acc = add(acc, rat(s, 64 * N**6))
        return cnt, acc
    accs = [ZERO] * (M - 1)
    for N, vs in s1.items():
        base = 64 * N**6
        den = base
        for m in range(2, M + 1):
            den *= base
            accs[m - 2] = add(accs[m - 2], rat(vs[m - 2], den))
    return cnt, accs


def make_bands(norm_points: dict[int, int], nmax: int, target: int) -> list[tuple[int, int]]:
    bands, start, acc = [], 1, 0
    for N in range(1, nmax + 1):
        acc += norm_points.get(N, 0)
        if acc >= target:
            bands.append((start, N + 1))
            start, acc = N + 1, 0
    if start <= nmax:
        bands.append((start, nmax + 1))
    return bands


def depth_for(w: int) -> int:
    d = 0
    while (1 << d) < w:
        d += 1
    return d


CORE = r'''import Programmes.SandierSerfaty.Bcons

/-!
# Stage `cs()` of the triangular-minimality certificate (lattice coefficients `c_1..c_38`), level L1

Generated by `results/proposal2/2026-10-26/A1-continuation/scripts/gen_cs.py` (do not edit). Transcribes
`core.hpp:150-172`: for mode 0 (`B = 256`, `m = 1`) and mode 1 (`B = 48`, `m = 2..38`) the exact integers
`2 Re((2n+k + i√3 k)^{6m})` are summed over the box `0 ≤ n ≤ B`, `-B ≤ k ≤ B` (`k ≥ 1` when `n = 0`) **grouped by
the norm** `N = n² + nk + k²`, each group is converted once with `rat(S_N, (64 N⁶)^m)`, the group values are added
(IV addition is exact, so the order of the groups does not matter), and finally
`c_m = (Σ + [-extra, extra]) · a^{-6m} / (6m)` with `extra = 8 (4/3)^{3m} B^{2-6m} / (6m-2)`.

The norms are split into bands `[N0, N1)`. In row `n`, the points with norm `< N` form the k-interval
`|2k + n| ≤ isqrt(4N - 3n² - 1)`, so the points of a band are the outer interval (`N1`) minus the inner one (`N0`),
both clamped to the box; they are grouped in a binary trie on the bits of `N - N0` built by divide and conquer
(recursion depth logarithmic). Each band also returns its point count; `Assemble.lean` checks that the bands tile the
norm range and that the counts add up to the box size.
-/

namespace ProgSandierSerfaty.L1.Cs

open ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV

def re6 (n k : Int) : Int :=
  let ar := 2 * n + k
  let bi := k
  let ar2 := ar * ar
  let bi2 := bi * bi
  ar2 * ar2 * ar2 - 45 * ar2 * ar2 * bi2 + 135 * ar2 * bi2 * bi2 - 27 * bi2 * bi2 * bi2

def im6 (n k : Int) : Int :=
  let ar := 2 * n + k
  let bi := k
  let ar2 := ar * ar
  let bi2 := bi * bi
  6 * ar * ar2 * ar2 * bi - 60 * ar * ar2 * bi * bi2 + 54 * ar * bi * bi2 * bi2

/-- `[2 Re z^m, m = 2..38]` by the C++ recurrence `nr = re re6 - 3 im im6; im = re im6 + im re6; re = nr`. -/
def m1pw : Nat → Int → Int → Int → Int → List Int
  | 0, _, _, _, _ => []
  | f + 1, re, im, r6, i6 =>
    let nr := re * r6 - 3 * im * i6
    let ni := re * i6 + im * r6
    (2 * nr) :: m1pw f nr ni r6 i6

def ptVals (mode : Nat) (n k : Int) : List Int :=
  if mode = 0 then [2 * re6 n k] else
  let r := re6 n k
  let i := im6 n k
  m1pw 37 r i r i

inductive Tr where
  | nil : Tr
  | leaf : Int → List Int → Tr
  | node : Tr → Tr → Tr

def addL : List Int → List Int → List Int
  | a :: as, b :: bs => (a + b) :: addL as bs
  | [], bs => bs
  | as, [] => as

def merge : Nat → Tr → Tr → Tr
  | _, .nil, t => t
  | _, .leaf n a, .nil => .leaf n a
  | _, .leaf n a, .leaf _ b => .leaf n (addL a b)
  | f + 1, .node a b, .node c d => .node (merge f a c) (merge f b d)
  | _, .node a b, .nil => .node a b
  | _, t, _ => t

/-- The trie with the single entry `vals` at key `key` (LSB first, `d` levels), tagged with its norm. -/
def single : Nat → Nat → Int → List Int → Tr
  | 0, _, nrm, vals => .leaf nrm vals
  | d + 1, key, nrm, vals =>
    if key % 2 = 0 then .node (single d (key / 2) nrm vals) .nil else .node .nil (single d (key / 2) nrm vals)

def normOf (n k : Int) : Int := n * n + n * k + k * k

def ptTr (mode d : Nat) (N0 n k : Int) : Tr :=
  let nrm := normOf n k
  single d (nrm - N0).toNat nrm (ptVals mode n k)

/-- Trie of the points `(n, k)`, `k0 ≤ k < k0 + c` (divide and conquer). -/
def rangeTr (mode d : Nat) (N0 n : Int) : Nat → Int → Nat → Tr
  | _, _, 0 => .nil
  | 0, k, _ => ptTr mode d N0 n k
  | f + 1, k, c =>
    if c = 1 then ptTr mode d N0 n k else
    merge d (rangeTr mode d N0 n f k (c / 2)) (rangeTr mode d N0 n f (k + ((c / 2 : Nat) : Int)) (c - c / 2))

/-- `{k ∈ [klo, B] : n² + nk + k² < N}` as `[a, b]` (empty when `a > b`). -/
def kiv (B n N : Int) : Int × Int :=
  let klo := if n = 0 then 1 else -B
  let D := 4 * N - 3 * n * n
  if D ≤ 0 then (1, 0) else
  let s : Int := (IV.isqrt (D - 1).toNat : Int)
  (max (-((s + n) / 2)) klo, min ((s - n) / 2) B)

/-- The k-intervals of row `n` with norm in `[N0, N1)`. -/
def ranges (B n N0 N1 : Int) : List (Int × Int) :=
  let o := kiv B n N1
  let i := kiv B n N0
  if o.2 < o.1 then [] else
  if i.2 < i.1 then [o] else
  ([(o.1, i.1 - 1), (i.2 + 1, o.2)]).filter (fun r => r.1 ≤ r.2)

def rowTr (mode d : Nat) (B N0 N1 n : Int) : Tr × Nat :=
  (ranges B n N0 N1).foldr (fun r acc =>
    let c := (r.2 - r.1 + 1).toNat
    (merge d (rangeTr mode d N0 n 24 r.1 c) acc.1, c + acc.2)) (.nil, 0)

/-- Rows `n0 ≤ n < n0 + c` (divide and conquer). -/
def rowsTr (mode d : Nat) (B N0 N1 : Int) : Nat → Int → Nat → Tr × Nat
  | _, _, 0 => (.nil, 0)
  | 0, n, _ => rowTr mode d B N0 N1 n
  | f + 1, n, c =>
    if c = 1 then rowTr mode d B N0 N1 n else
    let l := rowsTr mode d B N0 N1 f n (c / 2)
    let r := rowsTr mode d B N0 N1 f (n + ((c / 2 : Nat) : Int)) (c - c / 2)
    (merge d l.1 r.1, l.2 + r.2)

def addLI : List IV → List IV → List IV
  | a :: as, b :: bs => add a b :: addLI as bs
  | [], bs => bs
  | as, [] => as

/-- `rat(S_m, base^m)` for `m = 2..38` (`den` starts at `base`, multiplied by `base` before each use). -/
def m1rat : List Int → Int → Int → List IV
  | [], _, _ => []
  | s :: ss, base, den => rat s (den * base) :: m1rat ss base (den * base)

def trSum (mode : Nat) : Tr → List IV
  | .nil => []
  | .leaf nrm vals =>
    let base := 64 * (nrm * nrm * nrm * nrm * nrm * nrm)
    if mode = 0 then (match vals with | s :: _ => [rat s base] | [] => []) else m1rat vals base base
  | .node a b => addLI (trSum mode a) (trSum mode b)

/-- Band `[N0, N1)` of mode `mode`: (point count, group sums). -/
def bandVal (mode d : Nat) (N0 N1 : Int) : Nat × List IV :=
  let B : Int := if mode = 0 then 256 else 48
  let r := rowsTr mode d B N0 N1 24 0 (B + 1).toNat
  (r.2, trSum mode r.1)

/-- The final scaling `core.hpp:170`. `res` = mode-0 sum (m = 1) followed by the mode-1 sums (m = 2..38). -/
def finalize (aI : IV) : Nat → List IV → List IV
  | _, [] => []
  | m, r :: rs =>
    let B : Int := if m = 1 then 256 else 48
    let h : Nat := 6 * m
    let extra := div (mul (mul (ofInt 8) (powI (rat 4 3) (3 * m))) (IV.inv (powI (ofInt B) (h - 2)))) (ofInt ((h : Int) - 2))
    mul (mul (add r ⟨-extra.v, extra.v⟩) (IV.inv (powI aI h))) (IV.inv (ofInt (h : Int))) :: finalize aI (m + 1) rs

/-- Bands tile `[lo, hi)` in order. -/
def tiles : Int → Int → List (Int × Int) → Bool
  | lo, hi, [] => decide (lo = hi)
  | lo, hi, b :: bs => decide (b.1 = lo) && decide (b.1 < b.2) && tiles b.2 hi bs

def sumIV : List IV → IV
  | [] => ofInt 0
  | a :: as => add a (sumIV as)

def sumLI : List (List IV) → List IV
  | [] => []
  | a :: as => addLI a (sumLI as)

end ProgSandierSerfaty.L1.Cs
'''


def lean_list_iv(xs: list[tuple[int, int]]) -> str:
    return "[" + ",\n    ".join(lit(x) for x in xs) + "]"


def main() -> int:
    sc = load_scalars(OLD_DUMP)
    a = sc["a"]
    co_cpp = [sc[f"co{m}"] for m in range(1, M + 1)]
    res, sums0, sums1 = brute(a)
    if res != co_cpp:
        bad = [m + 1 for m in range(M) if res[m] != co_cpp[m]]
        print("BRUTE MISMATCH at m =", bad)
        return 1
    print("brute-force cs mirror == C++ co[1..38]")
    pts0: dict[int, int] = {}
    pts1: dict[int, int] = {}
    for mode, B, d in ((0, B0, pts0), (1, B1, pts1)):
        for n in range(B + 1):
            for k in range(1 if n == 0 else -B, B + 1):
                N = n * n + n * k + k * k
                d[N] = d.get(N, 0) + 1
    target0 = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    target1 = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    bands0 = make_bands(pts0, 3 * B0 * B0, target0)
    bands1 = make_bands(pts1, 3 * B1 * B1, target1)
    out0, out1 = [], []
    tot0 = ZERO
    for (N0, N1) in bands0:
        c, v = band(0, N0, N1)
        out0.append((N0, N1, c, v))
        tot0 = add(tot0, v)
    tot1 = [ZERO] * (M - 1)
    for (N0, N1) in bands1:
        c, v = band(1, N0, N1)
        out1.append((N0, N1, c, v))
        tot1 = [add(x, y) for x, y in zip(tot1, v)]
    assert sum(o[2] for o in out0) == sum(pts0.values()) == 131584
    assert sum(o[2] for o in out1) == sum(pts1.values()) == 4704
    fin = finalize([tot0] + tot1, a)
    if fin != co_cpp:
        print("BAND MISMATCH")
        return 1
    print(f"band formulation == C++ co: {len(bands0)} mode-0 bands, {len(bands1)} mode-1 bands")
    csdir = L1DIR / "Cs"
    csdir.mkdir(parents=True, exist_ok=True)
    (csdir / "Core.lean").write_text(CORE)
    chunks = []
    hdr = "import Programmes.SandierSerfatyL1.Cs.Core\n\nnamespace ProgSandierSerfaty.L1.Cs\n\nopen ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV\n\n"
    for mode, outs in ((0, out0), (1, out1)):
        for idx, (N0, N1, c, v) in enumerate(outs):
            d = depth_for(N1 - N0)
            vals = [v] if mode == 0 else v
            name = f"M{mode}B{idx:03d}"
            body = (f"/-- cs mode {mode}, norms [{N0}, {N1}): {c} points. Generated by gen_cs.py. -/\n"
                    f"def {name.lower()}_lit : Nat × List IV := ({c}, {lean_list_iv(vals)})\n\n"
                    f"set_option maxRecDepth 100000 in\n"
                    f"theorem band_{name.lower()} : bandVal {mode} {d} {N0} {N1} = {name.lower()}_lit := by decide +kernel\n\n"
                    f"#print axioms band_{name.lower()}\n\n"
                    "end ProgSandierSerfaty.L1.Cs\n")
            f = csdir / f"{name}.lean"
            f.write_text(hdr + body)
            chunks.append({"id": f"cs/{name}", "stage": "cs", "kind": "chunk", "file": str(f.relative_to(L1DIR.parents[1])),
                           "module": f"Programmes.SandierSerfatyL1.Cs.{name}", "deps": ["Programmes.SandierSerfatyL1.Cs.Core"],
                           "ops_hint": c * (1 if mode == 0 else 40), "order": c * (1 if mode == 0 else 40)})
    # planted false chunks: last bit of the first mode-0 band, and the count of the first mode-1 band
    for (mode, idx, kind) in ((0, 0, "ulp"), (1, 0, "count")):
        N0, N1, c, v = (out0 if mode == 0 else out1)[idx]
        d = depth_for(N1 - N0)
        vals = [v] if mode == 0 else list(v)
        if kind == "ulp":
            vals[0] = (vals[0][0] + 1, vals[0][1])
        else:
            c = c + 1
        name = f"PlantM{mode}B{idx:03d}{kind.capitalize()}"
        body = (f"/-- PLANTED FALSE (must be rejected by the kernel): band [{N0}, {N1}) of mode {mode} with "
                f"{'the lower endpoint + 1 ulp' if kind == 'ulp' else 'the point count + 1'}. -/\n"
                f"def plant_lit : Nat × List IV := ({c}, {lean_list_iv(vals)})\n\n"
                f"set_option maxRecDepth 100000 in\n"
                f"/-- The honest refutation (must compile). -/\n"
                f"theorem plant_refuted : bandVal {mode} {d} {N0} {N1} ≠ plant_lit := by decide +kernel\n\n"
                "#print axioms plant_refuted\n\n"
                f"set_option maxRecDepth 100000 in\n"
                f"/-- The planted claim (must be rejected: exactly one error, here). -/\n"
                f"theorem plant_claim : bandVal {mode} {d} {N0} {N1} = plant_lit := by decide +kernel\n\n"
                "end ProgSandierSerfaty.L1.Cs\n")
        f = csdir / f"{name}.lean"
        f.write_text(hdr + body)
        chunks.append({"id": f"cs/{name}", "stage": "cs", "kind": "planted", "file": str(f.relative_to(L1DIR.parents[1])),
                       "module": f"Programmes.SandierSerfatyL1.Cs.{name}", "deps": ["Programmes.SandierSerfatyL1.Cs.Core"],
                       "ops_hint": 1, "order": 10**9 + idx})
    # assembly: tiling, counts, final scaling = coList (C++ co[1..38] in Bcons.lean); imports every band chunk
    imps = "\n".join(f"import Programmes.SandierSerfatyL1.Cs.M{mo}B{i:03d}" for mo, outs in ((0, out0), (1, out1)) for i in range(len(outs)))
    b0 = ", ".join(f"({o[0]}, {o[1]})" for o in out0)
    b1 = ", ".join(f"({o[0]}, {o[1]})" for o in out1)
    l0 = ", ".join(f"m0b{i:03d}_lit" for i in range(len(out0)))
    l1 = ", ".join(f"m1b{i:03d}_lit" for i in range(len(out1)))
    conj = " ∧\n    ".join([f"bandVal 0 {depth_for(o[1]-o[0])} {o[0]} {o[1]} = m0b{i:03d}_lit" for i, o in enumerate(out0)] +
                          [f"bandVal 1 {depth_for(o[1]-o[0])} {o[0]} {o[1]} = m1b{i:03d}_lit" for i, o in enumerate(out1)])
    proofs = ", ".join([f"band_m0b{i:03d}" for i in range(len(out0))] + [f"band_m1b{i:03d}" for i in range(len(out1))])
    asm = (imps + "\n\n/-! # Assembly of the `cs` stage (L1). Generated by gen_cs.py (do not edit). -/\n\n"
           "namespace ProgSandierSerfaty.L1.Cs\n\nopen ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV\n\n"
           f"def bands0 : List (Int × Int) := [{b0}]\ndef bands1 : List (Int × Int) := [{b1}]\n"
           f"def lits0 : List (Nat × List IV) := [{l0}]\ndef lits1 : List (Nat × List IV) := [{l1}]\n\n"
           "/-- The mode-0 bands tile `[1, 3·256²]` and the mode-1 bands `[1, 3·48²]` (every box norm is ≥ 1 and ≤ 3B²). -/\n"
           f"theorem cs_tiles : tiles 1 {3*B0*B0+1} bands0 = true ∧ tiles 1 {3*B1*B1+1} bands1 = true := by decide +kernel\n\n"
           "/-- The band point counts add up to the box sizes `256 + 256·513` and `48 + 48·97`. -/\n"
           "theorem cs_counts : (lits0.map Prod.fst).sum = 131584 ∧ (lits1.map Prod.fst).sum = 4704 := by decide +kernel\n\n"
           "set_option maxRecDepth 100000 in\n"
           "/-- The band sums, scaled as in `core.hpp:170`, give exactly the C++ `co[1..38]` (= `coList`, Bcons.lean). -/\n"
           "theorem cs_final : finalize aC 1 (sumIV (lits0.map (fun x => sumIV x.2)) :: sumLI (lits1.map Prod.snd)) = coList := by\n"
           "  decide +kernel\n\n"
           "/-- Stage `cs`, L1: every band chunk theorem and the assembly. -/\n"
           f"theorem cs_stage : ({conj}) ∧\n    finalize aC 1 (sumIV (lits0.map (fun x => sumIV x.2)) :: sumLI (lits1.map Prod.snd)) = coList :=\n"
           f"  ⟨⟨{proofs}⟩, cs_final⟩\n\n#print axioms cs_tiles\n#print axioms cs_counts\n#print axioms cs_final\n#print axioms cs_stage\n\nend ProgSandierSerfaty.L1.Cs\n")
    fa = csdir / "Assemble.lean"
    fa.write_text(asm)
    chunks.append({"id": "cs/Assemble", "stage": "cs", "kind": "assemble", "file": str(fa.relative_to(L1DIR.parents[1])),
                   "module": "Programmes.SandierSerfatyL1.Cs.Assemble",
                   "deps": ["Programmes.SandierSerfatyL1.Cs.Core"] + [c["module"] for c in chunks if c["kind"] == "chunk"],
                   "ops_hint": 1, "order": 2 * 10**9})
    (CONT / "manifests").mkdir(parents=True, exist_ok=True)
    (CONT / "manifests" / "cs.json").write_text(json.dumps({"stage": "cs", "core": [{"module": "Programmes.SandierSerfatyL1.Cs.Core",
        "file": "Programmes/SandierSerfatyL1/Cs/Core.lean"}], "chunks": chunks,
        "inputs": {"old_dump_sha256": sha256(OLD_DUMP)}}, indent=1))
    print(f"wrote {len(chunks)} chunk entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
