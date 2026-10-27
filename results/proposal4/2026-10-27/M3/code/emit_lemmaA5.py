"""Emit formal_cert/Programmes/YukawaBccFcc/LemmaA5.lean: untrusted dyadic chain tables + kernel checks + the
real-number statements of Luo-Wei Lemma A.5 (A.6), (A.7), (A.8) and the finite constants of Lemma 6.1's proof.

Every Lean `decide +kernel` check is first mirrored here in exact Fraction arithmetic (so a failing table is caught
before Lean), but the Lean kernel is the judge.

usage: python -I emit_lemmaA5.py OUT.lean [--tamper-cell]   (--tamper-cell writes a control with 3/1000 -> 4/1000 ... see code)
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from pathlib import Path

P = 52
DEN = 2 ** P
NTERMS = 30

NTAB = {1: 12, 2: 6, 3: 24, 4: 12, 5: 24, 6: 8, 7: 48, 8: 6, 9: 36, 10: 24, 11: 24, 12: 24}
MTAB = {3: 8, 4: 6, 8: 12, 11: 24, 12: 8, 16: 6, 19: 24, 20: 24, 24: 24, 27: 32, 32: 12, 35: 48, 36: 30, 40: 24,
        43: 24, 44: 24, 48: 8}

PI_LO = F(314159265358979323846, 10 ** 20)
PI_HI = F(314159265358979323847, 10 ** 20)


def int_cbrt_bracket(x: F, digits: int) -> tuple[F, F]:
    s = 10 ** digits
    t = x * s ** 3
    # exact integer cube root by Newton on integers
    n = t.numerator // t.denominator
    r = int(round(n ** (1 / 3))) if n < 10 ** 300 else 1 << (n.bit_length() // 3)
    for _ in range(400):
        r2 = (2 * r + n // (r * r)) // 3
        if r2 == r:
            break
        r = r2
    while (r + 1) ** 3 <= t:
        r += 1
    while r ** 3 > t:
        r -= 1
    rlo, rhi = F(r, s), F(r + 1, s)
    assert rlo ** 3 < x < rhi ** 3
    return rlo, rhi


R_LO, R_HI = int_cbrt_bracket(F(2), 20)
S_LO, S_HI = int_cbrt_bracket(F(1, 16), 20)
PA_LO, PA_HI = PI_LO * R_LO, PI_HI * R_HI
PB_LO, PB_HI = PI_LO * S_LO, PI_HI * S_HI


def exp_sum(t: F, n: int) -> F:
    s = F(0)
    term = F(1)
    for m in range(n):
        if m > 0:
            term = term * t / m
        s += term
    return s


def exp_rem(t: F, n: int) -> F:
    return abs(t) ** n * (F(n + 1) / (math.factorial(n) * n))


def e_ok(z: F, n: int) -> bool:
    return n > 0 and abs(z / 8) <= 1 and exp_sum(z / 8, n) - exp_rem(z / 8, n) >= 0


def e_lo(z: F, n: int) -> F:
    return (exp_sum(z / 8, n) - exp_rem(z / 8, n)) ** 8


def e_hi(z: F, n: int) -> F:
    return (exp_sum(z / 8, n) + exp_rem(z / 8, n)) ** 8


def floor_dy(x: F) -> int:
    return (x.numerator * DEN) // x.denominator


def ceil_dy(x: F) -> int:
    return -((-x.numerator * DEN) // x.denominator)


def dy(k: int) -> F:
    return F(k, DEN)


def chain_lo(z0: F, zh: F, length: int) -> tuple[list[int], int]:
    assert e_ok(z0, NTERMS) and e_ok(zh, NTERMS)
    s = floor_dy(e_lo(zh, NTERMS))
    out = [floor_dy(e_lo(z0, NTERMS))]
    for _ in range(length - 1):
        out.append(floor_dy(dy(out[-1]) * dy(s)))
    return out, s


def chain_hi(z0: F, zh: F, length: int) -> tuple[list[int], int]:
    assert e_ok(z0, NTERMS) and e_ok(zh, NTERMS)
    s = ceil_dy(e_hi(zh, NTERMS))
    out = [ceil_dy(e_hi(z0, NTERMS))]
    for _ in range(length - 1):
        out.append(ceil_dy(dy(out[-1]) * dy(s)))
    return out, s


def pol(w: str, tab: dict[int, int], q: F) -> F:
    return sum((F(n if w == "id" else 1) * c * q ** n for n, c in tab.items()), F(0))


def lean_list(name: str, vals: list[int]) -> str:
    chunks = [vals[i:i + 128] for i in range(0, len(vals), 128)]
    body = " ++\n  ".join("[" + ", ".join(str(v) for v in ch) + "]" for ch in chunks)
    return f"set_option maxRecDepth 100000 in\ndef {name} : List ℕ :=\n  {body}\n"


def lit(x: F) -> str:
    return f"({x.numerator} / {x.denominator} : ℚ)"


def main() -> int:
    out = Path(sys.argv[1])
    # chains
    c1, s1 = chain_lo(-PA_HI * 1, -PA_HI * F(1, 10000), 1001)        # FCC lower, t = 1 + k/10000
    c2, s2 = chain_hi(-PB_LO * 1, -PB_LO * F(1, 10000), 1001)        # BCC upper, t = 1 + k/10000
    c3, s3 = chain_lo(-PB_HI * F(11, 10), -PB_HI * F(1, 2000), 2001)  # BCC lower, t = 11/10 + k/2000
    c4, s4 = chain_hi(-PA_LO * F(11, 10), -PA_LO * F(1, 2000), 2001)  # FCC upper, t = 11/10 + k/2000
    # mirror the cell checks
    eps = F(1, 10 ** 18)
    min6 = min(PA_LO * pol("id", NTAB, dy(c1[j + 1])) - PB_HI * pol("id", MTAB, dy(c2[j])) - eps - F(3, 1000)
               for j in range(1000))
    min7 = min(pol("one", MTAB, dy(c3[j + 1])) - pol("one", NTAB, dy(c4[j])) - eps - F(1, 10000) for j in range(2000))
    assert min6 > 0 and min7 > 0, (float(min6), float(min7))
    z8 = (PA_LO - 3 * PB_HI) * F(21, 10)
    assert e_ok(z8, NTERMS) and 8 * e_lo(z8, NTERMS) > F(25, 2)
    print("rational slack A6", float(min6), "A7", float(min7), "A8", float(8 * e_lo(z8, NTERMS) - F(25, 2)))
    tamper = "--tamper-cell" in sys.argv
    hdr = "import Programmes.YukawaBccFcc.Basic\n" if not tamper else "import Programmes.YukawaBccFcc.LemmaA5\n"
    if tamper:
        # Reject control: the A.7 margin raised from 1/10000 to 1/1000 at every cell must FAIL in the kernel
        # (the true minimum slack is ~7.6e-5 + 1e-4, so cell 0 violates it).
        txt = hdr + """
