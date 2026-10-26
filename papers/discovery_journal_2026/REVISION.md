# REVISION: « Le journal des découvertes » (FR), after AUDIT.md (ACCEPT_WITH_CORRECTIONS)

Date: 2026-10-26. Reviser: an AI agent (Claude), separate from the auditor. No human has reviewed this revision.
Scope: only files under `papers/discovery_journal_2026/` were changed. Nothing was committed, pushed or published.
The two spare-file removals were staged with `git rm` because the files were tracked.

## Blocking items

| # | Status | What was done |
|---|---|---|
| B1 | applied (fix b) | `code/make_backmatter.py` now writes a 4-column table at `\linewidth`. The DOI or repository is printed under the title in the 2nd cell (`\newline{\footnotesize …}`), and the 5th column is gone. `cadre/fabrication.tex` no longer wraps the table in `pleinelargeur` (a plain `\begingroup…\endgroup` instead). Re-rendered: PDF pp. 142–143 (book pp. 130–131). Every DOI on both pages can be read in full, with no clipping. |
| B2 | applied | The 8 hard-coded references now use `\ref{ch:cNN}`. The labels are set automatically by `\contribution` in `main.tex`. Places changed: c03 ×3 → `ch:c04`; c04 ×2 → `ch:c03`; c17 → `ch:c01`, `ch:c06`, `ch:c20`; c18 → `ch:c19`. `main.aux` resolves them to the final numbers: c19 = 3, c20 = 5, c03 = 7, c04 = 10, c01 = 18, c06 = 20. These match the audit's table from `main.toc`. |
| B3 | applied | The « humain » wording was replaced with the audit's exact text in `cadre/elenchus.tex`, `chapters/c03.tex`, `chapters/c10.tex` (5 places) and `chapters/c18.tex`. `pdftotext` finds 0 hits for « raisonnement(s) humain(s) » or « preuve humaine ». |
| B4 | applied | c13: the ten lemmas are now \niveau{A}, with the audit's text: replayed without error on 26 October 2026, after the paper was published, and they say only that the statement is not vacuous. A margin note cites the replay row: `results/kernel_replay_2026-10-26/replay.jsonl`, line 86, module `Programmes.SandierSerfatyStatement`, rc 0. I checked that row against the file myself. |
| B5 | applied | (1) The Part III opener in `main.tex` now uses the audit's conditional wording. (2) `neurosymbolique.tex` now says « seules quatre étapes sur douze, soit 0,136 % des opérations ». (3) `elenchus.tex` rule 3 now reads « Dans les travaux de l'automne… » and rule 4 « Dans les travaux de la fin de l'année… n'est pas celui qui le vérifie ». |
| B6 | applied | c16 now reads « Le 23 septembre 2026, le dépôt public openai/math a livré une démonstration ». |
| B7 | applied | The chapter title is now « La méthode Elenchus, expliquée simplement ». This shows in the TOC and the running heads, as checked on the PDF. The comment on line 1 was updated to match. The opening uses the audit's neutral sentences. No thought is attributed to any family member. The generic idiom « recette de grand-mère » (jam-label analogy) stays, as the audit allows. |

## Nonblocking items

