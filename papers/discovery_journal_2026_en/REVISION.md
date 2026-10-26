# REVISION: "The Discovery Journal" (EN), mirroring the FR revision after AUDIT.md

Date: 2026-10-26. Reviser: an AI agent (Claude). No human has reviewed this revision.
Source of the corrections: `papers/discovery_journal_2026/AUDIT.md`, `REVISION.md` and `CHANGES_FOR_EN.md` (FR, committed in b5f7b93).
Scope: the English frame (`main.tex`, `cadre/`, `code/`) and chapters c01–c10 and c16–c20. c11–c15 were not touched in the first pass (they were still being translated); their corrections (B4 in c13, N15 in c12) were mirrored in the second pass, below.
Nothing was committed, pushed or published.

## Blocking items

| # | Status | What was done |
|---|---|---|
| B1 | applied | `code/make_backmatter.py` now writes a 4-column table at `\linewidth` (`@{}r X p{2.3cm} c@{}`); the DOI or repository is printed under the title and date in the 2nd cell (`\newline{\footnotesize …}`); the 5th column is gone. Header: "No. / contribution (chapter title), DOI or repository / field / rigour". Docstring updated. `cadre/fabrication.tex` uses `\begingroup…\endgroup` instead of `pleinelargeur`. Rendered PDF pp. 132–133 (book pp. 120–121): every DOI and repository name is readable in full, no clipping. |
| B2 | applied | c03 ×3 → `Chapter~\ref{ch:c04}`; c04 ×2 → `Chapter~\ref{ch:c03}`; c17 → `\ref{ch:c01}`, `\ref{ch:c06}`, `\ref{ch:c20}`; c18 → `\ref{ch:c19}`. `main.aux` resolves them to c19 = 3, c20 = 5, c03 = 7, c04 = 10, c01 = 18, c06 = 20 (Elenchus = 1, c08 = 8), the same final numbers as the FR book. c01 "next chapter" and c02 "previous chapter" are correct (18 → 19) and were kept, as in FR. The frame's "Chapter~1" (cover, prologue) is the Elenchus chapter, correct. |
| B3 | applied | `cadre/elenchus.tex` (QU-1 certificate): "human-style reasoning" → "reasoning written by AI agents, which neither a machine nor a human has checked (level~C)", as the brief asked, consistent with the book's definition of C. c03: "a human argument" → "an argument written by AI agents, not checked by the machine". c10 (5 places, 6 edits): "proved only on paper, by AI agents"; "a written, step-by-step proof (drafted by AI agents)"; "(written proof, not checked by the machine)"; "a simpler written proof"; "stays at level~C, a line of reasoning carried out by AI agents"; "a proof written on paper (C)". c18 opening badge: "a line of reasoning, carried out by AI agents under the author's direction, and measured only on a small corpus written by the project itself". Extra (not in FR): `cadre/neurosymbolique.tex` "as a human proof" → "as a proof written for human readers" (it describes the textbook's proof, which was AI-written; FR keeps « démonstration humaine »). `pdftotext`: 0 hits for "human-style", "human proof", "human argument", "a human reasoned". |
| B4 | applied (second pass, see below) | c13: ten lemmas now \niveau{A}, replayed 26 October, margin note citing replay.jsonl line 86. |
| B5 | applied | (1) Part III opener in `main.tex`: "refuted first by calculation and then, in one precise case, by a certificate: for several forces, the triangular lattice is no longer the best when quantum jitter is taken into account, in a simplified model." (2) `neurosymbolique.tex`: "of the Sandier--Serfaty certificate, only four stages out of twelve, that is 0.136 % of the operations, have made it into the kernel". (3) `elenchus.tex` rule 3: "In the autumn work, no measurement is reported without its two controls."; rule 4: "In the work of the end of the year, the AI agent that produces a result is not the one that checks it." |
| B6 | applied | c16: "On 23 September 2026, the public repository openai/math delivered a proof". |
| B7 | applied | Title and line-1 comment: "The Elenchus method, explained simply" (TOC and running heads checked on the PDF). Opening: "If I had to explain to someone who is not a scientist what I did this year, … a question anyone can ask: *how can you tell whether a machine is telling the truth?*" No thought is attributed to any relative. The generic jam-label idiom "grandmother's recipe, never tested" stays, as in FR. |

