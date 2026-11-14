# Independent adversarial audit of M3 (papers/p4_yukawa_bcc_fcc_check)

Auditor: an independent AI audit agent (producer != verifier), 2026-10-27. No human has audited this paper.
Scope: main.tex / main.pdf, ledger/, data/ (code, logs, JSONs), publication_meta.json, formal_cert/Programmes/YukawaBccFcc/ (12 sources).
Scratch: /tmp/m3audit/ (my scripts: `aud_ewald.py`, `aud_misc.py`, `aud_arb.py`, `build.py`, `gen_allax.py`; outputs `*.json`, `build/`).
Repository files written: this file and `data/leanchecker_replay_audit.json`. No git writes. No write to the shared olean dir
`formal_cert/.olean_out`: every olean I built went to `/tmp/m3audit/olean`, and the shared dir was *removed* from my LEAN_PATH
(not merely shadowed), so nothing of the producer's build was reused. All processes ran under `taskset -c 4,5`, at most two at a time.

## VERDICT: ACCEPT_WITH_CORRECTIONS

No mathematical error, no discrepancy with Luo and Wei, no unsound Lean step found. The headline (YBC-C-0009: every printed number and
inequality that was checked holds) stands as scoped. Corrections concern one unfair characterisation of the authors' Lemma A.3 endpoints,
precision of the "seventeen statements" wording, listing which Lean statements are weaker than the printed ones, a broken reproducibility
recipe, and status lines that this audit makes stale.

### What I checked with my own code (independent of the producer's scripts)

1. **Paper read** (arXiv 2610.31456v1 via alphaXiv, pp. 1-2, 4, 9, 11, 13, 19, 22-27). Definitions (1.2): L_F = 2^{-1/3} D3, L_B = L_F^*,
   a = 2^{1/6}; Lemma A.5 (A.6)-(A.8), Lemma 6.1 proof, Lemmas A.1, A.3, A.4, A.6 compared line by line with the Lean sources (item list below).
   arxiv.org/abs/2610.31456 fetched: v1 only, **no ancillary-file section**, no comments field. The producer's statement (main.tex:69, 274)
   that the A.4 partition data are not public is confirmed, although the paper (p. 4, p. 25) says they "accompany the manuscript".
2. **Shell multiplicities** re-enumerated by brute force over Z^3 (|m|^2 <= 640): (N_1..N_12) = (12,6,24,12,24,8,48,6,36,24,24,24) and the
   17 nonzero M_l (l <= 48) = paper's table = Lean table, exactly. N_n < 30n (n <= 320) and M_l < 30l (l <= 640) hold on that range.
   The normalisation is right: |v|^2 = 2^{-2/3}|m|^2 on D3 gives squared length 2^{1/3}n at |m|^2 = 2n (even norm forces even coordinate
   sum, so "integer triples of norm 2n" = D3 vectors), and L_B = 2^{-2/3}{same parity} gives 2^{-4/3}l.
3. **kappa\* by a fourth, structurally different method**: the classical Yukawa Ewald split with a free splitting parameter eta
   (erfc real-space kernel, reciprocal 4pi e^{-(G^2+k^2)/4eta^2}/(G^2+k^2), self term 2eta/sqrt(pi) e^{-k^2/4eta^2} - k erfc(k/2eta)), mpmath 70 digits.
   Self-checks: G at eta = 1 and eta = 1.3 agree to < 5e-70; against a direct real-space sum at kappa = 6, |diff| < 1.1e-40.
   **kappa\* = 1.71792186846990386425087416660628171879468538** (identical at eta = 1 and 1.3).
   This agrees with the producer's (E) 1.717921868469903864250874 +/- 1.67e-25 and (Q) 1.71792186846990386425087416661 in every printed digit,
   lies in (D)'s interval and in (A.9). G'(kappa\*) = 1.566242612e-4 (paper: 1.566e-4).
   (Disclosure: my first run computed the lattice scales 2^{-2/3}, 2^{-4/3} at 15 digits before raising the precision, which gave an
   eta-dependent 1e-17 error and kappa\* = 1.71792186847053; it was discarded and rerun with all constants at 70 digits.)
