# Revision of the English edition after AUDIT.md (ACCEPT_WITH_CORRECTIONS)

Only files in `papers/textbook_formalisation_2026_en/` were edited. Nothing was committed, pushed or published.

## Applied

- **B1 (blocking).** `ch1_fondations.tex`: the Levy--Khintchine remark now ends "(standard; see~\cite{ch2ssv})".
  `preface.tex`: the sentence now reads "..., with a reference where the bibliography has one and the mark
  ``(standard)'' otherwise; they add no new claim." The other four remarks keep "(standard)" and have no new key.
- **N1.** Bochner remark in `ch3_quantique.tex` replaced by the audit's text (continuous integrable radial function; soft shoulder
  example; singular potentials such as 1/r out of scope).
- **N2.** The ten added exercises are now titled "($\dagger$) University exercise: ..." (ch1 to ch5, two each). The preface
  says the dagger is a label, not a difficulty rating. The sentence suggested by the audit (with the dagger instead of the star)
  is added in `ch1_fondations.tex` after "(from * to ***)".
- **N3.** "Answer." added to four exercises, with the audit's verified text only: ch3 harmonic chain (c, d), ch3 Gaussian CM (c),
  ch5 Yukawa Laplace transform (c), ch2 theta identity (d). The other University exercises received no new answers
  (those of ch4 already had them; ch1 x2, ch2 Laplace representations, ch5 fixation have no answer text in AUDIT.md).
- **N4.** "Admit the Poisson summation formula" became "Take for granted the Poisson summation formula" (ch2).
- **N5.** "Conclude on the inconclusive nature of the test." became "Explain why the test is inconclusive." (ch3).
- **N6.** Preface sentence added: code listings and logs are reproduced as run, so their comments are in French
  (the sentence about figure labels being in French was already there).
- **N7.** Chapter 5 Bernstein remark now says "on $[0,\infty)$ with finite integral for every $t>0$".
- **N9.** `\label{ch4:ex:moranmart}` added to the Chapter 4 Moran martingale exercise. The Chapter 5 exercise now begins
  "(This restates Exercise~\ref{ch4:ex:moranmart} for readers of this chapter alone.)". The Chapter 5 exercise is kept.
- **N12.** "Relatedly, Doob's" became "In the same setting, Doob's" (`appB_probabilites.tex`).

## Not changed (noted)

- **N8.** Repeated University remarks (Bernstein x4, Levy--Khintchine x2, hitting probabilities x3, differentiation x2) are kept;
  the chapters are meant to be read independently. The optional replacement of the `ch2` remark was not applied.
- **N10.** The `montgomery` citation in the Poisson remark of Chapter 1 is kept (optional change not applied). It is a second-hand
  citation, see `refs_ch1.tex`.
- **N11.** The dedication pairing risk inherited from the French edition is left to the author. No change.
- **N13.** Superseded by the rebuild below.

## Build (pdflatex x3, `main.tex`)

- Errors: 0 (no `!` line in `main.log`). Undefined references or citations: 0. "Rerun" warnings: none after the third pass.
- Overfull boxes: 10 in the log, the largest 8.61 pt; none above 15 pt.
- Pages: 181.
- `pdftotext`: "Famille" 0 occurrences; "[?]" 0; the dagger appears 21 times.
