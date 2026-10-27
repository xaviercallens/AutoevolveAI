# Independent adversarial audit of C1 (papers/p4_amplifier_census)

Auditor: an independent AI audit agent (producer != verifier), 2026-10-27. No human has audited this paper.
Scope: main.tex / main.pdf, ledger/, data/ (code, logs, census JSONs), publication_meta.json, formal_cert/Programmes/AmplifierCensus/.
Scratch: /tmp/c1audit/. Scripts are in /tmp/c1audit/scripts/ and outputs in /tmp/c1audit/out/.
I wrote only two files in the repository: this file and `data/leanchecker_replay_audit.json`. I made no git writes.
I did not write to the shared olean dir `certified_numerics_olean`: every olean I built went to /tmp/c1audit/olean.

## VERDICT: ACCEPT_WITH_CORRECTIONS

I found no mathematical error. The headline stands as scoped (Tier C):
- no connected unweighted graph with N <= 10 has N_eff > N under death-Birth updating;
- Richter's graph J?ouPjI[@i? (N = 11) has N_eff = 2668552698098/242579025123 > 11;
- hence, under Allen's weak-selection criterion, the smallest such amplifier has 11 vertices.

What supports it:
- **Census.** I wrote my own solver, with a method different from the producer's: exact batched modular Gauss-Jordan plus CRT, with no floats in the decision. It agrees on every count.
  - N = 3..7: networkx atlas.
  - N = 7, 8, 9: a fresh `nauty-geng -cq`. The N = 9 run covers all 261,080 graphs.
  - N = 10: a uniform random sample of 20,000 graphs, plus all 177 graphs the producer singles out.
- **Lean.** The Lean modules rebuild from source into a private olean dir. They are byte-identical to the producer's, and the axioms are within the whitelist.
- **Kernel replay.** The leanchecker replay passes on **all five** modules: **rc 0**.
- **Exact checks.** The worked examples, the slope identity on 5 graphs, the four certified finite-r signs and both bisection endpoints all reproduce with my own exact code.

The corrections below concern sourcing, one wrong count, rounding direction, two literature discrepancies that need rewording, and stale status lines. None changes a mathematical claim.

## BLOCKING

None.

## NONBLOCKING (with exact fixes)

1. **Allen eq. (3) is NOT an open discrepancy. The published version prints the correct formula.**
   arXiv v1 (p. 6) prints `3r - 1 + r^{-(N-1)} - 3r^{-(N-2)}`. The published PLoS Comput. Biol. 16(1):e1007529 (printable PDF, p. 4, Eq (3)) prints `3r - 1 + r^{-(N-3)} - 3r^{-(N-2)}`. That is the form the exact chain, Kaveh eq. (20) at d = 1, Hindersin–Traulsen SI eq. (18) and Richter 2020 eq. (12) all agree with.
   My own exact 2^N chain agrees with the r^{-(N-3)} form, and disagrees with the v1 form, on C4, C5 and C6 at r = 5/4 and r = 3/4 (6/6 cases).
   So the v1 misprint was corrected before publication. Fixes:
   - main.tex:294: replace "We report the disagreement and do not assert whose error it is; ... has not been raised with the authors" with "arXiv v1 misprints the exponent; the published version (PLoS CB 2020, Eq (3)) has r^{-(N-3)} and agrees with the exact chain".
   - main.tex:338 (Limitations, "Open discrepancies"): drop eq. (3).
   - Update ledger AMC-C-0007 to match.
   - The paper cites the published version (main.tex:359) but says "(v1 read)". It should say that eqs. (5)-(9) and the definitions are identical in the published version. I checked this (published pp. 4-6).
2. **Richter's r_max is a second discrepancy, not "a different quantity".** main.tex:257 says Richter "reads r_max ≈ 1.00075 off a figure; our bracket is a different, certified quantity".
   Richter states r_max ≈ 1.00075 in his text (2008.01446v1 p. 8: "For the interval 1 < r < r_max ≈ 1.00075, the fixation probability of the graph is larger...") and in the Fig. 1 caption. It is the same crossing.
   The paper's own certified signs contradict it: (+) at 1.0007, 1.000775 and 1.0008125. I certified (+) independently at r = 1251/1250 = 1.0008 (ρ_G − ρ_K = 7.826e-10, error bound 2.5e-28) and at 16013/16000.
   Fix: "Richter states r_max ≈ 1.00075 (text p. 8 and Fig. 1); our certified (+) signs at 1.0007-1.0008125 and the bracket [1.0008233, 1.0008235] place the first sign change above that value. Richter's value is approximate (read near the resolution of his Fig. 1b); it is inconsistent with the certified signs, and the cause was not investigated (cf. τ_max)". Add it to main.tex:338.