namespace YukawaBccFcc

/-! REJECT control (must fail to compile): Lemma A.5 (A.7) cell table with a tampered margin 1/1000. -/
def cellA7bad (j : ℕ) : Bool :=
  decide (0 ≤ C3.getD (j + 1) 0) &&
  decide ((1 / 1000 : ℚ) < polQ (fun _ => 1) Mtab 48 (C3.getD (j + 1) 0) - polQ (fun _ => 1) Ntab 12 (C4.getD j 0)
    - 1 / 10 ^ 18)

theorem cellA7bad_0 : cellA7bad 0 = true := by decide +kernel

end YukawaBccFcc
"""
        out.write_text(txt)
        return 0
    ntab_lines = "\n".join(f"  | {n} => {c}" for n, c in NTAB.items())
    mtab_lines = "\n".join(f"  | {n} => {c}" for n, c in MTAB.items())
    mk = list(MTAB.keys())
    mv = list(MTAB.values())
    txt = hdr + f"""
/-!
# M3: Luo–Wei (arXiv 2610.31456) Lemma A.5 and the finite constants of Lemma 6.1, kernel-checked

Generated by `results/proposal4/2026-10-27/M3/code/emit_lemmaA5.py`. The tables `C1n … C4n` are untrusted dyadic
numerators (denominator `2^{P}`); the kernel checks every chain step, every cell and every constant with
`decide +kernel`. No `sorry`, no `native_decide`, no new axioms.

Main statements (paper notation `a² = 2^{{1/3}}`, `π 2^{{-4/3}}`):
* `fcc_multiplicities`, `bcc_multiplicities`: the shell counts printed in the proof of Lemma A.5 (kernel-enumerated).
* `lemmaA5_A6`  : (A.6) for every integer `0 ≤ j < 1000`.
* `lemmaA5_A7`  : (A.7) for every integer `0 ≤ j < 2000`.
* `lemmaA5_A8`  : (A.8).
* `lemma61_*`   : the numerical constants used in the proof of Lemma 6.1, the Prop. 4.1 bracket at `x ≤ 1/128`, and
  the two omitted-tail sums (as bounds on every partial sum).
* `lemmaA6_tail`: the rational tail bound printed in the proof of Lemma A.6.
NOT formalised: theta functions, Poisson summation, `D(1) = 0`, the derivative argument, hence Lemma 6.1 itself.
-/

namespace YukawaBccFcc

open Finset

def Ntab : ℕ → ℕ
{ntab_lines}
  | _ => 0

def Mtab : ℕ → ℕ
{mtab_lines}
  | _ => 0

theorem Nc_tab : ∀ n ∈ Icc 1 12, Nc n = Ntab n := by decide +kernel

theorem Mc_tab : ∀ l ∈ Icc 1 48, Mc l = Mtab l := by decide +kernel

/-- `(N_1, …, N_12)` as printed in the proof of Lemma A.5. -/
theorem fcc_multiplicities :
    (List.range 12).map (fun i => Nc (i + 1)) = {list(NTAB.values())} := by decide +kernel

/-- The nonzero BCC indices `l ≤ 48` and their multiplicities `M_l`, as printed in the proof of Lemma A.5. -/
theorem bcc_multiplicities :
    ((List.range 48).map (· + 1)).filter (fun l => Mc l ≠ 0) = {mk} ∧
      ({mk} : List ℕ).map Mc = {mv} := by decide +kernel

/-! ## Constants -/

def rLo : ℚ := {lit(R_LO)}
def rHi : ℚ := {lit(R_HI)}
def sLo : ℚ := {lit(S_LO)}
def sHi : ℚ := {lit(S_HI)}
def paLo : ℚ := piLo * rLo
def paHi : ℚ := piHi * rHi
def pbLo : ℚ := piLo * sLo
def pbHi : ℚ := piHi * sHi

