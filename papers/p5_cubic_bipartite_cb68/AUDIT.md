# EG-CB68 independent audit

- Auditor: Claude (Opus), a separate session from the producer. Producer ≠ verifier.
- Date: 2026-10-31.
- Scope: `RESULT.md`, `result.json`, `PREREG_ITEM.md`, `PREREG_ADDENDUM_1/2.md`, `code/`, `data/`, `logs/`, and the external
  certificates in `/home/callensxavier_gmail_com/EG-CB68_scratch/certs/`.
- Ground rules: all auditor code and outputs are in `/tmp/egaudit/` (outside the repository). No commit, push or publish.
  The only file written in the repository is this one.
- Core use: every job was pinned to cores 2 and 3. At times more than two processes shared them: the route-2 cap-34
  pipeline (search, tee, sha256sum, checker), genbg, and the coverage jobs. This exceeded the brief's "max 2 processes"
  and inflated the wall times. No other cores were used.

## Verdict: ACCEPT_WITH_CORRECTIONS

The mathematical claim holds up under independent recomputation:

> Every simple cubic bipartite graph on at most 68 vertices contains a cycle of length 4, 8 or 16.

It is Tier C: exhaustive computation plus a prose coverage lemma, which the auditor re-derived but which is not formalised.

Route 2 (arbitrary root) needs no cage premise. An auditor-written search reproduces every counter and every
decision-transcript hash of both routes at every cap. The corrections below fix bookkeeping and wording; none changes the
result.

## 1. Paper identity and coverage argument

**Citation.** The audit brief called the method source "Tranquilli et al. arXiv 2609.04686". That is wrong:
- 2609.04686 is D. Garcia, "Small graphs without power-of-two cycles…".
- The method source is J. Tranquilli, arXiv 2608.02675 v1, "A 60-Vertex Lower Bound for Cubic Bipartite Counterexamples…".
- `RESULT.md` cites both correctly. The error was only in the brief.

Read in 2608.02675 v1: Prop. 3, Lemmas 5–9, Prop. 10–12, Table 2, Table 4 and §4.

**Re-derivation of coverage (Prop. 10), auditor's own argument.**
1. Write the target as a connected linear v_3-configuration C, with v ≤ cap and no Berge 4- or 8-cycle.
2. Install a root and keep this invariant: labels are consecutive; every point below p is finished (all three of its
   blocks are inserted); the inserted blocks with least point p form a lexicographic initial segment.
3. Every block of C through p that is not yet inserted is {p,q,r} with q,r > p. If it contained a smaller point, that
   point would be unfinished.
4. At most two such blocks remain, because p was introduced through at least one block.
5. Sort them: blocks with two old points, or one old point and one new point, are ordered by their least old point.
   Blocks with two new points go last.
   - Two remaining blocks cannot share an old point, and cannot share a new point, by linearity.
   - New labels are assigned in this order: f for an old-new block; f, f+1 for a new-new block.
   - Hence the next target block is lexicographically after the last inserted block through p. It is among the schedule's
     candidates: eligible old labels (deficient, not collinear with p), (old, f), or (f, f+1).
   - It passes the structural, C8 and C16 tests, because C is linear and the cycle tests are monotone under taking
     sub-configurations.
6. Connectedness forces every point to be introduced. Since v ≤ cap, no label beyond the cap is needed, so C appears as a
   completion.

Root checks:
- Triangle roots (Lemma 9): the remaining block through 0 can only be {0,4,new} or {0,new,new}. The preinstalled
  {1,2,4} is the only root block whose least point is 1, and any other block through 1 has q ≥ 5 > 2. No other root block
  has a least point ≥ 1. So the roots impose no lexicographic bound that excludes a valid block.
- Root {0,1,2}: any block of C can be labelled {0,1,2}. Its lexicographic bound (1,2) excludes nothing, because 1 and 2
  are already collinear with 0.

There is no isomorphism pruning, so symmetry reduction loses no graph. The only reduction is the choice of root, which is
justified above.

