# A2 paper revision (after AUDIT.md, ACCEPT_WITH_CORRECTIONS)

Blocking
- B1: deleted ", and Fefferman asks for a proof of one of four statements" in section Implications; ledger P2NS-C-0005 text replaced by the audit's sentence ("This is not a Clay determination: ..."); ledger rebuilt (26 claims, 26 evidence blobs), gate re-run: exit code 1, 0 blocking, 4 LEDGER_UNAUDITED_TIER_A flags (unchanged, open).
- B2: "every one of its 88,400 declarations re-passes the Lean kernel" replaced by the audit's sentence (Lean.Replay skips 51 _unsafe_rec auxiliaries, 12 NS + 39 Euler, none in any proof closure, and 4 congr_simp duplicates); same added in the Replay section after the table, parenthetical in the abstract; also in ledger X-0005 and publication_meta.json.

Nonblocking
- N1 leanchecker per-module, not transitive (abstract, Replay, ledger X-0006). N2 second Clay erratum sentence in section 1. N3 auditor's audit_nonvac_Rn / audit_nonvac_periodic / audit_zero_data_ok with axiom lines (new section Independent AI audit; fidelity item (d) updated). N4 53,750/34,646 vs 53,752/34,648 explained. N5 7-module bit-identical rebuild sample cited. N6 "independently (of the corpus authors)" at first use in abstract.
- Limitations: "leanchecker --fresh (Mathlib re-check) not run" added.
- New section "Independent AI audit"; "no human audit" retained.
- publication_meta.json: version v1.1, description updated (audited, limits).

Build: pdflatex twice, 11 pages, 0 undefined refs, 0 overfull, 0 warnings. Nothing committed, pushed or published.

---

# v1.2 (2026-10-27): clarification only, not a correction of results

Trigger: docs/studies/NS_CRITIQUE_CHECK_2026-10-28.md. That study classified the public "Lean verified a weaker assertion" discussion as (a) for the substance, with a minor (b) wording risk in our abstract. It drafted C1-C4. No result, number, tier, gate outcome or conclusion changed in v1.2. The ledger still has 26 claims (4 A, 4 L, 8 C, 10 X) and 26 evidence blobs; only the statement text of P2NS-C-0007 changed.

## Changes
- **C1 (abstract, new "Scope" sentences).** The audited Navier-Stokes theorems are the forced breakdown alternative (C) and, with the errata's periodic-pressure condition, (D). They do not address the unforced (A)/(B). The sentence is scoped to Navier-Stokes because the abstract also mentions the unforced Euler theorem.
- **C2 (abstract; new item in "What is not established"; ledger C-0007 (iv)).** Statement identity is checked against the corpus's challenge file. Statement fidelity is judged against Fefferman's text. Neither is compared with OpenAI's natural-language papers, and we make no claim that the Lean statements or development match them. A report that "Lean verified a weaker assertion than published" is therefore neither confirmed nor refuted here.
- **C3 (Caveat on (D)).** The "main-text-only reading" qualification was already present in v1/v1.1 (abstract l.71, caveat l.298, H9 paragraph). v1.2 adds one sentence. It says that "weaker" means only weaker than a main-text-only reading of (D), because of the errata's periodic-pressure condition, and that the Lean matches the errata-corrected (D). It also says this sense is unrelated to the lemma-level "weaker" of arXiv:2610.08144 Section 3.1.
- **C4 ("What is not established").** The secondhand relay ("according to its alphaXiv text ... we did not read it ourselves and cite it only as relayed") is replaced by a direct reading with section numbers. A bibitem `bch` was added.
- **Title page.** The date now reads v1.2 (clarification only). The DOI line now reads "New version of doi:10.5281/zenodo.23661381"; no new DOI is stamped.
- **publication_meta.json.** Changes: version v1.2; a one-sentence Clarification paragraph at the top of the description; a notes entry saying this is a new version of doi:10.5281/zenodo.23661381. The old notes line "mentioned only as relayed by H9, not read" is replaced. New related identifiers: isNewVersionOf 10.5281/zenodo.23661381 (doi), and references arXiv:2610.08144.

## Direct reading of Bastounis, Circelli, Hansen, arXiv:2610.08144v1 [math.AP], 6 Oct 2026
Source and coverage:
- The full extracted text of v1 came from the alphaXiv full-text tool: about 84.6k characters, 3,214 lines.
- All of it was read: abstract, Sections 1-5, Appendix A and the references.
- Figures 1-4 are images, and their content was not read.
- The full text is not stored in any tracked path.

Quotes, each at most 25 words:

