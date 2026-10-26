# Independent adversarial audit: B3 preprint `papers/p2_3d_feasibility/`

Auditor: an independent Claude agent instance (producer != verifier). It did not write the study or the paper. Date 2026-10-26.
Scope: main.tex / main.pdf, gen_numbers.tex, make_all.py, code/, data/, ledger/, publication_meta.json, results/proposal2/2026-10-26/B3/.
The auditor edited nothing except this file and ran no git commands. Scratch copies of the code were run in /tmp/b3audit/, so the paper directory was not touched.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The central argument holds up. The calibration step of the planar proof is described correctly. The literature energies check out independently. The cheap numerics reproduce byte for byte. The main text keeps "proof architecture" and "3D" apart. Two things block release. First, the files shipped in `data/` still carry a rigour claim and a parameter-count scope that the paper itself withdraws, and one leftover phrase in Section 5.2 repeats that scope. Second, the Euler-count "transfer" as written in the paper fails for non-simple cells. The study note fixes this with a genericity step, but that step was dropped from the paper.

---

## What was checked and what was found

### (1) The obstruction argument, step by step
- **Lemma 1 (dual identity).** I re-derived it. With -Δh = 4π(δ - 1), ∫∇h·∇H = 4π(H_reg(0) - ∫H). Hence (1/8π)∫|∇h|² = sl(H) + H_reg(0) - ∫H - (1/8π)∫|∇H|², and with H_reg(0) = 0 this gives F(H) as stated. Consistency check: H = h - C_reg gives F = C_reg - e = 2e - e = e, using n3b's C_reg = 2·Madelung. The renormalization bookkeeping is openly omitted, so Tier C is appropriate.
- **Lemma 2 (ceiling).** Correct. The planar method's certified inequality is applied through G13 to separated configurations only. The bcc configuration is separated: nearest-neighbour distance (√3/2)·2^{1/3} ≈ 1.091 > R ≈ 0.620. So the ceiling does apply, but the hypothesis "for every configuration" should say so (NB-8).
- **Lemma 3 (slack).** (i) For radial and axial H the gradient set at x is a linear subspace (span{e_r} or span{e_r, e_θ}), so the Pythagorean bound is right. (ii) R is unitary in the Dirichlet inner product on the R-invariant hexagonal pyramid, so ‖(1-R)h‖ = ‖(1-R)(h-H)‖ ≤ 2‖h-H‖. That is correct. (iii) Additivity is correct.
- **Class inclusions.** An axial H on a regular hexagonal pyramid is invariant under the 60° rotation. Piece-intrinsic data on the six congruent in-face sectors (all related by R itself) force H∘R = H. This is correct.
- **Symmetry claims.** The face trace's C6 symmetry comes from inversion through the face centre (a bcc symmetry that maps the face plane to itself) combined with C3. The interior of the pyramid has only C3v, because R60 about [111] is not in O_h. Both statements are correct. A consequence worth stating: the face-trace cos6ψ mode is R-invariant, so the hierarchical slack comes entirely from the interior modes that are odd under R (cos3ψ type). The paper says this in words.
- **Rotation-convention control.** The paper says this control "was not run". **The auditor ran it**, as /tmp/b3audit/ctl.py, using the paper's own `bounds_for_gradient` on 2^16 scrambled-Sobol points (seed 5) in the (+,+,+) hexagonal pyramid:
  - Non-radial field invariant under rotation about n̂, f = (n·x)³ + ρ⁴: hier 5.4e-35, axial 3.9e-36 (full Dirichlet 1.28e-3).
  - Field Re((u+iv)⁶), i.e. cos6ψ, R-invariant but not axial: hier 3.0e-37, axial 2.8e-7. So it is killed by the pair bound and detected by the azimuthal bound, as theory says.
  - Field Re((u+iv)³), i.e. cos3ψ, odd under R: hier 1.29994e-4, which equals its full Dirichlet energy 1.29994e-4. This is exactly the prediction, since (1-R)/2 = 1 on this mode.
  - Conclusion: the convention in `Gr = gradf(P @ R.T) @ R` is correct.
- **Is "rigorous for local ansätze with ≤ 4 parameters" justified? No.** This claim is in data/result.json `rigorous_for` and in data/FEASIBILITY.md §0 and §6. It fails on two counts.
  - It is not rigorous. The lemmas are hand arguments (C), and their evaluation is floating-point quasi-Monte Carlo without enclosures (X).
  - The parameter count is not the operative hypothesis. The bound uses only invariance under the 60° rotation R on the hexagonal pyramids (or the axial or radial structure). A piece-intrinsic class with 10 parameters is still covered. A 2-parameter class that reads neighbour data is not.
  - The main text mostly gets this right (Section 4.1: "a gloss on the symmetry class, not a separate hypothesis"). But Section 5.2 still says "ansatz classes that carry neighbour data and exact piece data of five or more parameters", and the shipped data/ files still say "rigorous". See BLOCKING-1.