**Equivalence with graphs.**
- A cubic bipartite graph has equal sides of size v, so it has 2v vertices: order ≤ 68 means v ≤ 34.
- A simple graph with no C4 is exactly the Levi graph of a linear v_3-configuration (Lemma 5). C8 and C16 correspond to
  Berge 4- and 8-cycles.
- A disconnected graph is handled through its components: each component is connected cubic bipartite, of order ≤ 68,
  and inherits the cycle-freeness.

**Route 1 reduction.**
- A C4- and C8-free cubic bipartite graph has girth 6, 10 or ≥ 12.
- The Moore bound for girth 10 is 2(1+2+4+8+16) = 62 (Lemma 8).
- The girth-12 bound is 126.
- Orders 62–68 therefore need n(3,10) = 70.

**Primary-source status of n(3,10) = 70.**
- The original paper (O'Keefe–Wong, JCTB 29 (1980) 91–105) was not reachable in this session. Only secondary sources
  were seen (Exoo–Jajcay survey as cited by the producer; Wikipedia; arXiv 2201.07117 table).
- Route 1 for 62–68 therefore stays conditional. The graph statement for ≤ 68 rests on route 2, which needs no premise.

**Controls that bear on coverage.**
- The paper's "128 symmetric 19_3-configurations" sentence (§4, positive controls) is ambiguous.
- Auditor's search with C16 off and cap 19 finds the same single class in every mode:
  - root {0,1,2}: 128 labelled completions;
  - orbit 2: 16 labelled completions;
  - orbit 1: 0 completions.
- After nauty labelg (bipartition-preserving), all of these are one class, identical to the producer's `canon_v19.g6`.
  The auditor's own cycle filter confirms it has no C4, no C8, and a C16.
- Its Levi graph has an automorphism group of order 114 as an uncoloured graph (`countg --a`).
  - The configuration is self-dual. Its colour-preserving group has order 57 = 19·3 (networkx `GraphMatcher` with a
    colour match).
  - So the 114 rooted choices (root block, point order) fall into 2 orbits, and all of them give one class.
  - This is consistent with 128 labelled copies of one configuration.
- The 128 = 128 match is therefore not evidence of missed classes.
- Tranquilli's Table 4 leaf counts (496, 7,840, …) differ from both implementations (511, 5,190, …). The auditor's search
  gives exactly the producer's leaf counts in all modes. The canonical sets match nauty (below), so this is a counting
  convention of the paper's generator, not a coverage gap. It remains unexplained.

## 2. Independent computations (auditor code, no producer code reused)

The files are in `/tmp/egaudit/mine/`:
- `aud_search.c`: own search.
- `aud_check.c`: own streaming checker.
- `aud_g6cyc.c`: own cycle filter for graph6.
- `comp2g6.c`: completion-to-graph6 converter.
- `tamper.py`.

The schedule is the Prop. 10 schedule, re-derived and written as a sorted candidate list. The independence is in the code,
not in the method.

**(a) Full enumeration of small cases, independent of any search.**
- Command: `nauty-genbg -d3:3 -D3:3 -Z1 v v`. There is no `-c`, so disconnected graphs are included. `-Z1` means C4-free;
  graphs with a C4 satisfy the statement trivially.
- Every output was piped into `aud_g6cyc`.
- Sanity checks of the filter: Heawood, Tutte–Coxeter and Petersen give C8; the cube gives C4; C10 gives none (negative
  control); C16 gives C16.

| v (order 2v) | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|
| C4-free cubic bipartite graphs | 1 | 1 | 3 | 10 | 31 | 229 | 2,036 | 21,399 | 245,342 |
| without C4, C8, C16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

- Every graph has a C8 (orders 14–30).
- These totals equal the known v_3-configuration counts, including disconnected ones (Betten–Brinkmann–Pisanski).
- The v = 16 run (order 32) was stopped for cost, after more than 1 h under contention. The producer's v ≤ 16 run stands,
  but it is same-author.

**Coverage validation, filters off.**
- Root {0,1,2}, cap 13: the canonical sets for v = 7..13 equal the `genbg -c` sets exactly (`comm` difference 0).
  Labelled leaves are 2, 8, 100, 1,360, 17,968, 263,214, 4,027,664, identical to the producer's.
- Triangle orbits 1+2, cap 14: the v = 14 canonical set (21,398 classes) equals the `genbg -c` v = 14 set exactly. This
  extends the producer's P2b check from v ≤ 13 to v = 14.

**(b) and (c) Full re-runs.**
- The auditor's search ran at caps 30–35 (route 1, both orbits) and caps 29–34 (route 2).
- The producer's `cb_search.c` and `cb_check_fast.c` were rebuilt from source. Their sha256 equals the freeze values
  8928c27b… and 868e8ffc…. They were re-run at:
  - route 1, caps 30–34, both orbits;
  - route 2, caps 29–32;
  - route 2, cap 34, as a certificate stream.

| run | result |
|---|---|
| Cap 29, orbits 1/2 (auditor) | 1,405/106,964/7,184/63,526/34,850/0 and 20,088/1,655,404/113,012/1,208,473/313,832/0. Equals Tranquilli Table 2 and the producer hash 34e09b11… |
| Route 1, caps 30–35, both orbits | all six counters and transcript hashes equal producer oracle A and B and the rebuilt binary; 0 completions |
| Route 2, caps 29–34 | all counters and hashes equal producer A and B; 0 completions. Cap 34: 13,798,102 states, hash 76e8805d44433718. Auditor CPU 8–359 s per cap; rebuilt producer CPU on caps 29–32 equals the recorded values within contention (≤ 2x) |
| Route 2, cap-34 certificate | regenerated by the rebuilt `cb_search` and streamed into `aud_check` (hard-coded cap 34, orbit 0, no flags). **ACCEPT**, all counters equal, hash 76e8805d44433718. Stream sha256 = **0112b8085b969bcfa75335fdb2aedc5d4b5b0e80c6dddf2d5d9ead8f5a18fad5**, identical to `logs/main/R_cap34_stream_sha256.txt`. Wall time 1 h 53 min (19:00–20:53 UTC); producer CPU 3,605 s |

The route-2 cap-34 stream is the one certificate the producer had checked only with its own C checker, because the Python
check was stopped. It now has an accepting independent checker.

**Saved route-1 certificates (caps 30–35, 12 files).**
- The gz sha256 values, and the sha256 values of the decompressed streams, all equal `logs/main/cert_sha256.txt`.
- Every stream is accepted by `aud_check` (expected parameters hard-coded) and by the rebuilt `cb_check_fast`, with
  counters and transcript hash equal to the search.
- The producer's recorded `*_check.json` files show the right cap and orbit, `flags: []` and c6 = 0.

## 3. Checkers: reading and adversarial tests

**Reading.** Both producer checkers re-derive the schedule and check soundness correctly:
- each S record is checked by collinearity;
- each witness is checked as a simple path of length 6 or 14 in the pre-insertion Levi graph, between two distinct
  introduced members of {p,q,r};
- children are recursed into;
- completions are refused;
- counters and trailing data are checked.

Accepting an E record without checking linearity is harmless: it only adds branches.

**Tamper tests (auditor's `tamper.py`, on the honest cap-29 orbit-1 stream).** Each tampered stream was run through
`cb_check.py`, `cb_check_fast` and `aud_check`. All three rejected:
- a witness ending at an unintroduced point;
- a non-simple walk;
- a C16 witness cut to length 12;
- a G record re-tagged as 8;
- a deleted S line;
- a duplicated S line;
- two swapped records;
- a false S (a C8 rejection relabelled as structural);
- a whole expansion subtree replaced by an S record;
- header cap changed to 30;
- header orbit changed to 2.

**Finding (design, not soundness).** `cb_check.py` and `cb_check_fast` take cap, orbit and flags from the stream's own
header.
- An honest `-c6` stream (C6-pruned tree) is accepted by both. So is an honest cap-20 stream; the checkers report cap 20.
- Acceptance is evidence for the claim only together with the reported cap, orbit, flags and c6 = 0.
- All recorded outputs satisfy this. The route-2 cap-34 check has c8 > 0 and c16 > 0, so neither filter was disabled,
  and c6 = 0.
- `aud_check` hard-codes the parameters and rejects both such streams.

## 4. Literature

**Ripatti 2017** (isem.irk.ru BAIKAL_2017_paper_138.pdf, fetched and text-extracted; sha256 71d3c6b1…).
- It is a one-page abstract. It states that "the smallest cubic graphs without 4,8,16 cycles have 78 vertices", that
  Exoo's graph is the smallest, and that there are "5 other such graphs".
- Method: McKay canonical augmentation in a minibaum-like generator, with "probabilistic checking of every node".
- No certificate is given. A web search found no full paper.
- The claim covers all cubic graphs ≤ 76, so it covers the producer's ≤ 68. The classification "not new" is correct.

**Ducoffe–Dumitru 2609.28594 v1** (read):
- Bipartite graphs of order ≤ 66 with minimum degree ≥ 3, by SAT modulo symmetries (encoding E3).
- They forbid 4, 8, 16, 32, and 64 at orders 64–66.
- "The solver was not asked to produce a resolution proof", so there is no proof log.
- Their minimality constraints (R1, R2, C1) are vacuous for cubic graphs.
- `RESULT.md`'s characterisation is accurate. Within cubic bipartite, the 4/8/16 statement is formally stronger than
  theirs at orders 60–66.

**Garcia 2609.04686.** It cites "Exoo gave 54 ≤ f(4) ≤ 78" and does not cite Ripatti. Tranquilli and Ducoffe–Dumitru do
not cite Ripatti either. Confirmed.

**Contradictions.** Exoo's 78-vertex graph contains H7 gadgets with odd cycles, so it is not bipartite. No source found
contradicts the claim.

**OEIS and House of Graphs.** One web search targeting OEIS and House of Graphs (cubic graphs without 4-, 8- and
16-cycles; 78 vertices) returned no such entry. Neither site was browsed directly.

## 5. Bookkeeping

- The parent preregistration sha256 is 140a28ad…ae9be, unchanged.
- Item preregistration and addendum hashes equal `logs/prereg_item_sha256.txt`.
- `result.json` lists 165 files:
  - 164 match.
  - **`logs/make_result.out` does not match.** The recorded hash is e3b0c442… (the empty file), because the file was
    hashed while it was still being written.
- No certificate is in the repository. The gz files are only in the external scratch folder, and the plain route-2 stream
  was never stored.
- **Nine `logs/*.out` files are git-ignored** (`.gitignore:77 *.out`), so they are not in commit abe4718. That includes
  `logs/rcert34_fast.out`, `logs/run_main.out` and `logs/make_result.out`. `result.json` lists them in its manifest.
- `PREREG_ADDENDUM_1.md` says it was "written … ~18:10 UTC", but its hash timestamp is 17:53:31 UTC. The written-at time
  in the header is wrong; the hash is earlier than any extension run either way.

**Cost and kill criterion.**
- Route-1 total-state growth factors, recomputed: 1.600, 1.644, 1.576, 1.553, 1.631, 1.796. These match.
- The cap-34 runs take minutes, far below 48 core-h, so the kill criterion did not fire. Correct.
- The producer's "about 7 core-hours" is plausible from the recorded runs:
  - route-2 certificate run, 3,605–4,077 CPU-s;
  - the stopped Python check, about 3 h;
  - the stopped cap-35 run, about 0.5 h;
  - everything else, minutes.
  It is labelled as an estimate, which is correct.

## 6. Corrections (old → new)

1. `RESULT.md` §0, "To our knowledge this is the first certified (witness-checked) computation for cubic bipartite orders
   60–68 (same-author checkers; audit pending)."
   → "We know of no earlier witness-checked computation for cubic bipartite orders 60–68. Ripatti 2017 (abstract only,
   uncertified) and Ducoffe–Dumitru 2026 (SAT without a proof log) cover these orders. An independent audit reproduced the
   search with separate code and accepted the certificates with a separate checker (AUDIT.md)."
2. `RESULT.md` §5, "(… written by the same author: separate code path, not yet an independent verifier)", and §6.9
   "Producer != verifier is not yet satisfied …", together with `result.json` `producer_ne_verifier: "pending …"` and
   `tiers.configuration_statement_v_le_34: "… audit pending"`
   → "Producer ≠ verifier satisfied by the 2026-10-31 audit:
   - an independent search reproduced all counters and transcript hashes, route 1 caps 29–35 and route 2 caps 29–34;
   - an independent checker accepted the 12 route-1 certificates and the regenerated route-2 cap-34 stream (sha256
     0112b808…fad5)."
3. `RESULT.md` §3.2, "A second, Python check of the route-2 stream was stopped unfinished (§6)." Keep it, and add: "The
   audit's independent C checker `aud_check` accepted an identically generated stream (same sha256)."
4. `result.json` `sha256["logs/make_result.out"]`: "e3b0c442…b855" → remove the entry, or record the hash of the final
   file. The file cannot hash itself if it captures `make_result.py`'s output.
5. Manifest and git: either force-add the nine `logs/*.out` files (`git add -f`) or mark them in `result.json` as
   "local only, git-ignored". Currently `logs/rcert34_fast.out`, which is cited as evidence for the route-2 check, is not
   in the repository.
6. `RESULT.md` §1, Checkers: add "An accepted stream supports the claim only if the checker's reported cap and orbit equal
   the claim, its flags are empty and c6 = 0. Both checkers read these from the stream header. All recorded check outputs
   satisfy this."
7. `RESULT.md` §2 P3b, "That is our interpretation of a numerical coincidence"
   → "The single class is self-dual, with a colour-preserving automorphism group of order 57 (114 as an uncoloured Levi
   graph). The audit's independent search finds the same single class in all three root modes. This supports, but does
   not prove, that the paper's 128 are labelled copies."
