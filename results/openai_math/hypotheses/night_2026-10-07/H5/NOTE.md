# H5 lane note, night 2026-10-07: C* = 5/2 is false; tensor powers give C* >= 3

Every number below comes from a JSON file in this directory (named in brackets). Exact values
are Python `Fraction`s over integer arithmetic. "Proved" means proved on paper in this note; nothing
here is Lean-checked.

## Setting

Inputs F_v (v = 0, 1, 2) are constant on the 2^-N squares of [0,1)^2. Level l = 0..N-1 has dyadic
intervals of length 2^-l; L_I = 2^l ∫ F0(x0,x1) F1(x1,x2) F2(x2,x0) h_I0(x0) h_I1(x1) h_I2(x2)
over the admissible triples (n0 xor n1 xor n2 = 0), with h_I = +1 on the left half and -1 on the right
half. All scales of length >= 2 together contribute |T|, where T = ∫ F0 F1 F2. Write
R(F) = S(F) / prod_v ||F_v||_3, with S = |T| + H and H = sum over levels and triples of |L_I|.
For ±1 inputs every norm is 1, so R = H + |T|. C_N = sup R at resolution N, and C* = sup_N C_N.

## 1. Verdict on H5' (preregistered rule): REFUTED

Chunk `W_N8_witness_x_witness` is preregistered and its controls passed. For F = w4 ⊗ w4, where
w4 = sign(best_inputs_N4.npz) and ⊗ is the Kronecker product (w4 on the top 4 bits, w4 again inside
each cell), the integer certifier gives ratio^3 = 12167/512, i.e. **R = 23/8 = 2.875 > 5/2 + 1e-9**
[chunks/W_N8_witness_x_witness.json]. All 12 rotations and sign flips in that chunk give the same
value. The preregistration requires a recheck for ±1 inputs:

- `h5_exact.exact_ratio`: 23/8. Parts: T 1/16; levels 7..0: 1, 1/2, 1/2, 1/4, 1/4, 1/8, 1/8, 1/16.
- An independent implementation written from the definition: 23/8. The conventions were checked on 2026-10-08 against the upstream preprint in the read-only openai-math clone ("An L3 bound for the dyadic triangular Hilbert form", sections/01-introduction.tex, eq. local-form): h_I = 1_left - 1_right, prefactor 2^-k, coupling F0(x0,x1) F1(x1,x2) F2(x2,x0), and XOR admissibility. It enumerates triples as
  (n0, n2, n1 = n0 xor n2) and contracts in a different order.
- The float value from `h5_dyadic.ratio`: 2.875.

[verify_tensor.json; witness saved as witness_N8_w4xw4.npz]. The power control (P01) passed: the
Haar-free form at N=4 was certified at ratio 5.

## 2. The product rule, which explains 5/2

**Lemma (product rule).** Let f be ±1 at resolution N1 and g be ±1 at resolution N2. Then
R(f ⊗ g) = H(g) + |T(g)| R(f).

*Proof.* Put F = f ⊗ g at resolution N = N1 + N2.

(a) Coarse levels l < N1. Each Haar function is constant on every coarse cell of side 2^-N1.
The integral therefore splits into a sum over coarse cells (a0, a1, a2). Each summand is
h-values × f0[a0,a1] f1[a1,a2] f2[a2,a0] × 2^-3N1 T(g), since rescaling a cell to [0,1) turns
∫ g0 g1 g2 into T(g). Hence L_I(F) = T(g) L_I(f) for every coarse triple, and T(F) = T(g) T(f).

(b) Fine levels l >= N1. Write I_v = 2^-N1 (a_v + J_v), with J_v dyadic of level l - N1 in [0,1).
The interval index is a_v 2^(l-N1) + j_v, so the XOR condition holds if and only if
a0^a1^a2 = 0 and j0^j1^j2 = 0. The prefactor splits as 2^l = 2^N1 · 2^(l-N1), and the measure gives
2^-3N1. So L_I(F) = f0[a0,a1] f1[a1,a2] f2[a2,a0] · 2^-2N1 L_J(g). The f-product has modulus 1,
and there are 2^(2N1) admissible (a0, a1). Summing |L_I(F)| over a level therefore gives
sum_J |L_J(g)| at level l - N1, and the fine levels add up to H(g).

