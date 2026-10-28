# Independent verification of the v1.2 clarification (producer != verifier)

Date: 2026-10-28. Verifier: a separate AI agent instance (Claude). It did not produce v1.2 and ran its own checks. No person has reviewed this audit. Scratch: /tmp/a2v12/.

**Verdict: ACCEPT_WITH_CORRECTIONS.** Four small wording corrections (items 1-3 and 3b) should be made before publication. Items 4-6 are optional. No result, number, tier, gate outcome or conclusion changed between the published version and v1.2.

## What was compared
- Published baseline: commit 3498cb4. Its main.pdf has md5 2c76574b6e03ccfe36d1d2a71c0db3f5, which equals the file p2_navier_stokes_audit.pdf on Zenodo record 23661381 (fetched through the Zenodo API; record metadata version "v1.1", DOI 10.5281/zenodo.23661381).
- v1.2: HEAD b991b3d (this audit is pinned to that commit). The working tree is clean for papers/p2_navier_stokes_audit/.
- I compared main.tex, publication_meta.json, ledger.json and build_ledger.py with Python difflib (unified diff, 57 lines).

## (1) The preprint, read directly
Source: arXiv:2610.08144v1, full text from the alphaXiv extraction (84,629 characters, 3,214 lines). I read all of it: abstract, Sections 1-5, Appendix A and the references. Figures 1-4 are images and were not read. The title, the authors (A. Bastounis, F. Circelli, A. C. Hansen), "[math.AP]" and "6 Oct 2026" all match bibitem `bch`.

Each of our sentences, checked against the preprint (main.tex line numbers):

| Our text | Preprint (quote, at most 25 words) | Finding |
|---|---|---|
| l.79 and l.324: "at the commit audited here" / "cites the corpus at commit f9e8bc5" | Sec. 3.1, Ex. 3.1: "We compare this estimate with the cited Lean declarations at commit f9e8bc5"; also Sec. 3.2, Ex. 3.3 | Correct |
| l.80: "lemma-level mismatches (... m+5 ... where the paper uses m+4)" | Rem. 3.2: "each contain a similar m + 5 derivative requirement, rather than the expected m + 4 derivatives from the NL paper" | Correct. The examples are Lemma 8.6/(8.19) and (10.19), both intermediate. |
| l.324: "Lean estimate is 'strictly weaker' than the paper's (8.19)" | Sec. 3.1: "This estimate is then strictly weaker than equation (8.19) due to the extra derivative on the right-hand side." | Correct. The Lean lemma needs a stronger hypothesis (m+5), so its conclusion is weaker. |
| l.324: "a footnote adds that some such Lean results are incomparable" | fn. 5: "some such Lean results are actually incomparable with (3.1), due to the mismatch in the type of derivative." | Correct |
| l.324: Sec. 3.2 "a different bound by a different argument" | Sec. 3.2: "a Lean proof of a different bound obtained by a substantively different mathematical argument." | Correct. "substantively" is dropped (optional item 5). |
| l.324: "Remark 3.4 says the two examples are not exhaustive" | Rem. 3.4: "the fact that we display only two examples does not mean that these are the only cases of mistranslations." | Slight overstatement (item 3) |
| l.324: "Section 3.3 does not examine the Euler formalisation but predicts..." | Sec. 3.3: "beyond the scope of this paper to carefully examine the autoformalisation of the Euler proof"; "based on some examinations ... with both AI and manual tools"; "the likelihood of substantial mistranslations is very high." | The quote is verbatim, but "does not examine" overstates (item 1) |
| l.324: "makes no claim about the correctness of OpenAI's natural-language proof" | Sec. 1, Disclaimer: "We do not make claims about the correctness of OpenAI's NL proof, we only make statements about mistranslations into Lean." | Correct |
| l.324: "framing (Section 1, type (i); Section 3.4) takes the theorem statement as already faithfully translated" | Sec. 1 (i): "Suppose a theorem (the statement, not including a proof) has already been faithfully and correctly translated into Lean." Sec. 3.4: "Input: A faithful Lean translation X′ of an NL theorem X" | Correct as a description of the general setting. It is a premise, not a finding about the corpus (optional item 6). |
| l.324: "does not examine the top-level Lean statement" | No example or passage examines `navier_stokes_breakdown_R3/_periodic` | Correct, by reading and search |
| l.324: "does not discuss forcing for Navier-Stokes or Fefferman's alternatives (A)-(D)" | Keyword search: "unforced" occurs only for Euler (Sec. 3.3); "Forcing"/"force" occur only in the titles of refs [2] and [18]; "Fefferman" occurs only in ref [23] (the Clay designation, Sec. 3) and as a co-author of ref [16]; a whole-file grep for `\((A|B|C|D)\)|alternative|errat|top-level|challenge|periodic pressure|pressure` hits only the SCI notation "Γn(A) ... ∀A ∈ Ω" (App. A.1.1, Def. A.1) and the lemma-level pressure-flux bound (Sec. 3.2, Ex. 3.3); no "alternative", "errat", "top-level", "challenge" | Correct |
| l.80: "makes no claim about the top-level statements either way" | Sec. 1: "A third possibility is that the NL proof provides stronger statements than what the formal proof actually establishes ... The latter happens in OpenAI's announced proof"; Sec. 1: "The Lean code merely tells us that the theorem is correct" | Essentially right: the only worked cases are lemmas. But the Sec. 1 general sentence does not say which level, so "either way" is more than we can quote (item 2). |
| l.305: Sec. 3.1 "calls some Lean estimates weaker than those of OpenAI's natural-language paper" | Sec. 3.1 heading: "When the NL paper declares stronger statements than what Lean proves."; "the Lean results discussed in this section are weaker than (3.1)" | Correct. The separation from our (D) "weaker" is correct. |
| l.324: Sec. 5.1 "AI-performed semantic verification failed in another autoformalisation project" | Sec. 5.1: "this semantic verification was, however, mainly performed by other AIs [46 ...]. The fact that this failed highlights the difficulty ..." | Correct. "mainly" is dropped (optional item 5). The project is Meta's. |
| Ledger P2NS-C-0007 | (iv) now adds that identity is checked against the challenge file and fidelity against Fefferman, not against OpenAI's papers | Contains no description of the preprint, so there is nothing about the preprint to verify there. See item 4. |

