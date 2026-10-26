# Independent audit of the English university edition (`papers/textbook_formalisation_2026_en/`)

Auditor: independent AI agent (producer != verifier). No human has reviewed this audit.
Date: 2026-10-26. Object: `main.pdf` (181 pages, `pdfinfo`) and the `.tex` sources, compared with the audited
French edition `papers/textbook_formalisation_2026/` (AUDIT.md and AUDIT_APPENDICES.md, revisions applied).
Scratch files (scripts and outputs): `/tmp/tb2enaudit/` (`extract.py`, `numcmp.py`, `tiercmp.py`, `checks.py`,
`checks_out.txt`, `numcmp.txt`, `en.txt`, `fr.txt`, `pg-*.png`). I made no git writes and did not rebuild the PDF.

## VERDICT: ACCEPT_WITH_CORRECTIONS

The translation is faithful. Numbers, tiers, citations, Lean names and cross-references match the French edition
exactly in every chapter and appendix (the scripts below show this). All 19 University remarks state true standard
facts and are tagged Tier L. All 10 (*) University exercises are well posed, and every answer I recomputed is
correct. The honesty statements are preserved, with none softened or strengthened. The Easter-egg constraints hold.
One blocking item remains: the preface makes a false claim about the University remarks. There are also 13 nonblocking items.

---

## BLOCKING

**B1. Five University remarks have no citation key, but the preface says every remark gives a reference.**
`preface.tex:47-49` says the remarks "state the general textbook form of a tool used in the text (...) and give a
reference". These five cite nothing and end only with "(standard)", so they fail the citation-key requirement:
`appA_analyse.tex:96-102` (differentiation under the integral), `ch1_fondations.tex:326-330` (Lévy–Khintchine),
`ch2_flux_formalisation.tex:616-622` (differentiation under the integral), `ch3_quantique.tex:157-163` (Poisson in
R^d with shift) and `ch3_quantique.tex:641-647` (Bochner). A related weakness, not counted among the five: `ch1_fondations.tex:225-230` cites only
`montgomery`, "for the planar case", and `refs_ch1.tex:5` says that paper was cited at second hand and never opened (see N10).
The French edition has no such blocks, so this claim is new in the English edition.
The fix has two parts. (a) Add an existing key where it genuinely covers the fact: at `ch1_fondations.tex:329`, replace
`(standard).` with `(standard; see~\cite{ch2ssv}).` The key `ch2ssv` exists (`refs_ch2.tex:41`), and the parallel remark
`ch2_flux_formalisation.tex:729` already cites it. I do not propose `app:williams` for the two differentiation remarks,
because I have not confirmed that Williams states that result.
(b) For the remarks the bibliography has no key for (Bochner, Poisson in R^d, differentiation under the integral),
correct the preface. In `preface.tex:48-49`, replace
`formula in $\R^d$, the theory of absorbing Markov chains) and give a reference; they add no new claim.`
with
`formula in $\R^d$, the theory of absorbing Markov chains), with a reference where the bibliography has one and the mark ``(standard)'' otherwise; they add no new claim.`

---

## NONBLOCKING

**N1. The Bochner remark overreaches slightly** (`ch3_quantique.tex:643-645`; rendered on p. 51). The sentence "a radial potential whose
planar Fourier transform takes negative values is not positive definite" holds within Bochner's hypotheses, that is, for a
continuous function. It says nothing about the singular potentials used elsewhere in the book (Coulomb, Riesz, Yukawa,
dipolar), and the clause "whereas the Gaussian ..., with transform ... > 0, is;" reads awkwardly. Replace
`In particular a radial potential whose planar Fourier transform takes negative values is not positive
definite, whereas the Gaussian $e^{-\pi a|x|^2}$, with transform
$a^{-1}e^{-\pi|k|^2/a}>0$, is; so is every completely monotone $g(|x|^2)$ with finite mixing measure, as a positive
mixture of Gaussians (standard).`
with
`In particular a continuous integrable radial function whose planar Fourier transform takes negative values is not
positive definite (the soft shoulder above is an example). The Gaussian $e^{-\pi a|x|^2}$, whose transform
$a^{-1}e^{-\pi|k|^2/a}$ is positive, is positive definite, and so is every completely monotone $g(|x|^2)$ with finite
mixing measure, being a positive mixture of Gaussians (standard). Singular potentials such as $1/r$ fall outside
the scope of this statement.`