lemma a2_br : (rLo : ℝ) < a2 ∧ a2 < (rHi : ℝ) :=
  a2_mem rLo rHi (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel)

lemma b2_br : (sLo : ℝ) < b2 ∧ b2 < (sHi : ℝ) :=
  b2_mem sLo sHi (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel)

lemma pa_mem : ((paLo : ℚ) : ℝ) ≤ Real.pi * a2 ∧ Real.pi * a2 ≤ ((paHi : ℚ) : ℝ) :=
  mul_mem (by decide +kernel) (by decide +kernel) pi_mem a2_br

lemma pb_mem : ((pbLo : ℚ) : ℝ) ≤ Real.pi * b2 ∧ Real.pi * b2 ≤ ((pbHi : ℚ) : ℝ) :=
  mul_mem (by decide +kernel) (by decide +kernel) pi_mem b2_br

lemma pa_pos : 0 < Real.pi * a2 := mul_pos Real.pi_pos a2_pos

lemma pb_pos : 0 < Real.pi * b2 := mul_pos Real.pi_pos b2_pos

/-! ## Chains -/

def dy (k : ℕ) : ℚ := (k : ℚ) / 2 ^ {P}

{lean_list("C1n", c1)}
{lean_list("C2n", c2)}
{lean_list("C3n", c3)}
{lean_list("C4n", c4)}
def C1 : List ℚ := C1n.map dy
def C2 : List ℚ := C2n.map dy
def C3 : List ℚ := C3n.map dy
def C4 : List ℚ := C4n.map dy

def s1 : ℚ := dy {s1}
def s2 : ℚ := dy {s2}
def s3 : ℚ := dy {s3}
def s4 : ℚ := dy {s4}

theorem C1_ok : chainLo s1 C1 = true := by decide +kernel
theorem C2_ok : chainHi s2 C2 = true := by decide +kernel
theorem C3_ok : chainLo s3 C3 = true := by decide +kernel
theorem C4_ok : chainHi s4 C4 = true := by decide +kernel

theorem C_len : C1.length = 1001 ∧ C2.length = 1001 ∧ C3.length = 2001 ∧ C4.length = 2001 := by decide +kernel

theorem eOK_all : eOK (-paHi * 1) {NTERMS} = true ∧ eOK (-paHi * (1 / 10000)) {NTERMS} = true ∧
    eOK (-pbLo * 1) {NTERMS} = true ∧ eOK (-pbLo * (1 / 10000)) {NTERMS} = true ∧
    eOK (-pbHi * (11 / 10)) {NTERMS} = true ∧ eOK (-pbHi * (1 / 2000)) {NTERMS} = true ∧
    eOK (-paLo * (11 / 10)) {NTERMS} = true ∧ eOK (-paLo * (1 / 2000)) {NTERMS} = true := by decide +kernel

theorem heads_ok :
    (0 ≤ C1.headD 0 ∧ C1.headD 0 ≤ eLo (-paHi * 1) {NTERMS}) ∧ (0 ≤ s1 ∧ s1 ≤ eLo (-paHi * (1 / 10000)) {NTERMS}) ∧
    (eHi (-pbLo * 1) {NTERMS} ≤ C2.headD 0) ∧ (eHi (-pbLo * (1 / 10000)) {NTERMS} ≤ s2) ∧
    (0 ≤ C3.headD 0 ∧ C3.headD 0 ≤ eLo (-pbHi * (11 / 10)) {NTERMS}) ∧
      (0 ≤ s3 ∧ s3 ≤ eLo (-pbHi * (1 / 2000)) {NTERMS}) ∧
    (eHi (-paLo * (11 / 10)) {NTERMS} ≤ C4.headD 0) ∧ (eHi (-paLo * (1 / 2000)) {NTERMS} ≤ s4) := by decide +kernel

/-- Generic lower-chain bound: entry `k` is below `exp(-p (t₀ + k h))`. -/
lemma chain_lo_bound {{p : ℝ}} {{ph t0 h s : ℚ}} {{C : List ℚ}} (hp : p ≤ ph) (ht0 : 0 ≤ t0) (hh : 0 ≤ h)
    (hok : chainLo s C = true) (e0 : eOK (-ph * t0) {NTERMS} = true) (eh : eOK (-ph * h) {NTERMS} = true)
    (hd0 : 0 ≤ C.headD 0) (hd1 : C.headD 0 ≤ eLo (-ph * t0) {NTERMS}) (hs1 : s ≤ eLo (-ph * h) {NTERMS})
    (k : ℕ) (hk : k < C.length) :
    ((C.getD k 0 : ℚ) : ℝ) ≤ Real.exp (-p * ((t0 : ℝ) + k * (h : ℝ))) := by
  have hs : (s : ℝ) ≤ Real.exp (-p * (h : ℝ)) :=
    le_trans (by exact_mod_cast hs1) (exp_neg_lo {NTERMS} hp hh eh)
  have hx : ((C.headD 0 : ℚ) : ℝ) ≤ Real.exp (-p * (t0 : ℝ)) :=
    le_trans (by exact_mod_cast hd1) (exp_neg_lo {NTERMS} hp ht0 e0)
  have := chainLo_sound s _ (Real.exp_pos _).le hs C _ hok hd0 hx k hk
  rwa [geom_exp] at this

