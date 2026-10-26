# AUDIT: « Le journal des découvertes » (papers/discovery_journal_2026/, 153 pp, FR draft)

Auditor: an independent adversarial AI agent (Claude). It is separate from the producer agents but comes from the same model family. No human has reviewed the book or this audit.
Date: 2026-10-26.
Object audited: the working tree at commit d800bed (`main.pdf` of 14:02, `build_report.json`: 3 pdflatex passes rc 0, 153 pages).
Scratch work: `/tmp/jaudit/` (`recompute.py`, `dois.py`, `prep_figs.py`, regenerated figures in `out/`, page renders).
No file other than this one was written in the repository, and no git command was run.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The book is honest on the points that matter most:

- Sandier–Serfaty is not claimed as proved, in c13, c14 and the frame.
- No Clay problem is claimed as solved. c15 explicitly gives credit for the Navier–Stokes corpus to its authors.
- Every chapter built on openai/math says it is conditional on an AI-generated theorem that is not peer reviewed.
- « Aucun mathématicien humain ne les a relus » appears in the credits, the prologue, the frame and every chapter.
- Retractions are told faithfully, with correct DOIs.

Every checked number matches its source. The 7 regenerated figures are bit-identical to the printed ones. All 20 DOIs resolve, and their titles and dates match. The selection follows `TOP20_final.json`.

**7 blocking items** must be fixed before Zenodo or GitHub publication:

- a clipped table;
- wrong hard-coded cross-references;
- AI reasoning described as « humain »;
- one stale badge;
- three overclaims in the frame;
- one wrong date;
- an invented family reference.

All of them are text or layout fixes. None changes a result.

---

## BLOCKING

### B1. The 20-row table is clipped on the verso page. The DOIs of picks 1–10 cannot be read.
- **Where.** `cadre/fabrication.tex:68-72` (`\begin{pleinelargeur}\input{gen/table20.tex}\end{pleinelargeur}`). It renders on book p. 130, which is PDF page 142, a verso.
- **What I saw.**
  - On the render (`pdftoppm -r 110`, crop of the right edge), the last column is cut at the paper edge: « DOI ou dép… », « doi 10.528… ».
  - `pdftotext -layout` gives the same truncation, « 3/3 doi 10.528 », for rows 1–10.
  - The recto page (p. 131, PDF 143) is correct.
- **Cause.** `adjustwidth*` decides odd or even where the environment opens. That happens at the bottom of p. 129 (recto), so it widens to the right. The unbreakable tabular then floats to p. 130 (verso), where the right side is the paper edge.
- **Fix (either one).**
  - (a) In `fabrication.tex`, insert `\clearpage` immediately before `\begin{pleinelargeur}`. Give each of the two tabulars in `gen/table20.tex` its own `pleinelargeur` (edit `code/make_backmatter.py`).
  - (b) Simpler: drop the 5th column. Put the DOI under the title in the 2nd cell, `\newline{\footnotesize\doi{…}}` (in `make_backmatter.py`), and set the table at `\linewidth`, with no `pleinelargeur`.
- Re-render PDF pages 142–143 and check them.

### B2. Seven hard-coded cross-references point to the wrong chapter
The parts reorder the contributions, but these lines were written for the old rank order. The real numbers, from `main.toc`, are: Elenchus = 1, c17 = 2, c19 = 3, c18 = 4, c20 = 5, c16 = 6, c03 = 7, c08 = 8, c09 = 9, c04 = 10, c10 = 11, c05 = 12, c12 = 13, c11 = 14, c13 = 15, c14 = 16, c15 = 17, c01 = 18, c02 = 19, c06 = 20, c07 = 21.

