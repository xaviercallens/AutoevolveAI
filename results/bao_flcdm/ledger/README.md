# BAO run claim ledger (Elenchus format)

6 claims registered in `SocrateAI-Scientific-Elenchus`'s tier-capped ledger
format (X<C<L<B<A), each with a content-addressed evidence blob in
`evidence/` (the blob's own sha256 is its filename; `ledger.py` verifies
this, not just trusts it).

Verify:
```
python3 <elenchus>/tools/ledger.py --evidence-dir evidence ledger.json
```

## Real findings from running the gate (not fabricated for illustration)

1. **LEDGER_TIER_INVERSION (blocked, fixed)**: the first draft filed the
   "this run agrees with DESI's published value" claim as Tier B
   (exact_harness), but it depends on a Tier L citation (`BAO-L-0001`, DESI's
   quoted number) — a claim can never exceed the effective tier of what it
   rests on. Refiled as `BAO-L-0002`, Tier L. The gate caught a real bug in
   how this session modeled its own epistemic dependencies, not a schema
   typo.
2. **LEDGER_UNAUDITED_TIER_A (flagged, left open, not silenced)**: the 3
   Lean claims (`BAO-A-0001..3`) are kernel-verified but `audit: null` — no
   independent party has certified that the Lean *statement* means what its
   English gloss claims (the kernel only checks the *proof* is valid for the
   statement as written; a wrong formalization of a true idea can still
   compile). This is disclosed here rather than fabricated as `audit: true`,
   which would defeat the entire point of the ledger. An honest audit would
   need a second reviewer (human or a separate model call with no sight of
   this session's own reasoning) reading `formal/ANSE/BAO_FlatLCDM.lean`
   against `docs/literature/BAO_FLCDM_LITERATURE_REVIEW_2026.md`'s stated
   physics and confirming the match independently.

See `LL.md` §11 and `TODO.md` item 12 for how this was built and what
adopting the ledger project-wide would need.