Adding (a) and (b): S(F) = |T(g)| (|T(f)| + H(f)) + H(g) = |T(g)| R(f) + H(g), and all norms are 1. ∎

Checks:

- The lemma holds exactly on 6 random ±1 pairs [verify_tensor.json].
- It predicts every exactly evaluated tensor pair in tensor_search.json.
- It is tested in tests/openai_math/test_night_h5_tensor.py.

**What 5/2 is.** Let g2 be the ±1 maximiser at N=2 found by the exhaustive search (chunk E2_00).
It has R = 2, H = 3/2 and T = 1/2 [tensor_search.json]. The committed N=2 witness signs have the
same (R, H, T). Then R(g2 ⊗ g2) = 3/2 + (1/2)(2) = 5/2, exactly the N=4 value, and the tensor square
has (H, T) = (9/4, 1/4). The committed N=4 witness w4 has the same (H, T) = (9/4, 1/4). But it is
**not** itself a Kronecker product: each F_v, rearranged into a 16×16 matrix (4×4 coarse block
index × 4×4 inner index), has rank 12, not 1 (one numpy call, 2026-10-08). So the claim is only this:
5/2 is the value of g2 ⊗ g2. The ascent witness is a different extremiser with the same per-term
profile, and whether it is equivalent to g2 ⊗ g2 under a symmetry of the form was not checked.

The exact decomposition of the N=4 witness [explain_N4.json] shows the same structure:

| | per-level parts |
|---|---|
| levels 3, 2, 1, 0 | 1, 1/2, 1/2, 1/4 |
| T | 1/4 |

- Within each level, every triple has the same modulus |int|: 8, 32, 256 and 1024. Only the finest
  level saturates (|int| = b^3, all 64 triples).
- The other levels run at efficiencies 1/2, 1/2, 1/4, and T at 1/4. These are the
  (H, T) = (3/2, 1/2) profile of g2 ⊗ g2 by the lemma: levels 3, 2 carry H(g2) = 1 + 1/2, and
  levels 1, 0 and T carry |T(g2)| (1 + 1/2 + 1/2).
- At level 2 the sign of L_I depends only on n1.
- The 2D Walsh spectrum of each F_v has full support (256 of 256). The structure is a Kronecker
  (tensor) one, not a sparse Walsh pattern.

**Corollary (C* >= 3, proved).** Let g^(r) be the r-fold tensor power of g2, at resolution 2r. Then
R_r = 3/2 + (1/2) R_(r-1), with R_1 = 2, so R_r = 3 - 2^(1-r). This gives:

| r | N | R_r | evaluated |
|---|---|---|---|
| 2 | 4 | 5/2 | |
| 3 | 6 | 11/4 | evaluated exactly, through g2 ⊗ w4 |
| 4 | 8 | 23/8 | |
| 6 | 12 | 95/32 | independent code only, through w4^(⊗3) |

The N=12 row is in [verify_tensor.json]. The N = 6 and N = 7 values (11/4) are in
[tensor_search.json]. Since C* >= R_r for every r, **C* >= 3**. More generally,
C* >= H(g)/(1 - |T(g)|) for every ±1 g with |T(g)| < 1.

The Hoelder ascent stayed at 2.5 at N = 5..8 in every run tonight: 18 preregistered ascent
chunks, per-chunk best between 2.49991857 and 2.49999999. It never found 11/4 at N = 6 or 7, or 23/8 at N = 8. Local
ascent from these initialisations does not see tensor structure.

## 3. Upper bounds for restricted classes

