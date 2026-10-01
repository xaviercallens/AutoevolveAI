---
name: anse-lean-prover
description: >-
  Maintain, compile, and develop Lean 4 machine-verified DEPLOYMENT INVARIANTS
  for ANSE: LoRA parameter budget constraints, FFN FLOP monotonicity (scoped
  explicitly), energy cost ordering, and CI/CD gate checks. Frame all results
  honestly as "configuration compliance verifiers", NOT as novel mathematical
  theorems. Use this skill whenever modifying Lean files or verifying deployment
  property soundness.
---

# ANSE Lean 4 Prover Skill (v2 — Post Strong-Reject Lessons)

This skill guides the agent in editing and verifying Lean 4 deployment invariants for ANSE.
It incorporates lessons from a full peer-review cycle (Strong Reject → Accept) to ensure
papers and proofs produced in a single pipeline run meet publication standards.

> **KEY LESSON (2026-09-30):** A "Strong Reject" was issued because the prior skill
> framed trivial arithmetic constraints as "computational physics theorems." The correct
> framing is: Lean 4 acts as a **strongly-typed CI/CD configuration checker** that
> exhaustively verifies all input configurations satisfying stated premises — stronger
> than unit tests, not a claim to theoretical novelty.

---

## 1. Directory Structure

```
formal/
├── lakefile.toml        # Lake build configuration (TOML format)
├── lean-toolchain       # Toolchain pin: leanprover/lean4:v4.34.0-rc2
└── ANSE/
    ├── Basic.lean           # Core definitions, states, metrics
    ├── JEPA.lean            # World model & representation invariants
    ├── Performance.lean     # Vectorization, hash tables, backtracking
    ├── MicroML.lean         # Neural parameter limits, dimension barriers
    ├── Autopoiesis.lean     # Banach fixed-point & hot-swap validity
    └── LayaDecision.lean    # NAR CPU deployment invariants (I1–I5)
```

**Build Environment:**
```bash
export PATH="/home/xavkal/.elan/bin:$PATH"
# formal/.lake → /mnt/data/home/xavkal/lean-builds/anse-formal-lake/.lake
# ~/.cache/mathlib → /mnt/data/home/xavkal/.cache/mathlib
cd formal && lake build
```
Expected: **~2135 jobs, 0 errors, 1 acknowledged sorry** (`cpu_energy_bounded` only).

---

## 2. Formalization Philosophy: Invariants, NOT Theorems

When generating new Lean 4 proofs, strictly distinguish:

| ✅ Correct Framing | ❌ Forbidden Framing |
|---|---|
| "Machine-verified deployment invariant" | "Novel computational physics theorem" |
| "Configuration compliance gate" | "Fundamental mathematical breakthrough" |
| "Compile-time static checker" | "Thermodynamic proof" |
| "Stronger than a unit test" | "Weierstrass existence" / "Banach hot-swap" (unless formally connected) |

**The value of Lean 4 vs Python/Pydantic:**
> Lean 4 provides *compile-time static verification* before any Python runtime or cloud
> resource is initialized. Invariants compose across the full codebase: a proof that
> passes can be referenced transitively by other proofs. Python asserts run once at
> startup and cannot be reused as formal lemmas.

---

## 3. Correct FLOP Complexity Scoping (CRITICAL — Fixes Strong Reject Flaw D)

**Full Transformer FLOP model (always document this):**
```
FLOPs(L, d, d_ff) ≈ 12 × B × L × d²   (FFN projections, d_ff = 4d)
                   + 4 × B × L² × d    (self-attention QK + AV aggregation)
```

**When proving FLOP bounds in Lean 4:**
- Name the definition `ffnFLOPs`, NOT `singlePassFLOPs` or `narFLOPs`
- Add a docstring stating **explicitly**: "This does NOT model the O(L²·d) attention term"
- Add backward-compatible aliases if existing proofs use old names
- The FLOP invariance theorem (I3) holds ONLY at equal sequence lengths — state this clearly

