# FIDELITY: English edition against the revised French edition

Date: 2026-10-26. Checker: an AI agent (Claude), helped by three AI read-only sub-agents for the side-by-side reading. No human has reviewed this check.
- **Compared:** `papers/discovery_journal_2026/` (FR, after its audit revision, commits b5f7b93 + e05aa1d) with `papers/discovery_journal_2026_en/` (EN).
- **Nothing was committed, pushed or published.** The French files were not edited.

## 1. Mechanical comparison (`code/fidelity_check.py`)

`python -I code/fidelity_check.py` compares 35 file pairs:
- `main.tex`
- the 11 files in `cadre/`
- the 3 files in `gen/`
- `chapters/c01`–`c20`

It first removes LaTeX comments. It then extracts these sequences, in order, from each file and compares them. Full output: `fidelity_report.json`.

| Sequence | What it extracts and how it normalises |
|---|---|
| `dois` | Every Zenodo record number. |
| `numbers` | Every number in the text and in math. The decimal comma is normalised: FR `0{,}377`, or `0,6` in text, becomes `0.377`. A bare comma in FR math is a list separator. Thousands separators are removed: FR `1\,685\,129`, EN `1{,}685{,}129` and `88,400` all become plain digits. Removed first: layout dimensions, colour mixes, TikZ coordinates, DOIs, labels, refs and file names. |
| `percents`, `months` | Numbers followed by %. Month names, FR mapped to EN. |
| `niveau`, `refs`, `labels`, `doi_macro`, `figures` | Every `\niveau{}` badge. Every `\ref`, every `\label`, every `\doi{}`. Every `\includegraphics` file name. |
| `headings` | Chapters only: one `\chapter` plus the five `\section*` headings, mapped FR → EN. That is the six headings. |
| `number_words` | Spelled-out cardinals 2–20, 30, 100 and 1000. |

Each pair is rated:
- `ok`: the sequences are identical.
- `order`: the same tokens in a different order.
- `mismatch`: anything else.

**Controls** (run on every invocation, see the `controls` block of the report):
- **Negative.** The unmutated c13 pair is all `ok`. Three formatting-only edits change no status:
  - `1{,}685{,}129` → `1685129`
  - `88,400` → `88\,400`
  - `478~seconds` → `478 seconds`
- **Positive.** Seven content mutations of EN c13 each make their own check fire:
  - one number changed (478 → 487)
  - one decimal changed (−6.73003 → −6.73030)
  - the badge A → As
  - one DOI digit changed
  - the month September → October
  - one figure file swapped
  - one heading renamed

  All 7 fired. By the A → As positive control, the badge check would also have flagged c13's stale `As` badge (B4) before Step 1 (inferred from the control, not run on the old file).

### Mismatch list and resolution (final run)

| File | Check | Finding | Resolution |
|---|---|---|---|
| all 35 pairs | dois, numbers, percents, months, niveau, refs, labels, figures, headings | identical, in the same order | none needed. This covers all 20 chapters with their six headings each, the dedication (`dedicace.tex`) and the hidden-image page (`images_cachees.tex`, 5 figures, 3 numbers, the date "26 October"). |
| `cadre/retraits.tex` | numbers: `order` | « publie le 24 juillet » against "On 24 July, … publishes" | Word order only. Not an error. |
| `chapters/c18.tex`, `chapters/c20.tex` | doi_macro: `mismatch` | FR writes `doi:10.5281/zenodo.N` as plain text; EN uses the `\doi{}` macro (4 and 3 times). | Presentation only. The record numbers themselves match exactly (`dois` ok). Not an error. |
| 17 files | number_words: `mismatch` / `order` | Every hit was read in context. They come mainly from four patterns: FR « les deux » / « toutes deux » rendered as "both" or "the"; FR « rien de neuf » ("new"); "several hundred" for « plusieurs centaines »; compounds (« quatre cent vingt » = "four hundred and twenty", « trente et une » = "thirty-one"), plus c01's EN "caught between the two", which has no number word in FR. | No number changed. Not an error. The EN-only "four" in `fabrication.tex` is the translation-process sentence, which exists only in EN. |

Script fixes while developing it, recorded for honesty:
- FR math lists (`$0,1,2,3$`) and TikZ coordinates were at first read as decimals.
- `\,` inside FR math was split.
- `\div1` swallowed a digit.

All four were extractor bugs, not text differences. They were fixed before the final run.

## 2. Side-by-side reading (meaning, not numbers)

Read in full, FR against EN, paragraph by paragraph: **15 chapters and 6 frame files.**

| Part | Chapters read |
|---|---|
| I | c17, c18, c19, c20 |
| II | c16, c03, c10 |
| III | c05, c12, c11 |
| IV | c13, c14, c15 |
| V | c01, c02, c06, c07 |
| Frame | Elenchus, neuro-symbolic, letter, prologue, withdrawals, cover |

c11–c15, c18, c20 and the letter were read by the main agent. The rest were read by three AI sub-agents, and every finding they reported was checked against the files before any edit.

