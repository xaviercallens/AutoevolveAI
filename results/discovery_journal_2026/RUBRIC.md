# Selection rubric: the 20 contributions of the discovery journal (frozen before scoring)

Frozen on 2026-10-26, before any record was scored. It applies identically to every candidate, whatever its domain.

## Candidates
- The 112 distinct Zenodo works (`zenodo_inventory.json`). Duplicate deposits are merged, and versions are merged under their concept.
- The 57 science-relevant GitHub repositories (`github_inventory.json`). A repository is a candidate only if it is not already represented by a Zenodo work.
- Several records of one research line (for example the five autoresearch potentials) may be merged into one contribution, provided the merge is declared.

## Score (0–3 per criterion; total out of 21)
1. **Rigour reached (Elenchus):**
   - 0 = floating point only (X);
   - 1 = human argument (C) or cited literature (L);
   - 2 = Lean with an axiom check (A, no replay);
   - 3 = Lean with an axiom check and a kernel replay, or a certificate re-executed by an independent checker.
2. **Independent check:**
   - 0 = none;
   - 1 = self-check only;
   - 2 = independent AI audit with a verdict;
   - 3 = independent audit with the audit's corrections applied and recorded.
3. **Reproducibility:**
   - 0 = none;
   - 1 = code available;
   - 2 = code, data and commands;
   - 3 = also re-run by an agent other than the producer, with matching output.
4. **Synthesis:** how many of the four pillars it joins: mathematics, physics or biology, numerical simulation, formal proof. Score 0–3 for joining 1–4 pillars (1 pillar = 0, 4 pillars = 3).
5. **Honesty and learning value:**
   - 0 = later retracted with no correction published;
   - 1 = no caveat;
   - 2 = caveats stated;
   - 3 = a published negative result, a self-correction, or a refutation that taught the method something.
6. **Novelty within the programme:**
   - 0 = a duplicate or minor variant;
   - 1 = an incremental step;
   - 2 = a new result or tool;
   - 3 = a new method that later work reused.
7. **Value to people:** whether a non-specialist can see why it matters for knowledge, health, energy, education or trust in AI. 0 = none, 3 = clear and concrete.

## Hard rules
- **Exclusions:** a work whose central claim was withdrawn or refuted is not selected as a success. It may be selected only as a lesson, and is then scored on the withdrawal paper itself.
- **Records as found:** a record's claims are taken as the inventory records them. "Peer reviewed by AI agents" is not human peer review.
- **Domain balance:** at least 2 contributions each from mathematics, physics, genetics/biology, numerics/software and AI methodology/verification. At most 7 from any one domain.
- **Lessons:** at least 3 of the 20 must be negative results or self-corrections.
- **Ties:** broken by rigour, then by independent check, then by the earlier date.
- **Publication:** every score is published with a one-line justification citing the inventory field it rests on.
