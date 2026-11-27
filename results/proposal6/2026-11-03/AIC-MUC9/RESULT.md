# AIC-MUC9: independent exact recheck of arXiv 2610.10108 (Braverman, He)

Outcome: CONFIRMED for the finite checks A1-A10 (Tier C/X), plus the flow LP optimum (Tier X, floating). This is a RECHECK of a claim by others; no novelty claim. We do not claim the Li-Li conjecture is "solved" beyond what the checks show: the step "this finite example refutes the conjecture in the intended capacity model", the pipelining argument R_code >= 1, and the BGS17 amplification / Omega((log n)^eps) corollary are Tier L (literature, not checked). All code is our own; the authors' repository/verifier was NOT run (third party, licence unchecked). Preregistration: `PREREG_ITEM.md` (sha256 a0582465525ea294946f065ccc9b1696f2f573608c09d28fb464ef2e0d44eb29), written before any computation on the construction.

## What was pinned from the paper (Section 4, deterministic code)
Note: the plan item calls the example "non-deterministic"; in the paper, Section 3 is the non-deterministic certificate (166 deleted edges, 744 edges, bound 744/830) and Section 4 is the deterministic causal code (175 deleted edges, 735 edges, 157 sessions, bound 735/785 = 147/157). The 735/785 claim is Section 4, which is what was checked. Section 3 was not recomputed.
Construction: F9 = F3[theta]/(theta^2+1), element r <-> eta_r; T = 91 ordered triples; point i, line 91+j; candidate edge e_{10i+r} with increasing neighbours; R (175 indices), pi (182), C, J (9 each), B = R\(C u J) (157); physical edges oriented earlier->later in pi, deleted later->earlier; local rule Q(lambda,mu) (points) / Q(lambda^3,mu^3) (lines), basis = first two triples of T cap z-perp, no renormalisation. R and pi were hand-transcribed from the extracted appendix text into `/home/callensxavier_gmail_com/muc9_thirdparty/appendixA_transcribed.py` (not in the repo; sha256 in result.json). Fetch: `arXiv 2610.10108v1`, Appendix A (pp. 13-14). In the repo only the hashes of R, pi, C, J are stored.

## Prior-art search (2026-11-02, alphaXiv discover + web search)
- 2610.09367, "Network Coding Can Beat Routing in Undirected Multiple-Unicast Networks" (Toronto, Tsinghua; 7 Oct 2026): an independent counterexample (per search summary: admits binary linear network coding; max degree 3 family with polylog advantage). Same day as 2610.10108. Not read in full by us.
- 2610.20079 (Undirected Network Coding and Faster External-Memory Integer Sorting, 14 Oct 2026) and 2610.33655 (24 Oct 2026) from the same Toronto/Tsinghua group: follow-ups. Not read.
- 2608.06042, 2608.06070 (Aug 2026, "Session interaction framework", "Beyond cut metrics"): pre-refutation attempts at the conjecture. Not read.
- 2510.18737 / FOCS 2025 (Braverman, He): earlier undirected multicast gap via locally decodable codes, which refuted a stronger version.
- The paper itself cites the OpenAI "Finite tensor savings and exact Fourier circuits" (25 Sep 2026) as implying a refutation too; that preprint was not found in the search results and was not opened.
- A "Breakthrough Tracker" page (kingy.ai) rates the result provisional / not peer reviewed and says the checker is author-supplied, not independently replicated (secondary source, unverified). MathWorld (Li-Li Conjecture page) lists the 182/735/157 counterexample.
- Background (not re-read): Li-Li 2004; Harvey-Kleinberg-Lehman 2004/2006; Adler-Harvey-Jain-Kleinberg-Lehman 2006; Jain-Vazirani-Yuval 2006; Braverman-Garg-Schvartzman 2017.
Conclusion: refutations are not new in this window (two independent same-day papers exist); this recheck adds only independent computation of one of them. No independent replication of the Princeton verifier was found.

## Controls (run first, `logs/controls.log`, `data/controls.json`; ALL PASS)
- P1 butterfly (directed): GF(2) XOR code decodes all 4 inputs at rate 1; our LP gives routing max concurrent rate 0.5.
- P2 undirected: 4-cycle with 2 opposite sessions LP = 1.0 (= edges/sum dist); single edge = 1.0; path with 2 sessions = 0.5.
- N3 field: t^2 = 0 and t^2 = 1 versions fail the field checks; the true field passes all.
- N1 tampered R (restore edge 7, delete edge 0): 2 vertices violate d-=d+=5, and 20/20 causal trials fail.
- N2: renormalising (lambda,mu) at all neighbours of one vertex (the paper says not to): 20/20 trials fail decoding; scaling one local-code row by theta: 17/20 fail (3 pass by chance, e.g. input-dependent); adding 1 to one transmitted symbol: 20/20 fail. (An earlier version of the renormalisation control touched only one neighbour and passed; that was a flaw in the control, replaced; the log of the final run is reported.)

