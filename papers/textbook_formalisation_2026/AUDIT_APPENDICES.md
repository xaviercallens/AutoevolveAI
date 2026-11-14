# Independent audit of the appendices (A–F) and the Easter-egg images — textbook 2026 FR

Auditor: an independent Claude agent (producer != verifier). Audited commit 78915c1 of branch
`worktree-openai-math-discovery`, `main.pdf` with 175 pages. Scope: `appA_analyse.tex`, `appB_probabilites.tex`,
`appC_lean.tex`, `appD_numerique_certifie.tex`, `appE_reproduction.tex`, `appF_exemples_code.tex`,
`easter_eggs_figures.tex`, `refs_app.tex`, `code/lean/appC_*`, `code/appC_leanchecker.py`, `code/appD_certifie.py`,
`code/examples/**`, `code/easter_egg_images.py` (through its self-check record), `figures/appF_*` and `figures/egg_*`.
Chapters 1–5 were not re-audited. Scratch files are in `/tmp/tb2appaudit/`. I made no git writes.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The mathematics is sound with one exception: a counterexample in B contradicts the book's own definitions. Every
number I re-ran matched the book. No tier violation was found: every `\tierA` in the new parts points to a module
replayed by `leanchecker` with rc 0, or to a certificate that the script itself replays. The three BLOCKING items
are quick to fix:

- the appendix-F Lean listing prints a module path that gives away the family meaning of the acronyms;
- the counterexample in B is false;
- a mojibake string appears in the printed appendix E.

---

## What I re-ran (actual output, 2026-10-26)

| Check | Command (cores 4,5) | Result |
|---|---|---|
| Moran N=3, r=2 with `fractions.Fraction` | inline script | p=(1/3,1/6,4/15,2/15); det(I−Q)=7/45; N=[[18/7,15/7],[6/7,45/14]]; t=(33/7,57/14); B(·,3)=(4/7,6/7); B(·,0)=(3/7,1/7); formula (1−r^{-i})/(1−r^{-N}) = (4/7,6/7). **All match appB:121–131.** Eigenvalues of Q: 1/3 and 23/30. |
| Lean C3 | `lean_pinned.py compile appC_3_recurrence.lean` | rc 0, 8.5 s; the three axiom lines are identical to appC:155–157 (including `simp_exemple` → `[propext]`) |
| Lean C6 | `lean_pinned.py compile appC_6_contrefacon.lean` | rc 0, 57.5 s (cold); both lines "does not depend on any axioms", **as claimed** |
| leanchecker replay (independent) | `appC_leanchecker.py /tmp/... appC_1 appC_5 appC_6` | E1 rc 0 (90.9 s), E5 rc 0 (87.8 s), E6 **rc 1** with the exact "declaration type mismatch … True … False" message, module-inexistant rc 1, `all_controls_pass: true` |
| `native_decide` claim (appC:303–306) | test file compiled with the pinned toolchain | `nd_test` depends on `[nd_test._native.native_decide.ax_1_1]`; `decide +kernel` gives no axioms. **Claim confirmed.** |
| Appendix D script | `appD_certifie.py /tmp/...` | rc 0; every value in appD:87–89, 124–127, 183–187 reproduced; 7/7 checks pass. mpmath gives I=0.746824132812427025399467436131…, which lies inside [lo,hi]. |
| Appendix E command | `ch1_theta.py` | rc 0; the lines quoted in appE:379–385 are reproduced exactly |
| Appendix F Python | `f04_wright_fisher.py`, `f05_graph_fixation.py` (run in a copy of the book) | rc 0; stdout **byte-identical** to `logs/f04_wright_fisher.txt` and `logs/f05_graph_fixation.txt` |
| Rust crate copy | `diff -r` of the rusty worktree `crates/qf-textbook-examples` against `code/examples/rust` | identical. The worktree HEAD is `refs/heads/textbook2/code-examples-2026-10-26` = f01b82b730c86ccf05c1f773b11fe0a9b650cc7b, as stated in appF:49–50. I could not inspect the commit tree because the guard forbids `git -C`; the file mtimes (10:08) are earlier than the ref (10:09). The line ranges quoted in appF:340 and 357 are the intended functions. The Jacobian `cols[c][r]=P[c][r]−δ` is (P−I)^T, as appF:355 states. |
| Easter-egg numbers | hand and mpmath | ALIX: Θ−1 gives 1.50173 / 1.50388 at α=0.4. KAL: 0.2009 and 0.9765. ILENE: star with 8 vertices recomputed, centre 0.16670 and leaves 0.70013; Moran n=8 gives 0.50196. ALEXIS: the mixture ∫w(a)/(2a)e^{-r²/4a}da equals (π/2)(H0−Y0)(r) at r=0.5 and r=2 to 1e-12. AURELIA: p*=0.38/0.6=0.6333. |

