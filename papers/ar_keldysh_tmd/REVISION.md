# Stage 5 revision: ar_keldysh_tmd (lane H3)

Input: `AUDIT.md`, the Stage-4 independent audit by an AI agent instance (not a human), with the verdict
ACCEPT_WITH_CORRECTIONS. Every correction is listed below with how it was resolved. None was declined.

No Lean source changed. The sha256 hashes are the same as in the audit:
- `KeldyshCM.lean`: 1bac0d41…48647f2
- `KeldyshCMControls.lean`: d7e5516f…801f0606
- `Yukawa.lean`: a16397de…c033cf

Because the sources did not change, no Lean recompile was needed. The rusty-SUNDIALS commit is still `2e41505cc9df8c46d2b2d667c89ea53e977218ca`, with no new Rust changes, not pushed.

## Blocking

| # | Correction | Resolution |
|---|---|---|
| B1 | §3: "Step 7 ... is not \tier{C}" renders as "is not [C]", which inverts the tier. | Now reads "Step 7, the link to the Struve function, is not formalized; it is \tier{C}." I checked the rendered PDF text. |

## Non-blocking

| # | Correction | Resolution |
|---|---|---|
| N1 | §3 "Steps 1–6" vs §4 "Steps 0–6". | §3 now says "Steps 0–6 are mirrored in Lean". |
| N2 | Step 0: "off by at least 5.6e-3" is false at x = 0. | Now reads: "a perturbed integrand (2xy → xy) is off by at least 5.6e-3 at the six points with x > 0; at x = 0 the perturbation has no effect". There are 7 sample points {0, 0.01, 0.3, 1, 2.5, 7, 50}, six of them with x > 0. |
| N3 | The abstract's first sentence states the Tier C identification as fact. | Now reads "We give a human proof ([C], not machine-checked) that, as a function of t = r², it is a positive mixture of Gaussians …". The title is unchanged; the auditor called it acceptable once the abstract is tagged. The publication_meta description was tagged the same way. |
| N4 | §6 Materials: "Screening lowers the magnitude of the energy" without attribution. | Now says the lower magnitude of E_tri comes mostly from the lattice-independent +πρr₀ background term (the neutralisation convention, not lattice structure), as in Figs. 1 and 2. It then says separately that the structure-sensitive gap is also lower. |
| N5 | Step 7(a): V and V̂ are not in L¹, so the inversion is improper or distributional; (b), (d) and subordination are uncited. | Done in two parts, described below this table. |
| N6 | Suggested strengthening: route (e) alone proves Theorem 2 with only positive integrands. | Adopted as the main proof, described below this table. |
| N7 | §7 "22 queries (listed in search.json)". | Now reads "23 Hub searches, 22 distinct terms (11 listed in search.json and 12 in search2.txt, with "c2db" repeated)". I recounted from the files: 11 + 12 = 23 entries and 22 distinct strings. (Case-folding "c2db"/"C2DB" would give 21.) The ledger row KT-X-0008 says "22 Hub queries", which is consistent. |
| N8 | Ledger L rows (KT-L-0001/0002/0005 and the Remark 1.5 numbers) would be refused by strict Elenchus citation_check, and the excerpts linearise mathematics. | Kept the rows, and made the disclosure explicit. The Tiers paragraph now says the paper's L is looser than the strict `citation_check`. It names the rows that would be refused on kind, notes that linearised mathematics would not match verbatim, and records that SS Theorem 2 passes the strict check (Stage-4 audit). Re-filing them as kind-theorem rows would misdescribe them: they are an equation, table values and a README. Moving them to C would lose the fact that they are quoted from real sources. |
| N9 | publication_meta.json title differs from the PDF title; the notes could record the audit. | Changes listed below this table. |
| N10 | openai/math commit fd4aeeb could not be re-verified because the pinned copy has no .git. | Disclosed in the bibliography entry \cite{oai} and in publication_meta notes. The id is inherited from the earlier published ledger. Not re-verified here either. |
| N11 | Producer ≠ human verifier remains open; the 9 LEDGER_UNAUDITED_TIER_A flags stay open. | Unchanged and still open. The "Producer ≠ verifier" limitation now describes the Stage-4 agent audit and says it is not independent human verification. The ledger `audit` fields stay null. |

### N5: Fourier inversion caveat