3. **Rounding direction of the bracket.** main.tex:238 and main.tex:274 (and ledger AMC-C-0012) write the certified interval as [1.00082334, 1.00082349].
   The exact lower endpoint is 10248431/10240000 = 1.000823339844, so the decimal lower end is rounded *inward*. Fix: [1.00082333, 1.00082349], or write "≈" and give only the exact fractions.
4. **Wrong count in the slope control.** main.tex:287 says "on 163 graphs (every 40th) at N=7". The ledger AMC-C-0006 and data/RESULT.md:107 say "(163 graphs)" for the N = 7 subsample.
   data/code/controls.py:70 iterates `geng(7, [])[::40]`, which is 22 graphs, and the recorded `"graphs": 163` (controls.json:36) is the running total: 141 (all of N = 3..6) + 22.
   Fix: "on all 141 connected graphs with N = 3..6 and on 22 graphs (every 40th) at N = 7, 163 in total".
5. **Bibliography.** I opened every cited arXiv id. Corrections:
   - `tk` (main.tex:362): the first author is **J.** Tkadlec (Josef), not V. Title: "Limits on amplifiers of natural selection under death-Birth updating", PLoS Comput. Biol. 16(1):e1007494 (2020); arXiv:1906.02785. Authors: J. Tkadlec, A. Pavlogiannis, K. Chatterjee, M. A. Nowak.
   - `rich20` (main.tex:360): arXiv title "Constructing transient amplifiers for death-Birth updating: A case study of cubic and quartic regular graphs" (v1, 4 Aug 2020). Svoboda et al. ref. [17] and Richter 2022 ref. [51] cite what appears to be its journal version: "Spectral analysis of transient amplifiers for death–birth updating constructed from regular graphs", J. Math. Biol. 82, 61 (2021).
   - `rich22` (main.tex:361): "Spectral dynamics of guided edge removals and identifying transient amplifiers for death-Birth updating", arXiv:2204.12861. Svoboda et al. ref. [31] cites J. Math. Biol. 87(1):3 (2023).
   - `svo` (main.tex:365): "Amplifiers of selection for the Moran process with both Birth-death and death-Birth updating". J. Svoboda, S. Joshi, J. Tkadlec, K. Chatterjee. PLoS Comput. Biol. 20(3):e1012008 (2024), as cited in arXiv:2512.11164 ref. [40].
   - `bre` (main.tex:366): "Fixation location in structured populations". D. A. Brewster, G. Lippner, J. Tkadlec, M. A. Nowak. arXiv:2605.26411v3 (28 Jun 2026). It is Bd only, as the paper says.
   - These are correct as given: `allen`, `ht` (arXiv v2), `kav` (title and authors), `iso` (doi:10.5281/zenodo.23660071 resolves; Zenodo record 23660071 is "The isothermal theorem of evolutionary graph theory for birth-death updating, kernel-checked in Lean 4…", X. Callens, 2026-10-26), `mathlib` (arXiv:1910.09336) and `oeis`.
   - Drop the four "Title not re-verified" notes once the titles above are inserted.
6. **Novelty paragraph: Richter's ref. [6] is identifiable.** main.tex:331 says "Richter's ref. [6] (all graphs with N ≤ 10, Bd) was not identified".
   It is B. Allen, C. Sample, P. Steinhagen, J. Shapiro, M. King, T. Hedspeth, M. Goncalves, "Fixation probabilities in graph-structured populations under weak selection", PLoS Comput. Biol. 17(2):e1008695 (2021). From the PLoS article page (read via a fetch summary, not in full): its exhaustive analysis of all connected graphs up to size 10 is for **Birth-death** updating only. No exhaustive dB result was reported in what I read.
   Richter 2022 also cites, as ref. [2], Alcalde Cuesta, González Sequeiros and Lozano Rojo, "An accurate database of the fixation probabilities for all undirected graphs of order 10 or less" (IWBBIO 2017, LNCS 10209, pp. 209-220). I could not open that chapter.
   Its companion, "Suppressors of selection" (PLoS ONE 12(7):e0180549, 2017, same authors), computes all undirected graphs of order <= 10. It states: "we are only concerned here with the evolutionary dynamics of graphs under birth-death updating".
   I found no prior exhaustive N <= 10 dB weak-selection statement:
   - alphaXiv searches found none.
   - Neither did the 10 papers read: Allen 2019/2020, Allen 2021, Richter 2020 and 2022, Tkadlec 2019, Hindersin–Traulsen, Kaveh, Svoboda, Brewster 2026, and Brewster et al. arXiv:2512.11164.

   Note for context: the Tkadlec v1 abstract says "computer-assisted exhaustive searches have failed to discover amplification". The citation is to Hindersin–Traulsen, who classified random graphs (not all graphs) on an r-grid, so it is not an exhaustive weak-selection census.
   This is not a priority finding either way. Fix: replace the main.tex:331 sentence with the identification above and cite Allen 2021 and Alcalde Cuesta 2017 (Bd).