- **Counting argument.** It is marked unproved, correctly and repeatedly ("counting heuristic, not a theorem", Tier C, hidden identities not excluded). The arithmetic is right:
  - 144 flags / |O_h| = 48 gives 3 orbits. The 12 hex–hex edges give 48 flags (1 orbit). The 24 hex–square edges give 96 flags (2 orbits).
  - 4 conditions per type gives 8 or 12 conditions, against 3 multipliers.
  - The invariant identity (a + 6b + 2c)f - 12b - 4c is correct.
- **Euler identity.** v - e + f = 2 and 3v ≤ 2e give e ≤ 3f - 6, so Σ(6 - n_F) ≥ 12, with equality iff the cell is simple. Correct. **But** see BLOCKING-2: the inequality points the wrong way for K ≤ 0.

### (2) Numerics
- **Re-run.** `n1_energies.py` was re-run from a scratch copy under `python -I`, taskset cores 6,7. Exit 0, and the output is **byte-identical** to code/n1_energies.json. The stored code/n3_green_obstruction.json is identical to the study's copy.
- **Independent literature check (alphaXiv).** Alves, Bendazzoli, Evangelisti, Berger, arXiv:2103.01622, Table III gives η₀ (Ha·r_s): bcc -0.895929255, fcc -0.895873614, hcp -0.895838120, sc -0.880059440. Dividing by r_s = (3/4π)^{1/3} = 0.62035049 gives -1.4442308, -1.4441411, -1.4440838 and -1.4186487. These match the paper's -1.4442308, -1.4441411, -1.4440838 and the sc value to the printed digits. Two further sources agree: Muratov–Novaga eq. (5) (K_BCC ≈ -0.895929255682, K_FCC ≈ -0.895873615195; local source text mn.txt l.116–118) and Kozhberov, arXiv:2411.03863 (ξ_bcc = -0.8959292557, ξ_fcc = -0.8958736151). Note that n1's own "literature" comparison uses hard-coded constants, so it is not independent by itself. The checks above make it so.
- **Muratov–Novaga margin.** MN eq. (11): E(L_F) - E(L_B) ≈ 1.7938403e-4 with E(L_B) ≈ -2.888461503 (mn.txt l.196–197), i.e. twice our normalization. Confirmed. See NB-1: the paper's computed gap actually reproduces this to 7 digits, but a hand-typed constant hides that.
- **Slack error bars.** They are honestly reported as Monte Carlo standard errors and not as enclosures. Per seed: hierarchical s.e. 2.89e-7 and 2.88e-7 (8.75e-5 / 2.89e-7 ≈ 303); axial 2.37e-7 (≈ 448); radial 9.2e-6. The seed spreads are 7e-8 (hierarchical), 1.0e-7 (axial) and 4.0e-6 (radial), all within about 1 s.e. MC cell volume: 0.99990 and 1.00012. Hierarchical/gap = 0.9757, axial/gap = 1.1797. One caveat to state (NB-3): the s.e. is the iid formula applied to a single scrambled-Sobol sequence per seed. It is a heuristic, not a randomized-QMC confidence interval. Strict positivity does not depend on it, because the integrands are pointwise non-negative and are bounded away from 0 on open sets.

### (3) The 2D side
I read 04-calibration.tex in full (and 03-geometry.tex l.99–214, plus verification/data/certificate-record.txt).
- **Trial potential.** Eq. (cal:trial-potential) is H = B(r) + Σ(r/t(φ))^{k_i} D_i(t(φ)) with t = d sec φ. This matches G5 and Section 4.2.
- **Exact calibration.** Lemma cal:energy-identity shows H = h_△ - C_△ on each regular sector, by the vertex-ray baseline plus the edge correction, (-1)^m c_m r^k + (r/t)^k(V_m(t) - (-1)^m c_m t^k) = c_m r^k cos kφ. "Hence ∇H = ∇h_△ and the nonnegative square ... is zero." This matches the paper's G8 and its description "a function of (r,t) because cos 6mφ = T_6m(d/t)".
- **Stationarity.** Lemma cal:stationarity has λ and μ solve ∇_{d,x} g = 0 at (p, x₀), with K = 2g_p(x₀). This matches G9 and the "2 multipliers, 2 equations, one sector type" reading.
- **Other figures.** The incidence count of "at most 6N face-edge sectors" (Prop. cal:scalar-to-torus) matches G4. r_* = 1/√π is at 03-geometry l.99. "72.6 s on 32 threads" matches the certificate record (72.598 s, OMP_NUM_THREADS = 32).
- **Conclusion.** The paper's description of the calibration step is correct. The disclaimer "we did not re-read the manuscript" can now be replaced by this cross-check (NB-12).

