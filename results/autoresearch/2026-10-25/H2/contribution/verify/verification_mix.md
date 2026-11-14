# YukawaMix.lean: independent recompile (paper-stage agent, not the producer), 2026-10-25

- Input: verbatim copy of formal_cert/Autoresearch/YukawaMix.lean (sha256 6a940a7c...c374c6) with verifier_block.lean.txt
  appended, giving VerifyYukawaMix.lean (sha256 f347d67df563268ff6cc0062d9fdd95ae76650275424648a2f319b96e235ea0e).
  The copy recompiles the claimed proofs from source. It imports only Autoresearch.Yukawa (the olean verified earlier) and
  Triangular.AnyDensity, not the YukawaMix olean.
- Command: `taskset -c 4-7 python3 scripts/certified_numerics/lean_pinned.py compile results/autoresearch/2026-10-25/H2/contribution/verify/VerifyYukawaMix.lean --timeout 1700 --json-out .../compile_verify_yukawamix.json`
- Result: rc 0, 21.4 s. All 16 claimed theorems report `[propext, Classical.choice, Quot.sound]`.
- The verifier block compiled and was accepted:
  - `rfl` unfoldings of `yukawaMix` (= sum of w_i * exp(-kappa_i sqrt t)/sqrt t), `g`, and `DensityRho` (Iff.rfl);
  - `g kappa (r^2) = exp(-kappa r)/r` for r > 0;
  - statement pins of `yukawa_optimal_any_density`, `triangular_yukawaMix_optimal` and `latticeEnergy_yukawaMix_lt_top`;
  - `v_three_length_finite` (weights 1, 2, 1/2; screenings 1/2, 1, 3) and `v_mix_pos`. Both report the allowlist only.
- Planted `v_planted : AdmissiblePotential signedMix := sorry` reports `[propext, sorryAx, Classical.choice, Quot.sound]`,
  and so does its downstream use `v_planted_use : False`. So sorryAx propagates and is caught.
- Scope: this is an AI-agent audit, not a human statement-adequacy audit. The ledger keeps audit = null for every Tier A row.
