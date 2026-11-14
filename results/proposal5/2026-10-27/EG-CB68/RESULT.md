# EG-CB68 (Proposal 5, lane W1-c): cubic bipartite Erdős–Gyárfás check up to 68 vertices, a certified re-check, not a new bound. Producer report, unaudited

**Outcome: KEEP, class (d): an independent certified re-check, not a new bound.** We use LR-IND's wording.
- Every preregistered cap closed. The kill criterion never fired.
- The preregistered novelty claim (order 68 new) is **killed** by a prior claim that the same-day re-search on 2026-10-31
  found (below).

> Every simple cubic bipartite graph on at most 68 vertices contains a cycle of length 4, 8 or 16. Hence a cubic
> bipartite counterexample to the Erdős–Gyárfás conjecture has at least 70 vertices.

**Prior claim (kills the novelty).**
- A. V. Ripatti, "Faster approach for exhaustive search over graphs with certain properties", abstract, BAIKAL/MOTOR 2017
  (isem.irk.ru/conferences/mopt2017/Abstracts/BAIKAL_2017_paper_138.pdf). Read in session: the full one-page abstract.
- It states: "computationally show that the smallest cubic graphs without 4,8,16 cycles have 78 vertices".
- That claim covers **all** cubic graphs on at most 76 vertices, bipartite or not, so it covers our statement (≤ 68) and
  the planned extension (≤ 72).
- It is an abstract only. We found no full paper. The method uses "probabilistic checking of every node of the search
  tree", and no certificate is reported.
- Tranquilli (2608.02675), Ducoffe–Dumitru (2609.28594) and Garcia (2609.04686, who writes "Exoo gave 54 ≤ f(4) ≤ 78")
  do not cite it. The preregistration's novelty check missed it too.

**What this item therefore is:** an **independent, certificate-producing re-check, in the cubic bipartite class, of
uncertified computations**:
- Ripatti 2017, all cubic graphs ≤ 76: abstract only, probabilistic node checks.
- Ducoffe–Dumitru 2026, bipartite ≤ 66: SAT without a proof log. Their search forbids every power-of-two length (4, 8,
  16, 32 and, at 64–66, 64) and assumes minimality reductions. Our statement forbids only 4, 8 and 16, so for cubic
  bipartite orders 60–66 it is formally stronger than theirs, but not stronger than Ripatti's claim.

Tranquilli's certified result stops at 58. To our knowledge this is the first certified (witness-checked) computation for
cubic bipartite orders 60–68 (same-author checkers; audit pending). It is a re-check, not a new bound.

How each part is established:
- **Configuration statement** (no connected linear v_3-configuration with v ≤ 34 avoids Berge 4- and 8-cycles):
  **Tier C**, by exhaustive search plus separate witness checkers. The checkers are a separate code path by the same
  author; producer ≠ verifier is still pending the audit.
  - Route 1 (preregistered): Tranquilli's triangle-rooted search (arXiv 2608.02675 v1, §3), caps 30–34. Every certificate
    is accepted by the Python streaming checker.
  - Route 2 (cross-check, no Berge triangle assumed): arbitrary root, cap 34. Oracles A and B give identical transcript
    hashes, and the C checker `cb_check_fast` accepts the full certificate stream (sha256 recorded). A second, Python check
    of the route-2 stream was stopped unfinished (§6).