7. **Quote attribution.** main.tex:88 attributes "the smallest known unweighted dB-amplifier" to Richter and Svoboda jointly. That wording is Svoboda et al. (p. 5).
   Richter 2020 (p. 6) writes "The smallest graph for which N_eff > N was found is the quartic graph with size N = 11", meaning within his regular-input search.
   Richter 2022 (p. 8) writes "For regular graphs with N ≤ 10 vertices no transient amplifiers ... were found using the method". Fix the attribution accordingly.
8. **τ_max discrepancy is still unexplained (one hypothesis eliminated).** I confirm the parent's maximal remeeting time independently: 10066/569 = 17.690685, at vertex 9. The N = 12 cubic parent gives 18.294102.
   The hypothesis that Richter printed the *perturbed* graph's value is ruled out: max τ_i is 20.158191 on R11 and 22.067125 on the N = 12 amplifier.
   The identification of the graph is otherwise solid:
   - normalized-Laplacian λ₂(R11) = 0.056700 and k̄ = 3.8182, which equal Richter 2022 Fig. 1(a) (λ₂ = 0.0567, k̄ = 3.8182, N_eff = 11.0008, δ(G) = 3);
   - Richter 2020 Table 1 has A₄(11) = 1;
   - the four removals at vertex 9 are pairwise isomorphic (networkx), and R11 is isomorphic to them.

   Fix: add "the perturbed-graph values (20.158, 22.067) do not match either" to main.tex:222.
9. **Producer replay coverage.** main.tex:310 (and publication_meta.json "notes") say the producer replayed only Richter11 and Controls. The producer's record names only those two modules. Whether that replay also covered the imported Core.lean (which holds `eq5_unique` and `diff_nonpos`) depends on leanchecker's import semantics, which I could not settle (`leanchecker --help` did not print usage). The near-equal replay times, about 57-74 s per module, suggest that the imported environment is replayed too. My replay covers Core, DataR11, DataP11, Richter11 and Controls explicitly (all rc 0).
   Fix: cite data/leanchecker_replay_audit.json and list all five modules.
10. **Stale status lines after this audit.**
    - main.tex:40-42 ("No independent audit of any kind ... the producer-is-not-verifier recompile is pending");
    - main.tex:326 ("There is no AI audit either");
    - main.tex:335 ("No independent audit");
    - publication_meta.json "notes" ("no independent audit").

    Fix: cite this AI audit and the replay. Keep "no human audit" and "no statement lock", which remain true. The four LEDGER_UNAUDITED_TIER_A flags remain correct, because no *person* has certified the statements. I did not edit the ledger.
11. **Overflow guard in the enclosure (the only route I found to a wrong exclusion).** data/code/census_enclosure.py:118-121 casts `np.rint(x * 2^30)` to int64 and forms `A_s t` with an int64 `einsum`, without checking finiteness or magnitude.
    The rule is fail-safe against bad but finite floats:
    - a poor proposal only raises E and blocks exclusion;
    - `e < two31` is checked at line 157.

    A NaN or huge proposal, however, could wrap around in int64 and produce a small fake E. For realistic data this cannot happen: τ ≤ ~10^2 gives |t| ≤ 2^37 and row sums of |A_s t| ≤ ~2^50. My modular census agrees on every graph rechecked. But the hand proof should state the precondition.
    Fix: add `assert np.isfinite(x).all() and np.abs(t).max() < 2**50` before line 119, and one sentence in Step 5 (main.tex:145).
    I tried to break the rule with adversarial proposals (/tmp/c1audit/scripts/adversary.py, reimplementing lines 157-158 verbatim). The proposals were shrink, noise, edge-only shrink and random one-sided perturbations, at sizes 2^-4..2^-34, 384 trials per graph, on R11 (N_eff > N), the quartic parent, C10 and Petersen (N_eff = N), and K10 − e.
    The result: 0 wrong exclusions, 0 violations of the claimed bound |N̂ − N_eff| ≤ E X / (2^30 (2^31 − E)), and 210/384 correct exclusions of K10 − e.