REVISION.md's quote table: I checked each of the 23 quotes against the text and found every one verbatim (apostrophes normalised). There is one small imprecision in REVISION.md only: "Fefferman is cited only as [23]" should say that Fefferman is also a co-author of ref [16]. That reference is an Euler paper and not the Clay text.

## (2) No result changed
- **main.tex.** The diff is the date line, the DOI line, the new "Scope" abstract paragraph (l.76-80), one sentence added to the (D) caveat (l.305), the relay item replaced by two items (l.323-324), and bibitem `bch`. No table, number, tier tag of an existing claim, or conclusion line changed. The "What is not established" item on refereeing kept its first two sentences. Only the secondhand relay was removed.
- **ledger.json.** 26 claims before and after (A 4, L 4, C 8, X 10). The only changed field is the statement of P2NS-C-0007. No tier changed.
- **Gate.** I re-ran the Elenchus `tools/ledger.py` directly into /tmp/a2v12/gate_rerun.txt; I did not use run_gate.py, which overwrites gate_output.txt. The output is byte-identical to ledger/gate_output.txt and to the published gate_output.txt: exit_code=1, 0 blocking, 4 LEDGER_UNAUDITED_TIER_A (P2NS-A-0001..0004).
- **publication_meta.json.**
  - version is v1.2.
  - related_identifiers contains isNewVersionOf 10.5281/zenodo.23661381 (doi) and references arXiv:2610.08144 (arxiv).
  - A secret scan (token, ghp_, hf_, Bearer, password, ZENODO_TOKEN) found nothing.
  - Apart from the new Clarification paragraph, the description is unchanged.

## (3) Internal consistency
- The forced/unforced statements agree with the paper's earlier sections:
  - l.96: (A)/(B) have f≡0.
  - l.98-101: (C) and (D) both posit a smooth f.
  - l.90-92: the README says "data and forcing".
  - l.307: the (C) witness has zero data and nonzero force, and "forced, not unforced" criticism bears on (A)/(B).
