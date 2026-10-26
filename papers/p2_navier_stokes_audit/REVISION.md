# A2 paper revision (after AUDIT.md, ACCEPT_WITH_CORRECTIONS)

Blocking
- B1: deleted ", and Fefferman asks for a proof of one of four statements" in section Implications; ledger P2NS-C-0005 text replaced by the audit's sentence ("This is not a Clay determination: ..."); ledger rebuilt (26 claims, 26 evidence blobs), gate re-run: exit code 1, 0 blocking, 4 LEDGER_UNAUDITED_TIER_A flags (unchanged, open).
- B2: "every one of its 88,400 declarations re-passes the Lean kernel" replaced by the audit's sentence (Lean.Replay skips 51 _unsafe_rec auxiliaries, 12 NS + 39 Euler, none in any proof closure, and 4 congr_simp duplicates); same added in the Replay section after the table, parenthetical in the abstract; also in ledger X-0005 and publication_meta.json.

Nonblocking
- N1 leanchecker per-module, not transitive (abstract, Replay, ledger X-0006). N2 second Clay erratum sentence in section 1. N3 auditor's audit_nonvac_Rn / audit_nonvac_periodic / audit_zero_data_ok with axiom lines (new section Independent AI audit; fidelity item (d) updated). N4 53,750/34,646 vs 53,752/34,648 explained. N5 7-module bit-identical rebuild sample cited. N6 "independently (of the corpus authors)" at first use in abstract.
- Limitations: "leanchecker --fresh (Mathlib re-check) not run" added.
- New section "Independent AI audit"; "no human audit" retained.
- publication_meta.json: version v1.1, description updated (audited, limits).

Build: pdflatex twice, 11 pages, 0 undefined refs, 0 overfull, 0 warnings. Nothing committed, pushed or published.