## Headline results (`logs/main.log`, `data/main_results.json`)
- A1 GF(9) tables: associativity, distributivity, commutativity, inverses, no zero divisors, cyclic order 8, char 3: all exact, PASS.
- A2/A3: T = all 91 normalized projective points; |V|=182, 10-regular, |E|=910; any two points share exactly 1 line, any two lines exactly 1 point; girth 6 (no 4-cycles): PASS.
- A4: |R|=175 distinct indices in range, C and J disjoint 9-subsets of R, |B|=157, pi a permutation of 0..181: PASS (also a check that the transcription is consistent).
- A5: |E| after deletion = 735; d-(v)=d+(v)=5 and d+_C(v)=d-_J(v) at all 182 vertices (counted on the full 910-edge orientation): PASS.
- A6: every vertex local code has dimension 5 and is MDS (all 252 five-subsets of the 10 incident positions independent) at all 182 vertices.
- A7: exact Gaussian elimination over F9 on the 910x910 parity matrix: rank 744, dim W = 166 exactly (paper needs >= 166); dim W_C = 157; restriction of W_C to the B coordinates injective (rank 744 of the 744 physical+J columns), so W_C ~ F9^157.
- A8: 1000 random input tuples in F9^157 through the pi-ordered interpolation: 1000/1000 have exactly 5 known independent values at every vertex, produce an assignment in W, and every sink t_q outputs x_q. Also all 157 unit-vector inputs pass (linearity then gives all inputs). Tier X for the random sampling, C for the exact rank/injectivity argument it follows from.
- A9: BFS distances for the 157 sessions in G: all exactly 5 (min 5, sum 785).
- A10: 735 < 785 = 157*5; 735/785 = 147/157 (Fraction arithmetic).
- A11 (Tier X, floating HiGHS): undirected unit-capacity max concurrent flow LP on G with the 157 sessions (grouped by source into 66 commodities): optimum 0.9363057324840819 vs 147/157 = 0.9363057324840764 (ratio 1 + 5.8e-15): the fractional multicommodity optimum equals the distance bound, not merely below it. The rational bound 147/157 itself is exact (A10); the LP optimum is floating-point and no exact rational dual from the solver was checked (the length function l_e = 1 is an exact dual certificate for the upper bound 147/157 only).
Together: a code with common rate 1 per session (one F9 symbol per edge, 735 symbol transmissions) versus fractional flow <= 147/157, assuming the paper's capacity/pipelining model (Tier L).

## Not checked / caveats
- Authors' verifier/simulator not run; the paper's repo not fetched.
- The paper's analytic proofs (the dimension argument of Appendix B, identity (1) via power sums) were not re-derived; their conclusions (dim >= 166, decodability) were verified computationally on this instance only.
- Section 3 non-deterministic example (166/744/830) not recomputed.
- The throughput model (rate 1 via pipelining executions, capacity of an undirected edge shared between directions), the identification with the Li-Li/HKL conjecture's exact statement, the amplification theorem and Corollary 1.2: Tier L, unchecked.
- R and pi are as I transcribed them from extracted text; consistency checks (A4, A5, A7-A9 passing) make a transcription error essentially impossible, but an auditor should re-extract them from the PDF.
- Related OpenAI paper not opened.

## Tiers
C: A1-A7, A9, A10 (exact finite-field/graph/rational computations). X: A8 random-input simulation, A11 floating LP. L: refutation of the conjecture in the intended model, pipelining, amplification.

## Hashes of the construction
See `result.json` ("construction_hashes"): T, 910 candidate edges, 735 physical edges, R, pi, C, J, local evaluation matrices, local parity checks, session endpoint pairs.

## Auditor should redo
Re-extract R, pi, C, J from the PDF; run the authors' verifier separately (check its licence); independently recompute dim W with a different field implementation (e.g. Sage/GAP `GF(9)`); solve the LP exactly (rational) or verify the length-function dual; read the capacity/rate model and 2610.09367; read the OpenAI preprint.