/-- Generic upper-chain bound: entry `k` is above `exp(-p (t₀ + k h))`. -/
lemma chain_hi_bound {{p : ℝ}} {{pl t0 h S : ℚ}} {{C : List ℚ}} (hp : (pl : ℝ) ≤ p) (ht0 : 0 ≤ t0) (hh : 0 ≤ h)
    (hok : chainHi S C = true) (e0 : eOK (-pl * t0) {NTERMS} = true) (eh : eOK (-pl * h) {NTERMS} = true)
    (hd1 : eHi (-pl * t0) {NTERMS} ≤ C.headD 0) (hs1 : eHi (-pl * h) {NTERMS} ≤ S)
    (k : ℕ) (hk : k < C.length) :
    Real.exp (-p * ((t0 : ℝ) + k * (h : ℝ))) ≤ ((C.getD k 0 : ℚ) : ℝ) := by
  have hs : Real.exp (-p * (h : ℝ)) ≤ (S : ℝ) :=
    le_trans (exp_neg_hi {NTERMS} hp hh eh) (by exact_mod_cast hs1)
  have hx : Real.exp (-p * (t0 : ℝ)) ≤ ((C.headD 0 : ℚ) : ℝ) :=
    le_trans (exp_neg_hi {NTERMS} hp ht0 e0) (by exact_mod_cast hd1)
  have := chainHi_sound S _ (Real.exp_pos _).le hs C _ hok (Real.exp_pos _).le hx k hk
  rwa [geom_exp] at this

/-! ## (A.6) -/

/-- `allFrom f a n` checks `f a, …, f (a + n - 1)`. -/
def allFrom (f : ℕ → Bool) (a : ℕ) : ℕ → Bool
  | 0 => true
  | n + 1 => f (a + n) && allFrom f a n

theorem allFrom_sound (f : ℕ → Bool) (a : ℕ) :
    ∀ n, allFrom f a n = true → ∀ j, a ≤ j → j < a + n → f j = true := by
  intro n
  induction n with
  | zero => intro _ j h1 h2; omega
  | succ n ih =>
    intro h j h1 h2
    simp only [allFrom, Bool.and_eq_true] at h
    by_cases hj : j = a + n
    · rw [hj]; exact h.1
    · exact ih h.2 j h1 (by omega)

theorem blocks_sound (f : ℕ → Bool) (N : ℕ) (h : ∀ k < N, allFrom f (100 * k) 100 = true) :
    ∀ j < 100 * N, f j = true := by
  intro j hj
  exact allFrom_sound f (100 * (j / 100)) 100 (h (j / 100) (by omega)) j (by omega) (by omega)

def cellA6 (j : ℕ) : Bool :=
  decide (0 ≤ C1.getD (j + 1) 0) &&
  decide ((3 / 1000 : ℚ) < paLo * polQ (fun n => n) Ntab 12 (C1.getD (j + 1) 0)
    - pbHi * polQ (fun n => n) Mtab 48 (C2.getD j 0) - 1 / 10 ^ 18)

theorem cellsA6_b0 : allFrom cellA6 (100 * 0) 100 = true := by decide +kernel

theorem cellsA6_b1 : allFrom cellA6 (100 * 1) 100 = true := by decide +kernel

theorem cellsA6_b2 : allFrom cellA6 (100 * 2) 100 = true := by decide +kernel

theorem cellsA6_b3 : allFrom cellA6 (100 * 3) 100 = true := by decide +kernel

theorem cellsA6_b4 : allFrom cellA6 (100 * 4) 100 = true := by decide +kernel

theorem cellsA6_b5 : allFrom cellA6 (100 * 5) 100 = true := by decide +kernel

theorem cellsA6_b6 : allFrom cellA6 (100 * 6) 100 = true := by decide +kernel

theorem cellsA6_b7 : allFrom cellA6 (100 * 7) 100 = true := by decide +kernel

theorem cellsA6_b8 : allFrom cellA6 (100 * 8) 100 = true := by decide +kernel

theorem cellsA6_b9 : allFrom cellA6 (100 * 9) 100 = true := by decide +kernel


theorem cellsA6 : ∀ j < 100 * 10, cellA6 j = true := by
  apply blocks_sound
  intro k hk
  interval_cases k
  · exact cellsA6_b0
  · exact cellsA6_b1
  · exact cellsA6_b2
  · exact cellsA6_b3
  · exact cellsA6_b4
  · exact cellsA6_b5
  · exact cellsA6_b6
  · exact cellsA6_b7
  · exact cellsA6_b8
  · exact cellsA6_b9