| file:line | text now | the reader lands on | exact replacement |
|---|---|---|---|
| `chapters/c03.tex:49` | « (il le sera au chapitre suivant) » | ch. 8, the textbook | « (il le sera au chapitre~\ref{ch:c04}) » |
| `chapters/c03.tex:59` (caption) | « les valeurs exactes du chapitre suivant » | ch. 8 | « les valeurs exactes du chapitre~\ref{ch:c04} » |
| `chapters/c03.tex:87` | « un erratum, corrigé au chapitre suivant. » | ch. 8 | « un erratum, corrigé au chapitre~\ref{ch:c04}. » |
| `chapters/c04.tex:23` | « Le théorème amont (chapitre précédent) » | ch. 9, excitons | « Le théorème amont (chapitre~\ref{ch:c03}) » |
| `chapters/c04.tex:45` | « répare l'erratum du chapitre précédent. » | ch. 9 | « répare l'erratum du chapitre~\ref{ch:c03}. » |
| `chapters/c17.tex:31-32` | « les distances cosmologiques du chapitre~1, les probabilités de fixation du chapitre~7 » | ch. 1 = Elenchus, ch. 7 = c03 | « les distances cosmologiques du chapitre~\ref{ch:c01}, les probabilités de fixation du chapitre~\ref{ch:c06} » |
| `chapters/c17.tex:91` | « Le chapitre~20 raconte » | ch. 20 = fixation | « Le chapitre~\ref{ch:c20} raconte » |
| `chapters/c18.tex:85` | « Le chapitre suivant montre la même leçon appliquée au banc d'essai du projet lui-même. » | ch. 5, the thermostat; the test bench is ch. 3 | « Le chapitre~\ref{ch:c19} montre la même leçon appliquée au banc d'essai du projet lui-même. » |

These references are correct: c01→c02 « chapitre suivant », c02 « chapitre précédent », c12→c11 « chapitre suivant », and the prologue's « chapitre~1 » and « chapitre suivant ».

### B3. AI reasoning is called « humain ». This contradicts the book's level C and « aucun humain n'a relu »
The level C defined in the book (Elenchus fig. 1, dictionary) is « un raisonnement, mené ici par des agents d'IA, que personne n'a vérifié à la machine ». The ED-20 paper (`papers/p2_certified_zero_point/main.tex:212`) says the glue steps are « written arguments checked by no machine and no human referee ». A lay reader will take « humain » to mean a person did or checked the reasoning.