**N2. In Chapter 1, "(*)" collides with the difficulty stars.** In `ch1_fondations.tex`, `[*]` marks the *easiest*
exercises (l. 684: "of increasing difficulty (from * to ***)"; l. 686, 691, 711). The University exercises at l. 738 and
748 are titled "(*) University exercise", which a reader will take as "one star = easy". The preface disclaimer
(`preface.tex:50-51`) is far away. Fix at `ch1_fondations.tex:684`. Replace
`Hints follow the list of exercises. The exercises are of increasing difficulty (from * to ***).`
with
`Hints follow the list of exercises. The exercises are of increasing difficulty (from * to ***). The two final
``(*) University exercises'' are harder than all of these; their ``(*)'' is a label, not a difficulty rating, and they have no hints.`

**N3. Eight of the ten University exercises have no answer key.** Only the two in Chapter 4 give answers
(`ch4_genetique.tex:1277-1279, 1292-1293`). The others are correct and well posed (see the verification below), but a
student cannot check them. I suggest adding the following answers, each of which I verified numerically
(`checks_out.txt`):
- `ch3_quantique.tex:934` (after the exercise), add:
  `\emph{Answer.} c) With $v=\cos(\theta/2)$, $E_{\mathrm{zp}}=\frac{2\hbar}{\pi}\int_0^1\sqrt{K_1+4K_2v^2}\,dv
  =\frac{\hbar}{\pi}\Bigl[\sqrt{K_1+4K_2}+\frac{K_1}{2\sqrt{K_2}}\operatorname{arsinh}\bigl(2\sqrt{K_2/K_1}\bigr)\Bigr]$
  for $K_2>0$. d) For $K_2=0$: $\frac2\pi\approx0.637\le\frac{\sqrt2}2\approx0.707$ (in units of $\hbar\sqrt{K_1}$).`
- `ch3_quantique.tex:945`, add: `\emph{Answer.} c) $\hat f(\xi)=\int\frac{\pi}{t}\,e^{-\pi^2|\xi|^2/t}\,d\mu(t)\ge0$.`
- `ch5_cas_usage.tex:907`, add: `\emph{Answer.} c) $g_\kappa(t)=\int_0^\infty e^{-ts}\,(\pi s)^{-1/2}e^{-\kappa^2/(4s)}\,ds$.`
- `ch2_flux_formalisation.tex:1184`, add:
  `\emph{Answer.} d) $E(a)=a^{-1}\theta(1/a)^2-1$ and $\theta(1/a)^2=1+4e^{-\pi/a}+O(e^{-2\pi/a})$.`

**N4. A Gallicism** (`ch2_flux_formalisation.tex:1177`). "Admit the Poisson summation formula on $\R$" translates
"admettre". Replace `Admit the Poisson summation formula on $\R$:` with `Take for granted the Poisson summation formula on $\R$:`.

**N5. A Gallicism in a translated exercise** (`ch3_quantique.tex:900`). Replace
`Conclude on the inconclusive nature of the test.` with `Explain why the test is inconclusive.`

**N6. Code comments are in French, but the preface mentions only figures** (`preface.tex:51-52`). Appendix F's
listings are read unchanged from the French tree, so their comments and docstrings are in French
(for example `code/examples/python/f01_poisson.py:24` "Somme directe ...", and `f11_ilene.lean` comments such as "Temoin
negatif plante"). Appendix C (l. 47) and Appendix E (l. 32) each say this for their own listings; Appendix F says nothing.
Replace
`reused unchanged, so the labels inside some figures are in French; every caption is in English.`
with
`reused unchanged, so the labels inside some figures are in French; every caption is in English. Likewise, the code
listings and logs are reproduced exactly as they were run, so their comments are in French.`

**N7. The Bernstein remark in Chapter 5 omits the finiteness condition** (`ch5_cas_usage.tex:264-265`). The remark says "for a positive Borel
measure $\mu$" without requiring $\int e^{-ts}d\mu<\infty$ for $t>0$. The condition is implicit, because $g$ is
real-valued, but the other three Bernstein remarks (`appA_analyse.tex:224`, `ch2_flux_formalisation.tex:833`) state it.
Replace `for a positive Borel measure $\mu$~\cite{bernstein,widder}.` with
`for a positive Borel measure $\mu$ on $[0,\infty)$ with finite integral for every $t>0$~\cite{bernstein,widder}.`

**N8. The University remarks repeat each other.** Bernstein's theorem appears four times (`appA:222`, `ch2:831`, `ch5:264`, and
Theorem `ch1:thm:bernstein`). Lévy–Khintchine appears twice (`ch1:326`, `ch2:727`). Hitting probabilities as the minimal or unique
solution appear three times (`appB:120`, `ch4:303`, `ch5:598`). Differentiation under the integral appears twice (`appA:96`, `ch2:616`).
None of this is an error, since the chapters are meant to be read independently. Optionally, replace the
`ch2:727` remark with `\begin{uniremark}\tierL{} The Lévy--Khintchine representation of Bernstein functions
(University remark after Example~\ref{ch1:ex:bernstein}, \cite{ch2ssv}) is not formalised here; the library works only
with the derivative-sign definition above.\end{uniremark}`.

