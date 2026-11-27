# NS critique check (Gizmodo "weaker assertion"), written 2026-10-27/28

Read-only study. Our paper (papers/p2_navier_stokes_audit, doi:10.5281/zenodo.23661381) was NOT edited. Nothing committed or published. Web pages were read through a fetch tool that summarises pages, so quotes are limited to what it returned; items it could not open are marked.

## Step 1. What Gizmodo says
Mike Pearl, Gizmodo, "OpenAI trumpets 3 more math and science results...", published 26 Oct 2026 8:13 pm ET. https://gizmodo.com/openai-trumpets-3-more-math-and-science-results-along-with-a-new-plan-for-publishing-them-2000830956

Quoted fragment (the fetch tool truncated the sentence): "human readers digging around in OpenAI's Lean-verified solution" "became concerned that Lean verified a weaker assertion than what was initially written in what OpenAI published."

- No critic is named. The phrase is "human readers".
- Links in the passage: https://openai.com/index/navier-stokes-solution/ (403 to our fetcher, not opened) and https://www.science.org/content/article/openai-just-changed-math-forever-exactly-how-no-one-yet-knows (403, not opened).
- The word "critics" in the task brief is not in the Gizmodo text as returned; the article says "human readers" and "concerned". "Forced vs unforced" is not mentioned in the Gizmodo passage.

## Step 2. Primary sources found
1. Bastounis, Circelli, Hansen, "Navier-Stokes lost in translation: Why Lean verification of AI autoformalisation does not guarantee correct natural language proofs", arXiv:2610.08144v1 [math.AP], 6 Oct 2026. https://arxiv.org/html/2610.08144v1 (opened; the fetcher read characters 0-100000 of about 160891 in two passes; sections 5+ read only in outline). This is almost certainly what the Gizmodo "readers" refers to (inference, not stated by Gizmodo).
   Exact sentences returned:
   - Abstract: "we show that the formalised Lean proof does not correspond to the NL proof of blow-up of solutions to the Navier-Stokes equations."
   - Intro: "A third possibility is that the NL proof provides stronger statements than what the formal proof actually establishes ... The latter happens in OpenAI's announced proof of blow-up of Navier-Stokes equations." and "We do not make claims about the correctness of OpenAI's NL proof, we only make statements about mistranslations into Lean."
   - Sec. 3: "the Lean formalisation does not represent a semantically faithful translation of the NL paper".
   - Ex. 3.1 / Rem. 3.2: Lean estimates "each contain a similar m+5 derivative requirement, rather than the expected m+4 derivatives from the NL paper"; "The Lean code produced by OpenAI often has stronger conditions on bounds on the derivatives".
   - Ex. 3.3: "a Lean proof of a different bound obtained by a substantively different mathematical argument."
   - The fetcher reports the paper never mentions forcing, never discusses Fefferman's (A)-(D), and gives no claim that the top-level Lean theorem misstates the Clay problem. Its worked examples are intermediate lemmas.
