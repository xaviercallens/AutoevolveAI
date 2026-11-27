# AUDIT — « De la conjecture au noyau Lean » (manuel 2026, FR, CPGE)

Independent adversarial audit (producer ≠ verifier). Auditor: a separate Claude agent, 2026-10-26.
Scope: `main.tex`, `preface.tex`, `ch1`–`ch5`, `refs_ch*.tex`, `acronymes_listing.tex`, `Acronymes.md`, `FACTS.md`,
`code/`, `figures/`, `main.pdf`, against FACTS.md, the source papers in `papers/` and the Lean sources in `formal_cert/`.
Scratch: `/tmp/tb2audit/` (own scripts and rebuild; nothing in the book directory was modified except this file).
No human has audited this book or this audit.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The mathematics I checked is correct. I found no claim that Sandier–Serfaty is proved, that a Clay problem is
solved, or that anything is a breakthrough. The Lean listings I spot-checked are verbatim. The acronym file is
reproduced exactly. The blocking items are about **tier honesty** (Niveau A is used for statements that do not
meet the book's own Niveau A gate, and Niveau L is used for sources that other chapters say were never opened),
**one stale fact** (A2 is published) and **visible layout defects** (180 pt overfull running heads in ch1). Each
fix is local. None of them needs new mathematics.

---

## What I re-ran or recomputed myself (real output)

- **Rebuild.** `pdflatex` ×2 on a copy in `/tmp/tb2audit/build`: 110 pages, no undefined reference or citation,
  15 overfull hboxes (located in B5 and N-list). All 5 figures are found and included (`ch5_U1`…`ch5_U5`, input
  lines 185, 304, 400, 507, 645 of ch5).
- **Own exact script** `/tmp/tb2audit/check.py` (Fractions; the full 2^n configuration chain under birth–death
  updating, solved by exact elimination):
  - star n=3, r=2: centre **5/12**, leaf **2/3**, uniform **7/12**, Moran **4/7**. The table by cardinality order,
    (0, 5/12, 2/3, 2/3, 5/6, 5/6, 14/15, 1), equals `hStar` (Examples.lean:139). P⁺({0}) = P⁻({0}) = 1/2.
  - star with μ = (1/2, 1/4, 1/4): μW = μ is true; the centre gives 4/7.
  - star n=4: 392/1265, 168/253, 728/1265, Moran 8/15 (these agree with the Tier X values in ch4:979–980).
  - 4-cycle, r=2: P⁺({0,1}) = 1/3 and P⁻ = 1/6; P⁺({0,2}) = 2/3 and P⁻ = 1/3; stay probabilities 1/2 and 0; the
    jump chain goes up with probability 2/3 in both cases; every single-mutant start gives 8/15.
  - Moran N=3, r=2: (0, 4/7, 6/7, 1). N=10, r=3/2: φ₁ = 19683/58025 = 0.339215855234813, which matches the CVODE
    value 0.33921585523416337 of ch5 exercise U5a to 6.5e-13. ρ₁₀₀(1) = 0.005832 / 0.015709 / 0.090916.
  - ch1 numbox: Θ_A(0.5) = 2.008477918598, Θ_A(2) = 1.004238959299, Θ_A(3) = 1.000112671200, Poisson deviations
    4.4e-16 / 2.2e-16 / 8.9e-16, no-factor deviations 1.004 / 1.004 / 2.000, Θ_A(1) = 1.159595267,
    Θ_{Z²}(1) = 1.180340599. All agree with the book.
  - ch2: W(E_△) = π ln(2√2π / (√3 Γ(1/3)³)) = −4.1504128 ✓.
  - **ch5 U3 re-run, done independently** (I did not run `code/ch5_U3_helium.py`, because it writes into
    `figures/`): k* = 3.00379 Å⁻¹, 99 points, Δ = 0.0820, 29 / 7 / 63 compatible / undecided / refuted, 21/21 roton
    points refuted, ratio [1.617, 2.491], minimum margin 0.328, S_B fires 0 times, S = 1 fires 95/95, peak
    (2.058, 1.458) against a bound of 0.5853. Everything matches ch3 §3.4.3 and ch5 U3.
- **ch1 `T.lean`, recompiled** with `leanprover--lean4---v4.34.0-rc2`: the output equals the book's lines 533–537
  character for character, rc 0.
- **Acronyms.** The `acronymes_listing.tex` body (lines 11–149) is `diff`-identical to
  `formal_cert/Programmes/Famille/Acronymes.lean`. The records in `results/textbook_formalisation_2026/` show rc 0,
  five axiom lines within the whitelist, leanchecker rc 0 on the module and on its 10 in-repo sources, and controls
  that fail as intended (planted `sorryAx`; the `rfl` check against `harmonic_unique_of_var` gives a Type mismatch).
- **Lean listings checked verbatim against file:line** (13 listings, all match token for token; comments omitted
  where declared):
  - ch2: DipolarExciton.lean:22 and 94–96; Yukawa.lean:133–134; KeldyshCM.lean:31–36, 134–135, 190–191, 244,
    248–249, 354, 379, 390–392; SignedEndpoints.lean:33 and 79–85; CompletelyMonotone/Controls.lean:11–18;
    Bernstein.lean:49–51, 85–87, 160–161; SandierSerfatyStatement.lean:153–160; the openai/math pinned copy
    Energy/Basic.lean:26–29 and Universal.lean:9–11.
  - ch3: ZeroPoint/Basic.lean:91–92, 168–171, 201; ZeroPointCert/Basic.lean:127–144; FeynmanBijl/Basic.lean:262–268
    and 314–319.
  - ch4: PopGenFisher.lean:125–127 and 145; Absorption.lean:32–34, 45–53, 302–308; BirthDeath.lean:376–378;
    Examples.lean:230–231 and 239–243.
  - The one exception is ch1:583–586 (Riesz), where the line breaks differ from Riesz.lean:51–53 (N13).
- **ch4 leanchecker claim.** `results/kernel_replay_2026-10-26/ch4_popgen_trace/leancheck_ch4.json` exists: 10
  modules, all rc 0, 54.9–130.6 s, empty output, as stated in ch4:1055–1060.

## Human demonstrations: spot-check results (all correct unless listed in NONBLOCKING)

- **ch1.** Counting bound. Norms in A and the shell table (6, 6, 6, 12, 6; Z²: 4, 4, 4, 8, 4). M^{-T} and the
  autodual lemma (b₁ = (1, −1/√3)/a, |b₁|² = a², b₁·b₂ = −a²/2). Poisson for Gaussians: the ODE h′ = −(2πξ/α)h, the
  change of variables dx = du/V with (M^{-T}k)·u, and the Fejér evaluation. Jacobi. Leibniz closure. **CM∘Bernstein
  induction**: the quantification over all f, the step −(f∘h)′ = ((−f′)∘h)h′, and the sign
  (−1)^{n+1}(f∘h)^{(n+1)} = (−1)^n(Gh′)^{(n)} are all right. The dipole Euler mixture. The Fatou reduction. The
  exercise hints (the Epstein integral threshold s > 2; 1 − 2x + x⁴ < 0 at x = 2^{-1/3}).
- **ch2.** **Dipolar Pochhammer**: (−1)^r desc_r(−1/2) = asc_r(1/2), the bracket lemma, and the tail bound
  a − b ≤ (c/2)a³ through 2b² ≤ a(a+b). Yukawa: strong induction on φ′ = −(κ/2)t^{-1/2}φ, and e^x ≥ x²/2. Signed mix
  2e^{-1}(e^{1/2} − 2) < 0. erfcx bounds. Moments F_n = 2w u^{n+1}e^{-cu}. **Struve link** (a)–(d): DLMF 11.5.2 with
  ν = 0 gives 2/π; the Lévy subordinator; the inner integral (1/2)√(π/λ)·erfcx(√λ); the change of variables
  a = 1/(4b). **Subordination** Q(n). Quadrupole pair counting (6, −8, 2) and the identity
  3f − 4f(·+c) + f(·+4c) = Δ_c g + Δ_{2c} g + Δ_{3c} g. `signed_endpoints` and its counterexample G ≡ 1.
  The interval toy example.
- **ch3.** **Oscillator bound**: φ = mωxψ + ħψ′ and 2Re∫xψ̄ψ′ = −1. Chain ZPE (2/π)ħ√(K/m). Radial Hessian. The
  sum rule ⟨tr D⟩ = 4πa − (4π²/a)S(1/a), re-derived by Poisson. γ(τ) = (τ−1)/τ, with γ′(ρ) = rotation by −120°.
  lap_Q. **2×2 trace inequality**: tr(PM²) expansion and the column form. The quad_nonneg identity.
  Majorant U(0) = E(0). The logic lemma. Certificate arithmetic (−1.8415601; the esum threshold 1.0363). E″ = 8c,
  hence ΔE ≤ −0.92078. **Feynman–Bijl**: the double-commutator expansion (a)–(d), the Rayleigh lemma, the trial
  energy E₀ + ħ²k²/(2mS), and exercise (b)/(c) (the bound is attained). Bogoliubov S_B² = k²/(k*² + k²) and
  0 ≤ k(k − k*)². k* for ⁴He.
- **ch4.** Hardy–Weinberg. Δp = pqs/w̄. **The increment identity** W + a·pq = pw₁₁ + qw₂₂, checked again on
  w = (2, 1, 1) (11/100). Underdominance 7/19, 19/25 < 277/361. The control w = (−1, 1, 0). WF martingale and
  maximum principle. The geometric lemma with δ ≥ N^{-N}. **Moran fixation recurrence** Δ_i = r^{-1}Δ_{i−1}, the
  stay probability ri² + (N−i)², the block argument. Price (−13/36; −3/4; 1/6 vs 1/4). Cut balance. **Isothermal
  forward bias** P⁺ = r·P⁻ via out(S) = in(S), and the configuration-harmonic h with Δ⁻ = rΔ⁺. The 4-cycle. **Star
  n = 3**: the hand system of exercise ch4:ex:star, (a)–(e) re-derived. All exercise answers (WF N = 2 and N = 3,
  Moran N = 3, complete graph, 8/15).
- **ch5.** The U1 derivative formula. h_d(d²) = (1 − √2)/d. g₁ − 2g₂ = −0.2585. S_B algebra in U3a. 2DΩ identity
  in U4. φ₁ in U5a.

---

## BLOCKING

**B1. Niveau A is used for modules that do not meet the book's own Niveau A gate.**
The gate is defined three times. The preface (preface.tex:20–24) says axioms + leanchecker + grep. Ch1
(ch1:562–569) gives four controls plus producer ≠ verifier. Ch4 (ch4:40–44) gives the same as the preface.
FACTS.md:12–14 agrees. Three chapters then label Niveau A without the replay:
- ch2:171–178 (remark ch2:rem:skip) says the dipolar, Yukawa, Keldysh and CM-library modules have **no**
  leanchecker replay, and redefines their A as « celui de leurs articles ». This is a second, weaker definition of A
  inside the same book.
- ch3:532–535 (warnbox) says the same of ZeroPoint, ZeroPointCert and FeynmanBijl (« il reste à faire »).
- ch5:363 (U3, `sBog_le_sqrt`, QuantumFluids stack v4.34.0-rc2) and ch5:459 (U4, σ = 3, « Mathlib du projet »)
  give A with no replay mentioned.

Part of this is already covered and the disclaimers are out of date. `Autoresearch.Yukawa`,
`Autoresearch.KeldyshCM`, `Triangular.Riesz`, `Triangular.RieszFinite` and `Triangular.AnyDensity` were
leanchecker-replayed with rc 0 for the acronym gate (`results/textbook_formalisation_2026/acronymes_leanchecker_sources.json`).
A full-library replay is also running right now: `results/kernel_replay_2026-10-26/`. It is untracked, has 82 fresh
modules in `plan.json`, and 15 rows in `replay.jsonl`, all rc 0, including Triangular.*, DipolarExciton*, KeldyshCM
and PopGenFisher. Its grep (`grep_hits.json`, 871 files) has no code hit outside the declared planted-control
files. **Fix (preferred):** let it finish over every module cited in ch2, ch3 and ch5, add the external
σ = 3 / QuantumFluids stacks or say they are not covered, commit the record, and replace the two disclaimers:
- ch2:174–178, from « Par honnêteté : » to the end of the remark, with:
  « Par honnêteté : les articles sources de ces sections ne rapportaient pas de rejeu \texttt{leanchecker}. Ce rejeu
  a été fait pour ce livre le 2026-10-26 (enregistrement \texttt{results/kernel\_replay\_2026-10-26/}), sur les
  modules cités ici : code de retour~0 pour chacun, et la recherche textuelle ne trouve aucun jeton interdit hors des
  fichiers de contrôles plantés. Le rejeu porte sur les déclarations de ces modules ; Mathlib et le cœur de Lean
  sont chargés, non rejoués. »
- ch3:532–535, from « En revanche, aucun rejeu » to « et la recherche ci-dessus. », with the same text adapted to
  « ces trois modules ».

**Fix (fallback, if the replay is not finished before release):** keep the disclaimers, but stop calling these
statements plain Niveau A. Add to main.tex after line 31:
`\newcommand{\tierAs}{\textcolor{tierA}{\textbf{[Niveau A sans rejeu]}}}`
Then use `\tierAs{}` for every affected label: ch2 §2.3–2.4; ch3 lines 168, 187, 339, 421, 466, 474, 519–523, 647,
687, 702, 716, 758, 791, 794, 798; ch5:363, 459. (Yukawa and Keldysh are already replayed, see above.) Also add one sentence to ch1 §1.4.3, after line 569:
« Quand le rejeu \texttt{leanchecker} n'a pas été fait, nous écrivons \tierAs{} : liste d'axiomes, témoins plantés
et recompilation indépendante, sans rejeu du noyau. »

**B2. Statements checked only by their producer are labelled Niveau A** (ch1:569 makes producer ≠ verifier part
of the gate).
- ch2:231: « (\lean{g_inplane}, \tierA, module vérifié par le producteur seulement) ». The source
  (ar_dipolar_exciton/main.tex:88) also says producer-checked only. Replace with: « (\lean{g_inplane}, module
  \texttt{DipolarExcitonStep1.lean} vérifié par le producteur seulement : \tierC{} tant qu'un vérificateur distinct
  ne l'a pas recompilé) ». If the replay of B1 covers `Autoresearch.DipolarExcitonStep1`, and it is already rc 0 in
  `replay.jsonl`, say so instead and keep A.
- ch2:959, table row « Étapes complètes en L1 … \tierA »: two of the four stages (`calcLam` and `calcK`) had no
  producer ≠ verifier pass, as ch2:969–972 itself says. Replace the level cell `\tierA` with
  « \tierA{} pour \lean{init_constants}, \lean{bcons/eps} ; \tierC{} pour \lean{calcLam}, \lean{calcK} (pas de
  recompilation indépendante) ».

**B3. ch1:558, a tier inflation in the A2 warnbox.** The book says the forged declaration was « \emph{attrapé} par
le rejeu complet du noyau (\lean{leanchecker}) \tierA{} ». The A2 paper (p2_navier_stokes_audit/main.tex:376) files
the forged-declaration observation at **Tier X**, because it is about a planted invalid declaration. Replace
« \tierA{}. La leçon » with « (observation de niveau \tierX{} dans l'article A2 : elle porte sur une déclaration
volontairement invalide). La leçon ».

**B4. Niveau L is given to sources that other chapters say were not read.**
- ch1:250 (Montgomery, `\tierL{}~\cite{montgomery}`) and ch1:625. Ch3:37, ch3:191 and refs_ch3 (`ch3-montgomery`)
  state that the original « n'a pas été ouvert » and is cited second-hand through Deng–Luo.
- ch1:376 (Bernstein–Widder, `\tierL{}~\cite{bernstein,widder}`). refs_ch2 (`ch2widder`) says Widder was « non
  consulté ».

FACTS.md:16 defines L as « read and pinned ». Either the ch1 writer read Montgomery (1988) and Bernstein (1929), and
then refs_ch1 must say so with a page or theorem pin, or ch1 must say what ch3 says. Fix: in refs_ch1.tex, append to
`montgomery`: « Cité de seconde main, à travers K.~Deng et S.~Luo (arXiv:2411.17199) ; l'original n'a pas été
ouvert. ». Append to `widder`: « Non consulté ; cité d'après la bibliographie de Mathlib et de Cohn--Kumar 2007. ».
Then change ch1:250 to « \tierL{} (cité de seconde main)~\cite{montgomery} ». Change ch1:376 to « \tierL{} (énoncé
classique cité de seconde main)~\cite{bernstein,widder} ». Mirror this in the ch1:625 recap.

**B5. Layout: large overfull boxes, all located** (my rebuild's main.log).
- **176.5 pt and 181.9 pt, 7 occurrences** (log lines 1009, 1018, 1024, 1033, 1111, 1149, 1155). These are not
  tables. They are the **ch1 running heads** on the even pages 2–12 of chapter 1 (« CHAPITRE 1. FONDATIONS :
  RÉSEAUX, FONCTIONS COMPLÈTEMENT MONOTONES ET VÉRIFICATION FORMELLE »). Ch2, ch3 and ch4 set `\chaptermark`; ch1
  does not. Fix: ch1_fondations.tex:1, add `\chaptermark{Fondations}` right after `\chapter{…}`. (Use
  `\chapter[Fondations : réseaux, fonctions CM et vérification formelle]{…}` only if a shorter TOC entry is also
  wanted.)
- **115.9 pt at ch1:596–598.** The unbreakable `\lean{formal_cert/Programmes/CompletelyMonotone/Bernstein.lean}`.
  Fix: replace it with `\nolinkurl{formal_cert/Programmes/CompletelyMonotone/Bernstein.lean}` (hyperref is loaded,
  so it breaks at the slashes), or rewrite as « (extraits du fichier \lean{Bernstein.lean} du dossier
  \lean{formal_cert/Programmes/CompletelyMonotone/}, preuves omises) ».
- **48.6 pt** (log line 1270). The running head of ch4 §4.2. `\sectionmark{Wright--Fisher neutre}` sits at
  ch4:239, after `\label`, and the long title still reaches the head on the first page. Fix: write
  `\section[Wright--Fisher neutre]{Wright--Fisher neutre : martingale, fonctions harmoniques, absorption}` and drop
  the `\sectionmark`.
- Small ones (2.6–13.5 pt, NONBLOCKING): the ch4:187 display (split the chain of equalities over two lines with
  `\begin{multline}` or `aligned`), and ch5 at lines 380–383, 600–602, 804–807, 815–817 and 832–834 (long
  `\url`/`\texttt` tokens, plus exercise titles containing « (S) »). `\sloppy` locally, or `\allowbreak` in the
  paths, removes them.

**B6. A stale fact: the A2 Navier–Stokes paper is published.** The book says « article en préparation » at
ch1:473 (table row 7) and refs_ch1.tex:13 (`a2`, « paper in preparation »), and main.tex:67 defines `\StatusNS`
(« en préparation »), which is never used. The A2 paper carries **doi:10.5281/zenodo.23661381**
(papers/p2_navier_stokes_audit/main.tex:43; commit 3498cb4). FACTS.md:66 is outdated. Fix:
- ch1:473 reference cell: replace « article en préparation » with « doi:\,10.5281/zenodo.23661381 ».
- refs_ch1.tex:13: replace « record \texttt{results/proposal2/2026-10-26/A2/} (paper in preparation). » with
  « preprint v1, doi:10.5281/zenodo.23661381 (2026). Produit par des agents d'IA ; non relu par des pairs. »
- Delete the unused `\StatusNS` (main.tex:67–68), and update FACTS.md:66.

---

## NONBLOCKING

**N1. Preface, line 5: the first claim.** « Le point de départ est un théorème démontré et vérifié en Lean~4 »
states the upstream result with no conditional, although FACTS gives it Tier « L/A-conditional ». Replace with:
« Le point de départ est un théorème d'openai/math, dont la démonstration, produite par une IA et non relue par des
pairs, est vérifiée par le noyau de Lean~4 : ». Optionally say in ch1 §1.3 that the upstream statement was accepted
by Comparator in textbook v1 (papers/textbook_universal_optimality/ch1_foundations.tex:14). That is the only record
of a kernel-level check of the upstream closure: Acronymes.md says that upstream OAI modules were not replayed by
leanchecker.

**N2. The gate is described differently in different places.**
- ch1:16 says Niveau A means « avec un contrôle des axiomes utilisés ». Replace with « avec trois contrôles :
  axiomes de la liste blanche, rejeu du noyau (\lean{leanchecker}) et recherche des portes dérobées
  (§\ref{ch1:sec:lean}) ».
- The preface (line 20) has « trois vérifications », ch1:562 has « quatre contrôles », and the ch4:1235 exercise
  has « trois vérifications ». Say once, in ch1:562, « quatre contrôles (la compilation, puis les trois
  vérifications de la préface) ».

**N3. The definition of a Bernstein function is not the same in ch1 and ch2, and ch1 contradicts itself.**
- ch1:307 requires h : ]0,∞[ → ]0,∞[ (strictly positive). ch2:712 and Lean `IsBernsteinOn` require only h ≥ 0
  and add `hpos` separately.
- ch1:619 then says « Si $h\equiv0$ (qui est de Bernstein) ». Under ch1's own definition, h ≡ 0 is not a Bernstein
  function. The same problem is in ex. ch1:ex:comp (d) and its hint at ch1:733.

Fix: ch1:307, write « $h:\,]0,\infty[\to[0,\infty[$ … (définition de Lean \lean{IsBernsteinOn} ; le
théorème~\ref{ch1:thm:comp} demande en plus $h>0$) ». Change the example at ch1:312 to « $a,b\ge0$ ». At ch1:318,
say « Si $f$ est CM et $h$ de Bernstein \emph{strictement positive} ».

**N4. Wrong word in a hint, ch1:735.** « L'unicité de $\mu$ dans Bernstein--Widder et la positivité de $g$ en
$t=3$ concluent. » Replace with « L'injectivité de la transformée de Laplace (y compris pour les mesures signées)
montre que $g$ n'a pas de représentation à poids positif ; plus directement, $g(3)<0$ conclut. » The uniqueness in
thm ch1:thm:bernstein is stated only for positive measures.

**N5. A garbled statement, ch3:271–274** (prop. ch3:prop:intervalle). As written, it says that c(a) < 0 on the
whole of [0.15, 4]. Replace the body with: « Pour la gaussienne $e^{-\pi ar^2}$, parmi les valeurs
$0{,}15\le a\le4$ explorées, la courbure $c(a)$ est négative exactement sur l'intervalle numérique
$a\in(0{,}37668\,;\,1{,}58148)$ ; sur cet intervalle, le réseau triangulaire est un maximum local strict de
$E_{\mathrm{zp}}$. \tierX ». (Same meaning as prog_zero_point_optimality/main.tex:67.)

**N6. ch1 flow table, row 7 (ch1:473).** The level reads « \tierA{} ; pas de problème Clay résolu ». Make it
precise: « \tierA{} pour le rejeu noyau des énoncés du corpus ; fidélité à l'alternative (C) de Fefferman :
\tierC{} ; pas de « problème Clay résolu » ». The A2 paper (main.tex:75, 327) places that implication at Tier C.

**N7. French quality.**
- ch1:643: « reverifié » → « revérifié ».
- ch1:277: « noyau :\lean{…} » → « noyau : \lean{…} ».
- ch4:559: « Les contrôles suivants sont tous kernel-checked. » → « Les contrôles suivants sont tous vérifiés par
  le noyau. »
- ch4:1059–1061: « Les cinq modules jusque-là sans rejeu (…) ils satisfont donc maintenant la définition » →
  « Les cinq modules jusque-là sans rejeu (…) satisfont donc maintenant la définition ».
- ch5:597: « Le dépôt Genetic du propriétaire » → « Le dépôt Genetic de l'auteur ».
- ch5:618 and ch4:575: « fail-closed » → « (« fail-closed » : qui refuse par défaut) » at first use.
- ch5 comment lines 1–3: accents are missing (harmless).

**N8. Bibliography.** I found no duplicate `\bibitem` keys. But because everything goes into one
`thebibliography`, the same work is printed 2–3 times under different keys:
- oai/ch2oai, ckmrv/ch2ckmrv, v1/ch2txt/ch3-txtv1, montgomery/ch3-montgomery, widder/ch2widder;
- elenchus/ch2elenchus, p3/ch2cm, ch2dip/ch5:dipolar, ch2yuk/ch5:yukawa;
- ch3-db/ch5:donnelly, ch3-godfrin/ch5:godfrin, ch3-bsk/ch5:bsk, ch3-fb/ch5:p6, ch4:P7/ch5:p7, ch4:N4/ch5:n4.

Some of these copies contradict each other:
- `v1` (refs_ch1:11) gives the title « Universal optimality of the triangular lattice: a textbook ». The real title
  is « The Triangular Lattice and Universal Optimality » (as in ch2txt and ch3-txtv1).
- Montgomery and Widder: see B4.

Fix: merge onto one key per work (recommended), or at least correct `v1`'s title. Also:
- `ch2mn` (refs_ch2) has no title. Add it.
- The ch5 own-preprint entries lack the « non relu par des pairs » label that ch2, ch3 and ch4 carry. Add it.
- The ch1 entries carry no provenance labels at all (read or not read). Add them.
- `ch5:gb` is correctly labelled « non vérifiée ».

**N9. Easter eggs** (they are kept hidden as requested: the code docstrings give only the backronyms, the
dedication « À Ilene, Alexis et Aurelia. » is correct, and nothing in `code/` explains the names).
- FACTS.md:98–100 asks each chapter to mention the acronym « once, lightly, where the underlying result appears ».
  Only ch5:589 does (KAL, ILENE). Suggested one-liners:
  - ch2, after the D2 mention (line 84): « (ré-exporté au chapitre~5 sous le nom \lean{ALIX}) »;
  - ch2, after ch2:626: « (ré-exporté sous le nom \lean{ALEXIS}) »;
  - ch4, after thm ch4:thm:wflim: « (\lean{fixation_limit} reparaît sous le nom \lean{KAL}) »;
  - ch4, after thm ch4:thm:iso: « (\lean{isothermal_fixation_single} : \lean{ILENE}) »;
  - ch4, after cor. ch4:cor:haploide: « (\lean{fisher_haploid_nondecreasing} : \lean{AURELIA}) ».
- Two weaknesses in the hiding. The directory name `Famille` (ch5:768, Acronymes.md) states the family theme
  outright. And ch4:686 names the Genetic-repo lemmas `aurelia_mean_fitness_increment` and
  `kal_increment_is_variance`, which are *different* theorems from `AURELIA` and `KAL`. Renaming the directory
  would require recompiling the module, so this is the author's call. At least do not print the path in ch5:768:
  write « dans un fichier séparé de \texttt{formal\_cert/Programmes/} ».
- The dedication hint (main.tex:83) mentions only ALIX and KAL. That is fine if intentional.

**N10. The `rfl` identity claim.** `example : @ALIX = @src := rfl` checks that the two constants have
definitionally equal types (and, by proof irrelevance, equal values). It does not check syntactic identity.
Acronymes.md (« certifie que l'énoncé est littéralement celui de la source ») slightly overstates this: write « a
exactement le même type que la source, au sens de l'égalité définitionnelle ». The negative control (KAL vs
`harmonic_unique_of_var` → Type mismatch) is good. The book text (ch5 §5.7) makes no overclaim.

**N11. ch2:1040 (B3).** « il n'est connu optimal que parmi les réseaux de Bravais~\cite{ch2mn} \tierL ». As far as
I know, minimality of bcc among Bravais lattices for 3D jellium was open before 2026. The only support is
Muratov–Novaga, arXiv:2610.29732 (pinned « Théorème 1, p. 4 » in B3), and the bib entry has no title. Please
recheck this sentence against the pinned page and add the title. Without it, the reader cannot verify the claim.

**N12. ch4:1073–1074.** The trace « n'est pas versionnée » now exists at
`results/kernel_replay_2026-10-26/ch4_popgen_trace/leancheck_ch4.json` (untracked). Commit it and replace the
sentence with « La trace est \texttt{results/kernel\_replay\_2026-10-26/ch4\_popgen\_trace/leancheck\_ch4.json}. »

**N13. ch1:583–586.** The Riesz listing is reflowed: Riesz.lean:51 has `(hd : DensityOne C) :` on one line. It is
labelled « extrait » with « ... », but the box should also say « mise en page modifiée ». (The token content is
identical.)

**N14. ch1:505–538 (`T.lean`).** The book cites no record of this run. My recompile reproduces it exactly (see
above). Add the path of a saved record, or « (sortie reproduite par l'auditeur) ».

**N15. ch5:657 and ch5:663.** « deux affirmations » and « une des quatre propositions engendrées » do not obviously
agree. Add « (chaque affirmation est découpée par LeanFlow en propositions élémentaires) ».

**N16. Cross-chapter duplicated material is consistent.** The dipolar, Yukawa, Moran, isothermal, star, 4-cycle,
Bogoliubov and helium numbers agree across ch1–ch5, FACTS.md and the source papers. I checked P1 478 s, A1 4/12
and 1/12, 0.136 %, QU-1 8/12, (0.37668, 1.58148), U''(0) ∈ [−1.947713, −1.900168], ħ* = 0.1238, 130 / 167 / 20
for P3, 106 / 9 / 3.1e-10 for P7 CVODE, and 14 + 11 ledger flags. All 15 DOIs match FACTS.md. The P6 DOI
10.5281/zenodo.23653846 matches prog_superfluid_structure_factor/zenodo_doi.txt.

**N17. Exercises are well posed.** None asks the reader to prove something false or open without saying so. The
Gauss circle question (ch1:680) says optimality is not asked. The ch5 (S) exercises depend on scripts that write
into `figures/`. Warn readers to run them on a copy, or add an `--fig` option, so that a student run does not
overwrite the book's figures.

---

## Summary of blocking items
B1 Niveau A without leanchecker in ch2, ch3 and ch5 (finish and cite the running replay, or label it
« A sans rejeu »). · B2 producer-only `g_inplane` and `calcLam`/`calcK` labelled A. · B3 the A2 forged-declaration
observation is Tier X, not A (ch1:558). · B4 Montgomery and Bernstein–Widder are labelled L in ch1 although the
book says they were not read. · B5 overfull 176–182 pt ch1 running heads (add `\chaptermark`), 116 pt at
ch1:596–598, 48.6 pt ch4 §4.2 head. · B6 A2 is published (doi:10.5281/zenodo.23661381), not « en préparation ».
