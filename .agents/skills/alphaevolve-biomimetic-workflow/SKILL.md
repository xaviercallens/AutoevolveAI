---
name: alphaevolve-biomimetic-workflow
description: Execute the AlphaEvolve + Genetic Algorithm + Biomimetic MAP-Elites evolution workflow for AutoevolveAI / ANSE. Combines AlphaEvolve SEARCH/REPLACE diff evolution, AST genetic crossover and structural GP mutation (memoization, strength reduction, loop comprehension), NSGA-II Pareto-front non-dominated sorting, epsilon-Lexicase selection, diploid dominance masking, Artificial Immune System (AIS) negative selection, and Strong AI Coding Hardness (ARGOS-CYBER-001..005, ARGOS-EPIST-006, ARGOS-HARD-007..010).
---

# AlphaEvolve + Genetic Algorithm + Biomimetic Evolution & Strong Hardness Workflow

This workflow executes multi-island MAP-Elites + NSGA-II neuro-symbolic genetic evolution ([`anse/autopoiesis/alphaevolve_biomimetic.py`](file:///home/xavkal/xdev/AutoevolveAI/anse/autopoiesis/alphaevolve_biomimetic.py)) integrated with the ANSE Phase 3 Autopoiesis Hypervisor ([`run_phase3_evolution.py --uc 7`](file:///home/xavkal/xdev/AutoevolveAI/run_phase3_evolution.py)), the Gemini 4 Argon evolutionary self-healer ([`generate_and_evolve_hardened`](file:///home/xavkal/xdev/AutoevolveAI/anse/core/self_healing.py)), and the Antigravity CLI Harness (`python -m antigravity_harness alphaevolve`).

## 0. Next generation: ReticuLean

Two things this engine does not do are addressed by
[`reticulean-evolution`](../reticulean-evolution/SKILL.md) and
[`docs/RETICULEAN_PROPOSAL.md`](file:///home/xavkal/xdev/AutoevolveAI/docs/RETICULEAN_PROPOSAL.md):

* **No rung of the fitness vector is kernel-checked.** `(latency, memory,
  metabolic_energy, invariant_error)` are all empirical, and `ARGOS-HARD-008`
  blocks only the crudest input-ignoring gaming. ReticuLean adds a Lean-4 rung
  read via `#print axioms`, which `sorry` cannot pass.
* **Whether `homologous_crossover` actually recombines is never measured.**
  ReticuLean treats a candidate's behavioural profile over a probe battery as an
  aligned sequence, so the Reticulata quartet certificate decides it. Validated
  on synthetic arms: the margin separates clonal from recombinant populations,
  the violating count does not survive saturation, and both rate extremes are
  unusable.

Use this skill to run the existing engine; use `reticulean-evolution` when adding
an operator, or when asked whether crossover contributes at all.

## 1. Biomimetic Total Free Energy & 4D NSGA-II Pareto Objective

Every candidate genome is evaluated against both the scalar biomimetic Hamiltonian:

$$E_{\text{bio}}(c) = E_{\text{phys}}(c) + \lambda_{\text{epi}}\,\Omega_{\text{chromatin}}(c) + \lambda_{\text{AIS}}\,\Phi_{\text{non-self}}(c) + \lambda_{\text{allostasis}}\,\Psi_{\text{drift}}(c)$$

and the 4D NSGA-II non-dominated Pareto minimization vector:

$$\mathbf{f}(g) = \bigl(\text{latency\_ms}(g),\; \text{memory\_mb}(g),\; \text{metabolic\_energy}(g),\; \text{invariant\_error}(g)\bigr)$$

with **Crowding Distance** diversity preservation (`compute_pareto_fronts`) and **$\epsilon$-Lexicase Parent Selection** (`select_parent_lexicase`).

## 2. Structural AST Genetic Programming Operators (`ASTGeneticOperators`)

- **Auto-Memoization (`apply_memoization_mutation`):** Detects recursive functions lacking cache decorators and injects `from functools import lru_cache` + `@lru_cache(maxsize=None)`, evolving $O(2^n)$ exponential recursion into $O(n)$ dynamic programming without external LLM hints.
- **Algebraic Strength Reduction (`apply_strength_reduction_mutation`):** Rewrites `x ** 2` $\to$ `x * x` and `x ** 3` $\to$ `(x * x) * x` in hot expressions.
- **Loop-to-Comprehension Vectorization (`apply_loop_comprehension_mutation`):** Transforms `acc = []; for x in it: [if c:] acc.append(expr)` into `[expr for x in it [if c]]`.
- **Homologous Crossover (`homologous_crossover`):** Recombines AST functions across diploid parents while protecting methylated (`heterochromatin`) loci.
- **AlphaEvolve Diff Patching (`apply_alphaevolve_diff`):** Applies `<<<<<<< SEARCH ... ======= ... >>>>>>> REPLACE` blocks with AST syntax rollback safety.

## 3. Strong AI Coding Hardness Rules (`ArgosCyberDefenseAuditor`)

- `ARGOS-CYBER-001..005`: Blocks `os.system`, `subprocess(..., shell=True)`, `eval`, `exec`, `pickle.loads`, `marshal.loads`, unsafe `yaml.load`, and `torch.load(..., weights_only=False)`.
- `ARGOS-EPIST-006`: Blocks hardcoded `float('nan')` / `float('inf')` returns in objective/energy functions.
- `ARGOS-HARD-007`: Blocks silent exception swallowing (`except ...: pass` / `except ...: ...`).
- `ARGOS-HARD-008`: Blocks input-ignoring specification gaming (functions with explicit parameters returning constant literals without reading any input parameter).
- `ARGOS-HARD-009`: Blocks sandbox/timer monkey-patching (`time.perf_counter = ...`, `sys.modules = ...`, `builtins.* = ...`).
- `ARGOS-HARD-010`: Blocks dynamic import/FFI sandbox escapes (`__import__`, `ctypes.CDLL`, `shutil.rmtree`).

## 4. CLI & Workflow Commands

```bash
# 1. Single-file AlphaEvolve + Biomimetic evolution via CLI
uv run python -m antigravity_harness alphaevolve <target_file.py> --generations 5 --islands 3

# 2. Phase 3 Autopoiesis Workflow (UC7 + Gate G7)
uv run python run_phase3_evolution.py --uc 7 --limit 2 --samples 8 --out results/alphaevolve_workflow

# 3. Computational Physics & Applied Mathematics Kernel Evolution Pass
uv run python -m scripts.run_alphaevolve_physics_math_kernel

# 4. Unit Test Suite
uv run pytest tests/unit/test_alphaevolve_biomimetic.py tests/unit/test_gemini_argos_harness.py -q
```