2. Secondary on (1): Startup Fortune (https://startupfortune.com/a-new-paper-says-openais-navier-stokes-proof-and-its-lean-code-dont-match/): Hansen told New Scientist the paper does not claim the NL proof is wrong, "Nor do we say that it is correct"; OpenAI told New Scientist it knows of the gap and would fix NL errors. The article says it does not specify the direction of the mismatch and does not say the top-level statement is weaker. (New Scientist itself was not found or opened.)
3. Hacker News thread "Navier-Stokes Lost in Translation" https://news.ycombinator.com/item?id=49994145 (opened, 100k of 143k chars). User balaclava9 claims "The statement written in Lean, is not actually a correct description of the Navier-Stokes problem" and "We also don't know if Astra properly wrote the initial statement of Navier-Stokes correctly in Lean." This is an anonymous forum comment, with no argument in what we saw. Rebuttals: vilhelm_s "The 'statements' here are statements of lemmas, not the statement of the main theorem."; plepbpl "None of the examples are of the NS lean statement."; fasterik: the authors are not disputing that the formalization is a correct statement of the Millennium problem. kragen: OpenAI's result includes forcing.
4. Capraro on X, https://x.com/ValerioCapraro/status/2108153427742032300, search-result headline only: "BREAKING: OpenAI's solution to Navier-Stokes does not match its Lean verification." Page not openable (HTTP 402). Secondary-by-snippet; date not obtained.
5. Forced-vs-unforced context (Kingy, https://kingy.ai/blog/navier-stokes-ai-proof-claims-dispute/, secondary): Clay options A and B require no external force, C and D allow smooth force; OpenAI Theorem 1.1 is a forced result and "does not claim unforced Navier-Stokes blowup"; the same article notes the repository's review metadata is "self-assessed". De Domenico (manlius.substack.com, 10 Sep 2026) reports OpenAI "claims to have constructed [the singularity] in the forced case, with a smooth forcing function" and says it resolves the problem "by establishing cases C and D".
6. Not found: any State of Proof tracker entry, blog, or thread that argues the top-level Lean statement is weaker than the published claim. Searches were not exhaustive (Science article and OpenAI page returned 403; New Scientist, Quanta not opened).

## Step 3. What is alleged, and comparison with our paper
Primary allegation (Bastounis et al.): the Lean development of the proof does not faithfully mirror the NL paper; lemma-level hypotheses are stronger in Lean (m+5 vs m+4 derivatives), and at least one bound is proved by a different argument. They say nothing we could find about the top-level theorem, forcing, Fefferman's four statements, function space, or regularity.

Gizmodo's "Lean verified a weaker assertion than what OpenAI published" is a journalistic paraphrase. It is unsupported at the top-level-statement level by the one primary source we could identify; at lemma level it matches (stronger hypotheses = weaker lemma). We cannot say which Gizmodo meant.

Point by point (line numbers in papers/p2_navier_stokes_audit/main.tex):

| Point | Our paper | Comment |
|---|---|---|
| Lemma-level Lean vs NL mismatch | l.316: "We read neither of the corpus authors' papers, so nothing here compares the natural-language argument with the Lean development." Same bullet cites Bastounis et al. "only as relayed", reporting m+5 vs m+4 and that it "does not claim the top-level statements misstate the Clay problem". | Already said (a). l.316 relays the preprint via alphaXiv text, not a direct reading; the relay matches what we now read. |
| Top-level Lean = challenge statement | Abstract l.67-68 and Sec. "ident": elaborated closures identical to the reference challenge statements up to alpha-renaming. | Not contested by anyone. But identity is to the corpus's own challenge file, not to OpenAI's published NL Theorem 1.1. |
| Lean (C) is Fefferman's (C) | Abstract l.69-70, l.301: faithful; "Conditionally on fidelity ... the formal object proves Fefferman's alternative (C); that is not a Clay determination." | Compatible. |
| Forced vs unforced | l.301: "Criticism that the result is 'forced, not unforced' is therefore not a fidelity defect against (C) as Clay states it (it would bear on (A)/(B)); that is our reading of the PDF". | Already addressed (a), but only in the body; the abstract never says "forced". |
| Lean weaker than Clay main text | l.71 and l.298: periodic-pressure errata condition "makes the Lean nonexistence claim weaker" for (D). | Our own paper uses "weaker" for the Lean (D). A reader of Gizmodo may conflate this with the lemma-level "weaker". Disclosed, but see (b). |
| Lean weaker than OpenAI's NL published claim | Not addressed. We did not read OpenAI's NL paper (l.88, l.316). Bastounis's "NL proof states more than Lean proves" concerns the NL argument, which we explicitly do not audit. | Not a missed defect, but a scope hole the abstract does not state in so many words. |

## Classification
Primary: (a) for the substance. Everything the identifiable primary critique alleges is either outside our audit's declared scope (NL vs Lean, l.316) or already addressed (forced vs (C), l.301; periodic pressure, l.298). No (c): we found no critique showing a top-level statement defect that our audit missed, and the Gizmodo claim is unsupported by what it links, as far as we could verify.

Secondary: (b), minor. Adversarial reading: (i) the abstract says the Lean (D) is "weaker" and says fidelity holds for (C), but never says in the abstract that OpenAI's result is the forced alternative or that it does not touch (A)/(B); (ii) "faithful to Fefferman's (C)" could be read as "the Lean proves what OpenAI announced", whereas we compare only to Fefferman and to the corpus challenge file, never to OpenAI's published NL statement or proof; (iii) "weaker" now has two unrelated meanings in public discussion; (iv) our relay of the Bastounis preprint at l.316 is secondhand and should be replaced by a direct reading.

Caveat: the fetcher summarises; sections 5+ of the preprint and the full Gizmodo sentence were not fully seen; Capraro's thread and the OpenAI and Science pages could not be opened.

## Step 4. Draft clarification (NOT applied)
Abstract sentence, to add after "...that is not a Clay determination.":

> The theorem audited is the forced alternative (C) (and, with the errata's periodic-pressure condition, (D)); it does not address the unforced alternatives (A) or (B). We compare the Lean statements with Fefferman's text and with the corpus's challenge file, not with OpenAI's natural-language paper, and we make no claim that the Lean development matches that paper: an independent preprint (Bastounis, Circelli, Hansen, arXiv:2610.08144) reports lemma-level mismatches (for example m+5 against m+4 derivatives) and does not claim that the top-level statement misstates the Clay problem.

REVISION.md entry:

> v1.2 (clarification, not a correction of results). C1: abstract now states that the audited result is the forced alternative (C)/(D), not (A)/(B). C2: abstract and Section "What is not established" state that statement fidelity is measured against Fefferman's text and the corpus challenge file, not OpenAI's natural-language paper, so a public report that "Lean verified a weaker assertion than published" is neither confirmed nor refuted here. C3: "weaker" in the (D) caveat is qualified as "weaker than a main-text-only reading of (D), because of the errata's periodic-pressure condition", to avoid confusion with lemma-level hypothesis strength in arXiv:2610.08144. C4: the Bastounis et al. relay at l.316 is replaced by a direct reading of the arXiv text (Sections 3.1-3.3). No result, number or gate changed.

Follow-ups: read arXiv:2610.08144 Sections 3.1-3.3 in full; read OpenAI Theorem 1.1 and diff it against the challenge statement (this would settle "Lean weaker than published" at top level); ask the Gizmodo author which readers were meant.
