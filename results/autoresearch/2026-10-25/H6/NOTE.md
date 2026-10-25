# H6: dyadic triangular Hilbert form — product rule and C* ≥ 3, kernel-checked (producer only)

**Verdict: KEEP, all parts (a)–(d).** Attempt 1, 07:41–07:47 UTC, pinned Lean 4.34.1 + Mathlib.
This is producer-only. Tier A still needs an independent agent to recompile and audit the statements.

## What is checked
These are the files: `formal_cert/Autoresearch/DyadicHilbert.lean` (main), `DyadicHilbertW4.lean`
(a kernel check against the recorded witness) and `DyadicHilbertControls.lean`. All are in namespace
`AutoresearchDyadic`.

- **(a) Definitions.** A cell is `X N` (N bits, most significant first). An input is
  `Fn N = X N → X N → ℤ`. `T`, `L0` and `H` are defined by peeling off the top bit, unnormalised by 8^N:
  - `T` is `∑ F0 F1 F2`.
  - `H` is |level-0 Haar term| plus 2 × Σ over the four admissible top-bit triples (b0, b1, b0 xor b1)
    of `H` on the blocks. This is the level weight 2^l together with XOR admissibility.
  - `S = |T| + H` and `R = S / 8^N`.

  `tensor` is `numpy.kron`: the coarse factor sits on the top bits.
- **(b) Product rule.** `S_tensor` is the integer form, `S(f⊗g) = 8^{n1} H(g) + |T(g)| S(f)`.
  `product_rule` is the rational form, `R(f⊗g) = H(g)/8^{n2} + |T(g)|/8^{n2} · R(f)`. The identity
  itself needs only the coarse factor f to be ±1. R(f⊗g) is the actual ratio only when g is also ±1,
  and g is ±1 in every downstream use. The proof is by induction on the coarse depth, using `T_tensor`, `L0_tensor`,
  `H_tensor`, and the homogeneity lemmas `T_cmul` / `H_cmul` (the ±1 property enters only in the base case).
- **(c) Witnesses.**
  - `g2_R`: R(g2) = 2 at N = 2, by `decide`. The tables are the exhaustive argmax from chunk E2_00,
    compared programmatically.
  - `gpow4_R`: R(g2^{⊗4}) = 23/8 at N = 8.
  - `w4_R`: the recorded N = 4 witness w4 evaluates to 5/2 in the kernel.
  - `g2g2_S_direct`: S(g2⊗g2) = 10240 by direct `decide`, which matches the product-rule value
    `g2g2_S_rule`.
- **(d) Tensor powers.** `gpow_R` gives R(g2^{⊗r}) = 3 − 2/2^r for all r. `sup_ge_three` says that for
  every c < 3 there is a ±1 input at some finite N with R > c, i.e. **C* ≥ 3**.
- **Negative control.** `wrong_rule_refuted`: the rule with 8^{n2}·S(f) in place of |T(g)|·S(f) is
  refuted on f = g = g2 (10240 ≠ 14336).
- **Planted controls.** `ctl_sorry` gives [sorryAx] and `ctl_axiom` gives [ctl_cheat]. Both are caught.
  Every claimed theorem's axioms are a subset of {propext, Classical.choice, Quot.sound}; result.json
  has the verbatim output. A grep for sorry, admit, native_decide and axiom finds nothing in the claimed
  files.

## Definition fidelity (the main risk)
`defs_check.py` was run before any Lean was written. It mirrors the Lean recursion and agrees exactly
with the recorded independent implementation (`verify_tensor.py::direct_parts`) and with the recorded
values:

| input | R | H | T |
|---|---|---|---|
| g2 | 2 | 3/2 | 1/2 |
| w4 | 5/2 | 9/4 | 1/4 |
| w4⊗w4 at N = 8 | 23/8 | 45/16 | 1/16 |

It also agrees on random ±1 and random integer inputs. Its negative control (F2 transposed, so the
coupling is wrong) moves w4 to 25/32. In Lean, `w4_R` reproduces 5/2 on the recorded witness. On its
first compile that file was **rejected**: `decide` proved T = −1024 false, because two rows of a w4 table
had been retyped by hand wrongly. The tables were then regenerated from the npz. So the kernel check
does detect input errors.

## Caveats
- R = S/8^N is the ratio only for ±1 inputs. Every theorem here is stated for ±1 inputs.
- The value 23/8 is proved for g2^{⊗4}, not for w4⊗w4. Both give 23/8 in Python. w4 is not a Kronecker
  product.
- The conventions were taken from H5/NOTE.md, which checked them against upstream. This attempt did not
  re-read the upstream preprint.
- No upper bound is proved. C* = 3 is still a conjecture. No novelty claim is made.