### (4) Overclaim
- **Main text is clean.** The main text never says 3D bcc optimality is unprovable or false. Section 1 ("claims a negative about one proof strategy"), the proposition ("provided the floating-point slack values are correct") and the Limitations all keep the scope.
- **Remaining problems.**
  - (a) The abstract's "Outcome: no, with a precise scope" answers the title question more strongly than the evidence supports for richer classes (NB-10).
  - (b) Section 4.3's "would not be able to separate bcc from fcc by energy alone" is conceptually muddled (NB-6).
  - (c) The shipped data/FEASIBILITY.md contains statements that are wrong as written (BLOCKING-1): "cannot even certify W ≥ W_fcc" and "nor even exclude energies between bcc and fcc". Since W_bcc < W_fcc, no valid method can certify W ≥ W_fcc.

### (5) Citations
- **Tier-L gate.** I re-ran the Elenchus `tools/citation_check.py` myself on the 4 Tier-L claim files (ledger/citations/claim_*.json) against the local source texts. All 4 were **ACCEPTED**, rc = 0. The sha256 of all 7 pdftotext files matches ledger/sources/MANIFEST.md.
- **Prose quotations.** All 8 prose quotations are flagged verbatim in data/citation_check.json. I also grep-confirmed the key ones in the sources:
  - BL "Proving this fact is still an open problem." (bl.txt l.1240), with 1.44423 / 1.44415 / 1.41865 / 1.4508 at l.1248–1257.
  - Lewin c₁ ≈ 1.4508 (lew.txt l.2327).
  - RS "may depend on the choice of" (rs.txt l.6646).
  - AI "which remains open for d ≥ 3" (ai.txt l.253).
  - MN "substantially harder three-dimensional crystallization problem" (mn.txt l.1079) and the relative gap 6.2 × 10⁻⁵ (l.124).
- **Ledger gate.** gate_output.txt: 30 claims, no findings, exit 0.
- **Minor.** BL prints fcc "1.44415...", while the computed value is 1.444141. This is BL's rounding. Our value agrees with MN, Alves et al. and Kozhberov.

### (6) publication_meta.json
- **Accurate.** The numbers are right (8.75e-5 / 0.98, 1.06e-4 / 1.18, 3.09e-3, about 300 s.e., about 3e13 nodes, about 200 core-years against 221 in the macros, 30 claims / exit 0, 4 Tier-L). The commit prefix e23f5c2 matches the B3 study commit in the session's git log; the full SHA was not re-derived, by the no-git instruction. "Paper directory uncommitted" is consistent with git status.
- **Needs updating or completing.** See NB-9 and NB-11.

---

## BLOCKING

1. **The shipped `data/` files and one sentence in Section 5.2 contradict the paper's own scope.** They claim rigour and a parameter-count scope.
   - Exact fix in main.tex §5.2 (line 268): replace "It is the only argument against ansatz classes that carry neighbour data and exact piece data of five or more parameters, and it is a negative of Tier~C strength only." with: "It is the only argument against ansatz classes whose data are not invariant under the 60° rotation of the hexagonal pyramids (in particular, classes that carry neighbour data, whatever their number of parameters), and it is a negative of Tier~C strength only."
   - Optionally, in §4.1 (line 158), delete "at most four parameters in total" and keep the sentence of line 161 only.
   - Exact fix for data/: data/ must not be hand-edited as results (CLAUDE.md), so add a file `data/SUPERSEDED_STATEMENTS.md`, and a pointer to it in main.tex §Reproducibility, listing where the paper overrides the study note:
     - (i) `result.json` `rigorous_for` and FEASIBILITY.md §0/§6 "rigorous ... ≤4 parameters" are replaced by "Tier C lemma + Tier X floating-point evaluation, for classes invariant under the 60° rotation on hexagonal pyramids (or axial/radial); the number of parameters is not a hypothesis".
     - (ii) The "A" tier means C.
     - (iii) The note's "33 configurations" should read 32.
     - (iv) "cannot even certify W ≥ W_fcc" and "nor even exclude energies between bcc and fcc" are withdrawn. Since W_bcc < W_fcc no valid bound certifies W ≥ W_fcc; the gap comparison is scale context only.
     - (v) The note's labels "D6 bound / D6 group average / hex_D6" denote the single-rotation pair bound of Lemma 3(ii), not a D6 group average.
   - The alternative is to drop data/FEASIBILITY.md and data/result.json from the upload.

