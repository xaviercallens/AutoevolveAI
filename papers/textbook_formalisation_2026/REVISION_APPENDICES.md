# Revision of appendices A-F following AUDIT_APPENDICES.md (ACCEPT_WITH_CORRECTIONS)

Build: pdflatex x3 on main.tex, 175 pages, 0 errors, 0 undefined references, 0 overfull boxes (none above 15 pt).
`pdftotext main.pdf`: "Famille" 0 occurrences; no mojibake ("Ã" 0); `<rev>` prints correctly.
No git writes. Files edited: appA, appB, appC, appD, appE, appF, easter_eggs_figures.tex, refs_app.tex, main.tex (`upquote=true` only).

## BLOCKING
- B1 APPLIED (minimal fix). appF: listing of f11_ilene.lean now uses `firstline=2,firstnumber=2`; sentence changed to "Un fichier de 21 lignes, dont nous reproduisons les lignes 2 à 21, ..."; note "(La première ligne du fichier, import du module des acronymes, est omise ici.)". Whole-PDF grep: 0 "Famille". The source comments (acronymes_listing.tex, code/easter_egg_images.py) are untouched, as the audit allows.
- B2 APPLIED. appB remark "La connexité compte" replaced with the audit's exact text (E={0,1,2,3}, P(1,2)=P(2,1)=1).
- B3 APPLIED. appE: `<révision>` -> `<rev>` plus "(<rev> : la révision épinglée du tableau~\ref{appE:tab:hf})".

## NONBLOCKING
1. Applied (appA: A subset of R^p; remark on integrable-only version in proof of (1)).
2. Applied (appA: "Les sommes de réseau du plan ...").
3. Applied (appA exercise: tie rule, tau = -1/2 + 1.25 i equivalent by T to 1/2 + 1.25 i).
4. Applied (appB proposition harmmart).
5. Applied (appB uniqueness sentence).
6. Applied ((semi-)anneau commutatif).
7. Applied ("en pratique, tout théorème sur R ...").
8. NOT applied: the comment lies in code/lean/appC_3_recurrence.lean, outside the allowed edit scope (appA-F, easter eggs, refs_app, main.tex). Left for the caller (comment-only change per the audit).
9. Applied in appC and appE (replay time is the start-up of leanchecker, cause not measured).
10. Applied (`upquote=true` in `\lstset`).
11. Applied (appD "d'au plus un demi-ulp").
12. Applied (appD: different absolute tolerance, step-count comparison only indicative).
13. Applied (appE: python-flint invisible under -I; P1 certificate does not need it).
14. Applied (appE: working leanflow_mcp command from ~/LeanFlow-wt-p1/src, without -I).
15. Applied (appE: path now starts with .../SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/...).
16. Applied (appF: drifts "3 et 4 x 10^-3").
17. Applied: ALEXIS (n=1 only), ALIX (grid point equivalent corner, Nelder-Mead 1e-7), KAL (Wright-Fisher harmonicity at N=8), ILENE (floats for n=8, rationals for n=3).
18. Applied (appF table "X (calcul exact)"; \tierX added to captions of figures 4 and 5).
19. Applied (refs_app.tex: header "A a F", bibitems app:lhn and app:montgomery marked "(notice non revérifiée)", cited in appF).
20. Not applied: dedication in main.tex is the author's decision and outside the allowed edit scope. Residual risk: the dedication names next to the acronyms still allows pairing.