12. **Reproduction commands do not run as printed.** main.tex:346 pipes `nauty-geng -c N | python -I code/census_enclosure.py N`. The script reads a *file* and needs `<graph6 file> <N> <shard> <nshards> <out.json>` (census_enclosure.py:1).
    Fix: print the real invocation, e.g. `nauty-geng -cq 10 > g10.g6; python -I code/census_enclosure.py g10.g6 10 0 1 enc10.json; python -I code/finish_candidates.py enc10.json census_n10.json`.
    For the record: my fresh `nauty-geng -cq 10` output has sha256 bf530d38…0ab5, which **equals** the hash the producer recorded for .scratchpad/C1/geng_c10.g6 (data/result.json:395).
13. **Minor.**
    - **Timing.** main.tex:91 says "about 24 minutes" for N = 10, while main.tex:355 says 1237 s (20.6 min) for the enclosure. Say "1237 s enclosure plus the candidate solves".
    - **Gap column, N = 9 rounded up.** The "smallest gap" column (main.tex:180) and main.tex:152 give 0.0174 for N = 9, described as a certified lower bound ("at least"). The exact gap is 13/748 = 0.0173797 (graph H]~v~z~, N_eff = 6719/748), which is *below* 0.0174. The same happens at N = 4: 7/45 = 0.155556 is printed as 0.1556 (main.tex:175, :194). The other rows are rounded correctly. Fix: print 0.0173 (or 13/748) at main.tex:152, :180 and :199 and in ledger AMC-C-0002/-0005 (ledger.json:83, :120), and 0.1555 (or 7/45) at main.tex:175 and :194 and in AMC-C-0005. Optionally replace the float readings at main.tex:199-200 by the exact values 6719/748 (N = 9) and 6257/627 (N = 10). N = 10 is fine: 13/627 = 0.0207337 >= 0.0207, so the abstract's "at least 0.0207" holds. More generally, round lower bounds down.
    - **ControlsMustFail.** It fails at elaboration ("did not reduce to isTrue or isFalse"), not by a kernel `false` verdict, as main.tex:301 already admits. It shows only that the claim is not provable this way. The decisive control is `ctl_perturbed_vector_rejected`, which is kernel-checked and replayed.
    - **Allen page numbers.** main.tex:92 says "pp. 5, 7–8". The definitions are on v1 pp. 6 and 8.

## What I checked, and how

### (1) Criterion and model (Allen et al. 1906.01036v1, and the published PLoS version)
- **Equations.** Eq. (5) τ_ij = 1 + ½Σ_k(p_ik τ_jk + p_jk τ_ik) for i≠j, with τ_ii = 0 and p_ij = w_ij/w_i (= 1/k_i unweighted). Eq. (6) τ_i = 1 + Σ_j p_ij τ_ij. Eq. (7) Σπ_i²τ_i = 1. Eq. (8) ρ_G(1+δ) = 1/N + δ(N_eff−2)/(2N) + O(δ²), proved for weighted, undirected, connected graphs with no self-loops under dB with uniform initialization (Appendix B). Eq. (9) N_eff = Σπ_iτ_i. The definition (v1 p. 8, PLoS p. 6) is "amplifier of weak selection if N_eff > N".
- **Match to the paper and the Lean.** main.tex:117-123 and Core.lean `Eq5`/`remeet`/`neff` transcribe these exactly, including the ½ and π_i = deg_i/Σdeg.
- **Edge identity.** Eq. (edge) N_eff = 1 + (1/m)Σ_E τ_ij is exact algebra (π_i p_ij = 1/2m).
- **Worked examples, independently, with pure Fractions on eq. (5) (smallchecks.py):**
  - P3: τ01 = 5/3, τ12 = 8/3, all τ_i = 8/3, N_eff = 8/3.
  - K4 − e: N_eff = 173/45.
  - K3: N_eff = 3.
  - Stars S_n for n = 2..9: N_eff = 4n/(n+1) in all 8 cases.
  - Eq. (7) gives exactly 1 on P3, K4 − e and R11.