2. **As written, the Euler-count "transfer" (G4, §6.1, C-0014/C-0015) fails for non-simple cells, and the fix is missing from the paper.** With weight K(6 - n_F) and K ≤ 0, a cell with Σ_F(6 - n_F) ≥ 12 contributes K·Σ(6 - n_F) ≤ 12K. That is the unfavourable direction: fcc and hcp cells give 24K. In 2D, by contrast, Euler's inequality caps the number of sectors at 6N and so points the favourable way for K < 0. The study note (FEASIBILITY.md G4) restores the claim by restricting to simple tessellations, using density of generic configurations and continuity of W_N, but the paper dropped this.
   - Exact fix: after "The count therefore transfers with K ≤ 0 as in 2D" (main.tex line 259–260), add: "Unlike 2D, the Euler inequality Σ_F(6-n_F) ≥ 12 points in the unfavourable direction for K ≤ 0 (non-simple cells such as those of fcc and hcp give 24K). The transfer therefore uses an extra step: configurations with simple Voronoi cells are dense, and W_N is continuous on separated configurations, so it suffices to prove the bound for simple tessellations, on which Σ_F(6-n_F) = 12 exactly; the certificate domain must then include a margin below the separation distance (as the planar proof's b = 0.28209 < d_* does) to cover nearby perturbations."
   - Also add the same sentence to the C-0015 ledger statement, and rebuild the ledger and gate.

## NONBLOCKING (required before or at release unless noted)

1. **The fcc–bcc gap is hand-typed.** It is `gap = 8.969424e-05` in code/n3_green_obstruction.py l.252, and make_all.py l.53 reads it from N3. n1 computes 8.969202e-5. With the computed value, 2 × gap = 1.793840e-4, which matches Muratov–Novaga's 1.7938403e-4 to 7 digits. With the typed value the paper prints 1.7939e-4 against 1.7938e-4. Fix: make_all.py should use `N1["structures"]["fcc"]["gap_above_bcc"]` for BGapFcc, BTwoGap and the ratios. The ratios change only in the 5th digit, so the printed 0.98 and 1.18 are unchanged. Also: the 2D energies -4.1171606 and -4.1504128077 in `two_d_reference` are typed without a source. Give the source or compute them. Either way, soften "nothing is typed by hand" (§4 line 219, make_all docstring) to "except the quoted MN margin and the 2D lattice energies (source: ...)".
2. **The rotation-convention control has now been run.** Replace "a non-radial R-invariant control would, and was not run" (§4 line 230; Limitations line 297) with the auditor's result, or add the control to the code. Auditor's values, /tmp/b3audit/ctl.py, 2^16 points in one hexagonal pyramid: invariant non-radial field gives hier 5.4e-35; cos6ψ gives hier 3.0e-37 and axial 2.8e-7; cos3ψ gives hier 1.29994e-4, equal to its full Dirichlet energy 1.29994e-4. Label it as an independent-auditor result.
3. **MC error model.** State that the reported s.e. is the iid formula applied to one scrambled-Sobol sequence per seed, a heuristic. Two replicates are not a confidence interval. Also report that the 2D reference (`two_d_reference`, plain MC with 4e5 points) has no s.e. and that its MC hexagon area is 1.0011.
4. **Ledger and paper disagree on Lemma 3(i).** Ledger C-0011 says "closed cone field N(x)", the paper says "subspace". For a cone the bound is dist(∇h, N(x))², not |P_{N⊥}∇h|². Align on "linear subspace", which is all that is used.
5. **Limitations, line 298.** "A group average over the full dihedral group ... would give larger bounds". Reflection invariance of the piece-intrinsic class is not established: oriented in-face data need not be mirror-symmetric. Say "the cyclic group C6", or justify reflection invariance.
6. **§4.3, line 215–216.** Replace "so a certificate from these classes would not be able to separate bcc from fcc by energy alone" with "so the best certified constant from these classes lies below W_bcc by at least about the fcc–bcc gap; such a certificate could not exclude a hypothetical configuration whose energy is below W_bcc by less than that amount".
7. **§4.2, line 180.** "The face trace is representable by an in-face Chebyshev-type ansatz" is untagged. Tag it as C, and note that only modes ≤ 8 were measured.
8. **Lemma 2 hypothesis.** "for every configuration" should read "for every configuration to which the method applies (in the planar architecture: separated configurations, G13)". Add "bcc is separated (nearest-neighbour distance ≈ 1.091 > R ≈ 0.620), so the lemma applies to it."
9. **Audit status.** The AI-assistance disclosure (lines 40–42), Limitations "No audit" (line 302) and publication_meta.json `description` / `notes` ("no independent AI audit") must be updated to say that one independent AI audit (this file, verdict ACCEPT_WITH_CORRECTIONS) was done. No human audit has been done.
10. **Abstract, line 52.** Replace "\textbf{Outcome: no, with a precise scope.}" with "\textbf{Outcome: negative for the literal transcription (radial, axial and piece-intrinsic trial classes); only heuristically negative for richer classes.}"
11. **publication_meta.json.**
    - Add related identifiers for arXiv:1504.01153, 2202.09240, 2610.28547 and math/9811079 (cited) and for arXiv:2103.01622 if NB-2 / the literature check is cited.
    - Confirm that creators, license and upload type are supplied by the publish script, since they are absent here.
    - result.json `gap_hcp_minus_bcc: 0.00014692` should be 0.00014691 (n1: 1.469092e-4). This is cosmetic and lives in the study file, so note it in SUPERSEDED_STATEMENTS.md.
