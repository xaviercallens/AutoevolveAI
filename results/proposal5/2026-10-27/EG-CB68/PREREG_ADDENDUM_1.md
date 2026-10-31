# EG-CB68 preregistration addendum 1 (written 2026-10-28 ~18:10 UTC, before any arbitrary-root run at cap >= 35)

Why: the measured growth (cap 29 -> 31: triangle-rooted states x1.6 per cap, arbitrary-root x1.9 per cap, cap-31
arbitrary-root search 18 CPU-s) shows that the parent kill criterion does not fire. Cap 34 needs minutes, not 48 core-h.
The parent's own stretch goal is order 70. This addendum fixes, before running, how the remaining time box is used.

1. **Arbitrary-root mode (orbit 0, root block {0,1,2} only, no Berge triangle assumed).**
   By the same coverage argument as Tranquilli Prop. 10 (the root {0,1,2} is the lexicographically first block through 0
   under first-occurrence labelling), a closed cap-c tree covers every connected linear v_3-configuration with v <= c
   with no Berge 4- or 8-cycle. It needs **no Moore or cage premise**. It was added to the code before the freeze and
   is run for caps 29..34 as an in-scope cross-check that removes the Tier L premise n(3,10) = 70.
2. **Exploratory extension (not in the parent preregistration).** Arbitrary-root caps 35, 36, ... are run in order, each
   with its certificate streamed through a FIFO into `cb_check_fast` (C witness checker, tamper-tested), plus oracle B for
   transcript-hash agreement where time allows.
   - Stop rule: start cap c+1 only if its projection (measured growth factor times cap-c wall time, for producer + checker)
     fits in the remaining part of the 48 core-hour box, with the 24 h wall-clock deadline at 2026-10-29 17:06 UTC.
   - Claim if cap c closes with zero completions: "every simple cubic bipartite graph on at most 2c vertices contains a
     cycle of length 4, 8 or 16", Tier C (exhaustive search + independent witness checker). The coverage lemma is argued in
     the text; it is not formalised.
   - Order 70 (cap 35) also covers the three (3,10)-cages. A closed cap-35 tree implies that each of them has a C16.
3. Same controls as the parent and PREREG_ITEM.md. No new control is needed, because the mode and the checker were
   already exercised (P2 arbitrary-root canonical counts, P3b arbitrary-root C16-off cap 19).
4. Wording: any order above 68 is labelled "exploratory extension, preregistered only by this addendum, written after
   the cap-29..31 timing was known". It is a finite bound, not progress on the conjecture.