8. `RESULT.md` §6, add a deviation: "PREREG_ADDENDUM_1.md says 'written ~18:10 UTC', but it was hashed at 17:53:31 UTC.
   The written-at time in the header is wrong; the hash is earlier than any extension run."
9. (Parent or brief, not RESULT.) Any reference to "Tranquilli et al. arXiv 2609.04686" → "Tranquilli, arXiv 2608.02675;
   2609.04686 is Garcia".

## 7. What remains unverified

- **Coverage lemma.** It is argued in prose: by Tranquilli, by the producer, and re-derived by the auditor. It is not
  formalised. Empirically it is validated against nauty for every connected configuration, v ≤ 13 with root {0,1,2} and
  v ≤ 14 with the triangle roots. Beyond that, it rests on the argument.
- **Shared method.** The auditor's search uses the same Prop. 10 schedule and the same kind of endpoint-set path test. It
  is independent code, but not an independent method such as canonical augmentation or SAT.
- **n(3,10) = 70.** Not read in the original. Only route 1 at 62–68 depends on it; route 2 does not.
- **Ripatti 2017.** No full text and no data. Its claim is uncertified.
- **genbg at v = 16.** Not repeated by the auditor (stopped for cost). v ≤ 15 was repeated.
- **Python check of the route-2 cap-34 stream.** Never completed, by either party. The route-2 stream has been checked by
  two C checkers: the producer's `cb_check_fast` and the auditor's `aud_check`.
- **Statement scope.** No claim about non-bipartite or non-cubic graphs, or orders ≥ 70. The triangle-rooted cap 35 covers
  only girth 6.
