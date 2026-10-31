# DH-Ψ2 — independent audit

Auditor: independent Claude agent (producer ≠ verifier). Date 2026-10-31. Scope: `RESULT.md`, `result.json`, `code/`,
`data/`, `logs/` of this directory, preregistration item DH-Psi2 (sha256 `140a28ad…ae9be`, unchanged), paper
doi:10.5281/zenodo.23232389 (`papers/dyadic_triangular_hilbert/dyadic_triangular_hilbert.tex`).
All auditor code and outputs are in `/tmp/dhaudit/` (not tracked): `aud_eval.py`, `aud_tests.py`, `gauge_enum.c`,
`slices.py`, `compare.py`, `hashcheck.py`, `c_runs_audit.sh`, and their JSON outputs. Heavy work ran on cores 4 and 5 only,
with at most 2 processes.

## Verdict: ACCEPT_WITH_CORRECTIONS

The mathematical claim holds. Over all 2^48 sign inputs at N = 2, max Ψ = 3 (S = 192), there are 0 violations, and
4,608 reduced pairs attain the maximum. An enumeration that shares neither of the producer's two reductions reproduces
this, and it also reproduces the full histograms of all five modes bin by bin. The corrections below are about wording and
bookkeeping only.

## 1. Definitions re-derived and an exact evaluator of my own

From eq. (LI) and Prop. `prop:finite` at N = 2 (n = 4), in units of 1/64:
- T = Σ_{ijk} F0[i,j]F1[j,k]F2[k,i].
- Level 0 (k = 0) has one interval, [0,1), so A_0 = {(0,0,0)}. It contributes |Σ F0F1F2·h(i)h(j)h(k)| with prefactor 1,
  where h = +1 on cells 0 and 1 and −1 on cells 2 and 3.
- Level 1 (k = −1) has two intervals of 2 cells each, prefactor 2^1 = 2. The admissible triples (p, q, p⊕q) are
  (0,0,0), (0,1,1), (1,0,1), (1,1,0). The Haar function is h1(x) = +1 on the left cell (even x) and −1 on the odd cell.
- Scales k ≥ 1 sum to |T|. Scales k ≤ −2 vanish.
- So S_w = w|T| + |L_0| + 2Σ_{4 triples}|L_1|, and Ψ ≤ 3 ⇔ S_3 ≤ 192.

This matches the C comment block and `term_vectors` in `psi_exhaust.py`.

The orientation of h1 does not matter. Swapping the two cells inside one half-interval in one coordinate flips the sign of
every affected L_I and leaves |L_I| unchanged: Ψ was unchanged on 200 of 200 random inputs. The parity convention flagged in
RESULT.md is therefore not a risk. The real risks are the level weights, admissibility and the Haar scale, and the mutation
test below covers those.

`aud_eval.py` evaluates eq. (LI) as a literal integral:
- exact `Fraction`s on a refined grid of side 1/(2n);
- explicit enumeration of D_k and of the XOR condition for k = −N … 3;
- a literal check that L = 2^{−k}T for k = 1, 2, 3, and that scale k = −N vanishes;
- general N.

It does not use eq. (trace) or any producer code. Results (`aud_tests_3000.json`):

