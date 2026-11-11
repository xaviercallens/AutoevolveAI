# GE-2 prior-art screen (2026-11-11) -- VERDICT: GO-NARROWED (moderate scoop risk)

## Our published census (doi 10.5281/zenodo.23867827)
READ (papers/p6_bistable_networks_recheck/main.tex): it is an independent RECHECK of Peng, arXiv:2610.32739 (23 Oct 2026, unrefereed); it claims nothing new. The 681/27 census is Peng's. No erratum owed on novelty. Optional related-work update: the paper says no earlier enumeration of this exact class was found (consistent with my screen) but cites only Tang-Xu; add Banaji-Boros-Hofbauer 2406.13451, Joshi 2013, Joshi-Shiu 2013, Wilhelm 2009, Lixiviant 2026 (SECONDARY: from Peng's reference list).

## What exists (READ = full text or abstract+grep read via alphaXiv; SECONDARY = Peng's list / search snippets)
- Peng 2610.32739 (READ, full): 2 species, <=3 internal reactions on {X,Y,2X,X+Y,2Y}, inflow + linear removal; 27/681. Method planar-specific (Lemma 3 nullcline graph; JAC/DIV/ROOT/FLUX). Nothing on 3 species or 4 internal reactions. 19 days old: field active.
- Banaji-Boros 2207.04971 (READ abstract/intro): full classification of 3-species, 4-reaction bimolecular CLOSED networks for HOPF (86 minimal). Not bistability, no flows.
- Banaji-Boros-Hofbauer 2406.13451 (READ abstract+grep): 2 species, <=4 reactions, generic bifurcations of positive equilibria; Lemma 27 = simplest bistable bimolecular (closed; stable origin + positive). Lists open problem on further multi-stable networks.
- Joshi-Shiu 1603.06441, Atoms 1108.5238 (SECONDARY): bimolecular reversible 2-reaction fully open networks, 386 enumerated, multistationarity not stability, 11 atoms. Joshi 2013: one non-flow reaction (SECONDARY).
- Banaji-Pantea inheritance (1802.00306 area), Cappelletti-Feliu-Wiuf 1909.11940 (flows preserve bistability): tools, not censuses (SECONDARY).
- Tang-Xu 2008.03846, 2012.15437 (abstract only): 2-reaction / 1-D stoichiometric subspace. Wilhelm 2009 (SECONDARY): single example.
- Lixiviant 2026 (SECONDARY): 2-species cusp-minimal certified classification. Banaji 2609.07265, Banaji-Feliu 2409.06877, Banaji 2407.01760 (fully open multistationarity, sufficient conditions): tools. Zero-one papers 2406.11586, 2608.01116: different class.
- Searches (alphaXiv x5, web x2): no work found on a bistability census for 3 species, or 2 species with 4 internal reactions, with inflow+removal. Absence of evidence from a limited search; follow-ups could appear any week.

## Candidate classes (counts = trivial arithmetic, checked)
A. 2 species, <=4 internal edges: 6196 labelled (~3.1k orbits). Peng Thm 2 makes supersets of the 27 trivially bistable; new content only for 4-edge networks avoiding all 27. One-step extension of Peng: high scoop risk, low novelty.
B. (recommended) 3 species, 9 nonzero complexes {X,Y,Z,2X,2Y,2Z,X+Y,X+Z,Y+Z}, 72 directed edges, <=3 internal, inflow + linear removal per species: 1+72+2556+59640 = 62269 labelled, ~10.4k orbits under S3. Not in literature: Banaji-Boros is closed + Hopf; Peng/BBH/Lixiviant planar; Joshi-Shiu counts multistationarity not stability. Genuinely 3-species networks leave <=2 edges for X,Y so many are probably monostable; expected outcome is a certified census with perhaps a few new minimal bistable mechanisms, or a negative. Peng's Lemma 3/ROOT do not transfer to 3D; JAC (midpoint identity for quadratic fields) and sign certificates do; expect an UNDECIDED residue.
Caveats: Joshi-Shiu 1603.06441, Tang-Xu and the Lixiviant manuscript not read in full. Tools present: Singular, gp, sage, sympy 1.14.