4. **Lemma A.6 in my own ball arithmetic** (python-flint 0.9.0 arb, 300 bits, same Ewald split, rigorous tails from erfc(x) <= e^{-x^2}
   and r_3(k) <= 18k, all shells |m|^2 <= 400 enumerated): G(1.717921868469903) = [-1.35362654688e-19 +/- 3.3e-31] < -1e-19 and
   G(1.717921868469904) = [2.12616065470e-20 +/- 5e-33] > 1e-20; controls ...902 -> -2.9199e-19, ...905 -> +1.7789e-19; identical balls at
   eta = 1 and 1.25. Both printed signs of Lemma A.6 hold. (Disclosure: the venv has no flint; I used system `python3 -I` with an explicit
   sys.path entry for the already-installed `~/.local` flint 0.9.0. Nothing was installed. The version differs from the producer's 0.6.0,
   which makes the cross-check more independent, not less.)
   Paper's truncation, recomputed by me (`aud_trunc.py`, mpmath 50 digits, shell expansion of eq. (6.3), p. 23:
   G = sum_{L_B}(I - J) - sum_{L_F}(I - J), I by quadrature, J closed form, FCC n <= 12, BCC l <= 48):
   G_trunc(903) = -1.35362683011e-19, G_trunc(904) = 2.12615782248e-20 (producer: -1.35362683e-19, 2.12615782e-20). With the printed
   tail: -1.35362683e-19 + 7e-21 = -1.2836e-19 < -1e-19 (slack 2.84e-20); 2.12615782e-20 - 7e-21 = 1.4262e-20 > 1e-20 (slack 4.26e-21).
   True omitted tail = my arb G_full - G_trunc = 2.832e-26 at both kappa (producer: 2.83e-26). This also confirms that my eta-Ewald and the
   paper's (6.3)/(2.4) representation compute the same G.