**N = 1, all real inputs: C_1 = 1 (proved).** At N=1 the form has two terms:
S = (1/8)(|tr(ABC)| + |tr(DADBDC)|), with A, B, C = F0, F1, F2 as 2x2 matrices and D = diag(1, -1).

1. For a sign ε, |T| + |L| = max over ε of (1/8)|sum_{ijk} A_ij B_jk C_ki (1 + ε s_i s_j s_k)|.
2. The weight 1 + ε s_i s_j s_k takes the values {0, 2}. It equals 2 exactly on the 4 triples
   E_ε = {s_i s_j s_k = ε}.
3. For each (i, j) exactly one k has (i, j, k) ∈ E_ε, and the same holds for (j, k) and (k, i).
4. Hoelder on E_ε therefore gives |sum| <= 2 prod_v (sum_{ij} |F_v[i,j]|^3)^(1/3) = 8 prod_v ||F_v||_3.
5. Hence R <= 1. Constants attain 1.

The exhaustive ±1 search agrees: maximum 1 [chunks/E01_exhaust_N1.json].

**Hoelder-marginal bound, any N (proved; exact numbers are computer-assisted).**

1. S = max over sign patterns ε of sum_{ijk} W_ε(i,j,k) F0 F1 F2, where
   W_ε = sum_t ε_t w_t g0_t ⊗ g1_t ⊗ g2_t.
2. Hoelder with the measure |W_ε| gives R <= B_N, with
   B_N^3 = max_ε M0 M1 M2 / 2^(3N), where M0 = max_{ij} sum_k |W_ε|, and M1, M2 are defined cyclically.
3. Exact enumeration [holder_bound.json] gives B_1^3 = 1, B_2^3 = 8 and B_3^3 = 125/8. That is
   **C_2 <= 2 and C_3 <= 5/2 for all real inputs**. N=3 required all 2^21 patterns.
4. Controls: the Haar-free form gives B^3 = 27 and 64 (that is, N + 1, as it must). Random real
   inputs never exceeded the bound.

Consequences:

- **C_2 = 2 exactly over all real inputs** (bound 2, attained by g2).
- **2 <= C_3 <= 5/2**, with the lower bound from ones_N1 ⊗ g2 = 2.
- The marginal bound cannot be computed at N=4 (2^85 patterns). It stays a valid upper bound at
  every N, but B_N >= C_N >= 11/4 for N >= 6. So this method cannot give a uniform bound near 5/2.

**±1 inputs at N=2 (exact, computer-assisted).** The preregistered exhaustive search covers all
2^48 inputs, reduced by symmetry. All 32 E2 chunks completed, and in every chunk h5_exact agreed on
the argmax. The maximum is exactly **2** [summary.json: exhaustive_N2_complete true,
exhaustive_N2_max_ratio "2"]. This is consistent with the real-input bound B_2 = 2.

**±1 at N=3** was declared infeasible in the preregistration (2^126 (F0, F1) pairs). It was not attempted.

## 4. Conjecture (replaces H5'; labelled as a conjecture, evidence is weak)

**H5'': C* = 3.** We further conjecture that C_(2r) = 3 - 2^(1-r), attained by the tensor powers
of the N=2 maximiser g2.

- Evidence for: the tensor family converges to 3. Among the 4 non-constant ±1 bases tried, the
  largest fixed point H/(1 - |T|) is 3 (g2, the N=2 witness and w4; the N=3 witness gives 61/29).
  The constant base has H = 0 and T = 1, so its tensor powers stay at 1.
- Evidence against, or missing: no upper bound beyond N = 3 exists here. The upstream bound 40 is
  not formalized. Local ascent is demonstrably blind to tensor structure, so its failure to beat a
  value is not evidence.
- A natural next search maximises H(g)/(1 - |T(g)|) over ±1 g at N = 3, 4. This is a new
  objective: by the lemma, any g with a fixed point above 3 refutes H5''.

Novelty: unchecked. No source with a sharp constant for this form was found (2026-10-07).