/-- **Lemma A.5, inequality (A.6)** of Luo–Wei, for every integer `0 ≤ j < 1000`. -/
theorem lemmaA5_A6 (j : ℕ) (hj : j < 1000) :
    Real.pi * a2 * ∑ n ∈ Icc (1 : ℕ) 12, (n : ℝ) * (Nc n : ℝ) *
        Real.exp (-(Real.pi * a2) * n * (1 + ((j : ℝ) + 1) / 10000))
      - Real.pi * b2 * ∑ l ∈ Icc (1 : ℕ) 48, (l : ℝ) * (Mc l : ℝ) *
        Real.exp (-(Real.pi * b2) * l * (1 + (j : ℝ) / 10000))
      - 1 / 10 ^ 18 > 3 / 1000 := by
  have hc := cellsA6 j (by omega)
  simp only [cellA6, Bool.and_eq_true, decide_eq_true_eq] at hc
  obtain ⟨h0, hc⟩ := hc
  have hcR : ((3 / 1000 : ℚ) : ℝ) < ((paLo * polQ (fun n => n) Ntab 12 (C1.getD (j + 1) 0)
      - pbHi * polQ (fun n => n) Mtab 48 (C2.getD j 0) - 1 / 10 ^ 18 : ℚ) : ℝ) := by exact_mod_cast hc
  simp only [Rat.cast_sub, Rat.cast_mul, polQ_cast] at hcR
  have e1 : ∑ n ∈ Icc (1 : ℕ) 12, (n : ℝ) * (Nc n : ℝ) * Real.exp (-(Real.pi * a2) * n * (1 + ((j : ℝ) + 1) / 10000))
      = polR (fun n => n) Nc 12 (Real.exp (-(Real.pi * a2) * (1 + ((j : ℝ) + 1) / 10000))) :=
    shell_sum_eq (fun n => n) Nc 12 _ _
  have e2 : ∑ l ∈ Icc (1 : ℕ) 48, (l : ℝ) * (Mc l : ℝ) * Real.exp (-(Real.pi * b2) * l * (1 + (j : ℝ) / 10000))
      = polR (fun n => n) Mc 48 (Real.exp (-(Real.pi * b2) * (1 + (j : ℝ) / 10000))) :=
    shell_sum_eq (fun n => n) Mc 48 _ _
  rw [e1, e2, polR_congr _ Nc Ntab 12 Nc_tab, polR_congr _ Mc Mtab 48 Mc_tab]
  have hX := chain_lo_bound (p := Real.pi * a2) pa_mem.2 (by decide +kernel) (by decide +kernel) C1_ok eOK_all.1
    eOK_all.2.1 heads_ok.1.1 heads_ok.1.2 heads_ok.2.1.2 (j + 1) (by rw [C_len.1]; omega)
  have hY := chain_hi_bound (p := Real.pi * b2) pb_mem.1 (by decide +kernel) (by decide +kernel) C2_ok
    eOK_all.2.2.1 eOK_all.2.2.2.1 heads_ok.2.2.1 heads_ok.2.2.2.1 j (by rw [C_len.2.1]; omega)
  have tX : ((1 : ℚ) : ℝ) + ((j + 1 : ℕ) : ℝ) * ((1 / 10000 : ℚ) : ℝ) = 1 + ((j : ℝ) + 1) / 10000 := by
    push_cast; ring
  have tY : ((1 : ℚ) : ℝ) + ((j : ℕ) : ℝ) * ((1 / 10000 : ℚ) : ℝ) = 1 + (j : ℝ) / 10000 := by
    push_cast; ring
  rw [tX] at hX
  rw [tY] at hY
  have h0' : (0 : ℝ) ≤ ((C1.getD (j + 1) 0 : ℚ) : ℝ) := by exact_mod_cast h0
  have hF := polR_mono (fun n => n) Ntab 12 h0' hX
  have hB := polR_mono (fun n => n) Mtab 48 (Real.exp_pos _).le hY
  have hpa : ((paLo : ℚ) : ℝ) ≤ Real.pi * a2 := pa_mem.1
  have hpb : Real.pi * b2 ≤ ((pbHi : ℚ) : ℝ) := pb_mem.2
  have hpaLo0 : (0 : ℝ) ≤ ((paLo : ℚ) : ℝ) := by exact_mod_cast (show (0 : ℚ) ≤ paLo by decide +kernel)
  have hF0 := polR_nonneg (fun n => n) Ntab 12 h0'
  have hB0 := polR_nonneg (fun n => n) Mtab 48 (Real.exp_pos (-(Real.pi * b2) * (1 + (j : ℝ) / 10000))).le
  have m1 : ((paLo : ℚ) : ℝ) * polR (fun n => n) Ntab 12 ((C1.getD (j + 1) 0 : ℚ) : ℝ) ≤
      Real.pi * a2 * polR (fun n => n) Ntab 12 (Real.exp (-(Real.pi * a2) * (1 + ((j : ℝ) + 1) / 10000))) :=
    mul_le_mul hpa hF hF0 pa_pos.le
  have m2 : Real.pi * b2 * polR (fun n => n) Mtab 48 (Real.exp (-(Real.pi * b2) * (1 + (j : ℝ) / 10000))) ≤
      ((pbHi : ℚ) : ℝ) * polR (fun n => n) Mtab 48 ((C2.getD j 0 : ℚ) : ℝ) :=
    mul_le_mul hpb hB hB0 (pb_pos.le.trans hpb)
  push_cast at hcR
  linarith

/-! ## (A.7) -/

def cellA7 (j : ℕ) : Bool :=
  decide (0 ≤ C3.getD (j + 1) 0) &&
  decide ((1 / 10000 : ℚ) < polQ (fun _ => 1) Mtab 48 (C3.getD (j + 1) 0) - polQ (fun _ => 1) Ntab 12 (C4.getD j 0)
    - 1 / 10 ^ 18)

theorem cellsA7_b0 : allFrom cellA7 (100 * 0) 100 = true := by decide +kernel

theorem cellsA7_b1 : allFrom cellA7 (100 * 1) 100 = true := by decide +kernel

theorem cellsA7_b2 : allFrom cellA7 (100 * 2) 100 = true := by decide +kernel

theorem cellsA7_b3 : allFrom cellA7 (100 * 3) 100 = true := by decide +kernel