## Nonblocking items

| # | Status | Note |
|---|---|---|
| 1 | applied | `fabrication.tex`: "(The score of contribution No. 20 follows the inventory, which does not cite the list of axioms; the repository's check file gives it, hence the chapter's As badge.)" |
| 2 | applied | Domain disclosure in `fabrication.tex`: "The fields are those of the inventory: cosmology and teaching are counted there separately from physics, which explains why physics in the broad sense has nine chapters (seven in physics and two in cosmology)." |
| 3 | applied | `elenchus.tex`: "Two formulas, programmed in four ways and then a fifth time by the auditor, compute…" |
| 4 | applied | Jam analogy: "a level~A theorem is only worth as much as its statement, and the judge itself can, very rarely, be wrong". |
| 5 | applied | "the audit of one of the last papers of the year". |
| 6 | applied | "In 2026, OpenAI published proofs…". |
| 7 | applied | `neurosymbolique.tex`: integer-certificate paragraph badge → `\niveau{As}`. |
| 8 | applied | `\ref{ch:c08}` added to the openai/math dependency list (now c16, c03, c08, c09, c04, c10). |
| 9 | applied | `couverture.tex`: "(A, As, L, C or X)"; `dictionnaire.tex`: "Level (A, As, L, C, X)" with "As, ``the judge has looked, without replay''". |
| 10 | applied | `couverture.tex`: "from the records of the work itself" ("public" dropped). |
| 11 | not needed | The EN `retraits.tex` never had the double parenthesis. |
| 12 | applied | `retraits.tex`: "141 code packages (crates) out of 316". |
| 13 | already in EN | The EN generator already skipped the final period after ?, ! or . . |
| 14 | applied | c02: "and the gap from the best point is about 54.6 at H0 = 73". |
| 15 | applied (second pass, see below) | c12 caption: "(below $a\approx0.12$ the curvature is tiny and is not used)". |
| 16 | applied | c07 caption: "; in green, the star with weights at equilibrium, which gives back 4/7". |
| 17 | applied | `images_cachees.tex`: "The original theorems, replayed on 26 October, are level~A (for ALIX, subject to the upstream openai/math theorem); the five short names are exact aliases of them, not replayed themselves." Only the file name `Acronymes.lean` is printed. The directory name was also removed from the docstring of `code/easter_egg_images_en.py` (now just `Acronymes.lean`); the script never used that path. A grep of `main.tex`, `cadre/`, `chapters/`, `code/` and `gen/` finds the name only in `code/build.py`, where it is the forbidden-word check itself (never printed). |
| 18 | partly applied | `limite` default title → "The limits, point by point" (it repeated the section heading "What this does not say"); the PDF shows it in all chapters (15 at the first pass, 20 after the second). The other shape items are skipped, as in FR (style norms, optional). |
| 19 | applied | c20: "a calculation step such that $y=\omega h=1$". |
| 20 | applied | Bridge analogy: "unless the files or the tools change". |
| 21 | applied | (a) c08 header comment: the memory-note citation removed. The EN c17, c18, c19 headers never carried one. A grep for kebab-case `.md` names over `cadre/ chapters/ code/ gen/ main.tex` now finds nothing; the two "memory" hits left (prologue and dedication comments) are ordinary English ("no invented memory"), not note files. (b) No EN spare files exist; the EN build reads FR `ORDER.json`, already cleaned. (c) No EN copy of the Zenodo JSON. |
| 22 | applied | Dictionary: "The project admits only three standard Lean axioms, always the same ones"; "flows almost without friction". |
| 23 | skipped (author action) | Letter and prologue voice need the author's own sign-off. |
| 24 | applied | c20 analogy: the window sentences dropped; it now ends "…a little too *cold*; at large steps, it really does start to heat." |

## Translation-process sentence ("How this book was made")