12. **§2 and C-0019.** "We did not re-read the manuscript for this paper" can be complemented: "an independent audit re-read 04-calibration.tex (Lemmas cal:stationarity, cal:energy-identity, eq. cal:trial-potential) and found the description of G5–G9 accurate".
13. **Optional.** Cite an independent source for the Madelung values, for example arXiv:2103.01622 Table III, so that the "literature Madelung constants reproduced" control does not rest only on constants typed into n1_energies.py.

14. **Residual plan (§7, lines 276 and 284) overstates what the radial ceiling means.**
    - "Is in principle reachable without angular data" is too strong. W_bcc - 3.09e-3 ≈ -1.4473 is a ceiling evaluated at bcc only, and the slack behind it is itself only a lower bound. A real radial certificate must hold at the worst configuration, so its constant could sit anywhere at or below -1.4473. Replace with: "is an upper limit for the radial class; whether any radial certificate approaches it is untested."
    - Kill criterion, step 3 ("does not beat the radial-only ceiling ≈ -1.4473"). This compares an achieved axial constant with a radial *ceiling*, so it can kill a plan that beats every achievable radial certificate. Compare instead with Lieb–Narnhofer's -1.4508, or with an actually certified radial constant.
15. **Table 2 caption** says the seeds "agree to about 10⁻⁷". That holds for the axial and hierarchical rows only; the radial row differs by 4.0e-6, which is within 1 s.e. (9.2e-6). Add "(radial: 4×10⁻⁶, within one standard error)".
16. **Macro bug in make_all.py.** `\BSqSixC` equals `\BSqFourC` (5.85e-3) in gen_numbers.tex. The square face has no cos6ψ mode, so this is a mislabelled macro. It is unused in main.tex. Remove it or fix it.

**PDF check (main.pdf is what gets published).**
- main.pdf (02:56:47) is newer than main.tex (02:55:44), gen_numbers.tex (02:56:35) and all three figures (02:56:38–41).
- main.log has 0 "undefined" warnings.
- pdftotext shows no "??".
- The macro values appear rendered: for example 8.751 occurs 4 times, and "1.7939 × 10⁻⁴ ... 1.7938 × 10⁻⁴" appears as in the source.
- Conclusion: the build is current and clean. It still has to be rebuilt after the corrections above.

## Reproduction of this audit
- `taskset -c 6,7 .venv/bin/python -I /tmp/b3audit/n1_energies.py` (a copy of code/ with ewald3d.py), then `cmp` against code/n1_energies.json: identical.
- `.venv/bin/python -I SocrateAI-Scientific-Elenchus/tools/citation_check.py ledger/citations/claim_<k>.json /home/callensxavier_gmail_com/p2-b3-sources/<src>.txt` for mn_thm1, mn_prop6, lw_thm11 and rs_thm1: ACCEPTED, rc 0.
- `/tmp/b3audit/ctl.py` (the rotation control above) imports a scratch copy of code/n3_green_obstruction.py.