**N9. The Moran fixation exercise appears twice.** `ch4_genetique.tex:1282-1294` and `ch5_cas_usage.tex:885-894` are the same
optional-stopping exercise. Suggest replacing the Chapter 5 one. Alternatively, add `\label{ch4:ex:moranmart}` after
`ch4_genetique.tex:1282` and begin the Chapter 5 exercise body (`ch5_cas_usage.tex:886`) with
`(This restates Exercise~\ref{ch4:ex:moranmart} for readers of this chapter alone.)`.

**N10. The `montgomery` citation in the Poisson remark is weak** (`ch1_fondations.tex:229`). It sends the reader to a paper
the authors never opened (`refs_ch1.tex:5`) for a textbook fact. Optionally replace
`(standard; see also~\cite{montgomery} for the planar case)` with `(standard)`, or cite a textbook the authors have
checked.

**N11. The dedication still makes pairing possible** (inherited from the French edition, AUDIT_APPENDICES NB20). The constraints are met:
`pdftotext main.pdf` gives "Famille" 0 times; the dedication (p. 2, rendered) reads exactly "To Ilene, Alexis and
Aurelia."; and no family meaning is given (the acronyms expand to mathematical phrases such as "Isothermal Law: Every Node
Equivalent"). The residual risk from the French audit carries over unchanged: the three names sit next to theorems named
`ILENE`, `ALEXIS` and `AURELIA`. The author decides whether to accept this; no change is required.

**N12. Small wording issue in the optional-stopping remark** (`appB_probabilites.tex:250-251`). "Relatedly, Doob's martingale
convergence theorem ..." is correct. "Relatedly" is a little informal for a textbook; suggest "In the same
setting, Doob's ...".

**N13. Not rebuilt.** I audited the shipped `main.pdf` (timestamp 11:13) without recompiling. `pdftotext` shows no "??"
and no "[?]". I did not check overfull boxes, because there is no `main.log` in the directory. After applying B1 and N1–N7,
recompile three times and confirm 0 undefined references.

---

## What was checked, with evidence

### (1) The 19 University remarks (all tagged `\tierL{}`; counted by grep: appA 3, appB 2, appD 1, appF 1, ch1 2, ch2 3, ch3 2, ch4 3, ch5 2)
Every remark states a true standard fact. Notes on the cases the brief asked me to watch:
- **Dominated convergence** (appA:46). Measure-space form, a.e. convergence, $|f_n|\le g$ a.e., $g\in L^1$; conclusion
  $\int|f_n-f|\to0$. Correct; probability is the case $\mu(\Omega)=1$; cites `app:williams`.
- **Differentiation under the integral** (appA:96, ch2:616). Domination of $\partial_a f$ uniform in $a$ by an integrable $g$;
  differentiability for a.e. $\omega$. Correct.
- **Bernstein** (appA:222, ch2:831, ch5:264). CM on $(0,\infty)$ iff Laplace transform of a positive Borel measure on
  $[0,\infty)$ (finite for $t>0$), with $\mu$ unique. Correct; the measure need not be finite ($1/t$). Only the "if" direction
  is used, as ch2:834-835 says. See N7 for ch5.
- **Lévy–Khintchine** (ch1:326, ch2:727). $a,b\ge0$, $\int\min(1,s)\nu(ds)<\infty$. Correct. The example
  $\sqrt t=\frac1{2\sqrt\pi}\int(1-e^{-st})s^{-3/2}ds$ was verified numerically (t = 0.8: 0.894427190999916 both sides).
