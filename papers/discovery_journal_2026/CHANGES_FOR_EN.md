# Changes to mirror in the English edition (from the FR revision after AUDIT.md)

Paths are relative to `papers/discovery_journal_2026/`. « → » gives the new FR wording, so the English edition can match it. Item tags refer to AUDIT.md (B = blocking, N = nonblocking).

## main.tex
- [B5.1] Part III opener (`\partie{III}`): « réfutée d'abord par le calcul, ensuite par un certificat : le réseau triangulaire n'est plus le meilleur dès qu'on tient compte de l'agitation quantique » → « …ensuite, sur un cas précis, par un certificat : pour plusieurs forces, le réseau triangulaire n'est plus le meilleur quand on tient compte de l'agitation quantique, dans un modèle simplifié. »

- [N18, part] The default title of the `limite` box changed from « Ce que ça ne dit pas » (which repeated the section heading) to « Les limites, point par point ». In EN, change the default title so that it does not repeat the section heading either.

## cadre/elenchus.tex
- [B7] Line 1 comment and `\chapter` title → « La méthode Elenchus, expliquée simplement ».
- [B7] Opening sentence → « Si je devais expliquer à quelqu'un qui n'est pas scientifique ce que j'ai fait cette année, … une question que chacun peut se poser : comment savoir si une machine dit vrai ? ». The grandmother is gone. The jam-label idiom « recette de grand-mère » is kept.
- [N4] Jam analogy, end → « un pot contrôlé peut encore être mauvais, et un théorème de niveau A ne vaut que ce que vaut son énoncé, et le juge lui-même peut, très rarement, se tromper ; c'est la question de l'énoncé… ».
- [B5.3] Rule 3: « Dans ce projet, aucune mesure n'est rapportée… » → « Dans les travaux de l'automne, aucune mesure n'est rapportée sans ses deux contrôles. »
- [B5.3] Rule 4: « Dans ce projet, l'agent d'IA qui produit un résultat n'est jamais celui qui le vérifie. » → « Dans les travaux de la fin de l'année, l'agent d'IA qui produit un résultat n'est pas celui qui le vérifie. »
- [N5] « celui du dernier article de l'année » → « celui d'un des derniers articles de l'année ».
- [N20] Bridge analogy: « sauf si l'on change les fichiers » → « …les fichiers ou les outils ».
- [N3] QU-1 pencil sketch: « Quatre programmes indépendants calculent » → « Deux formules, programmées de quatre façons, puis une cinquième fois par l'auditeur, calculent ».
- [B3] QU-1 certificate: « certaines étapes qui relient les morceaux sont des raisonnements humains » → « …sont des raisonnements écrits par des agents d'IA, que ni une machine ni un humain n'a vérifiés. »
- [N6] « En septembre 2026, OpenAI a publié des démonstrations » → « En 2026, OpenAI a publié… ».

## cadre/neurosymbolique.tex
- [N7] Paragraph « Le certificat contrôlé par le juge »: badge `\niveau{A}` → `\niveau{As}`.
- [B5.2] « le certificat de Sandier--Serfaty n'est entré qu'au tiers dans le noyau » → « et du certificat de Sandier--Serfaty, seules quatre étapes sur douze, soit 0,136 % des opérations, sont entrées dans le noyau ».
- [N8] openai/math dependency list: `\ref{ch:c08}` was added (now c16, c03, c08, c09, c04, c10).

## cadre/couverture.tex
- [N9] AI declaration: « (A, L, C ou X) » → « (A, As, L, C ou X) ».
- [N10] Sources: « des dossiers publics des travaux eux-mêmes » → « des dossiers des travaux eux-mêmes » (the rest is unchanged: « (Zenodo, GitHub) et du dossier de sélection… »).

