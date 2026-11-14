# Revision after the independent AI audit (2026-10-26)

Audit: `AUDIT.md` (separate Claude agent, ACCEPT_WITH_CORRECTIONS). All four blocking items and all eleven nonblocking items were applied; none was declined. There is still no human audit.

Numbers in the new sentences are emitted as macros by `gen_inputs.py` from `data/` (new macros: `BCBelow*`, `ExtGamStar*`, `SlopeTwoPt`, `SlopeQuad*`, `SlopeCub*`, `SlopeSqAtTen`, `SchaEdge*`, `Ryd*Ms/Hz/Factor*`).

## Blocking
- **B1 (a_L).** Verified in the source: Astrakharchik et al. p.3 defines `a_L^-1 = (sqrt(3) n/2)^(1/2)`, so `a_L = a_nn`. The default `pdftotext` extraction scrambles this two-column sentence, which is why the first version missed it; `pdftotext -raw` keeps it. New quote row **B1-C-0116** (`ledger/citations/claim_astra_aL.json`, run through `run_citation.py` on the raw text stored at `programmes-2026-10-26/B1/src/cond-mat_0608246v2.raw.txt`; the real gate says REFUSED (kind), the verbatim-only check says ACCEPTED, as for the other quotes). B1-C-0011 rewritten (only the displacement reading remains), B1-X-0004 now depends on B1-C-0116, `ledger/sources/MANIFEST.md` corrected, main.tex Sec. 3.3 and Limitations, `publication_meta.json` description and notes.
- **B2 (SCHA alone).** Reading (a), Verdict B1c, Verdict table, kill-criterion paragraph, Limitations bullet 1, abstract: spinodal at or beyond melting only for gamma_c <= 0.28 (a tie to rounding at a = 0.7: 0.2798 against 0.28); for gamma_c = 0.30 it precedes the Lindemann point for a = 0.5-0.9 (gamma = 0.280-0.299). Where Lambda_1 is inside the band (a = 0.5-1 narrow, 0.45-1.1 wide) the negative verdict rests on SCHA alone. Same change in ledger B1-X-0004 and B1-X-0013 and in publication_meta.
- **B3 (scope).** Title, pdftitle, abstract ("The anharmonic test, within SCHA"; "disappears within SCHA"; "not a statement of physical absence"), publication_meta title. The subtitle phrase "at or beyond Lindemann melting" is withdrawn. The last sentence of the kill-criterion paragraph ("an artefact of the harmonic approximation") was also rescoped to SCHA.
- **B4 (audit disclosure).** Cover line, AI-assistance disclosure, Limitations, publication_meta description and notes now point to `AUDIT.md` (independent AI audit, corrections applied, no human audit). Each ledger row's `audit` field records the audit as an object. New Sec. 6 "Independent AI audit and revision" with the auditor's table.

## Nonblocking
- **N1.** Controls (iv) and Limitations: LS line -3.843, two-point -3.846, quadratic -3.848; hbar^2 coefficient ~15-16.5 (secant 14.7, quadratic 16.5); sentence that the fitted hbar^3 term (-141, three-point interpolation) is comparable at hbar ~ 0.1 (+0.165 against -0.141), so the stiffening is not a controlled O(hbar^2) correction. Also in ledger B1-X-0007.
- **N2.** Rust section: the Rust module re-implements the same Duffy-Gauss zone rule, only the real-space D differs; 1e-16 agreement means identical discrete sums; abstract says "two implementations" (not "independent"); the independent-quadrature check is the auditor's midpoint grid, cited in Sec. 6 (table quoted from AUDIT.md, not recomputed here). Ledger B1-X-0012 and publication_meta likewise.
- **N3.** main.tex Competitors paragraph: the >= 1e-5 minimum is the sampled point nearest rho; edge winners +1.65e-3 (a = 1, (0.30, 0.96)) and >= 7.6e-4 at a = 0.5 (winner (0.305, 0.955), +8.07e-4); from `scha.json`. **TRANSITION.md erratum** (the file is a byte-identical copy of the producer's record and its hash is in `data/MANIFEST.json`, so it is NOT edited here; the producer file under `results/proposal2/` is outside this task and was not touched):
  1. "2.6e-5 above triangular" for the harmonic Lambda_1 winner is the arc point nearest rho (x = 0.4826); the winner (0.30, 0.96) is +1.65e-3 above.
  2. "dressed-state lifetime (~27 us)" should read: bare 31P1/2 Rydberg lifetime 27 us; extracted dressed loss time 130(20) us against 2.2 ms expected (Zeiher et al., 1602.06313 p.3, p.5).
  3. 100.5 Hz should be 100.7 Hz (hbar^2/(m_Rb87 R_c^2)/h = 100.706 Hz).
  The paper already used the corrected values; a pointer to this erratum is in the Reproducibility section.
- **N4.** Ledger B1-C-0102 and B1-C-0008 now say "no evidence of a cluster crystal"; main.tex introduces the p.11 sentence as the authors' summary of the classical Gaussian-core cluster literature (refs [37,38], checked in the source: Mladek et al. PRL 96 and Speranza et al.), not their mean-field result.
- **N5.** Abstract and a "Meaning of first order" paragraph in Sec. 3.2 (and ledger B1-X-0002): finite-distortion stable lattice ties with rho before c(hbar) vanishes; the competitor sits on the stability boundary and is not an interior local minimum.
- **N6.** Rydberg time scale: sqrt(U0 E_Rc)/h = 426 Hz, 1/omega = 0.37 ms, period 2.3 ms; the 130 us loss time is shorter by a factor ~3 to ~18; the 10 ms (1/100.7 Hz) is named as the slowest scale.
- **N7.** Reworded to "has the negative Fourier component that the cluster criterion (Likos; [sub]) requires, and Henkel et al. (re-read) find roton softening and supersolid formation for it"; ledger B1-C-0009 likewise.
- **N8.** Step 3: "c_st >= 0 (a minimum); c_st > 0 is the computed value".
- **N9.** The quantum-melting statement is moved out of the Tier C sentence of the abstract and labelled "Inference, not literature (Tier X)"; same in Sec. 4 and the verdict table.
- **N10.** Reading (c) quotes gamma_SCHA at hbar* (0.30 at a = 0.5, 0.34 at a = 1) next to the harmonic gamma and notes the QMC anchors are true-<u^2> values.
- **N11.** publication_meta: "150 shapes per case (103-114 of them beyond the harmonic stability edge)". Ledger now has 39 rows (38 + B1-C-0116).

## Declined
None.