- **Slope identity against an independent exact chain.** I ran the full 2^N-state dB chain in Fractions and took the exact derivative (I−Q)x' = b' + Q'x at r = 1. The chain slope equals (N_eff−2)/(2N) **exactly** on 5 graphs:
  - P3: 1/9;
  - K4 − e: 83/360;
  - star S5 (N = 6): 1/9;
  - an irregular N = 6 "lollipop": 7444719/26738348;
  - C5: 3/10.

  K_N chain = closed form (N−1)/N·(1−1/r)/(1−r^{1−N}) = 1-D formula for N = 4, 5, 6.
  (My first chain draft omitted self-loop probabilities and failed every check. I caught that with K3/C4 controls before using any number.)

### (2) Census recheck (modcensus.py: exact, different method)
- **Method.** For each graph, I built the integer system 2k_ik_jτ_ij − k_jΣ_{k~i}τ_jk − k_iΣ_{k~j}τ_ik = 2k_ik_j.
  - I solved it by batched Gauss-Jordan modulo 18 primes below 2^31 (numpy int64, vectorised over graphs).
  - I recovered det and S = Σ_E y_e (Cramer numerators) by CRT. The number of primes was chosen per batch from a Hadamard bound; the worst case was 372 bits, against ~558 available.
  - N_eff = 1 + S/(m·det) is exact. Zero graphs needed the Fraction fallback.
  - A float64 solve served only as a cross-check of the reconstruction: max |float − exact| = 8.9e-15.
- **Results.**

| N | source | graphs | N_eff>N | =N | <N | regular | regular≠N | non-regular =N | min gap (exact) | nearest |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | atlas | 2 | 0 | 1 | 1 | 1 | 0 | 0 | 1/3 | P3 |
| 4 | atlas | 6 | 0 | 2 | 4 | 2 | 0 | 0 | 7/45 | K4−e (173/45) |
| 5 | atlas | 21 | 0 | 2 | 19 | 2 | 0 | 0 | 0.0753425 (= 11/146) | |
| 6 | atlas | 112 | 0 | 5 | 107 | 5 | 0 | 0 | 0.0612245 (= 3/49) | |
| 7 | atlas and fresh geng | 853 | 0 | 4 | 849 | 4 | 0 | 0 | 0.0318119 (= 23/723) | |
| 8 | fresh geng | 11,117 | 0 | 17 | 11,100 | 17 | 0 | 0 | 0.0330330 (= 11/333) | |
| 9 | fresh geng (all) | 261,080 | 0 | 22 | 261,058 | 22 | 0 | 0 | 13/748 = 0.0173797 | H]~v~z~ (6719/748 = 8.982620) |
| 10 | sample: 20,000 uniform (seed 20261027) + 177 producer-listed | 20,177 | 0 | 167 | 20,010 | 167 | 0 | 0 | 13/627 = 0.0207337 | I^~~~~~~w (6257/627) |

- **Cross-checks against the producer and OEIS.**
  - The graph counts equal OEIS A001349, which I fetched: 1, 1, 1, 2, 6, 21, 112, 853, 11117, 261080, 11716571.
  - My fresh geng -c 10 produced 11,716,571 lines.
  - The regular counts 1, 2, 2, 5, 4, 17, 22, 167 equal OEIS A005177 (fetched: a(3..10) = 1, 2, 2, 5, 4, 17, 22, 167).
  - All 167 N = 10 regular graphs give N_eff = 10 exactly.
  - The producer's 10 nearest-to-N non-regular graphs at N = 10 all have N_eff < 10. The top three are 6257/627, 165658/16605 and 5862575162/587783105, which match the producer's floats 9.979266, 9.976393 and 9.974045.
  - The exact nearest gaps for N = 4..8 equal the producer's table values (main.tex:193-198).
  - Structure check (networkx complement): the complement of H]~v~z~ is a 4-edge matching, so it is K9 minus a maximum matching. The complement of I^~~~~~~w is one edge, so it is K10 − e. This confirms the descriptions at main.tex:199-200.
