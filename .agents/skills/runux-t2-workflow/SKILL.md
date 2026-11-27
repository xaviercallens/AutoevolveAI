---
name: runux-t2-workflow
description: Autonomous T2 (Design, Research & Architecture) Workflow Runner for RunuX Kernel. Orchestrates Lean 4 proof triage & sorry elimination, P0 stub completion in network data path, blanket clippy allow removal, architecture/boot verification, ANSE energy minimization, and metric ratchet gates.
---

# RunuX T2 Workflow: Design, Research & Architecture Runner

This skill guides the autonomous execution of the **T2 (Design & Architecture)** workstream defined in `docs/roadmap/RUNUX_V12_VERIFIED_CORE_PLAN.md` and `docs/roadmap/BUSINESS_CASE_PRIORITIZED_PLAN.md`.

---

## 1. T2 Architecture & Tier Responsibilities

| Tier | Model | Scope | Verification Oracle |
|---|---|---|---|
| **T1 (Bulk)** | Claude Haiku 4.5 / Fast Model | `static mut` removal, single-`sorry` arithmetic search, `SAFETY:` documentation, test transcription | `metrics.py ratchet`, `check_unit.py` |
| **T2 (Design)** | Claude Sonnet 5 / Strong Reasoner | Stub completion (`reassembly`, `exthdrs`, `udp`), Lean lemma libraries, architecture/boot bring-up, clippy lint cleaning | `cargo test`, `check_unit.py`, `lean` standalone, banner tests |
| **T3 (Review)** | Claude Opus 5.5 / Human / ANSE | Axiom justification, spec-change approval, Miri security sign-off | Cryptographic proof token minting |

---

## 2. Core Execution Protocols

### Protocol 1: Physical Environment & Hardness Invariants
All commands must strictly adhere to the following physical constraints:
```bash
# Secondary storage target directory (prevents filling root disk)
export CARGO_TARGET_DIR=/media/xavkal/3ada43de-fc4a-43bd-a9f8-cf396fd17033/tmp/runux_target

# Test execution with single-thread determinism
cargo test --lib -p <crate> -- --test-threads=1
```

### Protocol 2: Lean 4 Proof Triage & Sorry Elimination
1. **Never run `lake build` in `formal/`** (avoids downloading Mathlib cache onto root partition).
2. Verify proofs directly via standalone `lean`:
   ```bash
   lean specs/lean4/MVK/<Phase>/<File>.lean
   ```
3. Classify `sorry` obligations:
   - *Arithmetic/Bounds*: Close using `omega`.
   - *Type-State / Idempotence*: Close using `rfl` or `decide`.
   - *Structural Induction*: Unfold definitions and apply `simp_all`.

### Protocol 3: P0 Stub Completion (Network Data Path)
1. **`reassembly`**: Replace constant stub returns with RFC 791/8200 fragment cache, overlap rejection (RFC 5722), and timeout expiration.
2. **`exthdrs`**: Implement RFC 8200 extension header chain parsing and boundary validation.
3. **`udp`**: Implement fallible socket hash table lookup.

### Protocol 4: Blanket Clippy Allow Removal
1. Remove `#![allow(clippy::all)]` from core crates (`kernel_types`, `page_alloc`, `slab`, `vmalloc`).
2. Run strict clippy with deny warnings:
   ```bash
   cargo clippy -p <crate> -- -D warnings
   ```
3. Replace blanket allows with narrow, justified item-level allows where necessary.

### Protocol 5: Anti-Cheat & Ratchet Verification
After every work unit:
```bash
uv run python scripts/metrics.py measure
uv run python scripts/metrics.py ratchet --baseline docs/roadmap/metrics/metrics.baseline.json
```
If any metric regresses, the change must be immediately rolled back.
