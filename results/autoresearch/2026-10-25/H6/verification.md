# H6 independent verification (producer ≠ verifier), 2026-10-25

**VERDICT: ACCEPT** (statement-adequacy notes below; none blocks).

## 1. Recompile + axioms
- I made a verbatim copy of `DyadicHilbert.lean`. I appended the body of `DyadicHilbertW4.lean` inline, so W4 was
  compiled in the same file rather than as a separate import, together with my own verifier block. I compiled it
  with pinned Lean 4.34.1 (`lean_pinned.py`, cores 4,5). Result: **rc 0, 36.2 s**.
- Axioms, verbatim:
  - `product_rule`, `S_tensor`, `g2_R`, `gpow_R`, `gpow4_R`, `sup_ge_three`, `wrong_rule_refuted`, `w4_R`,
    `g2g2_S_rule`: each `[propext, Classical.choice, Quot.sound]`.
  - `w4_pm1_0`: `[propext, Quot.sound]`.
  - `g2g2_S_direct`: `[propext]`.
  - My planted `VerifierH6.v_planted` (∃ ±1 input at N=2 with R > 3) `:= sorry`:
    `[propext, sorryAx, Classical.choice, Quot.sound]`. Caught.
- `#check sup_ge_three : ∀ c < 3, ∃ n F0 F1 F2, PM1 F0 ∧ PM1 F1 ∧ PM1 F2 ∧ c < R n F0 F1 F2`. The quantifiers are as
  claimed, and the statement is non-vacuous: the witnesses are the explicit `gpow v r`, and `PM1` forces every entry
  to be ±1. I proved `¬ PM1 (fun _ _ => 0)`.

## 2. Definition fidelity against the upstream preprint
I read `openai-math/preprints/An-L3-bound-for-the-dyadic-triangular-Hilbert-form-October-5-2026/build/sections/01-introduction.tex`,
eq. (local-form) and Thm (main). It defines:
- L_I = 2^{-k} ∫_{I0×I1×I2} F0(x0,x1) F1(x1,x2) F2(x2,x0) ∏ h_{I_v};
- h_I = 1_left − 1_right;
- admissibility n0⊕n1⊕n2 = 0;
- the bound Σ_k Σ_I |L_I| ≤ 40 ∏‖F_v‖_3.

The Lean recursion matches this:
- top-bit `false` is the left half, with sgn +1;
- the blocks are (b0,b1), (b1,b2), (b2,b0), with b2 = b0 xor b1 at every bit, which is bitwise XOR;
- the level weight 2^l comes from the factor 2 per recursion step;
- the 1/8 volume per step is absorbed into the 8^N normalisation;
- R = (|T| + H)/8^N is the ratio for ±1 inputs, whose L³ norms are all 1. Statement adequacy notes:
- (a) Levels finer than the resolution vanish for cell-constant inputs, because ∫h = 0 against a constant. This
  justifies truncating at levels 0..N−1.
- (b) The Lean S includes the full coarse tail Σ_{k≥1} 2^{-k}|T| = |T|. The preprint takes a finite S, which gives
  (1 − 2^{-K})|T|, so no finite S attains the Lean R exactly. The best constant is a sup over finite S, and
  `sup_ge_three` uses strict c < 3, so C* ≥ 3 transfers to the preprint's constant.
- (c) This is a lower bound for the **absolute-sum** constant of eq. (main). It is consistent with the upstream 40.

## 3. Independent recomputation
My script is `.claude/jobs/6ecda88c/tmp/verify_b2/h6_direct.py`. It is direct, not recursive: it enumerates every
level l and every triple (n0, n1, n0^n1) with exact Fractions, and reads the tables from the Lean files. Results:

| input | T | H | R | Lean |
|---|---|---|---|---|
| g2 | 1/2 | 3/2 | **2** | `g2_R` = 2 |
| w4 | −1/4 | 9/4 | **5/2** | `w4_T` = −1024, `w4_H` = 9216, `w4_R` = 5/2 |
| g2⊗g2 | 1/4 | 9/4 | 5/2 | `g2g2_S_direct` = 10240 = (5/2)·8^4 |
| g2⊗g2⊗g2 | 1/8 | 21/8 | 11/4 | `gpow_R` at r = 3: 3 − 2/8 |
| w4, F2 transposed (control) | −1/64 | 49/64 | 25/32 | my Lean check `decide`: T = −64, H = 3136 (= ·8^4) |
| constant 1, N=2 | 1 | 0 | 1 | my Lean check: T = 64, H = 0 |

Lean and my Python also agree on the wrong-coupling control, which is not a witness.

## Corrections (non-blocking)
1. The NOTE should state notes (b) and (c): the strict-c transfer to finite S, and that this is the absolute-sum constant.
2. 23/8 is proved for g2^{⊗4}, not w4⊗w4 (NOTE.md says so; keep it). C* = 3 stays a conjecture (no upper bound).