- The periodic-pressure statement is consistent with l.71 (abstract), l.106 (the errata quote), l.295 (table row "match with errata (caveat)"), l.303-304 (the caveat), H9 at l.309, and l.336.
- The new l.305 sentence agrees with l.71 and l.303.
- **Bibliography.** `bch` is 4th, and the rebuilt PDF numbers it [1] corpus, [2] fef, [3] h9, [4] bch, [5] fc, [6] comparator, [7] lean, [8] mathlib. No hard-coded "[n]" occurs in main.tex, build_ledger.py, ledger.json or publication_meta.json, and there are 0 "[?]". All citations are by key, so the renumbering is safe.

## (4) Wording safety
- The title (l.35) and l.58 still say the paper is not a claim that a Clay problem is solved, and credit goes to the corpus authors.
- Nothing in the new text accuses the preprint's authors or OpenAI; "mismatches" is neutral.
- The AI-only fidelity judgement is already Tier C (C-0002/C-0003; "Statement fidelity is a human judgement" item; the LEDGER_UNAUDITED_TIER_A flags). The new l.324 sentence points to it.
- One phrase is not acceptable as written: "none of it is a top-level statement defect" (l.324) reads as our asserting that the top-level statements are defect-free, which goes beyond a Tier C AI reading and beyond what the preprint addresses. See item 3b.

## (5) PDF rebuild
I copied the directory to /tmp/a2v12/build, deleted the aux/out/log/pdf files, and ran pdflatex twice with -halt-on-error.
- Both passes returned rc 0.
- The log has 0 "!" errors and no undefined-reference, overfull or LaTeX warnings.
- The PDF has 12 pages.
- pdftotext of the rebuilt PDF is identical to pdftotext of the committed main.pdf; the files differ only in bytes such as timestamps.

## Items
**Must change before publication**
1. **main.tex:324.** "Section~3.3 does not examine the Euler formalisation but predicts that" overstates what the preprint says. It reports preliminary examinations "with both AI and manual tools" and declines only a *careful* examination. Replace with: "Section~3.3 does not carefully examine the Euler formalisation (it reports only preliminary examinations) but predicts that".
2. **main.tex:80 (abstract).** "and makes no claim about the top-level statements either way" says more than we can quote. The preprint's Sec. 1 general sentence ("the NL proof provides stronger statements than what the formal proof actually establishes ... The latter happens in OpenAI's announced proof") does not name a level, and its only worked cases are lemmas. Replace with: "and does not examine the top-level statements". This matches l.324, and REVISION.md finding 4 already says it neither confirms nor contests our reading. Apply the same change to publication_meta.json if any such phrase is added there (none is present now).
3. **main.tex:324.** "Remark~3.4 says the two examples are not exhaustive" turns a non-claim into a claim. Replace with: "Remark~3.4 says that showing only two examples does not mean they are the only mistranslations".

3b. **main.tex:324.** Replace "and none of it is a top-level statement defect" with "and none of it identifies a defect in a top-level statement".

**Optional**
4. **main.tex:80.** The tag \tg{C}{0007} is attached to the preprint sentence, but the text of P2NS-C-0007 says nothing about the preprint. Either move the tag to the end of the preceding sentence ("...match those papers"), or add to C-0007 (iv) one clause: "a preprint at the audited commit reports lemma-level differences from the NL paper and does not examine the top-level statements". If C-0007 is changed, rebuild the ledger and re-run the gate.
5. **main.tex:324.** (a) The estimate the preprint calls "strictly weaker" is one it derives from the Lean lemma by taking a sup over all w with |w| ≤ m, and fn. 4 says that step "is not explicitly done" in the Lean; consider "so the estimate obtained from it is ...". (b) Restore "substantively different argument" (Sec. 3.2) and "mainly performed by other AIs" (Sec. 5.1) for fidelity to the preprint's wording.
6. **main.tex:324.** After "takes the theorem statement as already faithfully translated", add "as a premise of its general setting, not as a finding about this corpus". REVISION.md already makes this point, and the addition prevents the sentence being read as an endorsement.
7. **REVISION.md:68.** Change "Fefferman is cited only as [23]" to "the Clay text is cited only as [23] (Fefferman is also a co-author of ref. [16], an Euler paper)".
8. **publication_meta.json notes.** The sentence "only papers/p2_navier_stokes_audit/ is uncommitted" was carried over from v1 and is now stale. Also, the title page says "v1 2026-10-26" while the Zenodo record's version field is "v1.1". Consider "v1/v1.1 2026-10-26".

Nothing else needs to change. None of the items changes a result.