## cadre/dictionnaire.tex
- [N22] Axiome: « Lean accepte trois règles de base » → « Le projet n'admet que trois axiomes standard de Lean ».
- [N9] Entry « Niveau (A, L, C, X) » → « Niveau (A, As, L, C, X) », with « As, « le juge a regardé, sans rejeu » » inserted after A.
- [N22] Superfluide: « sans aucune friction » → « presque sans frottement ».

## cadre/fabrication.tex
- [N2] After « Aucun domaine ne peut avoir plus de sept places. », added: « Les domaines sont ceux de l'inventaire : la cosmologie et l'enseignement y sont comptés à part de la physique, ce qui explique neuf chapitres de physique au sens large (sept de physique et deux de cosmologie). »
- [N1] At the end of the paragraph before the table, added: « (La note de la contribution n° 20 suit l'inventaire, qui ne cite pas la liste des axiomes ; le fichier de contrôle du dépôt la donne, d'où la pastille As du chapitre.) »
- [B1] The table is no longer wrapped in `pleinelargeur`. It is now `\begingroup\small\renewcommand{\arraystretch}{1.22}\input{gen/table20.tex}\endgroup`.

## cadre/retraits.tex
- [N12] RunuX: « 141 modules sur 316 » → « 141 paquets de code (crates) sur 316 ».
- [N11] QU-1 item: « (23653833, (chapitre~\ref{ch:c12}), » → « (23653833, chapitre~\ref{ch:c12}), ».

## cadre/images_cachees.tex
- [N17 + caller] Intro: « Les énoncés sont de niveau~A (pour ALIX, …) ; les images sont… » → « Les théorèmes d'origine, rejoués le 26 octobre, sont de niveau~A (pour ALIX, sous réserve du théorème amont d'openai/math) ; les cinq noms courts en sont des alias exacts, non rejoués eux-mêmes. Les images sont… ». Never print or link the Lean file's directory. Only the file name `Acronymes.lean` appears.

## chapters/c02.tex
- [N14] « et vaut environ 54,6 à H0=73 » → « et l'écart au meilleur point vaut environ 54,6 à H0=73 ».

## chapters/c03.tex
- [B3] « est ici un raisonnement humain, non vérifié par la machine » → « est ici un raisonnement écrit par des agents d'IA, non vérifié par la machine ».
- [B2] « (il le sera au chapitre suivant) » → « (il le sera au chapitre~\ref{ch:c04}) ».
- [B2] Figure caption: « les valeurs exactes du chapitre suivant » → « …du chapitre~\ref{ch:c04} ».
- [B2] Limits box: « un erratum, corrigé au chapitre suivant » → « …corrigé au chapitre~\ref{ch:c04} ».

## chapters/c04.tex
- [B2] « Le théorème amont (chapitre précédent) » → « (chapitre~\ref{ch:c03}) ».
- [B2] « répare l'erratum du chapitre précédent » → « …du chapitre~\ref{ch:c03} ».

## chapters/c07.tex
- [N16] Figure caption, end: « …étoile en orange » + « ; en vert, l'étoile avec des poids à l'équilibre, qui retrouve 4/7 ».

## chapters/c08.tex
- [N21] Header comment: the memory-note citation was removed (comment only, nothing printed).