Proofs I checked line by line, all correct: dominated convergence and its uses (A thm cvd, cont, deriv, Gaussian
moments, including the exercise giving Γ(m+½)); Fourier properties; the Hankel transform; J0 (series, Wallis, Bessel
ODE by integration by parts); Γ(½); erfc bounds (the lower bound is A&S 7.1.13); the Struve series, its integral
representation and DLMF 11.5.2; Poisson in dimension 1 (periodisation, coefficients, Fejér) and on a lattice
(g=f∘M, ĝ(k)=V^{-1}f̂(M^{-T}k), y=Mz); the e^{-2πa|x|} exercise (f̂=a/(π(a²+ξ²)), coth, then π²/6); the Laplace and
subordination formulas (checked numerically); the SL2(Z) material (change of basis with ad−bc=1, Im formula,
point 1 by maximal imaginary part, stabilisers: S of order 4 / 2, and (τ−1)/τ fixing ρ, of order 3 mod ±I with
derivative ρ^{-2}, a rotation of −120°); Gauss reduction; B (geometric decay s_{n+m}≤s_n s_m, fundamental matrix,
t=N1, B=NR, P^n→B, maximum principle, Dirichlet, martingale r^{-X_n} including the algebra, optional stopping (1) and
(2), Moran by stopping, existence, uniqueness and positivity of the stationary law, the Doeblin contraction with
P^m=nδU+(1−nδ)R, the star π=(½,¼,¼) of period 2, uniformisation by a Poisson mixture); the WF exercise
E[X(N−X)]=(1−1/N)i(N−i); the times exercise (33/7, 57/14). D: interval inclusion, ball product, Euler stability
h≤2/λ, BDF2 coefficients, Newton matrix I−γhJ, WRMS. The explanation of "CVODE = Niveau X" in appD:223–231 is
correct and well argued.

---

## BLOCKING

**B1. The family meaning of the acronyms is exposed in appendix F (requirement 6).**
`appF_exemples_code.tex:518` prints `code/examples/lean/f11_ilene.lean` in full. Line 1 of that file is
`import Programmes.Famille.Acronymes`. The printed log `f11_ilene.txt` does not contain "Famille". `pdftotext`
finds exactly one occurrence of `Famille` in the whole PDF, and it is this listing line. Together with the
dedication in `main.tex` ("À Ilene, Alexis et Aurelia …"), this makes the family reading explicit. The Easter-egg
captions themselves are clean: only the English back-expansions are given, with no family wording.

Fix, either option:

- (minimal, fastest) Print the listing from line 2:
  `\lstinputlisting[language=Lean,style=appFcode,firstline=2,firstnumber=2]{code/examples/lean/f11_ilene.lean}`.
  Add after it: « (La première ligne du fichier, \texttt{import} du module des acronymes, est omise ici.) » Change
  « Un fichier de 21 lignes » (appF:517) to « Un fichier de 21 lignes, dont nous reproduisons les lignes 2 à 21, ».
  The `\tierA` records stay valid. "Famille" still appears in the shipped source folder and in the code comments
  (`acronymes_listing.tex:1`, `code/easter_egg_images.py:1`), but not in the PDF.
- (thorough) Rename `formal_cert/Programmes/Famille/` to `formal_cert/Programmes/Acronymes/`, then recompile with
  `--olean` and replay `leanchecker`. **Until that replay is redone, `acronymes_leanchecker*.json` no longer
  describes the renamed module.** ILENE (appF:528–529) and the five egg captions must then read `\tierAs` until a new
  record with rc 0 exists. After that, regenerate `f11_ilene.txt` and update the two comment lines.

**B2. The counterexample in appB:175–180 is false under the book's own definitions.**
With P(1,1)=1, state 1 is *absorbing* (by the definition in appB:58). Then A=E, T=∅, the chain is absorbing, and the
maximum principle holds vacuously. The remark therefore does not show what it claims. Replace lines 176–178 with:

> « Sans l'hypothèse « absorbante », le principe du maximum est faux. Sur $E=\{0,1,2,3\}$, avec $0$ et $3$
> absorbants et $P(1,2)=P(2,1)=1$, aucun état absorbant n'est accessible depuis $T=\{1,2\}$ : toute fonction avec
> $h(1)=h(2)$ est harmonique sur $T$, la valeur commune est arbitraire, et le problème de Dirichlet a une infinité de
> solutions. »

(Line 178, starting « C'est la raison d'être … », can stay.)

**B3. Mojibake in the printed appendix E.** `appE_reproduction.tex:172`: inside `\chemin{...}` (a `\url`
command), `<révision>` prints as `<rÃľvision>` (printed page 134 = PDF page 144, confirmed by rendering and `pdftotext`).
Replace it with
`\chemin{https://huggingface.co/datasets/<id>/resolve/<rev>/<fichier>}` and add after it « (\texttt{<rev>} : la
révision épinglée du tableau~\ref{appE:tab:hf}) ».

---

## NONBLOCKING

1. **appA:54–58 and 137.** The continuity theorem is stated for $A\subset\R$, but it is used for $\xi\in\R^d$, with
   $f$ only integrable (not piecewise continuous). Write « Soit $A$ une partie de $\R^p$ » and add to the proof of
   (1): « (la version du théorème~\ref{appA:thm:cont} pour une fonction seulement intégrable en $x$ a la même
   preuve) ».
2. **appA:276–277.** « l'erreur de troncature … décroît comme $1/R$ » holds in the plane. Write
   « Les sommes de réseau du plan d'un potentiel … ».
3. **appA:484–486 (exercise).** The very first rounding step is a tie (Re$(v\bar u)/|u|^2=7{,}5$), and a later step
   hits another tie at $-0{,}5$. Add: « (en cas d'égalité, prendre l'entier inférieur ; le résultat est
   $\tau=-\tfrac12+1{,}25\,i$, équivalent par $T$ à $\tfrac12+1{,}25\,i$, sur le bord de $\mathcal F$) ».
4. **appB:194.** « harmonique sur $E$ tout entier (en particulier sur $T$, et constante sur chaque état absorbant) »
   is clumsy, since a function is always constant on a single state. Write « Si $h$ est harmonique sur $T$ (elle l'est
   alors automatiquement sur $A$, car $P(a,a)=1$), alors $M_n=h(X_n)$ est une martingale. »