theorem cellsA7_b4 : allFrom cellA7 (100 * 4) 100 = true := by decide +kernel

theorem cellsA7_b5 : allFrom cellA7 (100 * 5) 100 = true := by decide +kernel

theorem cellsA7_b6 : allFrom cellA7 (100 * 6) 100 = true := by decide +kernel

theorem cellsA7_b7 : allFrom cellA7 (100 * 7) 100 = true := by decide +kernel

theorem cellsA7_b8 : allFrom cellA7 (100 * 8) 100 = true := by decide +kernel

theorem cellsA7_b9 : allFrom cellA7 (100 * 9) 100 = true := by decide +kernel

theorem cellsA7_b10 : allFrom cellA7 (100 * 10) 100 = true := by decide +kernel

theorem cellsA7_b11 : allFrom cellA7 (100 * 11) 100 = true := by decide +kernel

theorem cellsA7_b12 : allFrom cellA7 (100 * 12) 100 = true := by decide +kernel

theorem cellsA7_b13 : allFrom cellA7 (100 * 13) 100 = true := by decide +kernel

theorem cellsA7_b14 : allFrom cellA7 (100 * 14) 100 = true := by decide +kernel

theorem cellsA7_b15 : allFrom cellA7 (100 * 15) 100 = true := by decide +kernel

theorem cellsA7_b16 : allFrom cellA7 (100 * 16) 100 = true := by decide +kernel

theorem cellsA7_b17 : allFrom cellA7 (100 * 17) 100 = true := by decide +kernel

theorem cellsA7_b18 : allFrom cellA7 (100 * 18) 100 = true := by decide +kernel

theorem cellsA7_b19 : allFrom cellA7 (100 * 19) 100 = true := by decide +kernel


theorem cellsA7 : ∀ j < 100 * 20, cellA7 j = true := by
  apply blocks_sound
  intro k hk
  interval_cases k
  · exact cellsA7_b0
  · exact cellsA7_b1
  · exact cellsA7_b2
  · exact cellsA7_b3
  · exact cellsA7_b4
  · exact cellsA7_b5
  · exact cellsA7_b6
  · exact cellsA7_b7
  · exact cellsA7_b8
  · exact cellsA7_b9
  · exact cellsA7_b10
  · exact cellsA7_b11
  · exact cellsA7_b12
  · exact cellsA7_b13
  · exact cellsA7_b14
  · exact cellsA7_b15
  · exact cellsA7_b16
  · exact cellsA7_b17
  · exact cellsA7_b18
  · exact cellsA7_b19

/-- **Lemma A.5, inequality (A.7)** of Luo–Wei, for every integer `0 ≤ j < 2000`. -/
theorem lemmaA5_A7 (j : ℕ) (hj : j < 2000) :
    ∑ l ∈ Icc (1 : ℕ) 48, (Mc l : ℝ) * Real.exp (-(Real.pi * b2) * l * (11 / 10 + ((j : ℝ) + 1) / 2000))
      - ∑ n ∈ Icc (1 : ℕ) 12, (Nc n : ℝ) * Real.exp (-(Real.pi * a2) * n * (11 / 10 + (j : ℝ) / 2000))
      - 1 / 10 ^ 18 > 1 / 10000 := by
  have hc := cellsA7 j (by omega)
  simp only [cellA7, Bool.and_eq_true, decide_eq_true_eq] at hc
  obtain ⟨h0, hc⟩ := hc
  have hcR : ((1 / 10000 : ℚ) : ℝ) < ((polQ (fun _ => 1) Mtab 48 (C3.getD (j + 1) 0)
      - polQ (fun _ => 1) Ntab 12 (C4.getD j 0) - 1 / 10 ^ 18 : ℚ) : ℝ) := by exact_mod_cast hc
  simp only [Rat.cast_sub, polQ_cast] at hcR
  have e1 : ∑ l ∈ Icc (1 : ℕ) 48, (Mc l : ℝ) * Real.exp (-(Real.pi * b2) * l * (11 / 10 + ((j : ℝ) + 1) / 2000))
      = polR (fun _ => 1) Mc 48 (Real.exp (-(Real.pi * b2) * (11 / 10 + ((j : ℝ) + 1) / 2000))) := by
    rw [← shell_sum_eq]; simp
  have e2 : ∑ n ∈ Icc (1 : ℕ) 12, (Nc n : ℝ) * Real.exp (-(Real.pi * a2) * n * (11 / 10 + (j : ℝ) / 2000))
      = polR (fun _ => 1) Nc 12 (Real.exp (-(Real.pi * a2) * (11 / 10 + (j : ℝ) / 2000))) := by
    rw [← shell_sum_eq]; simp
  rw [e1, e2, polR_congr _ Nc Ntab 12 Nc_tab, polR_congr _ Mc Mtab 48 Mc_tab]
  have hX := chain_lo_bound (p := Real.pi * b2) pb_mem.2 (by decide +kernel) (by decide +kernel) C3_ok
    eOK_all.2.2.2.2.1 eOK_all.2.2.2.2.2.1 heads_ok.2.2.2.2.1.1 heads_ok.2.2.2.2.1.2 heads_ok.2.2.2.2.2.1.2
    (j + 1) (by rw [C_len.2.2.1]; omega)
  have hY := chain_hi_bound (p := Real.pi * a2) pa_mem.1 (by decide +kernel) (by decide +kernel) C4_ok
    eOK_all.2.2.2.2.2.2.1 eOK_all.2.2.2.2.2.2.2 heads_ok.2.2.2.2.2.2.1 heads_ok.2.2.2.2.2.2.2 j
    (by rw [C_len.2.2.2]; omega)
  have tX : ((11 / 10 : ℚ) : ℝ) + ((j + 1 : ℕ) : ℝ) * ((1 / 2000 : ℚ) : ℝ) = 11 / 10 + ((j : ℝ) + 1) / 2000 := by
    push_cast; ring
  have tY : ((11 / 10 : ℚ) : ℝ) + ((j : ℕ) : ℝ) * ((1 / 2000 : ℚ) : ℝ) = 11 / 10 + (j : ℝ) / 2000 := by
    push_cast; ring
  rw [tX] at hX
  rw [tY] at hY
  have h0' : (0 : ℝ) ≤ ((C3.getD (j + 1) 0 : ℚ) : ℝ) := by exact_mod_cast h0
  have hF := polR_mono (fun _ => 1) Mtab 48 h0' hX
  have hB := polR_mono (fun _ => 1) Ntab 12 (Real.exp_pos _).le hY
  push_cast at hcR
  linarith