- **Bochner** (ch3:641). Continuous $f$ is positive definite iff it is the Fourier transform of a finite positive measure. Correct;
  see N1 for the scope of the consequence.
- **Poisson in R^d** (ch1:225, ch3:157). The covolume factor $\operatorname{covol}^{-1}$ and the factor $\alpha^{-d/2}$ are correct.
  Checked numerically on the non-unimodular lattice $M=\begin{pmatrix}2&0.7\\0&1.3\end{pmatrix}$ at $\alpha=0.6$:
  both sides equal 1.037328276605741. The negative control (identity without the covolume factor) gives 2.697, which does not match.
  "Converges faster when $a$ is small" (ch3:161) is correct, since the reciprocal sum decays like $e^{-\pi|P|^2/a}$.
- **Hitting probabilities and hitting times** (appB:120, ch4:303, ch5:598). These are the minimal non-negative solutions
  (Norris Thm 1.3.2, 1.3.5), unique and bounded for a finite absorbing chain; $h_T=(NR)(\cdot,a)$ and $t=N\mathbf1$. Correct.
- **Optional stopping** (appB:247, ch4:285). The three sufficient conditions are stated correctly (Williams 10.10), as is
  $L^1$-bounded supermartingale convergence.
  The Chapter 4 use (bounded martingale, $T<\infty$ a.s. from Lemma `ch4:lem:geom`, a human proof tagged Tier C in the Wright–Fisher section) is correct.
- **Fundamental matrix** (ch4:389). $N_Q=\sum Q^n=(I-Q)^{-1}$, expected visits, $B=N_QR$, $t=N_Q\mathbf1$. Correct.
- **Floating point** (appD:38). $\mathrm{fl}(x)=x(1+\varepsilon)$, $|\varepsilon|\le u$ in the normal range. Correct.
- **BDF / Dahlquist** (appF:350). BDF1 and BDF2 are A-stable; the second Dahlquist barrier says A-stable LMMs have order at most 2; BDF3–5 are
  $A(\alpha)$-stable; CVODE uses orders 1 to 5. Correct.
All cited keys exist: `bernstein`, `widder`, `montgomery` (refs_ch1), `ch2ssv` (refs_ch2), `app:norris`, `app:williams`,
`app:ieee754`, `app:sundials` (refs_app). Cross-referenced labels all exist (`ch1:thm:bernstein`, `ch1:thm:comp`,
`ch1:prop:cloture`, `ch3:eq:einstein`, `ch3:ex:gauss`, `ch3:def:ezp`, `ch4:lem:geom`, `ch4:thm:moran`, `ch4:lem:moranbase`,
`appA:thm:cvd`, ...).

### (2) The 10 (*) University exercises: answers recomputed (`checks.py` → `checks_out.txt`)
- **Neutral Moran, N = 3** (ch4:1268), in exact `Fraction` arithmetic: $Q=\begin{pmatrix}5/9&2/9\\2/9&5/9\end{pmatrix}$,
  $R=\mathrm{diag}(2/9,2/9)$, $(I-Q)^{-1}=\begin{pmatrix}3&3/2\\3/2&3\end{pmatrix}$, $t_1=t_2=9/2$ (also found
  independently from the first-step equation), $B=\begin{pmatrix}2/3&1/3\\1/3&2/3\end{pmatrix}$, so the column for state 3 is $(1/3,2/3)$.
  **All match the printed answer.** Negative control: $t\ne4$ holds.
- **Moran martingale** (ch4:1282, ch5:885). The identity $\mathbb E[r^{-X_{n+1}}|X_n=k]-r^{-k}=r^{-k}(r-1)(q_k-p_k/r)$ is checked
  algebraically, and $(1-r^{-i})/(1-r^{-N})$ follows. Correct.
- **Harmonic chain** (ch3:919). The factorisation $D(k)=4\sin^2(k/2)(K_1+4K_2\cos^2(k/2))$ holds to within $10^{-16}$ at 3 values of $k$. For $K_2=0$:
  $E_{zp}=0.830050630243660=\frac2\pi\sqrt{1.7}$, which confirms $(2/\pi)\hbar\sqrt{K_1}$. For $K_2=0.4$: quadrature 0.946189133425091,
  Riemann sum with N = 4000 0.946189074, closed form (N3) 0.946189133425091. The Einstein bound
  $\frac\hbar2\sqrt{2K_1+2K_2}=1.0247$ holds, and for $K_2=0$, $0.6366\le0.7071$. The 1D form $\frac\hbar2\sqrt{\langle D\rangle}$ is the correct
  analogue of `ch3:eq:einstein` ($\sqrt{\langle\operatorname{tr}D\rangle/2}$ in 2D).