- The old Hankel route is now part (e), "a second route, kept as a cross-check".
- Part (e) says explicitly that V ∉ L¹(R²) and V̂ ∉ L¹(R²), so the inversion is improper (distributional) and not justified here.
- Part (e) also names its three standard integrals as uncited: the J₀ table integral, the erfc Laplace pair and Weber's integral.
- The subordination formula is now also stated to be used "without a citation".

### N6: route (e) as the main proof

Step 7 now proves Theorem 2 by an all-positive route:
- (a) DLMF 11.5.2 [L, KT-L-0004];
- (b) subordination, with the Lévy density, uncited, and Tonelli;
- (c) the elementary inner integral ∫u(1+u²)^{-1/2}e^{-λu²}du = ½√(π/λ) erfcx(√λ), via v = √(1+u²);
- (d) a = 1/(4b), which gives exactly w(b)/(2b).

The reviser (an AI agent, not a human) re-derived the prefactors in (b)–(d) step by step in this session, and they agree with the audit's derivation. They are also confirmed numerically (KT-X-0010). The result is still Tier C and still not machine-checked. The text credits the route to the Stage-4 audit, an AI agent.

New Tier X check, filed as ledger row KT-X-0010 with claim_licence false:
- Script: `results/autoresearch/2026-10-25/H3/contribution/route_e_check.py`. Output: `route_e_check.json`. Settings: mpmath dps 30, cores 4–7.
- Positive controls: the Struve form vs the Laplace form, the weight form and the mixture at 4 (r₀, r) points; the inner integral at 4 values of λ; the subordination formula at 2 points. Max relative error is 2.06e-17.
- Negative controls, each reported separately:
  - The inner integrand with e^{-λu} in place of e^{-λu²} misses the closed form by ≥ 0.37.
  - Subordination with a^{-1/2} in place of a^{-3/2} misses e^{-ρ√t} by ≥ 0.82.
  - Both are caught.
- A first version used "the inner closed form times 2" as a negative control. That was tautological: it is exactly 0.5 off once the positive control passes. It was replaced before the final build.

The numbers in the paper come from the new macros `\KTRouteEPosErr`, `\KTRouteENegInner` and `\KTRouteENegSub`, which `gen_inputs.py` generates from `route_e_check.json`. `gen_inputs.py` was re-run, and a diff against a snapshot showed that only these three macro lines changed.

Ledger row KT-C-0001 now describes the new main route and the cross-check route. Its evidence blob has an inline `text` field holding steps (a)–(d) of the main route, plus references to NOTE.md and AUDIT.md.

The "Definition fidelity" limitation no longer says the Hankel integral is "checked only numerically". It now says the main route rests on DLMF 11.5.2 [L] and on the subordination formula, which is uncited and checked numerically. The Novelty limitation now points to Step 7(a).

### N9: publication_meta.json changes

- The title is now identical to the PDF title. The PDF `pdftitle` metadata was also set to the full title, and `pdfinfo` confirms it.
- The notes record the Stage-4 agent audit: recompile rc 0, allowlisted axioms, its own planted sorry and axiom caught, scan bit-identical, cargo tests 28/0/1. They state that it is not a human review.

## Other changes made during the revision

- Reproducibility: the sha256 lines are now on their own line, which removes the one overfull hbox (15.6 pt).
- The ledger now has 30 claims: 9 A, 5 L, 6 C and 10 X. The paper's §8 count was updated to match.
- Superseded evidence blobs (the old KT-C-0001 and intermediate KT-C-0001/KT-X-0010 blobs) were removed by the new `ledger/prune_orphans.py`, which deletes blobs that `ledger.json` does not reference.
- `build_pdf.py` was added. It runs pdflatex twice and reports the page count, undefined references and overfull boxes.

## Rebuild and gate (real tool output)

- `build_pdf.py`: pdflatex rc [0, 0], **13 pages**, no undefined references, 0 overfull hboxes, no rerun warning. main.aux and main.out were removed afterwards.
- `python -I ledger/build_ledger.py`: "claims 30". Then `prune_orphans.py` removed 2 superseded blobs, leaving 30 remaining and 30 referenced.
- `python3 …/Elenchus/tools/ledger.py ledger.json --evidence-dir evidence`: **exit code 1**, 0 blocking findings, 9 flags, all `LEDGER_UNAUDITED_TIER_A` (KT-A-0001…0009). Output is in `ledger/gate_output.txt`. Exit code 1 is caused by the open flags only; they need a human statement audit.