5. **Tail rational** of A.6: exact Fraction value 6.52669862e-21 < 7e-21 (confirmed). The bound is valid: by (6.3) each omitted vector
   contributes I - J with I, J >= 0, so with |I - J| <= max(I,J) <=
   e^{-pi q}/(pi q), N_n < 30n, M_l < 30l the true majorant is 3.48e-22 (6.95e-22 with the paper's I + J counting, factor 60), so the printed
   7e-21 is conservative by an order of magnitude.
6. **Lemma A.5 in mpmath (40 digits), all 3000 cells**: min slack (A.6) 7.52141e-4 at j = 999, (A.7) 7.64588e-5 at j = 0, (A.8) 0.142967.
   Matches main.tex:145-146, 246. Lemma 6.1 constants: e^{-pi a^2} = 0.019098 < 1/49 = 0.020408, e^{-pi 2^{-4/3}} = 0.28744 < 3/10,
   pi 2^{-4/3} = 1.24674 < 5/4, e^{-2.1 pi a^2} = 2.455e-4 < 1/128. True omitted tails at t = 1: FCC 3.24e-21, BCC 8.5e-25 (both << 1e-18).
7. **Lemma A.1**: P(L_F,0) = 0.0558589404898, I(16/25,0) = 0.0561633811744; FCC partial bound 0.0263452 < 26459e-6 and BCC partial bound
   0.0295353 < 29536e-6. All as printed.
8. **Lemma A.3 (A.4) endpoints**: 11/25 - e^{alpha1} = 2.0513e-16, 147/1000 - e^{alpha2} = 1.3657e-16, e^{beta} - 4/3 = 1.8728e-16 (confirmed),
   but see NONBLOCKING 1: these are deliberate outward roundings, not near-misses.
9. **IEEE double**: my own float64 Ewald gives kappa\* = 1.7179218684739 (eta 1), 1.7179218684710 (eta 1.3), 1.7179218684704 (eta 2):
   errors 5e-13 to 4e-12, about 12 significant digits. The producer's 11 digits is one method; the intrinsic limit is about
   eps*|S|/G' ~ 1e-12. See NONBLOCKING 5.
10. **Lean**: see the Lean section. **Ledger gate** rerun to stdout (not to gate_output.txt): exit 1, 0 blocking, 8 x LEDGER_UNAUDITED_TIER_A,
    identical to ledger/gate_output.txt.

## Lean

**Sources.** sha256 of all 12 sources in formal_cert/Programmes/YukawaBccFcc/ match `data/result.json`; `data/lean/` is byte-identical
(`diff -r`). Forbidden-token scan of the five main modules (`sorry|admit|native_decide|implemented_by|skipKernelTC|addDecl|axiom|unsafe|opaque|extern|csimp|macro|elab|debug.|set_option`):
one doc-comment hit (Shells.lean:8) and four `set_option maxRecDepth 100000 in` on the table definitions in Chains.lean (harmless:
elaboration recursion depth for long list literals; not a kernel or trust setting).

**Private rebuild** (`/tmp/m3audit/build.py build`, pinned Lean 4.34.1 + Mathlib d13f23b7 from lean_pinned.py, shared .olean_out removed from LEAN_PATH):
Basic rc 0 (13.5 s), Shells rc 0 (119.9 s), Chains rc 0 (76.1 s), LemmaA5 rc 0 (959.6 s, no kill), Lemma61 rc 0 (11.7 s);
Axioms rc 0, Statements rc 0 (its `#check` output is identical to the producer's `data/logs/lean_statements.json`). The five oleans I built
are **byte-identical** (sha256) to the producer's in `formal_cert/.olean_out` (read only). Logs: /tmp/m3audit/build/*.json.

**Axioms.** `Axioms.lean`: all 17 exported theorems print exactly `[propext, Classical.choice, Quot.sound]`. Beyond the brief's 17, I
generated `AllAxioms.lean` (`gen_allax.py`) with `#print axioms` for **every** theorem/lemma/def in the five modules (138 declarations,
including `Nc_tab`, `Mc_tab`, `C1_ok..C4_ok`, `eOK_all`, `heads_ok`, `chain_lo_bound`, all 30 `cellsA6_b*`/`cellsA7_b*` blocks): rc 0,
127 x `[propext, Classical.choice, Quot.sound]`, 2 x `[propext, Quot.sound]`, 1 x `[propext]`, 8 x no axioms; **nothing outside the whitelist**.

**Kernel replay** (`leanchecker`, my oleans first and only on LEAN_PATH): **rc 0 on all five** modules, empty output:
Basic 59.3 s, Shells 168.1 s, Chains 89.7 s, LemmaA5 1091.2 s, Lemma61 55.7 s (record: `data/leanchecker_replay_audit.json`).

**Controls (my own runs).** Controls.lean rc 0 with `ctl_sorry : [propext, sorryAx, Classical.choice, Quot.sound]` and
`ctl_axiom : [propext, Classical.choice, Quot.sound, ctl_cheat]`: an exit-code gate would accept both, the axiom audit catches both.
RejectN7 rc 1 (`(kernel) application type mismatch` on `decide (Nc 7 = 46)`); RejectChain rc 1 and RejectCell rc 1 (elaborator
"`decide` failed ... reduction got stuck at the Decidable instance"); RejectWitness rc 0.
RejectWitness: I diffed `cellA7bad` and `C1bad` in RejectWitness.lean against RejectCell.lean / RejectChain.lean: the bodies are textually
identical (only the namespace differs). So `cellA7bad_0_false : cellA7bad 0 = false` and `bad_chain_false : chainLo s1 C1bad = false`
are kernel proofs that the tampered propositions are *false* (true /= false), not merely stuck. **I agree that RejectWitness is
decisive** for RejectCell and RejectChain. RejectN7's error is already a kernel `application type mismatch` on `decide (Nc 7 = 46)`,
decisive on its own; `N7_ne_46` confirms it. Independently, the tampered A.7 margin is genuinely violated: true slack at j = 0 is
7.65e-5 above 1e-4, i.e. the LHS is 1.76e-4 < 1e-3.

**Faithfulness (item 1 of the brief).** Lean vs printed statement:
- `lemmaA5_A6`, `lemmaA5_A7`, `lemmaA5_A8`: same expressions, same grids, same margins, same 1e-18, with a2 = 2^{1/3} = a^2 and b2 = 2^{-4/3}
  (`a2_cube`, `b2_cube` pin them). Faithful. They are stated over the *box counts* `Nc`/`Mc`; they equal the paper's N_n/M_l only via
  `Nc_eq_ncard` (2n < 36) / `Mc_eq_ncard` (l < 49), which cover n <= 12 and l <= 48. Equivalent, but the paper should say so where it shows
  the A.7 listing (main.tex:132-135). `sameParity` uses Lean's Int `%` (Euclidean, non-negative), so negative coordinates are handled
  correctly; the kernel tables agree with my count.
- `fcc_multiplicities`, `bcc_multiplicities`: exactly the printed tables. Faithful.
- `lemma61_exp_fcc`, `lemma61_exp_bcc`, `lemma61_pb_lt`, `lemma61_a2_gt`: exactly the printed constants. Faithful (t = 1 values; the
  t >= 1 use in the proof is by monotonicity, not in Lean).
- `lemma61_exp_fcc_21`: proved **at t = 21/10 only**; the proof of Lemma 6.1 uses e^{-pi a^2 t} < 1/128 **for all t >= 21/10**. Weaker
  (trivially extendable).
- `lemma61_prop41_bracket`: only the rational bracket 12 + 30((1-x)^{-2} - 1) < 25/2 for 0 <= x <= 1/128; the bound
  Theta(t,L_F) - 1 < x(12 + 30(...)) (Prop. 4.1 plus N_n < 30n) is not in Lean. Weaker.
- `lemma61_tail_fcc`, `lemma61_tail_bcc`: bound **every partial sum of the rational majorant** 30 sum n 49^{-n}, (75/2) sum l^2 (3/10)^l.
  The printed chain sum N_n e^{-pi a^2 n t} < 30 sum n/49^n (needs N_n < 30n for all n, and t >= 1) and the passage to the infinite series
  are not in Lean. Weaker (disclosed at main.tex:157 and 290 item 3).
- `lemmaA6_tail`: exactly the printed rational. Faithful, but it does not certify that this rational bounds the Ewald tail (I checked
  that by hand, item 5 above).
- `lemmaA1_rational`: 55995/10^6 < 7/125, i.e. 0.055995 < 0.056. Faithful and trivial; the substantive parts of A.1 (P(L_F,0) < 0.055995,
  I(16/25,0) > 7/125) are Tier C.
No statement is vacuous: all hypotheses are satisfiable (j < 1000, j < 2000, 0 <= x <= 1/128, any K) and the conclusions are concrete
inequalities between Mathlib reals.

## BLOCKING

None.

## NONBLOCKING (with exact fixes)

1. **Lemma A.3 endpoints are mischaracterised (fairness to the authors).** main.tex:250-252 (and ledger YBC-C-0006): "The dyadic endpoints
   look like double-rounded logarithms, so whether the bounds hold depends on the rounding direction ... a reader implementing the lemma in
   double precision could be misled".
   My computation: log(11/25)*2^53 = -7394735416760222.80 (printed numerator -...227), log(147/1000)*2^50 = -2158713440539057.95 (printed
   -...059), log(4/3)*2^54 = 5182419497180050.47 (printed ...053). Each printed endpoint lies 4.2, 1.05 and 2.53 units of its denominator
   **beyond** the exact logarithm, in the direction that makes (A.4) true. That is deliberate outward rounding, not nearest rounding.
   Moreover, in the proof of Prop. 3.1 (p. 9) the rationals 11/25 and 147/1000 are intermediate: the actual requirement is
   y_1 > (3072/15625)^{1/2} = 0.4434 and y_2 > 2304/15625 = 0.14746, so alpha_1 and alpha_2 have slack of about 3e-3 and 5e-4 in the
   argument; only beta (y <= 4/3) is tight, and e^beta >= 4/3 holds.
   Fix: replace the two sentences starting "The dyadic endpoints look like" with: "The endpoints are outward-rounded: their numerators lie
   4.2, 1.05 and 2.5 units of the dyadic denominator beyond the exact logarithms, in the safe direction. For alpha_1 and alpha_2 the rationals
   11/25 and 147/1000 are themselves intermediate (the proof of Proposition 3.1 has slack of about 3e-3 and 5e-4), so only the bound for
   beta is tight. These are the tightest margins we met in the appendix; at 320 bits all three hold, and we do not call them an error."
   Update YBC-C-0006 accordingly.
2. **"Seventeen finite statements" (title, abstract, main.tex:29, 60, 212).** The count is accurate as a count of Lean theorems with the
   whitelist axiom output, but (a) main.tex:60 juxtaposes "seventeen finite statements" with "the 17 nonzero BCC multiplicities", two
   different 17s; (b) `lemma61_prop41_bracket` is a for-all-x real inequality, not a finite statement; (c) about seven are one-line bridges
   or elementary facts: `Nc_eq_ncard`, `Mc_eq_ncard` (bridges), `lemmaA1_rational` (0.055995 < 0.056), `lemma61_pb_lt`, `lemma61_a2_gt`,
   `lemma61_prop41_bracket`, `lemmaA6_tail` (rational). The substantive ones are the two multiplicity tables, (A.6), (A.7), (A.8) and the
   1/49, 3/10, 1/128 constants, plus the partial-sum tails.
   Fix (abstract, main.tex:60): "seventeen Lean theorems (several of them one-line rational facts or bridge lemmas): the FCC shell
   multiplicities N_1..N_12 and the BCC multiplicities M_l at the 17 nonzero indices l <= 48 ...". Title may stay; alternatively
   "seventeen Lean statements kernel-checked".
3. **List the Lean statements that are weaker than the printed ones.** Add to Section 3 ("How to read a Tier A line", after main.tex:192)
   the list from the Faithfulness paragraph above: `lemma61_exp_fcc_21` at t = 21/10 only (paper: all t >= 21/10); `lemma61_prop41_bracket`
   only the rational bracket, not the Theta bound; `lemma61_tail_*` only the rational majorant's partial sums, not the shell sums; and
   `lemmaA5_*` over box counts, equal to N_n, M_l through `Nc_eq_ncard`/`Mc_eq_ncard`.
4. **Reproducibility recipe is broken** (main.tex:301-306). (a) All scripts take positional arguments (`m3_shells.py` and `m3_arb.py`
   read sys.argv[1], sys.argv[2]; `emit_lemmaA5.py` sys.argv[1]); the printed commands give none. (b) `data/code/m3_arb.py:25` adds
   `Path(__file__).parents[5]/.scratchpad/b2_pylib` to sys.path; from `papers/p4_yukawa_bcc_fcc_check/data/code/` that resolves to
   `.claude/worktrees/.scratchpad/b2_pylib`, not the repository's `.scratchpad/b2_pylib` (it was right only from
   `results/proposal4/2026-10-27/M3/code/`). The venv has no flint, so `.venv/bin/python -I code/m3_arb.py` fails. (c) "Commands
   (repository root)" but the paths are `code/...`, which only exist under `papers/p4_yukawa_bcc_fcc_check/data/`. (Found by reading the
   scripts; I did not run the producer's scripts.)
   Fix: give the commands with their arguments and full paths from the repository root, e.g.
   `.venv/bin/python -I results/proposal4/2026-10-27/M3/code/m3_shells.py <args>`, and state that m3_arb.py needs python-flint 0.6.0 from
   `.scratchpad/b2_pylib` (not in the venv); or make the sys.path entry relative to the repository root.
5. **IEEE-double wording** (main.tex:67 "IEEE double alone reaches only 11 digits"; :227-231; YBC-X-0001). That is the producer's
   direct sum. My float64 Ewald reaches about 12 significant digits depending on eta (errors 5e-13 to 4e-12). The intrinsic limit is
   eps*|S|/G'(kappa\*), about 1e-12. Fix main.tex:67: "(our IEEE-double direct sum reaches 11 digits; double precision cannot resolve the
   1e-15-wide enclosure (A.9), since rounding at 1e-16 in sums of order one moves kappa\* by about 1e-12)".