- **Rigor of the producer's integer residual bound (census_enclosure.py:1-15, 105-160), from reading.**
  - The unscaled system is (I−M)τ = 1 with M = ½p ≥ 0. Rows sum to ≤ 1, and the deficit is mass that hits the diagonal.
  - For a connected graph, one lazy walker step changes the distance by ±1, so the diagonal is reachable from every pair. Hence ρ(M) < 1, (I−M)^{-1} = ΣMⁿ ≥ 0, and (I−M)^{-1}1 = τ.
  - Scaling: each row was multiplied by 2k_ik_j ≥ 2, so ‖r‖∞ ≤ E/2^31. This is correct.
  - The componentwise bound |τ−x̂| ≤ ετ, together with τ_max ≤ x̂_max/(1−ε), gives the integer test at line 158. I re-derived it, and it equals N̂ + E X/(2^30(2^31−E)) < N.
  - The `e < two31` guard is present (line 157).
  - Regular graphs are never excluded (`ok and not regular`) and always go to the exact finisher, so the "= N" class is exact.
  - It covers every graph and every rounding case, subject to the int64-overflow precondition in NB-11.
  - Adversarial tests: see NB-11 (0 counterexamples).

### (3) Lean
- **Sources.** The sha256 of all six files equal main.tex:313-318, and data/lean/ is identical to the formal_cert sources (diff -r).
- **Grep.** I searched for `skipKernelTC|addDecl|native_decide|implemented_by|extern|#exit|set_option|debug.|unsafe|opaque|axiom|sorry|elab|macro|run_cmd`. The only hits are the planted `sorry` and `axiom ctl_cheat` in Controls.lean, plus comment and `#print` lines.
- **Fresh private build (core 4; oleans in /tmp/c1audit/olean, FIRST on LEAN_PATH, pinned Lean 4.34.1).**
  - Core rc 0, DataR11 rc 0, DataP11 rc 0, Richter11 rc 0, Controls rc 0.
  - ControlsMustFail **rc 1**.
  - All five oleans are **byte-identical** to the producer's.
- **`#print axioms`.**
  - R11_amplifier, P11_isothermal and eq5_unique: exactly [propext, Classical.choice, Quot.sound].
  - The three real controls are standard.
  - ctl_sorry reports sorryAx, and ctl_axiom reports AmplifierCensusControls.ctl_cheat. Both planted cheats are caught.
- **Pinned wrapper.** `taskset -c 4,5 python3 scripts/certified_numerics/lean_pinned.py compile formal_cert/Programmes/AmplifierCensus/Richter11.lean --json-out /tmp/c1audit/out/pinned_richter11.json`: rc 0, 27.8 s, the same three axiom lines.
- **Kernel replay (leanchecker 4.34.1 on my oleans): rc 0 for all five modules.** Core 62.5 s, DataR11 56.7 s, DataP11 61.2 s, Richter11 74.4 s, Controls 59.2 s. Details are in data/leanchecker_replay_audit.json.
  Replay does not audit axioms (Controls replays with rc 0 despite its planted cheats). The axiom audit is the `#print axioms` output.