- **Graph statement.** For graphs on at most 60 vertices: route 1 plus Tranquilli's Moore lemma.
  - For 62–68 vertices, route 1 additionally needs the Tier L premise n(3,10) = 70 (O'Keefe–Wong 1980, computer-assisted),
    read in the Exoo–Jajcay Dynamic Cage Survey (EJC DS16 v3, p. 7 Table 1, p. 10 §2.1.6), not in the original.
  - Route 2 needs no Moore or cage premise.

## 1. Method (as run)

- **`code/cb_search.c`** is a new C implementation written only from the paper's text (§3.1, Lemmas 5–7, Prop. 10). We did
  not open Tranquilli's repository. The search:
  - installs roots {0,1,3}, {1,2,4}, {0,2,5}, plus {0,4,6} (orbit 1) or {0,6,7} (orbit 2), or, in arbitrary-root mode,
    only {0,1,2} (orbit 0);
  - processes the least unfinished point p;
  - proposes {p,q,r} in lexicographic order, lexicographically after the last block through p whose least point is p.
    q and r range over eligible old labels (> p, degree < 3, not yet paired with p) or the next one or two fresh labels,
    within the cap;
  - rejects a proposal in this order: structural (q and r already share a block); C8 (a simple Levi path of length 6
    between two old points of the block); C16 (length 14);
  - records a completion as soon as every introduced point has degree 3.
- **Two oracles.** Oracle A computes DFS endpoint sets, cached per state. Oracle B joins complete lists of half-paths
  (length 3 or 7) per pair, uncached. Both produce the same FNV-1a hash of the ordered decision transcript in every run
  where both were run.
- **Checkers.** Witnesses come from a third small DFS.
  - `code/cb_check.py` (Python) and `code/cb_check_fast.c` (C, same rules) search for nothing.
  - They re-derive the proposal schedule as a sorted, filtered candidate list (a different formulation from the nested
    loops in `cb_search`).
  - They check every structural rejection directly, and check every C8/C16 witness as a simple path of the right length
    in the pre-insertion Levi graph between two distinct introduced members of the block.
  - They recurse into expansions, reject any completion, and recompute all counters against the END line.
  - Accepting a proposal needs no proof (it only enlarges the tree), so soundness rests on the rejections being witnessed
    plus the schedule being the Prop. 10 schedule.
- **Coverage argument.** This is Tranquilli Prop. 10. We re-derived it, including the lexicographic constraint with fresh
  labels: unseen points get the next labels; old-old blocks through p are distinct in their second point by linearity;
  and fresh-fresh blocks sort last. The arbitrary-root variant uses the same argument with root {0,1,2}, which is the
  lexicographically first block through 0 under first-occurrence labelling. **The argument is not formalised.** An auditor
  must re-derive it.
- **Reduction (route 1).**
  - With no C4 and no C8, a bipartite cubic graph has girth 6 or girth ≥ 10.
  - Girth ≥ 10 needs ≥ 62 vertices (Moore, Tranquilli Lemma 8).
  - Girth exactly 10 needs ≥ 70 vertices: n(3,10) = 70, Tier L.
  - Girth ≥ 12 needs ≥ 126 vertices (Moore).
- Frozen binaries: `logs/freeze_sha256.txt`. gcc 11.4.0 with `-O3 -march=native`. All runs used `taskset -c 2` or `-c 3`.

## 2. Controls (run before any headline number)

| id | control | result | pass |
|---|---|---|---|
| P1 | Cap-29 counters vs Tranquilli Table 2, orbit 1 (states, attempted, structural, C8, C16, completions) | 1,405 / 106,964 / 7,184 / 63,526 / 34,850 / 0. Identical | yes |
| P1 | Same, orbit 2 | 20,088 / 1,655,404 / 113,012 / 1,208,473 / 313,832 / 0. Identical | yes |
| P1 | 19-block states (paper §3.3: 337) | 46 + 291 = 337 (depth histogram) | yes |
| P1 | Oracle A vs B, cap 29 | same counters, same transcript hashes | yes |
| P1 | Python checker on the cap-29 certificates | accepted, counters equal | yes |
| P2 | C8 and C16 filters off: canonical classes for v = 7..13 (nauty labelg, bipartition kept) | 1, 1, 3, 10, 31, 229, 2,036 in triangle-rooted mode and again in arbitrary-root mode | yes |
| P2b | Set equality with `nauty-genbg -c -d3:3 -D3:3 -Z1`, v = 7..13 | all 7 sets equal | yes |
| P2c | genbg plus an independent DFS cycle filter (`g6_cycles.c`), v = 7..16 | 0 C4/C8-free configurations up to v = 16 (21,398 / 245,341 / 3,004,877 connected ones at v = 14/15/16 all contain C8), as our search says | yes |
| P3 | C16 off, cap 19, triangle roots | completions exist: 16 labelled, **1** isomorphism class (v = 19), which is C4/C8-free with a C16 (independent check). None at v < 19 | yes |
| P3b | Same in arbitrary-root mode | **128 labelled leaves**, 1 class. This is consistent with the paper's "128 symmetric 19_3-configurations" being 128 labelled copies of one configuration. That is our interpretation of a numerical coincidence | yes |
| N1 | C8 filter off, C16 on, cap 13 | completions appear: the Fano plane (v = 7), the only class | yes |
| N2 | C8 filter on, cap 8 (orbits 0, 1, 2) | 0 completions; with it off, Fano (v = 7) and 8_3 (v = 8) appear, and the checker accepts with completions allowed | yes |
| N2 | Heawood graph (networkx-only script) | isomorphic to `nx.heawood_graph`; girth 6; 21 eight-cycles; the C8 test rejects the last Fano block | yes |
| N3 | Tamper tests: truncated stream, flipped counter, corrupted C8 witness, wrong-length C16 witness, C16 relabelled as structural, deleted record, trailing data, inserted fake completion | all 8 rejected by `cb_check.py` and by `cb_check_fast` | yes |

Not matched, and not preregistered:
- Tranquilli's Table 4 "rooted/labelled leaves" (1, 4, 44, 496, 7,840, …). Our triangle-rooted leaves are
  1, 4, 44, 511, 5,190, 60,231, 752,362; our arbitrary-root leaves are 2, 8, 100, 1,360, …. Their leaf counts come from a
  generator whose conventions the paper does not describe. Only the canonical counts were preregistered, and those match.
- The `structural_alt_extra` diagnostic counter is unused.

Deviation in the controls: the first N2 run used cap 7, which `cb_search` refuses (minimum cap 8, "bad args"). The
`N2_cap7_*` files record that failure. N2 was rerun at cap 8.

## 3. Headline

### 3.1 Route 1: triangle-rooted, caps 30–34 (preregistered)

Counters are states, attempted, structural, C8, C16, completions. Every row: oracle B transcript hash equal to oracle A,
Python checker accepted.

| cap (order 2·cap) | orbit 1 | orbit 2 |
|---|---|---|
| 30 (60) | 2,247 / 197,766 / 13,106 / 115,032 / 67,382 / **0** | 32,153 / 2,838,956 / 187,816 / 1,992,302 / 626,686 / **0** |
| 31 (62) | 4,011 / 403,911 / 26,046 / 233,736 / 140,119 / **0** | 52,541 / 5,024,144 / 321,347 / 3,394,496 / 1,255,761 / **0** |
| 32 (64) | 7,112 / 742,895 / 46,650 / 411,221 / 277,913 / **0** | 82,021 / 8,648,052 / 528,841 / 5,649,649 / 2,387,542 / **0** |
| 33 (66) | 12,377 / 1,417,878 / 86,955 / 737,586 / 580,961 / **0** | 126,017 / 14,700,719 / 858,762 / 9,284,478 / 4,431,463 / **0** |
| 34 (68) | 23,143 / 2,972,750 / 180,011 / 1,424,785 / 1,344,812 / **0** | 202,602 / 25,227,209 / 1,432,521 / 15,207,779 / 8,384,308 / **0** |
| 35 (70) | 51,974 / 7,282,166 / 441,386 / 3,199,099 / 3,589,708 / **0** | 353,357 / 47,941,559 / 2,696,312 / 27,114,667 / 17,777,224 / **0** |

- At cap 35 the triangle-rooted search covers only girth-6 graphs. The three (3,10)-cages lie outside it; see §4.
- **Kill criterion.** The growth factor in total states was 1.60 at cap 30 and 1.64 at cap 31; the factors for caps 32–35
  were 1.58, 1.55, 1.63 and 1.80. The cap-34 runs took 5.4 CPU-s (orbit 1) and 43.3 CPU-s (orbit 2) with oracle A including certificate writing, and 2.0 s and 13.5 s with oracle B. That is far below 48 core-h, so the
  kill criterion did not fire.
- Certificates (gzip, about 129 MB in total) are kept outside the repository in `/home/callensxavier_gmail_com/EG-CB68_scratch/certs/`.
  `logs/main/cert_sha256.txt` records the sha256 of each one, plain and gzipped.

### 3.2 Route 2: arbitrary root (no triangle assumed), caps 29–34

Columns: states, attempted, structural, C8, C16, completions. The transcript hashes of oracle A and oracle B are equal at
every cap. CPU-s are single-core runs without a certificate.

| cap (order) | counters | CPU-s A / B |
|---|---|---|
| 29 (58) | 656,769 / 62,551,453 / 4,349,082 / 41,493,681 / 16,051,922 / **0** | 5.3 / 29.5 |
| 30 (60) | 1,221,044 / 123,345,322 / 8,394,650 / 82,188,835 / 31,540,794 / **0** | 11.2 / 59.4 |
| 31 (62) | 2,286,787 / 250,478,360 / 16,640,536 / 166,568,141 / 64,982,897 / **0** | 20.5 / 121.9 |
| 32 (64) | 4,178,622 / 500,012,963 / 32,156,507 / 328,949,906 / 134,727,929 / **0** | 39.1 / 246.6 |
| 33 (66) | 7,508,537 / 974,464,041 / 60,683,233 / 624,694,002 / 281,578,270 / **0** | 75.3 / 505.6 |
| 34 (68) | 13,798,102 / 1,899,509,410 / 115,596,123 / 1,154,879,407 / 615,235,779 / **0** | 149.8 / 1062.8 |

- **Cap-34 certificate.** It was re-generated by oracle A and streamed through a FIFO into `cb_check_fast`: **accepted**, all
  counters equal (`data/main/R_cap34_checkfast.json`).
  - Stream sha256: 0112b8085b969bcfa75335fdb2aedc5d4b5b0e80c6dddf2d5d9ead8f5a18fad5 (`logs/main/R_cap34_stream_sha256.txt`).
    It is too large to keep: tens of GB.
  - The certificate run's transcript hash (76e8805d44433718) equals that of the plain A run and of the B run.
- **A Python check** ran on an identically generated stream: a separate producer process on core 3 (the same transcript
  hash was expected).
  - It started at 2026-10-31 14:41 UTC and was **stopped unfinished** at 17:34 UTC, after the literature finding (§6).
  - It had read at least 17.5 GB, with no rejection up to then (it aborts at the first error).
  - Its partial stream hash was deleted, so there is nothing to compare.

## 4. Exploratory extension (beyond the parent preregistration)

**Not carried out.**
- Addendum 1 (hashed 2026-10-28 17:53 UTC, before any cap >= 35 arbitrary-root run) and addendum 2 (hashed 2026-10-31
  14:41 UTC, after the outage, still before any such run) allowed arbitrary-root caps 35, 36, ... within the box.
- Cap 35 (order 70) was started at 17:06 UTC on 2026-10-31.
- At 17:34 UTC the producer stopped it, together with the pending oracle-B runs, without any result. The reason: the
  same-day re-search found Ripatti 2017's claim f(4) = 78, which covers every cubic graph up to 76 vertices, so orders 70
  and 72 would also be only re-checks. No output from these runs is used (`logs/stopped_runs.txt`).
- The triangle-rooted cap-35 run in §3.1 (girth-6 part of order 70, Python-checked) was part of `run_main.sh`. It does not
  cover the (3,10)-cages and is not a statement about order 70.

## 5. Tiers and what is not claimed

- Configuration statement for v ≤ 34: **Tier C** (exhaustive enumeration plus separate witness checkers, written by the same author: separate code path, not yet an independent verifier). It is not a
  Lean proof. The coverage lemma is argued in prose.
- Graph statement ≤ 68 vertices: Tier C by route 2 alone. By route 1, Tier C for ≤ 60 vertices and Tier C conditional on
  the Tier L n(3,10) = 70 for 62–68.
- Not claimed: anything about the full Erdős–Gyárfás conjecture, or about non-bipartite or non-cubic graphs. No order is
  new as a bound: Ripatti 2017 claims every cubic graph on ≤ 76 vertices (uncertified), and Ducoffe–Dumitru cover
  bipartite ≤ 66.
- No Lean module was written. The parent marks Lean as optional for the reduction lemma, and the reduction is not needed
  for route 2.

## 6. Deviations

1. The parent assigns the search code to Sonnet; this producer is Opus.
2. Arbitrary-root mode (route 2) and the C checker `cb_check_fast` were added beyond the parent method. Arbitrary-root
   mode went in before the freeze. `cb_check_fast` was added after the freeze, logged in `freeze_sha256.txt`, and
   tamper-tested.
3. The (3,10)-cage premise was read only in a survey, not in the original O'Keefe–Wong paper.
4. N2 cap 7 to cap 8 (see §2). `heawood_c8.py` was fixed twice for networkx-version issues before it ran (logged).
5. The item preregistration (`PREREG_ITEM.md`) was written by the producer, and hashed before the first run.
   - Addendum 1 (extension) was written after the timing probe.
   - Addendum 2 moved the extension's wall-clock deadline after an external API spend-limit outage
     (2026-10-28 about 18:30 to 2026-10-31 14:40 UTC). It was written before any extension run.
6. An exploratory girth-≥10 run (C6 filter, C16 off, arbitrary root) was started and stopped at cap 33 for cost, before
   its result. Only its cap-31 output (0 completions) exists, in a session log. It is not used.
7. The repository guards `antigravity_guard.py` and `test_rigor_guard.py` both exit 1, on pre-existing files elsewhere in
   the repository. Neither flags an EG-CB68 file (`logs/guard_*.txt`). `pytest tests/` was not run.
8. **Novelty check failed.** Neither the parent preregistration nor our 2026-10-28 re-search found Ripatti 2017. The
   2026-10-31 re-search found it (via WebSearch, then read in session), and Garcia 2609.04686 was read for f(4) context.
   The outcome was therefore downgraded from "new bound at order 68" to "certified re-check", and the extension was stopped.
9. Producer != verifier is not yet satisfied. `cb_check.py`, `cb_check_fast.c`, `g6_cycles.c` and `heawood_c8.py` were
   written by the producer, so they are separate code paths, not independent verification. An independent audit is pending.
10. Compute: about 7 core-hours of the 48 core-hour box. This is an estimate from process wall times, not a measurement.
    Cores 2 and 3 only.

## 7. What an independent auditor must redo

1. Re-derive the coverage argument (Tranquilli Prop. 10) for both root modes. In particular, check that the lexicographic
   constraint "after the last block through p with least point p" is complete, given fresh-label assignment.
2. Rebuild `code/cb_search.c` and `code/cb_check_fast.c`. Re-run cap 29 (and compare with Table 2), then caps 30–34 in both
   modes, and compare with `data/main/*.json`.
3. Re-check at least the cap-34 triangle certificates with `cb_check.py`, using the gz files plus the sha256 values in
   `logs/main/cert_sha256.txt`. Read the checker independently, against the soundness conditions in §1.
4. Re-run the controls (`code/run_controls.sh` and `code/run_controls2.sh`), including the tamper tests.
5. Verify the premise n(3,10) = 70 in the original (O'Keefe–Wong, JCTB 29 (1980) 91–105), or rely on route 2 only.
6. Repeat the literature search on the day of any write-up. Try to locate a full version of Ripatti 2017 and its method
   (it uses probabilistic node checks), and confirm that our re-check classification is correct.
