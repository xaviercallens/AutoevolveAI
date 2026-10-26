# REVISION: "The Discovery Journal" (EN), mirroring the FR revision after AUDIT.md

Date: 2026-10-26. Reviser: an AI agent (Claude). No human has reviewed this revision.
Source of the corrections: `papers/discovery_journal_2026/AUDIT.md`, `REVISION.md` and `CHANGES_FOR_EN.md` (FR, committed in b5f7b93).
Scope: the English frame (`main.tex`, `cadre/`, `code/`) and chapters c01–c10 and c16–c20. **c11–c15 were not touched**: another translator is still writing them, and their corrections (including B4 in c13 and N15 in c12) are to be mirrored later.
Nothing was committed, pushed or published.

## Blocking items

| # | Status | What was done |
|---|---|---|
| B1 | applied | `code/make_backmatter.py` now writes a 4-column table at `\linewidth` (`@{}r X p{2.3cm} c@{}`); the DOI or repository is printed under the title and date in the 2nd cell (`\newline{\footnotesize …}`); the 5th column is gone. Header: "No. / contribution (chapter title), DOI or repository / field / rigour". Docstring updated. `cadre/fabrication.tex` uses `\begingroup…\endgroup` instead of `pleinelargeur`. Rendered PDF pp. 132–133 (book pp. 120–121): every DOI and repository name is readable in full, no clipping. |
| B2 | applied | c03 ×3 → `Chapter~\ref{ch:c04}`; c04 ×2 → `Chapter~\ref{ch:c03}`; c17 → `\ref{ch:c01}`, `\ref{ch:c06}`, `\ref{ch:c20}`; c18 → `\ref{ch:c19}`. `main.aux` resolves them to c19 = 3, c20 = 5, c03 = 7, c04 = 10, c01 = 18, c06 = 20 (Elenchus = 1, c08 = 8), the same final numbers as the FR book. c01 "next chapter" and c02 "previous chapter" are correct (18 → 19) and were kept, as in FR. The frame's "Chapter~1" (cover, prologue) is the Elenchus chapter, correct. |
| B3 | applied | `cadre/elenchus.tex` (QU-1 certificate): "human-style reasoning" → "reasoning written by AI agents, which neither a machine nor a human has checked (level~C)", as the brief asked, consistent with the book's definition of C. c03: "a human argument" → "an argument written by AI agents, not checked by the machine". c10 (5 places, 6 edits): "proved only on paper, by AI agents"; "a written, step-by-step proof (drafted by AI agents)"; "(written proof, not checked by the machine)"; "a simpler written proof"; "stays at level~C, a line of reasoning carried out by AI agents"; "a proof written on paper (C)". c18 opening badge: "a line of reasoning, carried out by AI agents under the author's direction, and measured only on a small corpus written by the project itself". Extra (not in FR): `cadre/neurosymbolique.tex` "as a human proof" → "as a proof written for human readers" (it describes the textbook's proof, which was AI-written; FR keeps « démonstration humaine »). `pdftotext`: 0 hits for "human-style", "human proof", "human argument", "a human reasoned". |
| B4 | **not mirrored** | It applies to c13, which this pass must not touch. |
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
| 15 | **not mirrored** | c12 caption: c12 is out of scope for this pass. |
| 16 | applied | c07 caption: "; in green, the star with weights at equilibrium, which gives back 4/7". |
| 17 | applied | `images_cachees.tex`: "The original theorems, replayed on 26 October, are level~A (for ALIX, subject to the upstream openai/math theorem); the five short names are exact aliases of them, not replayed themselves." Only the file name `Acronymes.lean` is printed. The directory name was also removed from the docstring of `code/easter_egg_images_en.py` (now just `Acronymes.lean`); the script never used that path. A grep of `main.tex`, `cadre/`, `chapters/`, `code/` and `gen/` finds the name only in `code/build.py`, where it is the forbidden-word check itself (never printed). |
| 18 | partly applied | `limite` default title → "The limits, point by point" (it repeated the section heading "What this does not say"); the PDF shows it in all 15 present chapters. The other shape items are skipped, as in FR (style norms, optional). |
| 19 | applied | c20: "a calculation step such that $y=\omega h=1$". |
| 20 | applied | Bridge analogy: "unless the files or the tools change". |
| 21 | applied | (a) c08 header comment: the memory-note citation removed. The EN c17, c18, c19 headers never carried one. A grep for kebab-case `.md` names over `cadre/ chapters/ code/ gen/ main.tex` now finds nothing; the two "memory" hits left (prologue and dedication comments) are ordinary English ("no invented memory"), not note files. (b) No EN spare files exist; the EN build reads FR `ORDER.json`, already cleaned. (c) No EN copy of the Zenodo JSON. |
| 22 | applied | Dictionary: "The project admits only three standard Lean axioms, always the same ones"; "flows almost without friction". |
| 23 | skipped (author action) | Letter and prologue voice need the author's own sign-off. |
| 24 | applied | c20 analogy: the window sentences dropped; it now ends "…a little too *cold*; at large steps, it really does start to heat." |

## Translation-process sentence ("How this book was made")

Kept, but made modest: "This English edition is a translation of the French edition, *Le journal des découvertes*, also made by AI agents under the author's direction: one translated the frame, and four others translated the contribution chapters in parallel. They tried to keep the same claims, the same levels and the same limits as the French text, but some wording may still differ from it." The facts (one agent for the frame, four for the chapters) were kept; only the tone was softened ("keeping the same claims" became "tried to keep", plus the closing caveat).

## Build (code/build.py, actual output)

Final build, after the last edit:

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