/-! ## (A.8) and the constants of Lemma 6.1 -/

/-- **Lemma A.5, inequality (A.8)**: `8 e^{{(π a² - 3 π 2^{{-4/3}}) 21/10}} > 25/2`. -/
theorem lemmaA5_A8 : 8 * Real.exp ((Real.pi * a2 - 3 * (Real.pi * b2)) * (21 / 10)) > 25 / 2 := by
  have hz : (((paLo - 3 * pbHi) * (21 / 10) : ℚ) : ℝ) ≤ (Real.pi * a2 - 3 * (Real.pi * b2)) * (21 / 10) := by
    push_cast; nlinarith [pa_mem.1, pb_mem.2]
  have hE := (eLo_le ((paLo - 3 * pbHi) * (21 / 10)) {NTERMS} (by decide +kernel)).trans (Real.exp_le_exp.2 hz)
  have hq : (25 / 2 : ℚ) < 8 * eLo ((paLo - 3 * pbHi) * (21 / 10)) {NTERMS} := by decide +kernel
  have hq' : ((25 / 2 : ℚ) : ℝ) < ((8 * eLo ((paLo - 3 * pbHi) * (21 / 10)) {NTERMS} : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at hq'
  linarith

/-- Proof of Lemma 6.1: `e^{{-π a²}} < 1/49`. -/
theorem lemma61_exp_fcc : Real.exp (-(Real.pi * a2)) < 1 / 49 := by
  have e0 : eOK (-paLo * 1) {NTERMS} = true := by decide +kernel
  have h := exp_neg_hi (p := Real.pi * a2) (pl := paLo) (t := 1) {NTERMS} pa_mem.1 (by decide +kernel) e0
  have hq : eHi (-paLo * 1) {NTERMS} < 1 / 49 := by decide +kernel
  have hq' : ((eHi (-paLo * 1) {NTERMS} : ℚ) : ℝ) < ((1 / 49 : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at h hq'
  simpa using lt_of_le_of_lt h hq'

/-- Proof of Lemma 6.1: `e^{{-π 2^{{-4/3}}}} < 3/10`. -/
theorem lemma61_exp_bcc : Real.exp (-(Real.pi * b2)) < 3 / 10 := by
  have h := exp_neg_hi (p := Real.pi * b2) (pl := pbLo) (t := 1) {NTERMS} pb_mem.1 (by decide +kernel) eOK_all.2.2.1
  have hq : eHi (-pbLo * 1) {NTERMS} < 3 / 10 := by decide +kernel
  have hq' : ((eHi (-pbLo * 1) {NTERMS} : ℚ) : ℝ) < ((3 / 10 : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at h hq'
  simpa using lt_of_le_of_lt h hq'

/-- Proof of Lemma 6.1: `π 2^{{-4/3}} < 5/4`. -/
theorem lemma61_pb_lt : Real.pi * b2 < 5 / 4 := by
  have hq : pbHi < 5 / 4 := by decide +kernel
  have hq' : ((pbHi : ℚ) : ℝ) < ((5 / 4 : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at hq'
  linarith [pb_mem.2]

/-- Proof of Lemma 6.1: `a² > 3 · 2^{{-4/3}}`. -/
theorem lemma61_a2_gt : a2 > 3 * b2 := by
  have hq : 3 * sHi < rLo := by decide +kernel
  have hq' : ((3 * sHi : ℚ) : ℝ) < ((rLo : ℚ) : ℝ) := by exact_mod_cast hq
  push_cast at hq'
  linarith [a2_br.1, b2_br.2]

/-- Proof of Lemma 6.1: `e^{{-π a² · 21/10}} < 1/128`. -/
theorem lemma61_exp_fcc_21 : Real.exp (-(Real.pi * a2) * (21 / 10)) < 1 / 128 := by
  have h1 : Real.exp (-(Real.pi * a2) * (21 / 10)) ≤ Real.exp (-(Real.pi * a2)) ^ 2 := by
    rw [← Real.exp_nat_mul]
    apply Real.exp_le_exp.2
    push_cast
    nlinarith [pa_pos]
  have h2 := lemma61_exp_fcc
  have h3 : Real.exp (-(Real.pi * a2)) ^ 2 < (1 / 49) ^ 2 :=
    pow_lt_pow_left₀ h2 (Real.exp_pos _).le (by norm_num)
  have h4 : ((1 : ℝ) / 49) ^ 2 < 1 / 128 := by norm_num
  linarith