```lean
-- CORRECT: scoped with honest docstring
/-- FLOPs for FFN subnetwork only: O(L × d²).
    The full Transformer also has O(L² × d) attention (not modeled here). -/
def ffnFLOPs (seq_len d : ℕ) : ℕ := seq_len * d * d

-- WRONG: implies completeness it does not have
def singlePassFLOPs (seq_len d : ℕ) : ℕ := seq_len * d * d
```

---

## 4. `sorry` Management Protocol

**Allowed:** Exactly ONE acknowledged sorry is permissible per paper — `cpu_energy_bounded`.
This sorry requires runtime telemetry injection (τ, M from JSON) into the type system.

**Future work to close it (from Accept reviewer, point C):**
> Use a Lean macro to read `results_5_datasets_lora.json` at **compile time**, inject
> concrete τ and M into the AST, and discharge via `norm_num`.

**Rules:**
1. Every `sorry` MUST be documented in paper Abstract and a Limitations section
2. Abstract must say "one proof obligation remains open" — NEVER "all theorems compile without sorry"
3. Run `lake build 2>&1 | grep sorry` and count occurrences before finalizing any paper
4. Limit: ≤1 sorry total; 0 sorry is the target

---

## 5. Compilation & Verification Commands

```bash
# Standard build (21s with Mathlib cache)
export PATH="/home/xavkal/.elan/bin:$PATH"
cd formal && lake build ANSE.LayaDecision

# Count sorries before paper finalization
lake build 2>&1 | grep "uses \`sorry\`"

# Full harness verification
cd .. && uv run python -m antigravity_harness verify --formal-dir formal
```

---

## 6. Proof Guidelines & Known Working Tactics

| Tactic | Use Case | Do NOT Use |
|---|---|---|
| `omega` | Linear ℕ/ℤ arithmetic only | For `a < b * a` (non-linear → use `lt_mul_of_one_lt_left`) |
| `lt_mul_of_one_lt_left` | Prove `0 < a → 1 < b → a < b * a` | `omega` for this |
| `linarith` | Real-valued linear inequalities | For ℕ multiplication (not semiring) |
| `positivity` | Prove `0 < product_of_positives` | For abstract inequalities |
| `Nat.mul_le_mul h1 h2` | Prove `a*b ≤ c*d` from `a ≤ c` and `b ≤ d` | `subst` on struct fields |
| `rw [h_field]` | Substitute struct field equalities | `subst` (only works on free vars) |
| `simp [h_bool]` | Eliminate boolean conditionals | `split_ifs` (brittle) |
| `ring` | Algebraic identities | For inequalities |
| `norm_num` | Concrete numeric computation | For symbolic algebra |

**Deprecated / Brittle:**
- `split_ifs` → use `rw [ite_eq_left]` / `rw [ite_eq_right]`
- `if_pos` / `if_neg` → deprecated, use `ite_eq_left` / `ite_eq_right`

---

## 7. Peer Review Quality Gate (Run Before Claiming Paper Is Done)

Before finalizing any Lean-backed paper, self-check ALL of these:

- [ ] `lake build` exits with 0 errors
- [ ] `grep "uses \`sorry\`" build.log` shows ≤1 occurrence, correctly named in abstract
- [ ] FLOP definitions are named `ffnFLOPs` with explicit "attention term NOT modeled" docstring
- [ ] No theorem claims to be novel mathematical research; all scoped as "deployment invariants"
- [ ] No self-authored peer reviews in the paper
- [ ] Affiliation is honest (independent/open-source research, not fictional institution)
- [ ] Accuracy metrics table is present (even if showing limitations)
- [ ] Latency table has sequence-length column to explain variance

---

## 8. Layer Environment Notes

```
/dev/sdb1 → / (OS, 97% full — keep clean)
/dev/sda3 → /mnt/data (916G, data disk)

~/.elan → /mnt/data/home/xavkal/.elan
~/.cache/mathlib → /mnt/data/home/xavkal/.cache/mathlib  (17,494 .ltar files)
formal/.lake → /mnt/data/home/xavkal/lean-builds/anse-formal-lake/.lake
```

Always prefix lake commands with `export PATH="/home/xavkal/.elan/bin:$PATH"`.
