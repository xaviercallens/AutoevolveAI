# REVISION - answers to AUDIT.md (ACCEPT_WITH_CORRECTIONS), 2026-10-26

Nothing committed or pushed. Files touched: main.tex, preface.tex, ch1..ch5 .tex, refs_ch1..5.tex (references.tex unchanged),
plus TIER_STATUS.md and this file. Rebuild: pdflatex x3, 111 pages (was 110), 0 errors, 0 undefined references or citations,
0 Overfull hbox in main.log (audit: 15).

## Blocking
- B1 DONE (partial replay, per module). Replay record read: 30 rows, all rc 0. Kept A where replayed (dipolar, Yukawa, Keldysh,
  CM library, Triangular, PopGen/EvoGraph) and rewrote ch2 remark rem:skip with the audit's wording scoped to those modules.
  Not (yet) replayed: Sandier-Serfaty (ch2 s2.5), ZeroPoint/ZeroPointCert/FeynmanBijl (ch3), ch5 U3/U4 external stacks. New label
  `\tierAs` ("Niveau A sans rejeu", defined in main.tex, explained in preface, ch1 list and ch1 gate paragraph). ch3 warnbox rewritten.
  Applied on ch3 lines 168,187,328,339,421,466,474,519,520,523,647,687,702,716,754,755,758,791,794,798; ch2 935,961,977,1010;
  ch5 363,459; ch1 flow table rows 3,5,6. See TIER_STATUS.md.
- B2 DONE. g_inplane: DipolarExcitonStep1 is rc 0 in replay.jsonl, so A kept and the text says so. ch2 table L1 row: As for
  init_constants and bcons/eps, C for calcLam and calcK.
- B3 DONE. ch1 warnbox: the forged-declaration observation is Tier X (A2 paper).
- B4 DONE. Montgomery and Bernstein-Widder: "cité de seconde main" in the ch1 theorem statements and recap; refs_ch1 notes added.
- B5 DONE. `\chaptermark{Fondations}` in ch1; ch4 s4.2 uses `\section[short]{long}` (sectionmark dropped); long \lean path at ch1:596 split.
- B6 DONE. A2 doi:10.5281/zenodo.23661381 in ch1 table row 7 and refs_ch1; unused \StatusNS and the status.tex hook removed from main.tex.

## Non-blocking
- N1 DONE (preface conditional wording). Not added: the Comparator remark in ch1 s1.3.
- N2 DONE: ch1 tier list and gate sentence ("quatre contrôles : compilation + trois vérifications de la préface").
- N3 DONE: ch1 Bernstein definition is h: ]0,inf[ -> [0,inf[ (IsBernsteinOn); the composition theorem requires h>0; example a,b>=0;
  ch2 says "positive au sens large". The h==0 remark is now consistent.
- N4 DONE. N5 DONE (ch3 proposition rewritten as audited). N6 DONE. N7 DONE: revérifié, "noyau :", ch4 "vérifiés par le noyau",
  ch4 "satisfont", ch5 "de l'auteur", fail-closed glosses (ch4 numbox body, ch5). Accent-less comment lines in ch5 left as is.
- N8 DONE: duplicates merged to one key per work; v1 title corrected; ch2mn title added; label added to ch5:sigma3; ch1 entries got
  provenance notes (Montgomery, Bernstein, Widder second-hand; others "lecture non consignée", because the ch1 writer's reading is
  not recorded: residual). REMOVED KEYS (appendix writers must not use them): ch2oai ch2ckmrv ch2txt ch3-txtv1 ch3-montgomery
  ch2widder ch2elenchus ch2cm ch5:dipolar ch5:yukawa ch5:donnelly ch5:godfrin ch5:bsk ch5:p6 ch5:p7 ch5:n4 (use oai ckmrv v1 montgomery
  widder elenchus p3 ch2dip ch2yuk ch3-db ch3-godfrin ch3-bsk ch3-fb ch4:P7 ch4:N4).
- N9 DONE: one-line acronym mentions: ALIX (ch1 s1.3), ALEXIS (ch2 after laplace_admissible), KAL, ILENE, AURELIA (ch4 clauses). ch5 no longer
  prints the "Famille" directory; ch4 no longer names the Genetic-repo kal_/aurelia_ lemmas. Acronymes.md (not mine) still says "Famille".
- N10 not mine (Acronymes.md). N11 DONE: ch2 B3 sentence pinned to Muratov-Novaga Theorem 1, p. 4 (bcc unique minimiser among covolume-one Bravais
  lattices, Born Coulomb energy; ledger claim_mn_thm1 of papers/p2_3d_feasibility), title added; no claim about "open before 2026".
- N12 DONE (trace path cited; the record is still untracked, parent should commit it). N13 DONE. N14 DONE ("sortie reproduite par l'auditeur").
  N15 DONE. N16 no action. N17 NOT done (warning that ch5 scripts write into figures/).
