# Erratum to papers/p4_amplifier_census (doi:10.5281/zenodo.23704563), owed after C1b

Status: DRAFT text only. `papers/p4_amplifier_census/main.tex` was NOT edited. Nothing here has been applied, committed or published.

## What was wrong

The published C1 paper reports that Richter (arXiv:2204.12861v1, p. 8) found no transient amplifier among regular-input graphs with N <= 10, and presents Richter's graph R11 (`J?ouPjI[@i?`, N_eff = 2668552698098/242579025123) as "the eleven-vertex example". It does not say that the same page (Fig. 1) shows **four** non-isomorphic N = 11 transient amplifiers, with printed N_eff 11.0008, 11.0128, 11.0056 and 11.0952. The exhaustive N = 11 census C1b (this directory) finds exactly four graphs with N_eff > 11, matching those four by N_eff, edge count and degrees (drawings not compared). So:

- R11 is **one of four** N = 11 amplifiers, not the example and not the only one (it has the smallest N_eff of the four).
- C1's headline ("no graph with N <= 10 is an amplifier; the smallest amplifier has exactly 11 vertices") is **unchanged**.
- C1's wording that nothing is exhaustive "over all graphs" for N >= 11 and that the census novelty is "to our knowledge" is unchanged.
- C1's Lean theorems (`R11_amplifier`, `P11_isothermal`, `eq5_unique`) are unchanged and correct as stated.

Sourcing note: the statement about Richter's Fig. 1 is transcribed from the C1b run note (`results/proposal4/2026-10-27/C1b/RESULT.md`, read from arXiv with alphaXiv in the C1b session). The agent that wrote this erratum did not re-open the PDF; whoever applies it should confirm the four printed values on p. 8 first.

## Edits (old -> new), by line of `papers/p4_amplifier_census/main.tex`

### 1. Abstract, lines 53-54
Old:
> Richter (2020) exhibited an eleven-vertex example.

New:
> Richter (2020, 2022) exhibited eleven-vertex examples (four in the 2022 paper).

### 2. Abstract, end (line 58-59)
Old:
> graphs}, the smallest dB amplifier has exactly $11$ vertices.

New:
> graphs}, the smallest dB amplifier has exactly $11$ vertices. (A companion exhaustive census at $N=11$ finds exactly four such graphs, those of Richter's Fig.~1; doi to be added.)

### 3. Section 1, lines 93-96
Old:
> Richter~\cite{rich20,rich22} and Svoboda et al.~\cite{svo} describe the eleven-vertex example. Svoboda et al.\ (p.~5) call it ``the smallest known unweighted dB-amplifier''; Richter (2020, p.~6) writes that ``the smallest graph for which $N_{\mathrm{eff}}>N$ was found is the quartic graph with size $N=11$'', meaning within his regular-input search, and Richter (2022, p.~8) reports that no transient amplifier was found for regular graphs with $N\le10$ using his method.

New:
> Richter~\cite{rich20,rich22} and Svoboda et al.~\cite{svo} describe eleven-vertex examples. Svoboda et al.\ (p.~5) call the quartic-minus-an-edge graph ``the smallest known unweighted dB-amplifier''; Richter (2020, p.~6) writes that ``the smallest graph for which $N_{\mathrm{eff}}>N$ was found is the quartic graph with size $N=11$'', meaning within his regular-input search; Richter (2022, p.~8) reports that no transient amplifier was found for regular graphs with $N\le10$ using his method, and shows (Fig.~1, same page) four non-isomorphic $N=11$ transient amplifiers, with $N_{\mathrm{eff}}$ printed as 11.0008, 11.0128, 11.0056 and 11.0952. The graph treated below is the first of these.

### 4. Section 3, "Richter's eleven-vertex graph", line 218 (first sentence)
Old:
> Graph6 \verb+J?ouPjI[@i?+: the unique quartic ($4$-regular) graph on $11$ vertices (among $265$) from which an \emph{amplifier constructor} edge removal works, minus one edge at the argmax-remeeting vertex.

New (append at the end of the first paragraph of that subsection):
> This is one of four $N=11$ amplifiers shown in Richter's 2022 Fig.~1 (the one with printed $N_{\mathrm{eff}}=11.0008$); it has the smallest $N_{\mathrm{eff}}$ of the four. It is not claimed to be the only $N=11$ amplifier.

### 5. Section 8 (Limitations), first bullet, line 343
Old:
> Richter~\cite{rich22} (p.~8) reports only that his iterative \emph{regular-input} procedure found none with $N\le10$; Svoboda et al.\ (p.~5) call Richter's graph ``the smallest known''.

New:
> Richter~\cite{rich22} (p.~8) reports that his iterative \emph{regular-input} procedure found none with $N\le10$, and shows four $N=11$ examples in his Fig.~1; Svoboda et al.\ (p.~5) call the graph treated here ``the smallest known''.

### 6. Same file, Section 4 table row, line 285 (optional)
The row "The smallest connected unweighted dB amplifier of weak selection has exactly 11 vertices" needs no change; add to its basis cell: "(at $N=11$ there are exactly four, see the companion census)".

### 7. `publication_meta.json` (`description`, `notes`) of the C1 record
Add the sentence: "Richter's graph is one of four N = 11 amplifiers shown in Richter 2022 Fig. 1; the companion exhaustive census (C1b, doi to be added) finds that there are exactly four." Also in `notes`, replace any wording that presents the eleven-vertex graph as the unique example by "an eleven-vertex example". (The title and description say "Richter's eleven-vertex graph", which stays correct; the file was only partly grepped for wording that implies uniqueness, so check it.)

### 8. Zenodo record
Publish as a new version of doi:10.5281/zenodo.23704563 (v1.1) with the edits above and the `related_identifiers` entry: this erratum's companion record, relation `isContinuedBy`/`continues` as chosen at publication. No change to the Lean files or to any count in C1.

## What does not change
All C1 counts (N = 3..10: 2, 6, 21, 112, 853, 11 117, 261 080, 11 716 571; ties 1, 2, 2, 5, 4, 17, 22, 167; no amplifier), the Tier A statements, the finite-r certificates for R11, and the two open discrepancies with Richter (tau_max, r_max).