Kept, but made modest: "This English edition is a translation of the French edition, *Le journal des découvertes*, also made by AI agents under the author's direction: one translated the frame, and four others translated the contribution chapters in parallel. They tried to keep the same claims, the same levels and the same limits as the French text, but some wording may still differ from it." The facts (one agent for the frame, four for the chapters) were kept; only the tone was softened ("keeping the same claims" became "tried to keep", plus the closing caveat).

## Build (code/build.py, actual output)

First-pass build (superseded: the final build, 20 chapters and 153 pages, is at the end of this file):

- pdflatex ×3: exit codes [0, 0, 0]; **143 pages**.
- 0 errors in the frame, 0 in the 15 present chapters.
- 0 undefined references.
- 0 overfull boxes above 15 pt (frame and chapters).
- Chapters present: c01–c10, c16–c20. c11–c15 appear as "In preparation" placeholders (expected until they arrive); the book's chapter numbering is already final, so the `\ref` numbers above will not move when they arrive.
- `pdftotext` on `main.pdf`: the Lean directory name occurs 0 times (also the build's own forbidden-word check: 0).
- Pages rendered with `pdftoppm -r 70` and read:
  - PDF 132–133 (book 120–121): the repaired table, 4 columns, DOIs/repositories in full, no clipping.
  - PDF 15: the Elenchus opening, new title "The Elenchus method, explained simply" and the neutral first sentences.
  - PDF 73: the Part III opener with the conditional wording.
  - PDF 142–143: the hidden-image spread, still one verso + recto pair; the new alias sentence fits, all five pictures and captions intact.
  - PDF 69: c10 opening, "proved only on paper, by AI agents" and "a written, step-by-step proof (drafted by AI agents)".

## Second pass (2026-10-26): chapters c11–c15

Each English chapter c11–c15 was read in full against the revised French chapter. Of the FR changes in `CHANGES_FOR_EN.md`, two touch these chapters (B4 in c13, N15 in c12). Both are now mirrored:

| # | File | What was done |
|---|---|---|
| B4 | `chapters/c13.tex` | The ten lemmas: `\niveau{As}` "…but no replay is recorded in the paper" → `\niveau{A}` "*the judge has looked*: the Lean kernel checked them, axioms within the short list, planted false proofs exposed, and the module was replayed without error on 26 October 2026, after the paper was published. These lemmas only say that the statement is not empty of meaning; they prove nothing about the conjecture." New margin `\reference`: "Replay of 26 October 2026, `results/kernel_replay_2026-10-26/replay.jsonl`, line 86: module `Programmes.SandierSerfatyStatement`, exit code 0." Both paths are set with `\nolinkurl`, as in FR. |
| N15 | `chapters/c12.tex` | Figure caption: "(below $a\approx0.12$ the curvature is tiny and is not used)" added after the band. |

The other checks found nothing to change:
- **B3.** c11, c12, c13 and c15 already call the AI reasoning "carried out here by AI agents / by an AI and not by a human", as FR does.
- **B2.** The only chapter cross-reference is c12's "the next chapter" (c12 = 13, c11 = 14). It is correct, and FR keeps it too.
- **N21.** The EN headers of c11–c15 never cited memory notes.
- **B6.** c13's "In September 2026" matches FR.

## Fidelity check

See `FIDELITY.md` for the method. The English files were changed as follows:

| File | FR | EN before | EN after | Why |
|---|---|---|---|---|
| `chapters/c07.tex` | « un agent d'IA distinct de la même famille de modèles » | "an AI agent distinct from the author but from the same family of models" | "an AI agent distinct from the one that produced the work but from the same family of models" | **Mistranslation.** The old text made the author (a human) the producer, and implied that he belongs to a "family of models". It also broke the producer ≠ verifier distinction. |
| `cadre/lettre.tex` | « Les humains aussi, et moi le premier. » | "Humans can too, and I am the first." | "Humans can too, starting with me." | **Mistranslation.** The old text could be read as "I was the first human to do this". |
| `cadre/prologue.tex` | « Début octobre, la méthode a commencé à servir » | "…started to pay off" | "…started to be put to use" | **Slight strengthening.** "Pay off" implies the method succeeded. |
| `cadre/prologue.tex` | « lui aussi non encore relu par des pairs » | "which has not been peer reviewed either" | "which has not yet been peer reviewed either" | Restores the "not yet" of the FR. |
| `chapters/c03.tex` | « \niveau{A} \emph{Le juge a regardé.} » | "The judge looked." | "The judge has looked." | Uses the book's fixed badge gloss. |
| `chapters/c20.tex` | « …sous l'étiquette « relu par les pairs en cinq tours ». » | (label only) | "…, a label with no basis: no human had reviewed them, and the review file came from a program that called no reviewer (see below)." | **EN-only clarification, not a translation error; pending FR adoption.** No reviewer of any kind (human or model) was called. In c20 the reader learns only four paragraphs later that the label was empty. The added facts are those of the FR prologue (« Aucun humain ne les avait relus : le fichier de relecture avait été produit par un programme qui n'appelait aucun relecteur ») and of c20 itself (« une relecture en plusieurs tours qui n'appelait aucun relecteur »). Suggested for FR c20 too; FR is not edited. |

After these edits: build 0 errors, 0 undefined references, 0 overfull > 15 pt, 153 pages, the directory name 0.

## Post-fidelity corrections (2026-10-26)

These items come from `papers/discovery_journal_2026_en/FIDELITY.md` §3. Each was checked against the source record, not against the book. The French and English editions were changed identically in substance. The checker is an AI agent (Claude). No human has reviewed these corrections. Nothing was committed, pushed or published.

1. **c07, three-site against four-site star: REAL (unexplained, not wrong).**
   - Source: `papers/p3_isothermal_theorem/main.tex`, Table `tab:ctl`.
     - l.159: star n=3, values 5/12 (centre), 2/3 (leaf), 7/12 (uniform), Tier A, EG-A-0009.
     - l.164: star n=4, values 392/1265, 168/253, mean 728/1265, Tier X, EG-X-0001, "*not* kernel-checked".
   - `AUDIT.md` l.60 and l.64 recompute the same numbers.
   - `code/fig07.py` has two panels: 3 sites, and 4 sites (complete, cycle, star centre, star at random).
   - So the X badge and the limits bullet were correct, but they described the figure's right panel, which the text never introduced.
   - The sentence « le centre est remplacé deux fois plus souvent » was incomplete.
     - Column sums of the n=3 star: centre 2, leaf 1/2, average 1. `main.tex` l.159 calls this "centre temperature 2".
     - So the centre is replaced twice as often as the average, and four times as often as a leaf.
   - Fix:
     - The pencil box now gives the column sums and both comparisons, and the 3-star values 5/12, 2/3, 7/12, marked as proved in Lean.
     - It introduces the 4-star (Moran 8/15; 392/1265, 168/253, 728/1265), marked as only computed.
     - The caption names both panels and their levels.
     - The level summary gives A to the theorem and the 3-star values, and X to the 4-star values of the figure.
     - The limits bullet says which star is X and which is proved.
   - The leaf value 168/253 is not plotted, and the text does not say it is.
2. **c16, « quatre fichiers » against « trois énoncés » / « trois modules »: NOT REAL as a factual error; the count was unexplained.**
   - Source: `papers/triangular_riesz/triangular_riesz.tex` l.140–143 (the record of doi:10.5281/zenodo.23285631, per `papers/triangular_riesz/zenodo_doi.txt`) names four proof files: `Riesz.lean`, `RieszFinite.lean`, `AnyDensity.lean`, `Controls.lean`. The fifth file, `Axioms.lean`, holds only the planted controls.
   - The four is correct. It is the three statement files plus `Controls.lean`, which holds verifier checks such as `riesz_neg_two_not_admissible` (the t↦t refusal).
   - FIDELITY guessed that the fourth file was the Lean counterexample. That guess is wrong: the counterexample is inside `AnyDensity.lean` (l.203).
   - The 26 October replay (`results/kernel_replay_2026-10-26/replay.jsonl`, REPLAY.md) has rc-0 rows for Triangular.Riesz, RieszFinite and AnyDensity, and none for Controls. The reason is that `scripts/kr_plan.py` l.10 skips every module whose name contains "Controls".
   - Fix: the count is kept, and both editions now say which four files there are and that the replay left out the control files by rule.
3. **c03, gaps to 2.2e-6 against a cut-off of about 0.018: NOT REAL (no contradiction); reworded.**
   - Source: `papers/ar_yukawa_crystal/data/NUMERICS.md` §1.
     - At κ=1 the shifted-force cut moves the triangular energy by 1.771212e-2 and the square energy by 1.770992e-2.
     - The square–triangular gap therefore moves by only −2.200e-6 (9.5363558e-3 published against 9.5341557e-3 exact).
     - The ordering triangular < square holds under the exact potential.
     - The erratum is that the truncated potential is not completely monotone, so the simulation studied an approximation.
   - Fix:
     - The limits bullet now says that the 0.018 is the shift of *each lattice's* energy, that both shift almost equally so the gap moves by only 2.2e-6, and that the triangle stays lower under the exact law. It keeps the erratum and its real consequence.
     - The caption now says "gaps" (« écarts ») instead of "values".
4. **c20, the label « relu par les pairs en cinq tours »: REAL (FR).**
   - Source: the record for doi:10.5281/zenodo.23525655 (`results/discovery_journal_2026/zenodo_inventory.json`): "edition 1 was described as peer reviewed; that is withdrawn. The bundled '5-round Opus peer review' file was generated by a script that calls no reviewer, and it is no longer distributed. … This paper has not been peer reviewed."
   - Fix: FR c20 now carries, where the label first appears, the sentence that EN already had: « une étiquette sans fondement : aucun humain ne les avait relus, et le fichier de relecture venait d'un programme qui n'appelait aucun relecteur (voir plus bas) ».
   - Sweep: I grepped both books (main.tex, cadre/, chapters/, gen/) for peer / pairs / relu / relect / review / cinq tours / five rounds / 5-round / Opus, and read the label passages in context: prologue, elenchus, retraits, c20, EN neurosymbolique.
   - No sentence says or implies that the label meant review by AI agents. Every passage says that no reviewer was called.
   - Outside the books, not edited: `results/discovery_journal_2026{,_public}/zenodo_inventory.{json,md}` classification notes say the label "denotes AI-agent (Opus) review". That contradicts the 23525655 record and should be corrected by whoever owns the inventory.
5. **c05, the 1.4–4 K data range: precision added (minor REAL).**
   - The chapter opens on superfluid helium, and the source paper's title says "superfluid ⁴He". `papers/prog_superfluid_structure_factor/main.tex` l.271 says the data are at 1.4–4 K and that no temperature is printed per point. l.309 and l.356 say that the temperature dependence was not quantified.
   - The chapter did not claim that every point was superfluid, but the « pas au zéro absolu » bullet did not say that part of the range is not superfluid.
   - Fix: the bullet now says that the data run from 1.4 to 4 K, that above about 2.17 K (the lambda point) liquid helium is no longer superfluid, that the table gives no per-point temperature, and that the temperature effect was not quantified.
   - The value 2.17 K is a textbook fact (the λ point at saturated vapour pressure). It is not taken from the paper's record.

**Build after these edits** (`code/build.py`, pdflatex ×3, actual output), both editions:
- exit codes [0, 0, 0], 153 pages.
- 0 errors, 0 undefined references, 0 overfull boxes above 15 pt (frame and chapters).
- 20/20 chapters present.
- `pdftotext`: the directory name occurs 0 times in either PDF.

**Fidelity check** (`code/fidelity_check.py`, rerun):
- c05 and c16: all ok.
- c03, c07 and c20: `numbers`, `niveau`, `refs` and `figures` ok.
- The remaining `number_words` hits are the known pattern: FR « les deux » → EN "both", and « deux fois » → "twice". c20's `doi_macro` difference is the old, presentation-only one.