| Point checked | Result |
|---|---|
| Sandier–Serfaty **not** proved | **Kept everywhere.** c13: "This chapter does not say that the conjecture is proved … not a peer review"; "Nothing is proved about the conjecture". c14: "the conjecture is not formally proved; nothing here says that it is"; 4 steps of 12, 0.136 %. Prologue, Elenchus and neuro-symbolic: the same. |
| Navier–Stokes is not a Clay solution, and credit goes to the corpus authors | **Kept.** c15: "The credit for these proofs belongs to the authors of the corpus"; "This is not an announcement that a Clay problem is solved"; "No Clay problem is declared solved". Elenchus: the same. |
| Conditional on openai/math | **Kept.** Part II opener, c16, c03, c08, c09, c04, c10 and the ALIX caption. c13 and c14 are conditional on the OpenAI manuscript. |
| No human mathematician has reviewed | **Kept at the same strength** in the cover, prologue, Elenchus, fabrication and neuro-symbolic files, and once per chapter. |
| Retractions told faithfully | **`retraits.tex` faithful**, item by item. The c18 and c20 retractions and the c17 hand-typed numbers are told as candidly as in FR. |
| c20's label "peer reviewed in five rounds" | The FR chapter (like the EN before this pass) quotes the label and says only four paragraphs later that the "multi-round review" called no reviewer. **The facts are not that AI agents did the review.** Per FR's prologue and Elenchus, *no* reviewer was called: neither a human nor a model. The EN now says at the label itself: "a label with no basis: no human had reviewed them, and the review file came from a program that called no reviewer (see below)". This is an EN-only divergence, built only from FR facts and pending FR adoption (§3.4); it is not a translation fix. **Note on the brief:** the label does not mean review by AI agents either; the record says no reviewer of any kind was called. |

### Genuine translation errors fixed in EN (also recorded in `REVISION.md`, "Fidelity check")

1. **c07.** "an AI agent distinct from the author" → "distinct from the one that produced the work". This was a meaning error: it made the author the producer, and the author a "model".
2. **letter.** "Humans can too, and I am the first." → "Humans can too, starting with me." This was a meaning error.
3. **prologue.** "the method started to pay off" → "started to be put to use". The old text was a slight strengthening.
4. **prologue.** "has not been peer reviewed either" → "has not *yet* been peer reviewed either".
5. **c03.** Badge gloss "The judge looked." → "The judge has looked." This is for consistency.
Separately, not a translation error: **c20** carries the EN-only label clarification above, pending FR adoption.

### Mirrored from the FR audit revision in this pass

These are not fidelity errors in the old sense: FR changed after the EN was translated.
- **c13 B4:** level A, replayed on 26 October, with the margin note citing `replay.jsonl` line 86, `Programmes.SandierSerfatyStatement`, exit code 0.
- **c12 N15:** the caption now says that below a≈0.12 the curvature is tiny and is not used.

### Points left as they are

- **EN Elenchus:** "(level~C)" after "neither a machine nor a human has checked". This was added in the first EN revision on purpose, and it matches the paragraph's badge.
- **EN additions that claim nothing new:**
  - the translation-process sentences (`couverture.tex`, `fabrication.tex`)
  - the c01 gloss on baryon acoustic oscillations
  - "plain-language summaries" / "glosses in plain language" for « en français »
  - c06 « a intégré » rendered as "handled"

## 3. Possible errors in the French (reported, not edited; to be checked by the FR reviser)

These were found by reading. Apart from point 4, none has been checked against the source records.

1. **c07, l. 51–53 against l. 66 and l. 91.** The pencil box works with a *three-site* star (4/7, 5/12). But the level summary and the limits box speak of the values of the « étoile à quatre sites ». Either the figure has a four-site star that the text never introduces, or this is a slip. The same sentence, « le centre est remplacé deux fois plus souvent », is twice the average, but four times as often as a leaf.
2. **c16, l. 56 against l. 9 and l. 66.** « Les quatre fichiers de preuve se compilent », but there are « trois énoncés » and the replay passed « sur les trois modules ». The fourth file may be the Lean counterexample (l. 52), but the text does not say so.
3. **c03, l. 59–60 against l. 86–87.** The caption says the published gaps differ from the exact ones by at most 2.2×10⁻⁶. The limits box says the cut-off lowered the energy by about 0.018, which is more than the 0.0095 gap. Both can be true if the shift cancels in the difference, but a short clause would help the reader.
4. **c20, l. 25.** The label « relu par les pairs en cinq tours » is not explained where it appears (see §2). Suggested FR wording: « …sous l'étiquette « relu par les pairs en cinq tours », une étiquette sans fondement : aucun humain ne les avait relus, et le fichier de relecture venait d'un programme qui n'appelait aucun relecteur (voir plus bas). »
5. **Minor:**
   - c03, l. 42–43: the factor 1000/999 is only an order-of-magnitude picture.
   - c05: the 1.4–4 K data range includes non-superfluid helium above about 2.17 K. The text does not claim otherwise.

## 4. Build (code/build.py, actual output after all edits)

- pdflatex ×3: exit codes [0, 0, 0].
- **153 pages**, the same as the FR edition.
- 0 errors, 0 undefined references, 0 overfull boxes above 15 pt (frame and chapters).
- 20/20 chapters present, 0 pending, no "In preparation" text in the PDF.
- No figure taken from the FR edition.
- `pdftotext`: `Famille` occurs 0 times.
- Rendered with `pdftoppm -r 70` and read:
  - PDF 91: the c13 badge, "Level A, the judge has looked…", with the replay margin note in full.
  - PDF 82: the c12 caption with the a≈0.12 clause.
  - PDF 43: the c20 opening with the label clarification.
  - PDF 152: the hidden-image verso, with the alias sentence.

## Verdict

**FAITHFUL, after corrections.**
- Every DOI, number, date, percentage, badge, cross-reference, label and figure, and all 120 chapter headings, agree with the French, in the same order.
- The two meaning errors (c07, letter) and three nuance errors (prologue ×2, c03) are fixed.
- No claim is softened or strengthened on the five sensitive points (Sandier–Serfaty, Navier–Stokes, openai/math condition, no human review, retractions).
- c20 is now clearer than the French on the "peer reviewed" label; the matching French fix is suggested, not applied.
- This verdict comes from AI agents only. A bilingual human reader has not checked it.