6. **Lean route deviation** (main.tex:164-165). The repository's binding rule is that Lean verification goes through
   `anse/formal/lean_runner.py`. The paper discloses the deviation, and its manual equivalent (compile, `#print axioms`, sorryAx rejected,
   whitelist) was redone here on all declarations. Keep the disclosure, and add "the equivalent checks were rerun by the independent
   audit (AUDIT.md)".
7. **Stale status lines after this audit.** main.tex:42-43 ("No independent audit of any kind (human or AI) exists"; "the
   producer-is-not-verifier clean recompile is pending"), :59 ("run by the producer; ... no independent recompile yet"), :177, :277 ("An
   independent clean recompile ... owed"), :284 ("There is no AI audit"), :292 ("The leanchecker replay was run by the producer"), and the
   same phrases in publication_meta.json "notes" and "description". Fix: "An independent AI audit (AUDIT.md, verdict
   ACCEPT_WITH_CORRECTIONS) rebuilt the five modules from source into a private olean directory and replayed them with leanchecker
   (rc 0 on all five, data/leanchecker_replay_audit.json; oleans byte-identical to the producer's); no human audit and no statement lock exist." Record the audit in the ledger
   rows' `audit` field only if the Elenchus convention allows an AI audit there; otherwise leave the 8 flags (they correctly say no *person*
   has certified the glosses).