/-- Proof of Lemma 6.1 (via Prop. 4.1): for `0 ≤ x ≤ 1/128`, `12 + 30((1-x)^{{-2}} - 1) < 25/2`. -/
theorem lemma61_prop41_bracket (x : ℝ) (_h0 : 0 ≤ x) (h1 : x ≤ 1 / 128) :
    12 + 30 * (1 / (1 - x) ^ 2 - 1) < 25 / 2 := by
  have hpos : (127 / 128 : ℝ) ^ 2 ≤ (1 - x) ^ 2 := by
    apply pow_le_pow_left₀ (by norm_num); linarith
  have hinv : 1 / (1 - x) ^ 2 ≤ 1 / (127 / 128 : ℝ) ^ 2 := one_div_le_one_div_of_le (by positivity) hpos
  have : (12 : ℝ) + 30 * (1 / (127 / 128 : ℝ) ^ 2 - 1) < 25 / 2 := by norm_num
  linarith

/-- Proof of Lemma 6.1, first omitted tail: every partial sum of `30 Σ_{{n ≥ 13}} n 49^{{-n}}` is `< 10^{{-18}}`. -/
theorem lemma61_tail_fcc (K : ℕ) :
    30 * ∑ k ∈ range K, ((13 + k : ℕ) : ℝ) * (1 / 49 : ℝ) ^ (13 + k) < 1 / 10 ^ 18 := by
  have h := tail_le (fun n => (n : ℝ) * (1 / 49 : ℝ) ^ n) 13 (14 / 637) (fun n => by positivity) (by norm_num)
    (by norm_num) (fun n hn => by
      have hn' : (13 : ℝ) ≤ n := by exact_mod_cast hn
      have hp : (0 : ℝ) ≤ (1 / 49 : ℝ) ^ n := by positivity
      simp only [Nat.cast_add, Nat.cast_one, pow_succ]
      nlinarith) K
  have : (30 : ℝ) * (((13 : ℕ) : ℝ) * (1 / 49 : ℝ) ^ 13 / (1 - 14 / 637)) < 1 / 10 ^ 18 := by norm_num
  linarith

/-- Proof of Lemma 6.1, second omitted tail: every partial sum of `(75/2) Σ_{{l ≥ 49}} l² (3/10)^l` is `< 10^{{-18}}`. -/
theorem lemma61_tail_bcc (K : ℕ) :
    75 / 2 * ∑ k ∈ range K, ((49 + k : ℕ) : ℝ) ^ 2 * (3 / 10 : ℝ) ^ (49 + k) < 1 / 10 ^ 18 := by
  have h := tail_le (fun n => (n : ℝ) ^ 2 * (3 / 10 : ℝ) ^ n) 49 ((50 / 49) ^ 2 * (3 / 10)) (fun n => by positivity)
    (by norm_num) (by norm_num) (fun n hn => by
      have hn' : (49 : ℝ) ≤ n := by exact_mod_cast hn
      have hp : (0 : ℝ) ≤ (3 / 10 : ℝ) ^ n := by positivity
      have hsq : ((n : ℝ) + 1) ^ 2 ≤ (50 / 49) ^ 2 * (n : ℝ) ^ 2 := by nlinarith
      simp only [Nat.cast_add, Nat.cast_one, pow_succ (3 / 10 : ℝ)]
      nlinarith) K
  have : (75 / 2 : ℝ) * (((49 : ℕ) : ℝ) ^ 2 * (3 / 10 : ℝ) ^ 49 / (1 - (50 / 49) ^ 2 * (3 / 10))) < 1 / 10 ^ 18 := by
    norm_num
  linarith

/-- The rational omitted-tail bound printed in the proof of Lemma A.6. -/
theorem lemmaA6_tail :
    60 * (1 / 49 : ℚ) ^ 13 / (1 - 1 / 49) + 60 * (3 / 10 : ℚ) ^ 49 / (1 - 3 / 10) < 7 / 10 ^ 21 := by decide +kernel

/-- The rational step of Lemma A.1: `55995/10⁶ < 7/125`. -/
theorem lemmaA1_rational : (55995 / 10 ^ 6 : ℚ) < 7 / 125 := by decide +kernel

end YukawaBccFcc
"""
    marks = ["/-! ## Constants -/", "/-! ## (A.6) -/", "/-! ## (A.8) and the constants of Lemma 6.1 -/"]
    names = ["Shells", "Chains", "LemmaA5", "Lemma61"]
    body = txt.rsplit("end YukawaBccFcc", 1)[0]
    cuts = [0] + [body.index(m) for m in marks] + [len(body)]
    for i, nm in enumerate(names):
        piece = body[cuts[i]:cuts[i + 1]]
        if i > 0:
            piece = f"import Programmes.YukawaBccFcc.{names[i - 1]}\n\nnamespace YukawaBccFcc\n\nopen Finset\n\n" + piece
        (out.parent / f"{nm}.lean").write_text(piece.rstrip() + "\n\nend YukawaBccFcc\n")
    print("wrote", out.parent, "chain lengths", len(c1), len(c2), len(c3), len(c4))
    return 0


if __name__ == "__main__":
    sys.exit(main())