- **Z² Gaussian sum** (ch2:1176). Jacobi residual at a = 0.37 is $-2\times10^{-31}$. For $(E(a)-(a^{-1}-1))/(a^{-1}e^{-\pi/a})$, I get 4.0004 at a = 0.05 and
  4.0000006 at a = 0.2 (so $O(a^{-1}e^{-\pi/a})$ holds, with constant 4). $E(a)/(4e^{-\pi a})$ is 1.00008 at a = 3 and 1.0000000065 at a = 6.
  Correct. The covolume factor for $\Z^2$ is $a^{-1}=a^{-d/2}$ with $d=2$, which is correct.
- **$e^{-\kappa\sqrt t}$ as a Laplace transform** (ch5:896), with $\kappa=1.3$. At t = 0.5 and t = 2, quadrature equals $e^{-\kappa\sqrt t}$ to 30 digits.
  The density $\frac{\kappa}{2\sqrt\pi}s^{-3/2}e^{-\kappa^2/4s}$ has total mass 1.000000000000000 (a probability density, the
  one-sided ½-stable law, so the normalisation is correct). The hint's identity $\int_0^\infty e^{-(u-a/u)^2}du=\sqrt\pi/2$ holds for a = 0.3 and 2,
  and the substitution $s=\kappa^2/(4u^2)$ reduces the integral to exactly this identity (checked by hand). Part (c): the transform of
  $(\pi s)^{-1/2}e^{-\kappa^2/4s}$ equals $e^{-\kappa\sqrt t}/\sqrt t$ (0.349523817372092 both sides).
- **Jacobi theta in R^d with covolume** (ch1:738). Checked with the lattice test above; parts (b) and (c) are correct
  ($\operatorname{covol}=1$ forced, and the invariant is $\alpha^{d/4}\Theta$).
- **Exponentials of Bernstein functions** (ch1:748). (a)–(c) are correct given Theorem `ch1:thm:comp` (which requires $h>0$, as
  assumed). Both $\ln(1+x)$ and $t+\sqrt t$ are Bernstein functions.
- **Laplace representations** (ch2:1165). $t^{-s}=\Gamma(s)^{-1}\int u^{s-1}e^{-tu}du$, and the identity for
  $\mathrm{shiftDiff}_{1,c}=t^{-1/2}-(t+c)^{-1/2}$ checks numerically (0.351068999902524 both sides). The label "Bernstein reading" exists
  (ch2:338). Correct.
- **Gaussian CM and FT** (ch3:936). Dirac at $t=\pi a$ is correct. The 2D FT of $e^{-t|x|^2}$ is $(\pi/t)e^{-\pi^2|\xi|^2/t}$ (Hankel quadrature
  0.729933161336398 both sides). $\int t^{-1}d\mu<\infty$ is exactly integrability of $f$ on $\R^2$. Correct.

### (3) Translation fidelity
**Script comparison of numbers** (`numcmp.py` → `numcmp.txt`). The script compares the multiset of digit strings in each
FR/EN `.tex` pair, after normalising the French decimal comma `{,}` and thin spaces and excluding the new University blocks.
- ch1–ch5, appA–appD, appF, easter_eggs_figures, acronymes_listing and all refs files have **0 mismatches** (for example ch2: 1100/1100;
  ch4: 1349/1349).
- `appE_reproduction.tex` has 15 numbers that appear only in EN, all inside the two added translation notes "(The comments read: ...)"
  at l. 223 and l. 326 (for example "115 rows, 106 accepted, 9 controls refused"), which translate the French listing comments.
  These numbers equal the French source (FR l. 316: "115 lignes : 106 acceptées, 9 témoins refusés").
- `preface.tex` has "1" and "5" only in EN, from the new paragraph "Chapters 1 to 5".
- `main.tex` has "026" and "1" only in EN: the `../textbook_formalisation_2026` input paths and "Version 1 (English university edition)".
- **No number is missing from or altered in the EN text.**
**Ordered check** (`numseq.py` → `numseq.txt`). Because the multiset check would miss two numbers swapped between sentences,
I also ran `difflib.SequenceMatcher` on the *ordered* number lists. 19 of the 22 pairs have 0 non-equal opcodes. appE, main and
preface have only `insert` opcodes, which are exactly the EN additions listed above. There are no `replace` and no `delete` opcodes anywhere.