5. **appB:281.** « une seule de ses droites a une somme égale à 1 » → « un seul vecteur de cette droite est de
   somme $1$ (la droite contient la loi stationnaire de la proposition~\ref{appB:prop:existence}, de somme $1$,
   donc sa somme n'est pas identiquement nulle) ».
6. **appC:117.** `ring` also works in commutative *semirings* (the example `double_somme` uses `ring_nf` on ℕ):
   « prouve une égalité dans un (semi-)anneau commutatif (identité de polynômes) ».
7. **appC:138–139.** « tout théorème sur $\R$ dépend des trois axiomes » → « en pratique, tout théorème sur $\R$
   dépend des trois axiomes ».
8. **`code/lean/appC_3_recurrence.lean:10`.** The comment « `simp` déplie la somme, `ring` conclut » does not match
   the proof (`rw`, `ring_nf`, `omega`). Use « -- Récurrence sur n ; `sum_range_succ` isole le dernier terme,
   `omega` conclut. » (This changes neither the axiom output nor any timing.)
9. **appC:284–286 and appE:439–440.** The explanation « leanchecker charge toutes les dépendances (Mathlib ou
   Lean) » does not fit examples 1 and 5, which import nothing. My replay still took 91 s and 88 s for them. Write
   « Une minute environ par module, même pour les exemples~1 et~5 qui n'importent rien : le temps est celui du
   démarrage de \lean{leanchecker}, pas celui du module (nous n'en avons pas mesuré la cause). »
10. **main.tex `\lstset` (affects appC:225 and every listing).** In the printed C6 listing, Lean backticks show as
    curly quotes (‘contrefacon, ‘‘False). Code copied from the PDF then does not compile. Add `upquote=true` to
    `\lstset` (or `\usepackage{upquote}`).
11. **appD:76.** « se trompe de moins d'un demi-ulp » → « se trompe d'au plus un demi-ulp ».
12. **appD:272–273.** From my knowledge (not re-checked here), the C reference `cvRoberts_dns` uses a vector
    absolute tolerance (1e-8, 1e-14, 1e-6), while `robertson.rs` uses a scalar 1e-8, so the step counts are not
    like-for-like. Add « (avec une tolérance absolue différente de celle de l'exemple Rust : la comparaison des
    nombres de pas n'est qu'indicative) ».
13. **appE:53–54 (cosmetic).** The sentence is true: the system `python3` does run the P1 certificate. Two
    clarifications would still help. Under `-I` the user site `~/.local` is not on `sys.path`, so
    `python3 -I -c "import flint"` fails. And `run-certificate.py` imports only the standard library. Suggested
    wording: « avec python-flint~0.9.0 dans \texttt{\~{}/.local} (invisible sous \texttt{-I} ; le certificat P1
    n'en a pas besoin) ».
14. **appE:133.** Verified: `.venv/bin/python -I -m leanflow_mcp.lean --help` fails with `ModuleNotFoundError: No
    module named 'leanflow_mcp'`. The text only says how the book's *scripts* work around this. Give a working
    command: « depuis \chemin{~/LeanFlow-wt-p1/src} :
    \texttt{\~{}/AutoevolveAI/.venv/bin/python -m leanflow\_mcp.lean AFFIRMATION.json --lean ...} (sans
    \texttt{-I}, qui retirerait le répertoire courant de \texttt{sys.path}) ».
15. **appE:235.** The elided path is ambiguous. The clone lives under
    `/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math/`
    (verified: the folder `verification/` exists there, with `run-certificate.py`). Write
    `.../SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/...`.
16. **appF:450.** « les dérives montent à $3\times10^{-3}$ » understates H: the log gives 3.07e-3 for S and 3.93e-3
    for H. Write « à $3$ et $4\times10^{-3}$ ».
17. **Easter-egg captions, precision fixes.** None of these makes a caption false, but each overstates or
    blurs a detail.
    - ALEXIS (l. 64): « $2\cdot10^{-13}$ » is consistent with `bins_sum_vs_struve_max_rel_err` = 2.2e-13, so no
      change is needed there. However, l. 67 says « $n=1$ et $n=2$ sont recoupées par différences finies », and the
      self-check records only `rel_err_n1_vs_finite_difference` (5.0e-9), with no n=2 entry. Write « $n=1$ est
      recoupé par différences finies de la forme de Struve », or add the n=2 check.
    - ALIX (l. 22): `grid_argmin` = (−0.5, 0.8684), the T-equivalent corner, about one grid step away; only
      Nelder–Mead reaches 1e-7. Write « le minimum de la grille (au point équivalent $-\tfrac12+i\tfrac{\sqrt3}2$, à
      un pas de grille près) et cinq minimisations de Nelder--Mead (à $10^{-7}$ près) retombent sur
      $\tau=e^{i\pi/3}$ ».
    - KAL (l. 38): the exact-rational harmonicity check for Wright–Fisher was done at N=8, not at the N=24 shown.
      Write « L'harmonicité des deux $h$ est vérifiée en rationnels exacts (pour Wright--Fisher, à $N=8$). »
    - ILENE (l. 47): the n=8 values are floating-point solves. Write « probabilités obtenues en résolvant le
      système linéaire sur les $2^n$ configurations (en flottants pour $n=8$, en rationnels pour $n=3$) ».
18. **appF:85–86, 234, 274.** The table says « exact (fractions) », which is not a tier. Write « X (calcul exact) »,
    and add `\tierX` to the captions of figures 4 and 5, like the other figures.
19. **refs_app.tex.** The header says « annexes A a E », but appendix F also cites literature without a bibitem
    (appF:285, Lieberman–Hauert–Nowak; appF:172, Montgomery). Add
    `\bibitem{app:lhn} E.~Lieberman, C.~Hauert, M.~A.~Nowak, \emph{Evolutionary dynamics on graphs}, Nature
    \textbf{433}, 312--316 (2005) (notice non revérifiée).` and
    `\bibitem{app:montgomery} H.~L.~Montgomery, \emph{Minimal theta functions}, Glasgow Math.\ J.\ \textbf{30},
    75--85 (1988) (notice non revérifiée).`, and cite them.
20. **main.tex dedication (outside the new parts, author's decision).** « À Ilene, Alexis et Aurelia » next to
    « Les quatre lettres d'ALIX et les trois de KAL se cachent… » already lets a reader pair names with acronyms.
    If the family meaning must stay hidden, consider not naming the acronyms next to the names.

## Item-by-item notes on the requested checks

- **(2) Lean appendix C.** I recompiled C3 and C6; both match. I also re-ran the leanchecker replay of E1, E5 and E6,
  and all three match. The forgery is explained correctly: `skipKernelTC` plus `addDecl` with a `True.intro`
  value; `#print axioms` stays clean; only the replay refuses it; the elaborator refuses the naive version. The
  four-control gate matches ch1:569. The tactics table is correct, apart from nonblocking item 6. The
  `native_decide` axiom naming is confirmed.
- **(3) D.** The directed-rounding, Arb (centre in arbitrary precision, radius rounded up) and BDF/Newton/WRMS
  explanations are correct. The tiers are correct: LeanFlow without replay gives `\tierAs`, the Arb enclosure gives
  `\tierC`, the conclusion gives `\tierC`, and CVODE gives X.
- **(4) E.** Commands verified in the sources:
  - `lean_pinned.py compile --olean --json-out` (`OUT=formal_cert/.olean_out` is hard-coded, as stated);
  - `dipolar_crystal refs|gaps|controls|main`;
  - `yukawa_crystal exact-refs|exact-relax|exact-saddle` (bin `src/main.rs`);
  - `lattice_phonon point|scan|frozen|ewald_static|duffy|curv|scha`;
  - `keldysh_jellium scan|points`;
  - the LeanFlow CLI (`--lean`, exit codes 0/1/2);
  - `robertson.rs` (rtol 1e-4, atol 1e-8, BDF max order 5, analytic Jacobian);
  - worktree HEADs tb2ch5 = cda9a905…, as in the table.

  Ran `ch1_theta.py` (matches) and `appD_certifie.py` (matches).
- **(5) F.** Every number quoted in the "Lecture" paragraphs of examples 1–12 was compared with its log. All agree,
  apart from nonblocking item 16. The Rust copy is identical to the rusty worktree at f01b82b.
- **(6) Images.** I opened all five PNGs. The captions match the panels and the self-check record
  (`results/textbook_formalisation_2026/easter_eggs_selfcheck.json`), and I recomputed the key values. No caption
  states anything false. Family wording: none in the captions; leak through B1.
- **(7) Tiers.** I read the records myself:
  - `acronymes_leanchecker.json`: `Programmes.Famille.Acronymes`, rc 0;
  - `acronymes_leanchecker_sources.json`: 10 rows, all rc 0;
  - `kernel_replay_2026-10-26/replay.jsonl`: every CompletelyMonotone, UniversalOptimality, PopGen, EvoGraph,
    Yukawa, Dipolar and Keldysh row has rc 0.

  The Mathlib files cited in appA:21–23 exist in the pinned `.lake`, and `Mathlib/Data/Real/Basic.lean` carries
  `deprecated_module`, consistent with appC:144. Every `\tierA` in the new parts is backed by a replay:
  - ALIX: Triangular.UniversalOptimality, rc 0;
  - KAL, AURELIA, wbar_increment: PopGen, rc 0;
  - ILENE and the star N4 values: EvoGraph + `acronymes_leanchecker*.json`, rc 0;
  - ALEXIS: CompletelyMonotone, rc 0;
  - ch2 potentials in F ex. 2 and 3: rc 0;
  - F ex. 10: the script replays and reports `leanchecker_rc 0`.

  `\tierAs` is used correctly in D:191, E:112 and F:438.
- **(8) Bibliography.** Every refs_app entry is marked « non revérifiée ». I checked Serre (PUF 1970, ch. VII),
  Norris (CUP 1997), Williams (CUP 1991) and Hindmarsh et al. (ACM TOMS 31(3) 363–396, 2005) from my knowledge: all
  correct, so no correction is needed. DLMF chapters 5/7/10/11 and §11.5.2 are correct.
- **(9) French and pedagogy.** The French is clear and correct. The level suits the CPGE target: the statements
  outside the programme (Fejér, Lebesgue, Bernstein's converse) are labelled `\tierL`. The exercises are well chosen
  and include negative controls. Minor wording: items 4, 5, 7.
- **(10) Layout.** Rendered printed pages 113 (B.8 Moran), 123 (C.6 forgery listing), 134 (E.1 Lean/LeanFlow) and 145
  (F.2 figure), i.e. PDF pages 123, 133, 144, 155. The layout is clean and the matrices are legible. Defects: B3 (mojibake) and item 10 (backticks).