| check | result |
|---|---|
| random sign inputs, own vs producer `direct_value` vs `h5_exact_value`, w_T = 1, 3, 4 | 3000/3000 |
| random sign inputs, Haar-free form, own vs `direct_value`, w_T = 1, 3 | 3000/3000 |
| random integer inputs in [−3, 3], own vs `direct_value`, w_T = 1, 3 | 300/300 |
| constant input | T = 1, H = 0, R = 1, Ψ = 3; Haar-free R = 3, Ψ = 5 |
| seed g (`tensor/rigor.json`) | T = 1/2, H = 3/2, R = 2, Ψ = 3 |
| producer argmax in each of the 5 modes, re-evaluated | 128 / 192 / 256 / 192 / 320, as claimed |
| N = 1 exhaustive (2^12 inputs) | max R = 1, max Ψ = 3 (the paper's theorem) |
| gauge invariance of T and H (random D0, D1, D2) | 200/200 |
| **mutation power**: own evaluator mutated, then compared against `direct_value` | level-1 weight 1 → 181/200 disagree; odd XOR class → 155/200; coarse Haar at level 1 → 148/200 |

The agreement tests therefore have power against the plausible definition errors.

## 2. My own enumeration, with a different reduction (`gauge_enum.c`)

- **Reduction: a diagonal sign gauge, not the F_v → −F_v flip.** The map (F0, F1, F2) → (D0F0D1, D1F1D2, D2F2D0), with D_v
  diagonal ±1, leaves every term Σ F0[i,j]F1[j,k]F2[k,i]·w(i,j,k) exactly invariant, for any weight w, because d_i²e_j²g_k² = 1.
  - On (F0, F1) the action has order 2^11. Its kernel is ±(I, I, I), and the action is free.
  - Canonical representatives: F0 with row 0 and column 0 all +1 (2^9 choices), and F1 with row 0 all +1 (2^12 choices),
    giving 2^21 pairs. Each orbit has exactly one representative.
  - The producer's set {F0[0,0] = F1[0,0] = +1} meets each orbit in exactly 2^9 pairs. So the prediction is that the
    producer's histogram equals 512 × mine.
- **No ℓ1 reduction.** For each representative the program takes a literal max over all 2^16 F2, in Gray-code order with 6
  integer accumulators. It also counts the F2 that attain the max. No float is used anywhere.
- **Cost.** About 23 min wall per Haar setting on one core, about 0.8 core-h for all five modes, against the producer's
  roughly 10 core-h.

Result (`gauge_haar.json`, `gauge_haarfree.json`; the comparison is in `compare.py`):

| mode | my max S | my pairs > 192 (×512) | my pairs at max (×512) | 512 × my histogram equals producer C and Python histograms |
|---|---|---|---|---|
| PSI | 192 | 0 (0) | 9 (4,608) | yes, every bin |
| R | 128 | 0 | 8 (4,096) | yes |
| PLANT4 | 256 | 1,449 (741,888) | 1 (512) | yes |
| HF_R | 192 | 0 | 1 (512) | yes |
| HF_PSI | 320 | 14,369 (7,356,928) | 1 (512) | yes |

Every argmax was rechecked by a literal triple sum. A by-product, not claimed by the producer: exactly 9 × 2 × 2^11 = 36,864
of the 2^48 sign inputs attain Ψ = 3. That is 18 maximising F2 summed over the 9 canonical pairs, times the orbit size.

**Reduction-free slices.** For F0 codes 0, 1, 7000, 12345, 21845, 30000 and 32767, in the producer's encoding, I took all
2^15 F1 with F1[0,0] = +1 and a literal max over all 2^16 F2. The per-slice histograms equal the producer binary's on
[a, a+1) in 35 of 35 (code, mode) cases. They include non-constant F0 with PLANT4 violations (code 1: 344 pairs > 192) and
with HF_PSI violations.

## 3. The producer's two reductions

Both reductions are proved here, and both are also confirmed empirically by §2, which uses neither of them.
- **Sign fix.** Every term is trilinear. F0 → −F0 and F1 → −F1 each negate every term, so they preserve every |term| and every
  max over F2. Fixing F0[0,0] = F1[0,0] = +1 loses nothing. These flips are also contained in the gauge-plus-flip group of §2.
- **ℓ1 reduction.** For fixed (F0, F1), each term is ⟨c_t, F2⟩ (weights w_t > 0 absorbed). Then
  - max_{F2} Σ_t |⟨c_t, F2⟩| = max_{F2} max_{s∈{±1}^6} ⟨Σ_t s_t c_t, F2⟩ (using |a| = max_s s·a);
  - = max_s max_{F2} ⟨Σ_t s_t c_t, F2⟩ (swap the two finite maxima);
  - = max_s ‖Σ_t s_t c_t‖₁ (the max of a linear form over the cube {±1}^16);
  - and s → −s leaves the norm unchanged, so s_0 = +1 can be fixed.

  This is an identity, not a heuristic.

## 4. Rebuild and rerun of `c_runs.sh` halves 0 and 1

- Rebuilt with `gcc -O3 -march=native` (system gcc) into `/tmp/dhaudit/psi_exhaust_rebuilt`.
- Ran a copy of `c_runs.sh` with only B and O redirected to `/tmp`. The original would overwrite `data/c_enum/` and run the
  stale binary.
- Both halves ran sequentially on core 4.
- Every output file is byte-identical to `data/c_enum/` and matches the sha256 in `result.json`:
  - half 0: PSI, R, PLANT4, HF_R, HF_PSI, the 3 brute-force files, DONE;
  - half 1: the same 9 files, all byte-identical as well.
- max_S = 192 for Ψ, and 0 violating pairs.

## 5. Controls, kill criterion, hashes

- **Controls are discriminating.**
  - Haar-free R reaches N + 1 = 3, the Prop. `prop:level` bound.
  - Haar-free Ψ reaches 5 at the constant input.
  - The planted w_T = 4 finds 741,888 violating pairs, including non-constant F0 with values strictly between 3 and 4 (the
    producer reports 49/16 … 7/2; I confirmed violations at code 1 independently).
  - So a search that silently under-maximised would have been caught. My N = 1 exhaustive check and the mutation test add
    power on the definitions side.
- **Kill criterion.** 40.89 s × 32768/328 / 3600 = 1.135 core-h (the file says 1.136, a rounding difference); × 5 modes =
  5.67 core-h, far below 60. It did not fire. Correct.
- **Hashes.**
  - All 199 entries of `files_sha256` match the files on disk, and no file on disk is unlisted.
  - The preregistration sha256 is the same at start and end, and equals `140a28ad…ae9be`.
  - One bookkeeping point: `code/psi_exhaust` (the binary) is listed in `files_sha256` but is not tracked by git (`git
    ls-files`), so a fresh clone fails that entry. See correction 4.

## 6. Corrections (exact old → new)

1. RESULT.md, Outcome:
   - old: "So Conjecture 1 of doi:10.5281/zenodo.23232389 holds for **sign inputs at resolution 2**."
   - new: "So the sign-input, resolution-2 case of Conjecture 7.1 (`conj:psi`) of doi:10.5281/zenodo.23232389 holds
     (finite exhaustive check)."
   - Reason: the paper numbers it 7.1 (`.aux`: `\newlabel{conj:psi}{{7.1}…}`).
2. RESULT.md, Outcome bullet:
   - old: "Two independent full enumerations agree on this."
   - new: "Two full enumerations agree on this. They are independent implementations, but they share the F0[0,0] = F1[0,0] = +1
     sign fix and the ℓ1 reduction over F2. A third enumeration by the auditor uses neither (diagonal sign-gauge reduction,
     literal max over all 2^16 F2) and reproduces 512 × its histogram bin by bin in all five modes (AUDIT.md)."
3. RESULT.md, Tiers:
   - old: "two independent implementations agreeing on full histograms" (also in `result.json` `"tier"`)
   - new: "two producer implementations plus an auditor enumeration with a different reduction, agreeing on full histograms".
4. `result.json`: either drop `"code/psi_exhaust"` from `files_sha256`, or annotate it as "untracked local build artifact,
   not reproducible across machines". Otherwise a fresh clone reports a missing file.
5. RESULT.md, "What an independent auditor must redo", item 2:
   - old: "The residual common-mode risk is narrower: the shared F0[0,0] = F1[0,0] = +1 convention and the shared l1 reduction over F2"
   - new: "Both shared reductions are exact identities (proved in AUDIT.md §3) and were confirmed by an enumeration that uses
     neither."
   - Optionally also drop the implication that the h1 parity convention is a risk: it is immaterial (§1).
6. Wording to keep everywhere:
   - "our own conjecture; exhaustive check at N = 2 for sign inputs (two producer enumerations plus an independent auditor
     enumeration); not progress on C*; Tier C".
   - Optional new fact: "36,864 of the 2^48 sign inputs attain Ψ = 3".

No correction changes a number.

## What remains unverified

- Nothing about real-valued inputs, N ≥ 3, or the value of C*. None of these is claimed.
- The Python float32 kernel was not rerun. It was cross-checked only through its histograms in `summary.json`, which equal
  512 × mine.
- Tier C only: no Lean or kernel certificate exists for the 2^48 statement. My enumeration is a second independent program,
  not a proof object.
- The compiler and the hardware are trusted, not checked. All three enumerations ran on the same machine: two through gcc,
  one through numpy/BLAS.