8. **"Three independent reproductions ... agreeing to about 22 digits"** (main.tex:66, 230). (E) and (Q) agree to all 25 printed
   digits; only (D) is limited (its radius is 4.5e-25, its interval width ~4e-24). Suggested: "(E) and (Q) agree to 25 digits, and (D)'s
   interval of width 4e-24 contains both". Optionally cite this audit's fourth value (classical eta-split Ewald, 70 digits, eta-independent):
   1.71792186846990386425087416660628...
9. **Lemma A.4 / ancillary files** (main.tex:69, 274): confirmed (arXiv abs page, 2026-10-27: v1 only, no ancillary-file section). Add the
   date of that check, and note that the paper itself (p. 4: "the complete interval computations and exact partitions accompany the
   manuscript") says the data exist, so requesting them from the authors is the route to M3c.
10. **Bibliography / credit.** Credit to Luo and Wei is clear and correct (title, arXiv id, v1 date 22 Oct 2026 [math.AP] verified).
   `zp` (main.tex:314): doi:10.5281/zenodo.23646105 is the producer lab's 2026-10-25 record "Triangular lattice minimises the planar
   Yukawa energy" (results/discovery_journal_2026/zenodo_inventory.md:216); the description (planar, own preprint, not extended here) is
   accurate. `mathlib` arXiv:1910.09336 and `arb` (IEEE Trans. Comput. 66 (2017) 1281-1292) are correct. Nothing missing that the text
   relies on.
11. **"What this is NOT" box** (main.tex:73-75) is accurate and adequate; tiers are applied consistently (A only to Lean, C to Arb and
   mpmath, X to float and guard logs). No overclaim found in the title beyond item 2.

## Numbers this audit produced (for the ledger)

| quantity | auditor value | producer |
|---|---|---|
| kappa\* (eta-Ewald, mpmath 70 d) | 1.71792186846990386425087416660628171879468538 | (E) ...903864250874 +/- 1.7e-25; (Q) ...90386425087416661 |
| G(...903), arb | [-1.35362654688e-19 +/- 3.3e-31] | -1.35363e-19 |
| G(...904), arb | [2.12616065470e-20 +/- 5e-33] | +2.12616e-20 |
| G'(kappa\*) | 1.566242612e-4 | 1.566e-4 |
| A.5 min slacks | 7.52141e-4 (j=999), 7.64588e-5 (j=0), A.8 0.142967 | same |
| A.6 tail rational | 6.52669862e-21 | 6.5267e-21 |
| float64 kappa\* | 1.71792186847388 / ...4710999 / ...4703832 (eta 1/1.3/2) | 1.7179218684625486 (direct) |