## chapters/c10.tex
- [B3] Analogy limit: « n'a été démontrée qu'à la main » → « n'a été démontrée que sur le papier, par des agents d'IA ».
- [B3] « L'article donne une preuve humaine, pas à pas, » → « L'article donne une preuve écrite, pas à pas (rédigée par des agents d'IA), ».
- [B3] Summary: « (preuve humaine) » → « (preuve écrite, non vérifiée par la machine) ».
- [B3] Audit episode: « une preuve humaine plus simple » → « une preuve écrite plus simple ». Also « reste au niveau « un humain a raisonné » » → « reste au niveau~C, un raisonnement mené par des agents d'IA ».
- [B3] Limits: « une preuve à la main (C) » → « une preuve écrite sur le papier (C) ».

## chapters/c12.tex
- [N15] Figure caption: after « pour 0,377<a<1,581 », added « (sous a≈0,12 la courbure est minuscule et n'est pas exploitée) ».

## chapters/c13.tex
- [B4] The ten lemmas: `\niveau{As}` « …mais aucun rejeu n'est enregistré dans le papier » → `\niveau{A}` « le juge a regardé : le noyau de Lean les a vérifiés, axiomes dans la liste courte, fausses preuves plantées démasquées, et le module a été rejoué sans erreur le 26 octobre 2026, après la publication du papier. Ces lemmes disent seulement que l'énoncé n'est pas vide de sens ; ils ne prouvent rien sur la conjecture. »
- [B4] New margin `\reference`: « Rejeu du 26 octobre 2026, results/kernel_replay_2026-10-26/replay.jsonl, ligne 86 : module Programmes.SandierSerfatyStatement, code de sortie 0. » Set both paths with `\nolinkurl` so they break in the margin.

## chapters/c16.tex
- [B6] « Début octobre, le dépôt public openai/math a livré » → « Le 23 septembre 2026, le dépôt public openai/math a livré ».

## chapters/c17.tex
- [N21] Header comment: the memory-note citation was removed.
- [B2] « du chapitre~1 … du chapitre~7 » → « du chapitre~\ref{ch:c01} … du chapitre~\ref{ch:c06} » (cosmological distances; fixation probabilities).
- [B2] « Le chapitre~20 raconte » → « Le chapitre~\ref{ch:c20} raconte ».

## chapters/c18.tex
- [N21] Header comment: the memory-note citation was removed.
- [B3] Opening badge line: « c'est un raisonnement de l'auteur, mesuré seulement sur un petit corpus qu'il a écrit lui-même » → « c'est un raisonnement, mené par des agents d'IA sous la direction de l'auteur, et mesuré seulement sur un petit corpus écrit par le projet lui-même ».
- [B2] « Le chapitre suivant montre la même leçon » → « Le chapitre~\ref{ch:c19} montre la même leçon ».

## chapters/c19.tex
- [N21] Header comment: the memory-note citation was removed.

## chapters/c20.tex
- [N24] Analogy: the window clauses were dropped. It now reads « Une famille accuse le thermostat de faire lentement surchauffer la maison. Quelqu'un pose enfin des thermomètres dans toutes les pièces, pendant des semaines : le thermostat ne surchauffe pas, il garde la maison un peu trop froide ; aux grands pas, il se met vraiment à chauffer. »
- [N19] « un pas de calcul y=1 » → « un pas de calcul tel que y=ωh=1 ».
- The As badge is unchanged (per audit item 1).

## chapters/ORDER.json
- `unused_files` → `[]` (the spare chapter was removed).

## code/make_backmatter.py (shared generator; mirror it in the EN generator)
- [B1] `table20.tex`: 4 columns at `\linewidth` (`@{}r X p{2.3cm} c@{}`). The DOI or repository moves under the title and date in the 2nd cell (`\newline{\footnotesize \doi{…}}`). The 5th column was dropped. The header is now « n° | contribution (titre du chapitre), DOI ou dépôt | domaine | rigueur ». The docstring was updated.
- [N13] `dois.tex`: no final period is added when the title already ends in ?, ! or . .

## gen/ (regenerated by code/build.py, not hand-edited)
- `gen/table20.tex`: the new 4-column layout.
- `gen/dois.tex`: the n° 7 title no longer prints « ?. ».

## Removed files (git rm)
- `chapters/spare_N2.tex`, `code/spare_fig12.py`, `figures/spare_c12_majorantes.pdf`, `figures/spare_c12_majorantes.png`. Remove the EN counterparts too, if any exist.

## Not changed (and why)
- N18, the rest (c12 length, figure placement, box order): skipped. These are style norms, and the audit marks them optional.
- N21(c) (the temp path in the copied Zenodo JSON): left as is, as the audit allows.
- N23 (the letter and the prologue voice): needs the author's own sign-off.
