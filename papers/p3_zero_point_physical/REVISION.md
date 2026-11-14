# Revision of N2 (papers/p3_zero_point_physical) after AUDIT.md (ACCEPT_WITH_CORRECTIONS, no blocking item)

Scope: text, ledger, metadata only. No code, Lean file or run file was changed (hashes in main.tex still valid). Nothing committed, pushed or published.

| # | Audit item | Action |
|---|---|---|
| 1 | Stale replay statements | "Kernel replay" paragraph rewritten: leanchecker 4.34.1, Taylor rc 0, Basic rc 0, ZeroPointCert.Basic rc 0 (data/leanchecker_replay.json); replay does not check axioms. Limitation bullet "No kernel replay recorded" deleted. |
| 2 | Stale audit statements | Disclosure paragraph, ledger section and limitation bullet now cite AUDIT.md (independent AI audit, ACCEPT_WITH_CORRECTIONS, no human audit, no statement lock). ledger/build_ledger.py: STATUS updated and an `ai_audit` field added to every Tier A row (the `audit` field stays null). Ledger rebuilt (24 claims) and gate re-run with ledger/run_gate.py: exit code 1, 0 blocking, 8 LEDGER_UNAUDITED_TIER_A flags (they ask for a person); gate_output.txt rewritten. |
| 3 | Riesz 4 overstated | Abstract table, Section 2 table, deviation (ii), Section 7 title and body, limitations bullet, publication_meta.json reworded as Tier X evidence (finite-difference E''(0)=+2.754, cutoff 40/100, one path), not certified either way. "Prereg error" replaced by "appears to conflate global and local refutation". |
| 4 | No quantum-transition implication | Sentence added to the Window-and-scope limitation: result concerns E_zp alone, classical energy has positive curvature at rho, nothing for E_cl + hbar E_zp, no transition claimed. Also in publication_meta.json. |
| 5 | Positivity rationals unused | Step 7 states that yuk*_lmin_lo, lminu_lo, qpd_lo are unused (theorems consume only yuk*_cert.1; positivity enters via hEU). Section 4 Positivity bullet notes they pass through float() (n2_certify.py lines 695, 759-761), rounded to nearest, harmless with margins >= 0.57. Same notes added to ledger PZP-A-0003/0004. |
| 6 | Step 4 wording | Added "(assuming E_zp is C^2 at rho, for paths with equal |tau'(0)|; not used by the headline)"; ledger PZP-C-0011 likewise. |
| 7 | hd1/hd2 endpoint gap | Note added in Step 6: differentiability near +-t0 closed by continuity because margins are strict; stated, not separately certified. Ledger PZP-C-0009 likewise. |
| 8 | Weak Lean negative controls | Controls table row and paragraph, and the LeanFlow paragraph: the substantive negative control is the certifier run (M_lo > 0); the Lean and LeanFlow rejections are arithmetic sanity checks. |
| 9 | Wrong ledger ID | PZP-C-0010 tag removed from the Hessian formula H = 2g'I + 4g''RR^T (no ledger row covers it). |
| 10 | "Classically optimal" source | Title, abstract and Section 1 now say "(H2, conditional)". Montgomery 1988 not cited (not checked). |
| 11 | P2 c-to-Laplacian factor | Not derivable here (it depends on P2's normalisation of c). The comparison column now uses this paper's own Tier X values E''(0)/2 (-1.554, -1.275, -3.8495); the asserted conversion (factor about 3.97) is dropped and said to be asserted. |
| 12 | Docstring errata | Mentioned only: erratum (c) added in the Limitations errata bullet (tail_bounds docstring "1 + 4 + 4 = 9", n2_certify.py:455, same as erratum (b)). Code not changed (hash pinned). |

Also: publication_meta.json brought in line (version v1, audit verdict, replay, gate exit code 1, Riesz 4 rewording, H2 conditional).
Build: pdflatex run twice, 0 errors, 0 undefined references, 10 pages (only sub-2pt overfull boxes in tables).