- `cadre/elenchus.tex:329-330`: « certaines étapes qui relient les morceaux sont des raisonnements humains. » → « certaines étapes qui relient les morceaux sont des raisonnements écrits par des agents d'IA, que ni une machine ni un humain n'a vérifiés. »
- `chapters/c03.tex:48`: « est ici un raisonnement humain, non vérifié par la machine » → « est ici un raisonnement écrit par des agents d'IA, non vérifié par la machine »
- `chapters/c10.tex:17`: « n'a été démontrée qu'à la main » → « n'a été démontrée que sur le papier, par des agents d'IA »
- `chapters/c10.tex:27`: « L'article donne une preuve humaine, pas à pas » → « L'article donne une preuve écrite, pas à pas (rédigée par des agents d'IA) »
- `chapters/c10.tex:60`: « (preuve humaine) » → « (preuve écrite, non vérifiée par la machine) »
- `chapters/c10.tex:71-72`: « l'auditeur a proposé une preuve humaine plus simple […] et reste au niveau \og un humain a raisonné\fg » → « l'auditeur a proposé une preuve écrite plus simple […] et reste au niveau~C, un raisonnement mené par des agents d'IA »
- `chapters/c10.tex:79`: « est une preuve à la main (\niveau{C}) » → « est une preuve écrite sur le papier (\niveau{C}) »
- `chapters/c18.tex:9`: « c'est un raisonnement de l'auteur, mesuré seulement sur un petit corpus qu'il a écrit lui-même » → « c'est un raisonnement, mené par des agents d'IA sous la direction de l'auteur, et mesuré seulement sur un petit corpus écrit par le projet lui-même »

### B4. c13 has a stale badge that contradicts the replay record, the table and the selection
- **Where.** `chapters/c13.tex:69-72` gives the ten Lean lemmas \niveau{As} and says « aucun rejeu n'est enregistré dans le papier ».
- **The record says otherwise.**
  - `results/kernel_replay_2026-10-26/replay.jsonl` row 86 is `Programmes.SandierSerfatyStatement`, rc 0.
  - `RESCORE.md` says the source sha256 35add509 equals the published file.
  - ED-14 owes its C1 = 3, its 3/3 in the book's table and its rank 5 entirely to this row.
- **Why it matters.** The book defines As as « quand le rejeu manque », so the badge is wrong under the book's own rule. A reader sees « 3/3 » in the table and « sans rejeu » in the chapter.
- **Fix.** Replace lines 69-72 with:
  « Les dix lemmes sont \niveau{A} \emph{le juge a regardé} : le noyau de Lean les a vérifiés, axiomes dans la liste courte, fausses preuves plantées démasquées, et le module a été rejoué sans erreur le 26 octobre 2026, après la publication du papier. Ces lemmes disent seulement que l'énoncé n'est pas vide de sens ; ils ne prouvent rien sur la conjecture. »

### B5. Three overclaims in the frame
1. **`main.tex:251-254`, the Part III opener.** It says « le réseau triangulaire n'est plus le meilleur dès qu'on tient compte de l'agitation quantique ». This is unconditional. The evidence is X for 8 of 12 potentials (ED-15) and an overall C certificate for one Gaussian along one shear (ED-20). Fix:
   « … réfutée d'abord par le calcul, ensuite, sur un cas précis, par un certificat : pour plusieurs forces, le réseau triangulaire n'est plus le meilleur quand on tient compte de l'agitation quantique, dans un modèle simplifié. »
2. **`cadre/neurosymbolique.tex:115`.** It says « le certificat de Sandier--Serfaty n'est entré qu'au tiers dans le noyau ». c14 says 4 stages of 12, which is 1 685 129 of 1 238 829 689 operations. I recomputed that as 0.136 %. Fix:
   « et du certificat de Sandier--Serfaty, seules quatre étapes sur douze, soit 0,136 % des opérations, sont entrées dans le noyau. »
3. **`cadre/elenchus.tex:121` and `:149`.**
   - Line 121 says « Dans ce projet, aucune mesure n'est rapportée sans ses deux contrôles ».
   - Line 149 says « l'agent d'IA qui produit un résultat n'est jamais celui qui le vérifie ».
   - Both are absolute, and the book contradicts them itself. c10:66 says « Au stade de l'article, producteur et vérificateur n'étaient pas séparés ». c18:71 says « Les audits des chiffres du dépôt sont ceux de l'auteur ». c20:78 says nobody other than the author reviewed it. The spring work had no controls (prologue, c17).
   - Fixes:
     - line 121: « Dans les travaux de l'automne, aucune mesure n'est rapportée sans ses deux contrôles. »
     - line 149: « Dans les travaux de la fin de l'année, l'agent d'IA qui produit un résultat n'est pas celui qui le vérifie. »

### B6. Wrong date for the upstream theorem
- `chapters/c16.tex:27` says « Début octobre, le dépôt public openai/math a livré une démonstration ».
- The sources date the manuscript 2026-09-23: `papers/triangular_riesz/triangular_riesz.tex` (« On 2026-09-23 the openai/math release posted a manuscript », bibitem « September 23, 2026 »), `papers/textbook_universal_optimality/FACTS.md`, and `papers/universal_optimality_tiered/…tex` bibitem.
- c03:215 and c13 say « En septembre 2026 ».
- Fix: « Le 23 septembre 2026, le dépôt public openai/math a livré une démonstration ».

### B7. A family member is invented (rule 6)
- **Where.** `cadre/elenchus.tex:3` (the chapter title, printed in the TOC and the running heads), `:1` (comment), `:5-6`: « La méthode Elenchus, expliquée à ma grand-mère » and « Si je devais expliquer à ma grand-mère […] une question qu'elle se pose sûrement ».
- **Why it is blocking.** This introduces a real family member of the author that the author did not supply, and attributes a thought to her. The rule is that no facts about any family member are invented. The idiom « recette de grand-mère » at :108 is generic and may stay.
- **Fix** (unless the author explicitly confirms the wording):
  - title: `\chapter{La méthode Elenchus, expliquée simplement}`
  - lines 5-6: « Si je devais expliquer à quelqu'un qui n'est pas scientifique ce que j'ai fait cette année, je ne commencerais pas par les théorèmes. Je commencerais par une question que chacun peut se poser : \emph{comment savoir si une machine dit vrai ?} »
  - update the comment on line 1 to match.

---

## NONBLOCKING

1. **The rigour column for c20 reads 1/3, but the chapter shows As.**
   - The scorer kept 1 because the inventory text omits the axiom footprint.
   - The Zenodo file `paper_a_v2_lean_gate.json` (fetched by me) lists the axioms for all 18 theorems of `PaperA_RK4EnergySign.lean`: only propext, Classical.choice and Quot.sound, and no sorry. The chapter is right.
   - Add to `fabrication.tex:66`: « (La note de la contribution n°\,20 suit l'inventaire, qui ne cite pas la liste des axiomes ; le fichier de contrôle du dépôt la donne, d'où la pastille As du chapitre.) »
2. **Domain labelling should be disclosed.**
   - Cosmology (2 picks) and education (1) are inventory domains separate from physics, so physics + cosmology = 9 chapters under a cap of 7 per domain.
   - This follows `SELECTION_final.md` §2 ("domains as found"), but a reader of `fabrication.tex:34-38` will not know it.
   - Add: « Les domaines sont ceux de l'inventaire : la cosmologie et l'enseignement y sont comptés à part de la physique, ce qui explique neuf chapitres de physique au sens large. »
3. **`cadre/elenchus.tex:314-315`** says « Quatre programmes indépendants ». ED-15 has two formulas implemented four ways, plus a fifth code written by the auditor (`prog_zero_point_optimality/AUDIT.md:22`). Use: « Deux formules, programmées de quatre façons, puis une cinquième fois par l'auditeur, calculent… »
4. **`cadre/elenchus.tex:110`** says « un théorème de niveau A est exactement aussi vrai que l'énoncé qu'il démontre ». This overstates the kernel (line 196 says « rarement ne veut pas dire jamais »). Use: « un théorème de niveau A ne vaut que ce que vaut son énoncé, et le juge lui-même peut, très rarement, se tromper ».
5. **`cadre/elenchus.tex:154`** says « celui du dernier article de l'année ». The N1 paper (doi 10.5281/zenodo.23667863, commit 9b2f2b6) came out later. Use « celui d'un des derniers articles de l'année ».
6. **`cadre/elenchus.tex:353`** says « En septembre 2026, OpenAI a publié des démonstrations ». The Navier–Stokes corpus was already being analysed on 12 September (22723078, `ARC.md:39`), so its release date is not established as September. Use « En 2026, OpenAI a publié… ».
7. **`cadre/neurosymbolique.tex:102`** labels the integer-certificate method \niveau{A}. Its two examples (c01, c02) are As. Use `\niveau{As}`, or add « (niveau A une fois rejoué) ».
8. **`cadre/neurosymbolique.tex:257`.** The list of chapters that depend on openai/math omits `\ref{ch:c08}`, the textbook, which « tout le livre en dépend ». Add it.
9. **`cadre/couverture.tex:63` and `cadre/dictionnaire.tex:44`** list « A, L, C ou X ». Add As: « (A, As, L, C ou X) », and in the dictionary « As, « le juge a regardé, sans rejeu » ».
10. **`cadre/couverture.tex:64-65`** says « Les faits et les nombres viennent des dossiers publics… ». A few facts come from the selection dossier's memory notes (for example the 13 defects of c01, `TOP20_final.json` c2). Use: « des dossiers des travaux eux-mêmes (Zenodo, GitHub) et du dossier de sélection ».
11. **`cadre/retraits.tex:69-70`** has a double parenthesis: « (23653833, (chapitre~\ref{ch:c12}), » → « (23653833, chapitre~\ref{ch:c12}), ».
12. **`cadre/retraits.tex:36`** says « 141 modules sur 316 ». The inventory says crates. Use « 141 paquets de code (crates) sur 316 ».
13. **`gen/dois.tex:9`** prints « population~?. » (double punctuation). In `code/make_backmatter.py`, skip the final period when the title ends in « ? ».
14. **`chapters/c02.tex:48` vs `:69`.** The text gives « vaut environ 54,6 à H0 = 73 », which is Δχ², and then « le score vaut 64,91 », which is χ². Both are called « score ». Use « l'écart au meilleur point vaut environ 54,6 » at line 48.
15. **`chapters/c12.tex:129`, figure caption.** The scan also gives c < 0 at a = 0.1 (−0.0062, `fig12.py` output; root 0.12269). Add « (sous a ≈ 0,12 la courbure est minuscule et n'est pas exploitée) ».
16. **`chapters/c07.tex:59`, caption.** The green bar (« étoile pondérée », 4/7) is not explained. Add « en vert, l'étoile avec des poids à l'équilibre, qui retrouve 4/7 ».
17. **`cadre/images_cachees.tex:25`** says « Les énoncés sont de niveau~A ». `Acronymes.lean` is not in `replay.jsonl`. Each alias is `rfl`-equal to a replayed theorem. Use: « Les théorèmes d'origine sont de niveau~A (pour ALIX, sous réserve…) ; les cinq noms courts en sont de simples alias, non rejoués eux-mêmes ». Also, the file sits in `formal_cert/Programmes/[nom du répertoire retiré]/`. Never link or print that path in the book or the GitHub README.
18. **Shape.**
    - c12 has 1224 words, above the ±20 % band (about 760–1140 around the mean of 953). Trim it.
    - Figure placement differs: inside the text for c01–c10, after « Pour aller plus loin » for c11–c20.
    - In c11–c16, prose precedes the analogy box, or the badge precedes the first section.
    - The `limite` box repeats its section heading (« Ce que ça ne dit pas » twice).
    - Harmonise these if time allows.
19. **`chapters/c20.tex:43`** says « un pas de calcul $y=1$ ». y is the product of frequency and step. Use « un pas de calcul tel que $y=\omega h=1$ ».
20. **`cadre/elenchus.tex:245`** (pont) says « sauf si l'on change les fichiers ». Add « ou les outils ».
21. **Clean the bundle before GitHub.**
    - LaTeX comments cite internal memory notes (`chapters/c08.tex:3`, `c17.tex:5`, `c18.tex:4`, `c19.tex:5`).
    - `chapters/spare_N2.tex`, `code/spare_fig12.py` and `figures/spare_c12_majorantes.*` are unused; ORDER.json says so. Remove them or move them to `unused/`.
    - `data/zenodo23119953_gwaya_v3_oracle_eval.json` contains a temp path `/mnt/data/xdev-cache/tmp/…`. It is copied from the public Zenodo record, so it is harmless but can be left as is.
22. **Dictionary.**
    - « Lean accepte trois règles de base » → « Le projet n'admet que trois axiomes standard de Lean ».
    - « Superfluide … sans aucune friction » → « presque sans frottement ».
23. **Author's own voice.**
    - The letter (`cadre/lettre.tex`) and the prologue opening were drafted by agents in the author's voice. They contain no invented fact about anyone. Line 103's « écrit en pensant à vous » is a sentiment.
    - The author should read and sign off on both before publication. The source already says « À PERSONNALISER ».
24. **The c20 analogy** (the windows) is hard to follow. Optional: drop the second sentence about the windows and keep « il garde la maison un peu trop froide ; aux grands pas, il se met vraiment à chauffer ».

---

## What was checked (actual outputs)

### (1) Honesty, line by line
- **Overclaim words.** I grepped the PDF text and the sources for « percée », « révolution », « résolu », « prouvé », « démontré » and « breakthrough ».
  - Every « résolu » is negated: prologue « ni de grand problème résolu », c15 « Ce n'est pas l'annonce qu'un problème du Clay est résolu ».
  - Every « prouvé » or « démontré » is attached to an A-level Lean statement or is negated.
  - The remaining overclaims are B5.
- **Sandier–Serfaty.** It is not claimed as proved in: prologue:83-84, elenchus:357-364, c13:20-22 and :87, c14:119-120 and :187, neurosymbolique:183-186.
- **Navier–Stokes.** It is not presented as a Clay solution, and credit goes to the corpus authors: prologue:84-85, elenchus:369-371, c15:228-231 and :293-295.
- **openai/math is flagged as conditional** in: credits, prologue:87-89, the Part II opener, c03, c04, c08, c09, c10, c16, the ALIX caption, and neurosymbolique:255-258.
- **« Aucun mathématicien humain n'a relu »** appears in the credits (couverture:60), prologue:85-86, fabrication:15-16, neurosymbolique:251, and once in each chapter.
- **Badges against the replay record.** The record is 93 rows, all rc 0. `result.json` gives OK 93 and SKIPPED 778, over 871 files with 0 escape-pattern hits.

| ch. | badge(s) | replay evidence | verdict |
|---|---|---|---|
| c01, c02 | As | BAO cert not in replay (`SELECTION_final.md` §2 "Not replayed: BAOCert") | correct |
| c03 | A | row 5 Triangular.UniversalOptimality | correct |
| c04 | A | rows 16-17 Yukawa, YukawaMix; `ar_yukawa_crystal/AUDIT.md:7` ACCEPT_WITH_CORRECTIONS, 5 corrections, 11 flags (:138) | correct |
| c05 | A (math), L (data), X (verdicts) | row 31 FeynmanBijl.Basic; `prog_superfluid_structure_factor/AUDIT.md:8`, 29/7/63, Δ_ds = 0.082 post hoc (:79, :136) | correct |
| c06 | A / C / X | rows 32-39 PopGen.* | correct |
| c07 | A / C / X | rows 26-30 EvoGraph.*; `p3_isothermal_theorem/AUDIT.md` verdict, forged skipKernelTC control (:38), star 5/12-2/3-7/12 and cycle 8/15 (:60-62) | correct |
| c08 | A (open/closed disk) | rows 1, 3 OpenDisk, OpenDiskAny | correct |
| c09 | A / C / X | rows 7-9 DipolarExciton* | correct |
| c10 | C / A / X | row 11 KeldyshCM | badges correct; wording B3 |
| c11 | A (logic), C (overall) | row 89 ZeroPointCert.Basic; `p2_certified_zero_point/AUDIT.md:9`, 206,468 cells, B = −1.84156 (:153, :221), Tier C overall (:207) | correct; wording B3 in elenchus |
| c12 | X headline, A for 19 lemmas | row 88 ZeroPoint.Basic; `prog_zero_point_optimality/AUDIT.md:19`, 19/19 declarations whitelisted (:71), five corrections C1–C5 (:229-270) | correct |
| c13 | As (ten lemmas) | **row 86 SandierSerfatyStatement rc 0** | **wrong, B4** |
| c14 | A | rows 40-87, 90 SandierSerfaty.* | correct |
| c15 | A (the four theorems) | not in `replay.jsonl` (the openai corpus); rests on the paper's own leanchecker runs, `p2_navier_stokes_audit/AUDIT.md:215` "AUDITREPLAY RESULT OK", verdict :3 | acceptable; c15 says it was redone in that study |
| c16 | A | rows 2, 4, 6 AnyDensity, Riesz, RieszFinite | correct |
| c17 | X | n/a | correct |
| c18, c19 | C | n/a | correct (wording B3 for c18) |
| c20 | As / X | not in replay; gate JSON on Zenodo lists the axioms for 18/18 | correct |

- **Retractions** (`cadre/retraits.tex`) were compared with `zenodo_inventory.json` `self_reported_caveats`: 22682139, 22853896, 22872083, 22985926, 23262132, 23468458, 23525655, 23526783, 23532595, 23532601, 20380024 and others.
  - Every claim and date matches: the « first formalisation » withdrawal; two QuantumFluids "findings" withdrawn after a literature check; the scripted review with invented referees (v2.1, 2026-10-19); « peer reviewed » withdrawn (23525655); POLE P286R refuted; Theorem 2.5 and the blow-up refuted; SQIsign accepts 256.
  - Every DOI cited anywhere in the book is in the inventory, except 23663551. I resolved it on the Zenodo API: the N2 Yukawa paper, 2026-10-26.
  - The only defects are B5-free typos: nonblocking items 11 and 12.

### (2) Facts: spot checks (more than 25) and recomputations
Recomputed independently (`/tmp/jaudit/recompute.py`, exact fractions or own code):

- **4-cycle**, 1 mutant, r = 2: **8/15** (exact birth-death solve).
- **3-star**: centre **5/12**, leaf **2/3**, uniform start **7/12**; Moran N = 3: **4/7**. The book matches (c07:52-53, figure).
- Moran N = 2, r = 2: 2/3 (c06).
- **Lattice energy** s = 4, density 1: triangular **5.7833**, square **6.0268**, a = 1.0746 (c16: 5.783 / 6.027); dilated ×2: 0.3615 (c16: 0.361).
- **Stiff equation** y′ = −50y: Euler factor −1.5 at h = 0.05, threshold **h = 0.04 = 2/50**, implicit 1/3.5 = 0.2857, e^{−2.5} = 0.0821 (c17).
- **RK4** |R(i)|² = 569/576 = 0.98785, also by direct evaluation (c20).
- Δχ² = 25 with 3 dof: p = 1.54e-5, **4.32 σ** (c02 « environ 4,3 sigmas »).
- **c01**: χ(0.295) at Ω_m = 0.29743 is 0.274742, inside [0.2747074, 0.2747769]; 1/E(0.295) = 0.86114.
- **c05**: k* = 3.0038 Å⁻¹, B(2.058) = 0.5853, ratio 2.49, excess 0.873.
- **c14**: 1 685 129 / 1 238 829 689 = 0.00136; Machin 3.140597 → 3.141621.
- **c13**: 6K + λ + 2πμ = −4.150416.
- **c11**: −1.900167 + 1.833534 × 0.031965 = −1.841558.
- **c12**: −0.0799 × 0.02² / 0.75 = −4.26e-5; direct −4.28e-5.
- **c04**: g(1), g(4), g(9) = 0.368, 0.068, 0.017; mixture at 1/4 = −0.258.
- **c09**: V(10) = 0.000993; orders of magnitude 1.66–4.85.
- **c10**: −2/9.
- **c08**: πa² = 3.628, 7/3.63 = 1.93, 1/3.63 = 0.28.

Checked against sources:

- ED-15: 1.4903 vs 1.5034 (`gen_numbers.tex:27-28`); roots 0.37668, 1.58148; 19 lemmas; five corrections.
- ED-14: 478 s (`\SSAPosChild` 478.001), 22 pairs, factor ≈ 22.56 and break-even 1.858, residual 1.008e-53, three loosenings with two rejected.
- ED-24: 2 440 modules; 53 752 + 34 648 = 88 400; 12 + 39 = 51; regex bug fixed (`main.tex:199-200`).
- ED-20: 206 468 cells.
- N2: twelve revisions (REVISION.md rows 1–12).
- c20: H* = 29/40 and 2 000 orbits (`data/…paper_a_v2_results.json`); 61.8 / 46.4 / 9.05 / 68.75 % (fig20 output); 18 Lean theorems with whitelist axioms (Zenodo gate JSON).
- c01: 13 defects (memory `certified-numerics-p1.md:16`).
- Replay: 93 modules, 871 files, KRForged rc 1 (`REPLAY.md:5-13`); the longest module took 914.9 s, which matches neurosymbolique's « jusqu'à un quart d'heure ».
- Book-level counts:
  - Zenodo: 144 records, 112 distinct titles (`zenodo_inventory.md` « Distinct titles: 112 »).
  - GitHub: 420 repositories, 317 forks, 82 kept, 57 science-relevant (`github_inventory.json` counts).
  - Selection: 113 candidates (`SELECTION_final.md` §1); 17 of 20 dated 8–26 Oct; 16 × 3, 1 × 2, 2 × 1, 1 × 0 (table); 3 lessons.
- **Upstream date**: 2026-09-23. This is wrong in c16 (B6).

**DOIs.** All 20 primary DOIs (plus 23120120 and the seven v1 stellarator copies) return HTTP 200 on `https://zenodo.org/api/records/<id>`. Titles match the table, and the publication dates match the dates printed in the table: 10-08, 10-10, 10-11, 10-25, 10-26, 10-03, 10-21, 10-19.

### (3) Selection
- The table (`gen/table20.tex`), the ranks in the chapter openers (`gen/titres.tex`) and `chapters/ORDER.json` follow `TOP20_final.json` picks 1–20 exactly, including ED-14 at 5 and ED-15 at 12.
- Each of the 20 appears in exactly one part. Parts I and V are in date order.
- **The swap.** `fabrication.tex:50-56` tells the N2 → ED-15 swap honestly: same grid; the 71 → 93 replay rows; « sorti, à égalité de note, départagé par la date puis écarté par le plafond de sept en physique ». This matches RESCORE.md.
- **Hard rules.**
  - At least 2 picks for each of the five domains: math 4, physics 7, genetics/biology 2, numerics 2, AI methodology 2.
  - Physics is at the cap of 7.
  - There are 3 lessons (ED-15, ED-20, L-STELLARATOR).
  - The exclusion rule was applied (the stellarator is scored on its edition 2).
  - The disclosure of the domain labels is nonblocking item 2.

### (4) Analogies
- All 20 chapter analogies, plus 9 in the frame, carry a stated limit (« Où l'image s'arrête »).
- None misleads about the mathematics. The best ones:
  - c11 says explicitly that one cannot tell a saddle from a summit.
  - c13 and c14 say that re-running the same code is not independent.
  - c14 gives 0.136 %.
- Two frame analogies overreach slightly: nonblocking items 4 and 20.
- c20 is confusing: nonblocking item 24.

### (5) Privacy
I scanned the book source, `code/`, `data/`, `gen/` and `figures/*.json` for:

- `/home/`, `/mnt/`, gmail or email patterns;
- `ghp_`, `github_pat_`, `hf_`, `sk-`;
- ZENODO_TOKEN, HUGGINGFACE_TOKEN, "Bearer", password, secret.

The results:

- No tokens or emails.
- One harmless temp path, `/mnt/data/xdev-cache/tmp/…`, inside a JSON copied from the public Zenodo record 23119953.
- None of the 19 private repository names (from `github_inventory.json`) appears in the source or the PDF.
- The repositories that are named (AutoevolveAI, rusty-SUNDIALS, triangular-universal-optimality-lean, GWAYA-GwenLayaOpenModel, Agora-K3-DarkMatter, the LeanProposal repository) are all PUBLIC.
- Internal memory-note references appear only in LaTeX comments (nonblocking item 21).

### (6) Family
- **Dedication** (`cadre/dedicace.tex:9`, `:14`; PDF p. 5, rendered):
  - « À mon père, un grand ingénieur. »
  - « À ma femme et à nos enfants, Ilene, Alexis et Aurelia. »
  - Both are exact.
- `pdftotext` on the PDF: **« [retiré] » (capitalised) does not occur.** The 30 lowercase hits are « famille de forces » and the like.
- **The father** is mentioned only in the dedication and in prologue:8, « le fils d'un grand ingénieur ». Nothing else is said about him.
- **The hidden-image spread** (PDF pp. 152-153, rendered) gives:
  - the five names;
  - their mathematical expansions (A Lattice Is eXtremal, …);
  - plain-math sentences.
  - It does not give any family meaning. The letter says « Je ne vous dirai pas ce qu'elles cachent ».
- **The one invented family element** is the grandmother (B7).

### (7) Figures
- I copied seven scripts (fig05, 07, 11, 12, 16, 17 and 20) so that they read the real data and write to `/tmp/jaudit/out`, then ran them. They print:
  - fig05: 29/7/63; 21 roton points; 0.328.
  - fig07: 8/15, 5/12, 2/3, 7/12, 4/7.
  - fig11: B = −1.84156, control +12.84.
  - fig12: roots 0.37668 and 1.58148.
  - fig16: 5.78336 / 6.02681; 2π slope at s = 2.
  - fig17: the explicit-step blow-up at h ≥ 0.0429.
  - fig20: 569/576; DOP853 0.618; RK4 0.464 / 0.0905.
- **All seven PNGs are pixel-identical** to `figures/` (numpy array equality).
- Each script reads the paper data files or computes from formulas, so the figures are generated from real numbers.

### (8) French, readability, shape, layout
- **Shape.** All 20 chapters have the five `\section*` headings in the same order, exactly one `analogie`, one `limite`, one figure and a margin reference. Length is 793–1224 words; c12 is over the band.
- **French.** The French is clear and warm. Every pencil-and-paper box is reproducible by a teenager. c11's « moyenne de racines carrées de matrices » is the hardest passage, but it is explained.
- **Typography.** The two typos are nonblocking items 11 and 13.
- **Pages rendered and read:**
  - PDF 1 (cover): fine.
  - 5 (dedication): fine.
  - 116-117 (c07 box and figure): fine, except the green-bar caption.
  - 142-143 (table): **clipped on 142, B1**.
  - 152-153 (hidden images): fine.

## What this audit did not do
- I did not re-run Lean or the kernel replay myself. I relied on `replay.jsonl` and `result.json`.
- I did not read every source AUDIT.md in full. I read targeted sections of six: c04, c05, c07, c11, c12 and c13, plus c15's.
- I did not verify the rusty-SUNDIALS audit numbers in c17 (47×, ratio 1.00), because they live in the GitHub repository, not on disk.
- I did not run fig18 or fig19, which need a local `lean`.
- This audit is by an AI agent. It is not peer review.


> Note de publication : le nom du répertoire du fichier Lean des cinq théorèmes cachés a été retiré de ce document (« 2 occurrence(s) ») pour ne pas révéler le sens des acronymes ; aucun autre passage de l'audit n'a été modifié.