| Where | Sentence (verbatim) |
|---|---|
| Abstract | "In particular, we show that the formalised Lean proof does not correspond to the NL proof of blow-up of solutions to the Navier-Stokes equations." |
| Sec. 1, type (i) | "Suppose a theorem (the statement, not including a proof) has already been faithfully and correctly translated into Lean." |
| Sec. 1 | "A third possibility is that the NL proof provides stronger statements than what the formal proof actually establishes, with (of course) different proofs." |
| Sec. 1 | "The latter happens in OpenAI's announced proof of blow-up of Navier-Stokes equations." |
| Sec. 1 | "The Lean code merely tells us that the theorem is correct, yet the NL proof with intermediate arguments, lemmas and results may be incorrect ..." |
| Sec. 1, Disclaimer | "We do not make claims about the correctness of OpenAI's NL proof, we only make statements about mistranslations into Lean." |
| Sec. 3 (intro) | "the Lean formalisation does not represent a semantically faithful translation of the NL paper" |
| Sec. 3 (intro), the only Clay mention | "and was designated a Clay Millennium Prize Problem in 2000 [23]" |
| Sec. 3.1 (heading) | "When the NL paper declares stronger statements than what Lean proves." |
| Sec. 3.1, Ex. 3.1 | "We compare this estimate with the cited Lean declarations at commit f9e8bc5" |
| Sec. 3.1, Ex. 3.1 | "The Lean code produced by OpenAI often has stronger conditions on bounds on the derivatives of various functions" |
| Sec. 3.1, Ex. 3.1 | "This estimate is then strictly weaker than equation (8.19) due to the extra derivative on the right-hand side." |
| Sec. 3.1, Rem. 3.2 | "each contain a similar m + 5 derivative requirement, rather than the expected m + 4 derivatives from the NL paper" |
| Sec. 3.1, fn. 5 | "some such Lean results are actually incomparable with (3.1), due to the mismatch in the type of derivative." |
| Sec. 3.2 | "the AI autoformalisation results in a Lean proof of a different bound obtained by a substantively different mathematical argument." |
| Sec. 3.2, fn. 7 | "does not appear to be used to prove the Navier Stokes theorem proposed by OpenAI." |
| Sec. 3.2, Rem. 3.4 | "the fact that we display only two examples does not mean that these are the only cases of mistranslations." |
| Sec. 3.3 | "OpenAI reported finite-time blow-up for the unforced incompressible Euler equations on R3, starting from smooth, compactly supported initial data." |
| Sec. 3.3 | "It is beyond the scope of this paper to carefully examine the autoformalisation of the Euler proof" |
| Sec. 3.3 | "our assessment is that the likelihood of substantial mistranslations is very high." |
| Sec. 3.4 | "Input: A faithful Lean translation X′ of an NL theorem X and an alleged NL proof Y of X." |
| Sec. 5.1 | "... this semantic verification was, however, mainly performed by other AIs ..." |
| Sec. 5.1 | "The fact that this failed highlights the difficulty that AIs have both with producing semantically faithful translations into Lean and with assessing the accuracy ..." |

Typography normalised: curly apostrophes became straight ones, and "R3" stands for R^3 as the extraction renders it. Otherwise the quotes are verbatim from the extracted text.

Absences, checked by reading the full text and by a keyword search:
- "forced" or "forcing" for Navier-Stokes does not occur. "Unforced" occurs once, for Euler (Sec. 3.3). "Forcing" and "force" occur only in the titles of references [2] and [18].
- Fefferman's alternatives (A)-(D) never occur. Fefferman is cited only as [23], for the Clay designation.
- There is no claim that the top-level Lean statement misstates the Clay problem, and no examination of the top-level Lean statement.

## Check of what v1/v1.1 said about the preprint
- "finds intermediate Lean lemmas that differ from the natural-language paper": confirmed. The worked examples are Lemma 8.6 / (8.19) in Sec. 3.1 and (10.19) in Sec. 3.2, both intermediate.
- "for example a derivative-count of m+5 against m+4": confirmed (Sec. 3.1, Ex. 3.1, Rem. 3.2). The Lean lemma needs m+5 derivatives, a stronger hypothesis, so it is "strictly weaker" than (8.19).
- "does not claim the top-level statements misstate the Clay problem": confirmed by absence. The paper makes no claim about the top-level statement either way. Its Sec. 1 / Sec. 3.4 framing presupposes a faithfully translated statement. That is a framing, not an endorsement, so we do not cite it as support for our fidelity reading.
- The earlier study's "Ex. 3.3" (different bound, different argument) is correctly placed. It is in Sec. 3.2, not Sec. 3.3. Sec. 3.3 is about Euler.

## Findings bearing on our conclusions (stated plainly; none changes a result, number, tier or conclusion)
1. **Same commit.** The preprint cites the corpus at commit f9e8bc5, the commit we rebuilt and audited. Its lemma-level mismatches between the Lean development and the natural-language paper therefore concern our audited object. They do not touch what we checked: rebuild, axioms, kernel replay, statement identity, and statement-level fidelity to Fefferman. They are also why our paper must not be read as saying the Lean matches OpenAI's paper. C2 now says so.
2. **Euler (Sec. 3.3), not reported by the earlier relay or study.** The preprint does not analyse the Euler formalisation. It predicts, from preliminary examinations, that substantial NL-to-Lean mistranslations are very likely. We audit the Euler Lean statements, with no Clay counterpart (C-0004), and make no claim about their correspondence to the Euler NL paper. So there is no conclusion change, and the prediction is stated in the paper.
3. **AI-made semantic verification (Sec. 5.1).** The preprint reports that faithfulness checking "mainly performed by other AIs" failed in another autoformalisation project (Meta). Our statement-fidelity judgement (C-0002, C-0003, C-0004) is made by AI agents only, and no person has audited any statement. This was already disclosed and is already Tier C with the LEDGER_UNAUDITED_TIER_A flags. The preprint is a published reason to give that AI-only judgement little weight until a person audits it. We say so rather than soften it; the paper now points to it in the C4 item.
4. **The preprint offers no independent support for our top-level fidelity reading.** Nothing in it confirms or contests that the Lean (C)/(D) statements are faithful to Fefferman.

## Ledger and build
- build_ledger.py: P2NS-C-0007 (iv) text extended with the C2 sentence. Rebuilt: "claims 26 {'A': 4, 'L': 4, 'C': 8, 'X': 10}; evidence blobs 26".
- git diff of ledger.json shows only that statement line changed.
- run_gate.py: exit_code=1, 0 blocking, 4 LEDGER_UNAUDITED_TIER_A flags (P2NS-A-0001..0004). This is unchanged; the audit status lines stay accurate.
- build_pdf.py (clean, pdflatex twice): 12 pages (was 11), 0 undefined refs, 0 overfull, 0 warnings, 0 errors.
- Nothing committed, pushed or published. No DOI stamped.