| # | Status | Note |
|---|---|---|
| 1 | applied | c20 rigour 1/3 vs the As badge: the audit's parenthesis was added to `fabrication.tex`. The As badge in c20 is kept. |
| 2 | applied | Domain disclosure added to `fabrication.tex`: cosmology and education are counted apart from physics, so physics in the broad sense has nine chapters (seven physics, two cosmology). |
| 3 | applied | `elenchus.tex`: « Deux formules, programmées de quatre façons, puis une cinquième fois par l'auditeur ». |
| 4 | applied | `elenchus.tex`, jam analogy: « un théorème de niveau A ne vaut que ce que vaut son énoncé, et le juge lui-même peut, très rarement, se tromper ». |
| 5 | applied | « celui d'un des derniers articles de l'année ». |
| 6 | applied | « En 2026, OpenAI a publié… ». |
| 7 | applied | `neurosymbolique.tex`: the integer-certificate paragraph badge is now \niveau{As}. |
| 8 | applied | `\ref{ch:c08}` (the textbook) was added to the list of chapters that depend on openai/math. |
| 9 | applied | `couverture.tex`: « (A, As, L, C ou X) ». `dictionnaire.tex`: « Niveau (A, As, L, C, X) », with « As, le juge a regardé, sans rejeu ». |
| 10 | applied | `couverture.tex`: « des dossiers des travaux eux-mêmes (Zenodo, GitHub) et du dossier de sélection ». The word « publics » was dropped. |
| 11 | applied | `retraits.tex`: the double parenthesis was removed. |
| 12 | applied | `retraits.tex`: « 141 paquets de code (crates) sur 316 ». |
| 13 | applied | `make_backmatter.py` skips the final period when a title ends in ?, ! or . (`gen/dois.tex` n° 7 is now correct). |
| 14 | applied | c02: « et l'écart au meilleur point vaut environ 54,6 à H0 = 73 ». |
| 15 | applied | c12 figure caption: « (sous a ≈ 0,12 la courbure est minuscule et n'est pas exploitée) ». |
| 16 | applied | c07 caption: the green bar (weighted star at equilibrium, 4/7) is now explained. |
| 17 | applied | `images_cachees.tex`: the original theorems, replayed on 26 October, are level A. The five short names are exact aliases, not replayed themselves. I checked that `Acronymes.lean` has an `rfl` alias example for each name and that the five source modules are rc-0 rows in `replay.jsonl`. The Lean file's directory is not printed or linked anywhere in the book. |
| 18 | partly applied | **Applied:** the repeated `limite` heading. In `main.tex` the default box title is now « Les limites, point par point », so it no longer repeats the section heading « Ce que ça ne dit pas ». All 20 `limite` boxes use the default title, and none is in `cadre/`; the PDF shows the new title 20 times. **Skipped:** the c12 trim (1224 words), figure placement, and the order of the analogy box and badge. The audit marks these « if time allows ». They are style norms, not errors. Trimming c12 would mean choosing which audited content to cut, and the audit does not say which. |
| 19 | applied | c20: « un pas de calcul tel que $y=\omega h=1$ ». |
| 20 | applied | Bridge analogy: « sauf si l'on change les fichiers ou les outils ». |
| 21 | applied (2 of 3) | (a) The LaTeX comments citing internal memory notes were removed from c08, c17, c18 and c19. A grep for memory-note names in `cadre/ chapters/ code/ gen/ main.tex` now finds nothing. (b) `chapters/spare_N2.tex`, `code/spare_fig12.py`, `figures/spare_c12_majorantes.{pdf,png}` were removed with `git rm`, and `ORDER.json` `unused_files` was set to `[]`. (c) **skipped**: the temp path inside `data/zenodo23119953_gwaya_v3_oracle_eval.json`. The audit says it may be left as is, because that file is a copy of the public Zenodo record. |
| 22 | applied | Dictionary: « Le projet n'admet que trois axiomes standard de Lean » and « presque sans frottement ». |
| 23 | **skipped (author action)** | The letter and the prologue opening must be read and signed off by the author. An agent cannot do that. |
| 24 | applied | c20 analogy: the window sentences were dropped, and the paragraph now ends « …un peu trop froide ; aux grands pas, il se met vraiment à chauffer ». |

## Build (code/build.py, actual output)

- pdflatex ×3: exit codes [0, 0, 0].
- 0 errors (frame and chapters).
- 0 undefined references.
- 0 overfull boxes above 15 pt, in the frame or in the chapters.
- **153 pages.** All 20 chapters are present.
- An intermediate build showed a 36 pt overfull in the new c13 margin note. I fixed it by setting the module name with `\nolinkurl` so that it can break.
- `pdftotext` on `main.pdf` finds le nom du répertoire (retiré) 0 times.
- Rendered and read with `pdftoppm -r 70`:
  - PDF 142–143: the repaired table, no clipping.
  - PDF 15: the Elenchus opening with its new title.
  - PDF 91: the c13 badge text and the replay margin note.
  - PDF 152–153: the hidden-image spread, still one verso + recto pair.

## Extra sweeps after the fixes

- **B3 sweep.** I searched the PDF text for « humain a raisonn », « à la main », « de l'auteur », « mené par l'auteur », « raisonnement humain » and « humaine ».
  - No other AI-made argument is called human.
  - The remaining « à la main » hits are about hand-typed values or hand calculation (cover, c17, c18, c16), not about who reasoned.
  - The remaining « humaine » hits are about human review, which has not happened, and that is correct.
- **Replay rows for the five acronym sources.** Each has its own rc-0 row in `replay.jsonl`: Triangular.AnyDensity, Programmes.PopGen.Absorption, Programmes.EvoGraph.BirthDeath, Autoresearch.KeldyshCM, Programmes.PopGen.Price.
- **Memory-note sweep.** I grepped the LaTeX comments for kebab-case `.md` names. The only hits are dated repository files (`manuscript_audit_2026-10-11.md`, `AUDIT_2026-09-2x.md`), not memory notes.

## Remaining notes

- `AUDIT.md`, which sits in this directory, quotes the Lean file's directory name (item 17). If `AUDIT.md` is shipped with the package, redact that path first. I did not edit `AUDIT.md`, because it is the auditor's record.
- `figures/c11_courbures.pdf` was already modified before this revision. I did not touch it.

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
- `pdftotext`: `Famille` occurs 0 times in either PDF.

**Fidelity check** (`code/fidelity_check.py`, rerun):
- c05 and c16: all ok.
- c03, c07 and c20: `numbers`, `niveau`, `refs` and `figures` ok.
- The remaining `number_words` hits are the known pattern: FR « les deux » → EN "both", and « deux fois » → "twice". c20's `doi_macro` difference is the old, presentation-only one.