- **Faithfulness.**
  - The edge lists of `edgesR11` and `edgesP11` (DataR11.lean:12, DataP11.lean:12) equal my independent graph6 decoding of J?ouPjI[@i? and J?ouPjI{@i? exactly.
  - P11 = R11 + {0,9}. The degrees are 3 at vertices 0 and 9 and 4 elsewhere, matching `GR11_deg`.
  - The certificate ZR11/DR11 equals my exact Fraction solution of eq. (5) entry by entry (121/121).
  - My exact N_eff(R11) = 2668552698098/242579025123 = 11.000756132 (margin 7.5613e-4), and N_eff(P11) = 11. Eq. (7) gives exactly 1.
  - `R11_amplifier` is a ∀τ statement with hypothesis Eq5. It is **not vacuous**: `tauR11_eq5` is a witness.
  - `eq5_unique` is a correct maximum-principle uniqueness. I read the proof: at the pair maximising δ/v, δ_ij = c·v_ij and δ_ij ≤ c·½Σp v = c(v_ij − 1), which forces c ≤ 0. The contradiction uses the constant 1 in eq. (5), `p_nonneg` and v > 0. No row-sum bound is needed, so it holds for an arbitrary A. Its hypotheses are satisfiable (witness tauR11 with `tauR11_pos`).
  - Lean certifies the linear system only. The link to fixation is Allen eq. (8) (Tier L), as stated.

### (4) Finite r (fixcert.py: my own 2046-state dB chain in exact rationals)
- **Method.**
  - A float64 dense solve, one float refinement, then x kept as an exact dyadic vector.
  - Exact Fraction residuals ρ = b − (I−Q)x and σ = 1 − (I−Q)T.
  - (I−Q)^{-1} ≥ 0 gives |x − x̃| ≤ ‖ρ‖∞·T_max, with T_max ≤ max T̃/(1−‖σ‖∞) = 242.41-242.42. This agrees with the producer's T_max ≤ 242.43.
  - ρ_K11 comes from the 1-D product formula and equals the closed form exactly.
- **Results.** The error bounds are ≤ 7.4e-28, so every sign is decided by a margin of more than 10^15.

| r | ρ_G − ρ_K11 (mine) | producer interval | sign |
|---|---|---|---|
| 10001/10000 | 3.020619e-9 | [3.02059, 3.02065]e-9 | + ✓ |
| 2499/2500 | −2.039737e-8 | [−2.03974, −2.03973]e-8 | − ✓ |
| 10248431/10240000 (bracket low) | 1.0155868e-12 | [9.829e-13, 1.0493e-12] | + ✓ |
| 4099373/4096000 (bracket high) | −4.0344210e-12 | [−4.0563, −4.0124]e-12 | − ✓ |
| 15003/15000 (extra) | 5.207952e-9 | — | + |
| 1251/1250 (extra) | 7.826351e-10 | — | + |
| 16013/16000 | 3.697159e-10 | [3.6969, 3.6974]e-10 | + ✓ |

So the certified sign change lies in (10248431/10240000, 4099373/4096000). Uniqueness of the crossing is not claimed, and I did not check it.

### (5) Overclaims, tiers and scope
- **Title and abstract.** They are correctly qualified ("unweighted", "death-Birth", "of weak selection").
- **"The smallest dB amplifier has exactly 11 vertices"** (main.tex:53, 273). It is prefaced by "within the weak-selection criterion for unweighted graphs" and filed Tier C, the tier of its weakest part. That is correct. N = 1, 2 are trivial.
  Suggested (optional): say "amplifier *of weak selection*" in that sentence too. Richter's graph is not certified as a transient amplifier in Allen's full sense (all r in (0,1) and r > r*), only at the listed points.
- **The "What this is NOT" box** (main.tex:68-72) is accurate and sufficient. The paper claims nothing medical, weighted, directed, other update rules or finite-strength.
- **Tier assignments.** They match what was done.
  - Tier A covers only the linear-system theorems.
  - L covers Allen's criterion and eq. (8).
  - C covers the census and the finite-r certificates.
  - X covers extrapolations.

  The ledger has 22 claims (4 A, 2 L, 14 C, 2 X), as stated at main.tex:324.
- **Smaller checks.**
  - The "212 non-complete regular graphs" (main.tex:261) = 219 regular (N = 4..10) − 7 complete. Correct; I did not re-run regular_check.
  - "994 graphs" (main.tex:129) = 2 + 6 + 21 + 112 + 853. Correct.

### (6) Ledger gate, repository guards, process
- **Ledger gate.** I ran the Elenchus `tools/ledger.py ledger.json --evidence-dir evidence` with output to /tmp/c1audit/out/gate_rerun.txt. It exits 1 with 0 blocking findings and 4 flags (LEDGER_UNAUDITED_TIER_A, AMC-A-0001..0004). The output is **byte-identical** to ledger/gate_output.txt. This is the honest state.
- **Repository guards** (antigravity_guard.py, test_rigor_guard.py, pytest tests/). The producer did not run them, and neither did I.
  They test the repository's Python code base (stubs, test rigour), not this paper's scripts or Lean. No claim of the paper rests on them, and the paper says so (AMC-X-0002, main.tex:336). They do not matter for the paper's correctness.
  They would matter only if the C1 scripts were to be committed into the tested code tree: the scripts have type annotations and no stubs.
- **My own process lapses, disclosed.**
  - Several Bash calls used `cd … &&` compounds.
  - One heredoc was refused by the guard, and I rewrote it with the Write tool.
  - One call used `$?`.
  - A few short python checks ran without taskset.
  - An idle driver wrapper (drive_small.py) sat beside two busy census processes for about 20 minutes, so at most 2 processes were busy.
  - Busy work used cores 4 and 5 only.
  - None of this touched git.