**What the new remarks say about the book.** Each remark's statement about the book's own content was checked against the book. ch4:394-395 says
absorption times are not formalised; this is recorded at `ch4_genetique.tex:1106`. ch3:162 refers to the "Poisson sum in reciprocal space used
below", which is used at `ch3_quantique.tex:236-237`. ch2:834-835 says the "if" direction only; the preceding paragraph (l. 825-829)
says the hard direction is not proved. ch5:266 refers to "the three steps above", and l. 242-248 contain these steps
(CM∘Bernstein, $t^{-1/2}$, product). ch2:730 refers to the "derivative-sign definition", which is the definition at l. 723-726. No remark
misstates verification status.
**Script comparison of markup** (`tiercmp.py`). The counts of `\tierA`, `\tierL`, `\tierC`, `\tierX`, `\cite{`, `\lean{`, `\ref{` and `\label{`
are identical in every pair once the new blocks are excluded. The only difference is the preface, which has one extra `\tierL` (in the
paragraph describing the remarks).
**15 passages read side by side** (FR → EN): ch1 warnbox on where the results come from (l. 24-30); ch1 Table 1.2 Clay
sentence (FR 486 / EN 499: "We do not claim that a Clay problem is solved."); ch2 opening warnbox (l. 38-47); ch2 ⊤≤⊤
warnbox ("this finiteness is not proved"); ch2 Sandier–Serfaty status box (FR 875 / EN 892: "is not proved in this
book ... AI-generated and not peer reviewed ... neither a proof, nor a verification, nor a peer review"); ch3 opening
and warnbox ("No human has audited them", Montgomery cited second hand); ch4 kernel-replay paragraph with its three
limitations; ch5 warnbox (U1/U2 conditional on `universal_energy_minimum`, AI-generated, not peer reviewed); ch5
Bogoliubov "what this does not show" (1.4–4 K, not T = 0); appA Debye–Hückel scope note; appB "Connectivity matters"
(the corrected counterexample E={0,1,2,3}, from FR audit B2, is carried over); appC axiom-whitelist rule; appD half-ulp; appE python-flint
(invisible under -I); appF triangular optimality "conditional on the upstream theorem" and the gradient-descent caveat;
appF f11 listing `firstline=2` with "lines 2 to 21" (FR audit B1 carried over). **All faithful. No claim is softened or
strengthened.** In the PDF, "Clay" occurs only as "no 'Clay problem solved'" and "We do not claim that a Clay problem is
solved". Sandier–Serfaty is "not proved" in the preface, ch1 and ch2.

### (4) Easter eggs
`pdftotext main.pdf | grep -c Famille` gives 0. "Famille" occurs once in the source, in a `%` comment line of `acronymes_listing.tex:1`, which is not
printed. The dedication on p. 2 (rendered and inspected) reads exactly "To Ilene, Alexis and Aurelia." It is followed by the sentence about ALIX and
KAL hidden in the Lean code of Chapter 5. No family meaning is given anywhere: a grep for family/daughter/son/wife/children
found only "the Gaussian family" and "a family resemblance (dipoles)", both mathematical. See N11 for the inherited pairing risk.

### (5) English quality
The prose is idiomatic, precise and at the right level for undergraduates (worked human proofs, explicit
conventions) and graduates (University remarks in measure-theoretic form, starred exercises). The terminology is standard
(completely monotone, Bernstein function, dynamical matrix, Brillouin zone, optional stopping, fundamental matrix).
Leftover Gallicisms are rare (N4, N5). French appears only inside figures and code listings, which is acknowledged in part (N6).

### (6) Rendered pages (pdftoppm, then read)
- PDF p. 2: dedication. Clean.
- PDF p. 61 (printed 51): Bochner University remark plus §3.5 and a Lean box. Typesetting is fine; the wording is the issue in N1.
- PDF p. 65 (printed 55): Exercises 3.5–3.13, including the start of the harmonic-chain University exercise. Formulas render correctly.
- PDF p. 88 (printed 78): Exercises 4.10–4.13, including the Moran N = 3 University exercise. The tier badge and enumerations render correctly.
No overfull text, missing glyphs or "??" were visible on these pages.
