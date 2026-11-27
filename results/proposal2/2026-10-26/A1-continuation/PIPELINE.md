# A1 continuation: resumable L1 pipeline for the remaining certificate stages

Date 2026-10-26. This continues proposal 2 / A1 (published as doi:10.5281/zenodo.23656804). A1 ported 4 of the 12
stages of the claimed Sandier-Serfaty finite certificate to Lean at level **L1**: the kernel re-executes the stage's
C++ interval computation (`decide +kernel`, never `native_decide`) and gets the C++ endpoints bit for bit. This
directory holds the machinery that ports the remaining stages: `cs`, `core_test`, `bdsup`, `inside_hess`,
`global_grid` and `table`, plus the planted controls. A detached scheduler runs it for days.

**L1 is not a proof of the conjecture.** The scope is unchanged from `../A1/CERTIFICATE_PORT.md`: L1 says nothing
about the real quantities (that is L2), and the fidelity of the C++-to-Lean transcription rests on bit equality with
the C++ outputs.

## Layout

| What | Where |
|---|---|
| New Lean sources (A1's 52 locked files are never touched) | `formal_cert/Programmes/SandierSerfatyL1/{Cs,Jet,CoreTest,Grid,Bdsup,InsideHess,GlobalGrid,Table}/` |
| Generators, mirrors, scheduler | `scripts/` (this directory) |
| Work list, one manifest per stage | `manifests/*.json` (the scheduler reads these) and `manifests_pending/*.json` (generated, not yet released) |
| Config, re-read every 10 s | `pipeline_config.json` |
| Summary, regenerated after every finished chunk | `STATUS.md`, `status_summary.json` |
| Per-chunk status (JSON) | `/home/callensxavier_gmail_com/a1l1_oleans/status/<stage>__<chunk>.json` |
| Per-chunk compile log (JSON with Lean output) and scheduler log | `/home/callensxavier_gmail_com/a1l1_oleans/logs/` |
| Olean root of each chunk | `/home/callensxavier_gmail_com/a1l1_oleans/roots/<stage>__<chunk>/` (on /home, not disk 2) |
| C++ dump of everything the new stages need | `/home/callensxavier_gmail_com/proposal2-2026-10-26/A1c/dump2/dump2.txt` (76 MB, sha256 `0b59caac84d6...`) |

### The data: `cpp/dump2_driver.cpp`

This driver is compiled against the **unmodified** corpus headers (`g++ -std=c++17 -O3 -fopenmp`) and run pinned to
cores 0-3 (11 min). It prints:
* the full table: `ts`, `orig`, `pts`, `cels` for all 6,826 nodes;
* the propagation states `pointS`, `cellS`. These are locals of `table()`, so they come from a verbatim copy of the
  propagation loop. Pushing the copy's states back through the corpus `fh()` reproduces the corpus `pts`/`cels` bit
  for bit (`table_replica_mismatches 0`);
* the per-cell `core_test` values and the running maxima;
* row checkpoints of `bdsup` (every 64 inner steps), `global_grid` (every 128) and `inside_hess` (every 64), from
  verbatim copies with prints added. The `bdsup` copy's output equals the corpus `bdsup()`.

`scripts/check_dump2.py` checks the dump against A1's own dump, which was run independently: all 55 common scalars
and all 1,998 old table nodes and cells are bit-identical, and the 22 printed record pairs are reproduced
(`dump2_consistency.json`).

### Gate before any scale-out

Each stage has an exact Python mirror of the C++ (`l1common.py`, `jetmirror.py`, `gridmirror.py`). A generator refuses
to write chunks unless its mirror reproduces dump2 bit for bit on every value it emits:
* cs: all 38 `co[m]`, by brute force and by the band formulation;
* core_test: all 1,886 cells;
* bdsup, inside_hess, global_grid: every C++ checkpoint of every row;
* table: `pts`, `cels`, `pointS`, `cellS` and the initial state.

The mirror is untrusted. It only produces witnesses (intermediate states), which the kernel recomputes, and window
boundaries. One chunk per stage was compiled by hand before release, to measure time and peak RSS and to see a
planted chunk fail.

## Stages: what each chunk proves

All chunk theorems are `decide +kernel` equalities between a kernel computation and a literal. An honest
`#print axioms` report is required (whitelist `propext`, `Classical.choice`, `Quot.sound`, no `sorryAx`).

* **cs** (`Cs/`, generator `gen_cs.py`). Norm bands `[N0, N1)`. Each band enumerates the box points with norm in the
  band (two k-intervals per row, from integer square roots), groups the exact integers `2 Re z^{6m}` by norm in a
  trie, and returns `Σ_N rat(S_N, (64N⁶)^m)` and the point count. `Assemble.lean` checks that the bands tile the norm
  range, that the counts add up to the box sizes (131,584 and 4,704), and that the final scaling equals A1's `coList`
  (the C++ `co[1..38]`). The `bcons` and `core_test` stages take `co` as a premise, so this stage discharges it.
  Planted controls: a band sum with +1 ulp, and a band count with +1.
* **core_test** (`Jet/`, `CoreTest/`, `gen_coretest.py`). This is a new transcription of the jet type `J` (with `pow`
  and its exact-zero affine shortcut, `log` through A1's interval `log`, `inv`, `sqrt`), of `cpol`, `sm`, `PQt` and
  `hor`, of `basis` for every segment, and of one `core_test` cell. `Jet/InitCheck.lean` recomputes the
  `init_after_co` literals (`VR`, `alp`, `beta`, edge values, `Tp0..2`, `-log R + π/2 R²`). The chunks hold 1,886 cell
  theorems. A segment-2 cell is split: 38 Horner witnesses, one per mode, then the bridging lemma `ctCell_seg2`. This
  is 19x faster (80 s against 1,515 s per cell). `Assemble.lean` checks `nsamp`, the running maxima against the C++,
  and **the bound check of core.hpp:274** (`bc.v < 6000 Q ∧ dsum.v < 2·10⁶ Q` after every segment). That is the
  assertion the A1 audit (B1) found uncovered.
* **bdsup / inside_hess / global_grid** (`Grid/`, `Bdsup/`, `InsideHess/`, `GlobalGrid/`, `gen_grid.py`).
  * Each stage has one file per grid row. A row is a chain of segment theorems
    `seg(st_k) = some st_{k+1}` between state literals defined once in the file, starting from the C++ initial state.
  * The lookup includes the exterior `tail` branch, which bdsup and global_grid reach for `t ≥ l`.
  * Windows are slices `winN off len` of one shared table literal, `Grid/Table.lean` (27 blocks). The per-chunk table
    copies (audit N1) are therefore consistent by construction.
  * `Grid/TableCheck.lean` checks that the shared table has 6,826 nodes, is sorted, ends at `l`, and that all meshes
    equal `nsamp`.
  * Each stage's `Assemble.lean` recomputes the stage outputs from the row final states in the C++ reduction order.
    It then checks them against the C++: the bdsup bounds; `gmin`, `drneg`, `factor`, `er_drop` and the
    grids.hpp:336 assertions; and the inside_hess hulls, with the failures equal to 0 and the minima positive.
  * Planted control per stage: segment 0 of row 0 with the end state +1 ulp.
* **table** (`Table/`, `gen_table.py`). Serial propagation, made parallel with **state witnesses**.
  * `Table/StateB*.lean` holds the C++ `pointS[i]`, `cellS[i]`.
  * Per node `i ≥ 1563`, `N{i}.lean` proves the propagation step `prop(ts[i-1], ts[i], pointS[i-1]) =
    (pointS[i], cellS[i-1])`, which needs the basis at the midpoint and at the cell.
  * It also proves `fh(ts[i], pointS[i]) = pts[i]` and `fh(cell, cellS[i-1]) = cels[i-1]`. The targets are the shared
    table literal itself, so the table stage verifies the very literal the grid stages consume.
  * `fh` is staged into the basis, `solve` (40 jets), the double sum `quad, e` in 11 fixed row blocks, and the final
    assembly. Interval addition is exact, so the grouping does not change the value. Segment 2 uses Horner
    witnesses.
  * `Z*.lean` covers the 1,562 segment-0 nodes with the closed form `fh0`.
  * `Init.lean` checks that `ss0(small)` (order 0) equals `pointS[1562]` and that the recomputed mesh (`n_i`, `ts`,
    `orig`) equals the shared table.
  * Planted control: step 1563 with `pointS.s1` +1 ulp.

## Scheduler (`scripts/scheduler.py`)

* There is one process, guarded by an `flock` on `/home/callensxavier_gmail_com/a1l1_oleans/scheduler.lock`.
* There is one Lean worker per configured core. Each worker runs `taskset -c N /usr/bin/time -v lean ...` through
  `scripts/l1lean.py`, so wall time and peak RSS come from the OS.
* Work runs smallest cost first: stages in `stage_order`, then cores, then planted controls, then chunks by
  `ops_hint`, then the assembly once all its dependencies are ok.
* **Memory guard.** At most `floor(mem_budget_gb / measured peak RSS of the stage)` concurrent workers (default
  24 GB). The default peak assumed before a stage's first measurement is 8 GB. No new worker starts while
  `MemAvailable < 9 GB`.
* **Acceptance.**
  * A genuine chunk is `ok` if rc = 0, there is no `sorry`, its axioms are within the whitelist, and an axioms report
    is present.
  * A planted chunk is `ok` (that is, correctly rejected) only if the following all hold: Lean fails with exactly one
    error; that error is a kernel refutation ("decide proved that the proposition ... is false" or the kernel type
    mismatch of `decide +kernel`), not a timeout, OOM or import error; and the honest refutation `plant_refuted`
    compiled with whitelisted axioms.
* **Resumable.** An entry that is `ok` (or `fail`) with the same source sha256 is skipped. A `running` entry left by a
  dead scheduler is killed if still alive and re-queued. Editing a chunk's source re-queues it, because its sha
  changes.
* `scripts/reclassify.py` re-classifies finished entries from their saved logs after a classifier fix. It never
  re-runs Lean.

### How to check progress

```
cat results/proposal2/2026-10-26/A1-continuation/STATUS.md          # summary table, failures, last 40 finished
tail -f /home/callensxavier_gmail_com/a1l1_oleans/logs/scheduler.log
cat /home/callensxavier_gmail_com/a1l1_oleans/scheduler.pid; ps -p "$(cat /home/callensxavier_gmail_com/a1l1_oleans/scheduler.pid)"
ls /home/callensxavier_gmail_com/a1l1_oleans/status | wc -l
```

### How to restart

```
bash results/proposal2/2026-10-26/A1-continuation/scripts/start_scheduler.sh     # detached (setsid nohup); a second copy exits (flock)
```

To load a changed `scheduler.py` without losing running work: `bash scripts/restart_scheduler.sh`. It SIGKILLs
the scheduler only; the workers run in their own sessions, and the new instance adopts them by pid. To stop
everything: `kill <pid>` (SIGTERM). Running workers are killed and re-queued. To pause without stopping: create
`/home/callensxavier_gmail_com/a1l1_oleans/PAUSE`, or set `"paused": true` in `pipeline_config.json`. Running chunks
finish and no new ones start.

### How to widen the cores (e.g. 0-7 once N1/N2/N4 are done)

Edit `pipeline_config.json`: `"cores": [0, 1, 2, 3, 4, 5, 6, 7]`. The file is re-read every 10 s, so no restart is
needed. The memory guard still applies: with the measured peaks (cs 6.2 GB, core_test 3.8 GB, grid rows about 6 GB)
and `mem_budget_gb = 24`, at most 3-6 workers run at once. The box has 29 GB, so 8 concurrent workers need a peak
of 3 GB or less, or a larger `mem_budget_gb` set deliberately, with `min_mem_available_gb = 9` as the safety net.

### Releasing a generated stage

A generator writes its manifest to `manifests_pending/`. Move it to `manifests/` only after the hand test of one
chunk and one planted chunk passes. The scheduler picks it up within 10 s.

## Generated sources and disk

* The literal defs in generated files are `noncomputable`: no compiled code, so the oleans are about 14x smaller, and
  the kernel evaluates them all the same.
* Expected sizes:
  * table: about 5,300 node files, about 0.4 GB of Lean source and a few GB of oleans;
  * grid stages: 0.1-0.2 GB of source.
* These files are generated deterministically from `dump2.txt` (sha recorded in every manifest) and the generators.
  Commit the generators and manifests. Do not commit the bulk chunk sources without LFS.

## State at the end of the setup session (2026-10-26 ~14:15 UTC)

| stage | generator | mirror gate | hand test (one unit) | queued chunks | done |
|---|---|---|---|---|---|
| cs | `gen_cs.py` | 38/38 `co[m]` bit-equal | yes | 45 | **all 45 ok**, including `Assemble` (`cs_stage`, `cs_final : … = coList`), and 2/2 planted controls rejected. **Stage cs is L1-complete.** |
| core_test | `gen_coretest.py` | 1,886/1,886 cells | segments 0, 1, 2 (witnesses), 4 and InitCheck pass | 693 | 596 ok, 0 fail, 2/2 planted controls rejected; segment 4 still running |
| bdsup | `gen_grid.py bdsup` | 519/519 rows at every C++ checkpoint | R0000 (51 segments) passes; planted control rejected | 552 | waiting for its turn |
| global_grid | `gen_grid.py global_grid` | 2,186/2,186 rows | R1000 (113 segments) passes | 2,188 | waiting |
| inside_hess | `gen_grid.py inside_hess` | 601/601 rows | R0000: all 255 segments pass. The row conjunction hit maxRecDepth; fixed by `fix_row_recdepth.py`, not re-run | 603 | waiting |
| table | `gen_table.py` | every node it wrote: `pts`, `cels`, `pointS`, `cellS`, init | Init (mesh + `ss0`) passes. N3100 (segment 2) passes completely. N1563 (seg 1) and N5300 (seg 4) pass every theorem except the final node conjunction, whose parenthesisation was fixed after the test. Z0000 passes | 5,393 | waiting |

The scheduler orders the stages by measured cost (`stage_order` in the config): cs, core_test, bdsup, global_grid,
inside_hess, table. A probation gate guards every stage: its cores, its planted control and its first genuine chunk
must pass before the bulk starts. A stage whose probation fails halts and is shown in STATUS.md.

### Projected time at the measured rates (`projection.json`, `scripts/make_projection.py`)

The per-unit times are hand-test compiles of one row, node or cell, measured at load average 15-17 with about two
Lean processes per core on cores 0-3. The wall times therefore overstate CPU time by up to about 2x (the global_grid
row: user 1,404 s, wall 2,005 s). Each range is wall/2 to wall, in core-hours.

| stage | units | measured wall per unit | core-hours |
|---|---|---|---|
| core_test (remaining) | 97 chunks | 80 s per seg-2 cell, 194 s per seg-4 cell | 8-16 |
| bdsup | 519 rows | 1,210 s | 87-174 |
| global_grid | 2,186 rows | 2,005 s | 609-1,218 |
| inside_hess | 601 rows | 7,784 s | 650-1,300 |
| table | 1,442 + 1,995 + 1,827 nodes (seg 1 / 2 / 3-5), plus 98 seg-0 files | 785 / 1,906 / 2,898 s, plus 75 s per file | 1,422-2,843 |
| **total remaining** | | | **2,776-5,550 core-hours** |

* 4 workers (cores 0-3): 29-58 days.
* 8 cores with the 24 GB memory guard: the measured peaks are 4-6 GB, so about 5 concurrent workers, 23-46 days.
* 8 concurrent workers, only if `mem_budget_gb` is raised and they fit: 14-29 days.
* cs took 7.4 core-hours and core_test so far 13.3. Both are done or nearly done.
* The core_test estimate is an upper bound. The seg-4 hand test (194 s per cell) used the jet core before the `bm0Of`/`basisW` refactor, which computes `PQt` once. In the scheduler, seg-4 files of 3 cells take about 60 s, about 20 s per cell. Expect the same kind of overestimate wherever a hand test ran under heavy contention.

This is above the A1 audit's 854-2,240 core-hours. The grid stages cost about 1.5-1.9 s of wall per `G(·,·,true)` on
this loaded machine, against A1's 0.31-0.52 s, and the seg-4 table nodes are slow.

Optimisations that should pay off, none implemented yet:
* Witness `PQt` and the mode jets for segments 3-4, as was done for segment 2. In core_test this made segment 2 19x
  faster, and segment-4 basis evaluations are the slowest unit.
* Profile the grid `G` per call. Window length is not the cause: bdsup with 4-step segments was slower than with
  16-step ones, at 2,828 s against 1,210 s.
* Use STATUS's measured user times once the first few hundred chunks of each stage are in.

### Memory and disk

* Peak RSS per chunk (measured):
  * cs: 6.2 GB
  * core_test: 3.9 GB
  * grid rows: about 5.9 GB
  * table nodes: 4.3-5.3 GB
  * table Init: 11.5 GB (one chunk)
* The guard counts the expected peak of every running worker by file group, so one 11.5 GB chunk does not throttle
  the stage.
* The generated Lean sources take 0.8 GB (`formal_cert/Programmes/SandierSerfatyL1/`, mostly the 5,300 table node
  files). Do not commit them without LFS: the generators, the manifests and the dump sha reproduce them exactly.
* The oleans are about 5x the source size (all literal defs are `noncomputable`), roughly 4-5 GB in total;
  /home has 36 GB free.

### Fixes applied during the session that a reader of the logs should know about

* The planted controls of cs and core_test were first classified `fail`. The cause was a classifier string-match bug
  (the backtick in "`decide` proved"). `reclassify.py` re-classified them `ok` from the saved logs; Lean was not
  re-run.
* The grid window check now waives the first-node test when the window starts at table index 0, where the C++ range
  is clamped (`atStart`). Before that fix, bdsup R0000 segment 0 was refuted by the kernel.
* The scheduler was replaced twice by SIGKILL + restart. The new instance adopted the running workers by pid (cs
  M1B006 then core_test S2C0076-79), so no work was lost.

## Rusty-SUNDIALS cross-check (Tier X, independent of Lean)

Worktree `/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ss-table`, branch `physics/sandier-serfaty-table-cvode-2026-10-26`,
crate `crates/qf-sandier-serfaty-table`. Results: see `result.json` and that crate's README.

Commit `ea03b28399524966e760b8868fe429050b8ed9dd` (not pushed). It reads the table propagation as the ODE
`s1' = t b`, `s2' = -2 b~ + t b~²`, `ps_k' = b~ - k ps_k / t` (from core.hpp:254-259 and `solve` in `fh`), with
`b = basis(t, seg)` in f64 duals. It integrates with this repository's CVODE (BDF), restarted at every breakpoint, from
`ss0(small)`, and compares the result with the certificate's 144-bit enclosures `pointS` (rounded outward to f64) at 437
nodes.

**Verdict: PASS.**
* At rtol 1e-13 and 1e-14, every CVODE value lies inside its enclosure: 17,640 global values and 8,800 node-to-node
  values.
* The negative controls leave the enclosures:
  * `b -> (1 + 1e-6) b`: 17,600 of 17,640 values fall outside, by up to 1.4e-7;
  * `k -> k (1 + 1e-6)`: 3,342 `ps` values fall outside.
  Both are far beyond the measured solver drift of at most 9.9e-13 between rtol 1e-13 and 1e-14.
* Coarser tolerances (1e-8 to 1e-12) fail. The solver error is then larger than the enclosure widths, which are
  1e-14 to 1e-10 for s1.
* fmt, clippy (`--workspace --features experimental -D warnings`) and the crate's 4 tests pass.
* This is evidence, not proof: f64 and CVODE carry no error bound.
