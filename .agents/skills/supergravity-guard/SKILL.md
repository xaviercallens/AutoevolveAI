---
name: supergravity-guard
description: Integrate and enforce SuperGravity zero-trust execution attestation, anti-simulation AST inspection, ephemeral context management, and deterministic verification in any autonomous agent workflow.
---

# SuperGravity Guard Agent Skill

This skill equips any autonomous coding agent (Antigravity, Claude Code, Cursor, Copilot) with the **SuperGravity Zero-Trust Verification Framework**.

## Core Capabilities
1. **Zero-Trust Completion Check**: Never accept natural language task completion without calling the cryptographic attestation gate.
2. **Anti-Simulation & Anti-Stub Audit**: Automatically scans git diffs for empty functions (`pass`, `...`), `NotImplementedError`, or fake mock variables (`mock_*`, `dummy_*`, `fake_*`).
3. **Ephemeral Context Pruning**: Automatically offloads bulky outputs (>60 lines) into `.scratchpad/<hash>.log` and references them via addressable tokens.
4. **Execution Receipt Verification**: Asserts that unit tests physically execute production code modules (`sys.settrace`).

---

## When to Use This Skill
- Before marking any development task or PR subtask as "COMPLETE".
- When inspecting agent-generated code for hidden stubs, hallucinated dependencies, or fake synthetic datasets.
- When running long test suites or commands that threaten to overflow context limits.
- When auditing code against formal computational physics principles ($E = \text{Time} + \text{RAM}$).

---

## Operational Instructions

### Step 1: Pre-Audit Working Tree
Before running any tests, run the AST implementation auditor on staged and unstaged changes:
```bash
python execution_attestation.py
```
- If the exit code is non-zero, inspect the output for flagged stubs or mock data.
- Refactor the code to provide a genuine, functional implementation before proceeding.

### Step 2: Verify Runtime Execution Trace
Assert that the unit tests actually executed the target production module:
```bash
python execution_attestation.py <target_module> <test_path>
# Example:
python execution_attestation.py anse.symbolic tests/phase1/test_sandbox.py
```
- If successful, this command mints a cryptographic proof receipt in `.antigravity_attestation` and prints:
  `[PROOF_TOKEN: <token_hex>]`

### Step 3: Offload Heavy Tool Outputs
When executing scripts or commands expected to emit large logs, pipe through the context manager:
```python
from context_manager import truncate_and_offload_context

raw_log = run_command(...)
safe_prompt_context = truncate_and_offload_context("tool_execution", raw_log)
```

### Step 4: Verify 5-Gate Hardened Quality Pipeline
Before pushing or merging, run the hardened static analyzer:
```bash
python .antigravity/hooks/hardened_gate.py
```
Ensures:
- Radon Cyclomatic Complexity $\le 10$ across all methods.
- Zero Ruff lint errors.
- Zero Bandit security vulnerabilities.
- Zero dead code reported by Vulture.
- Strict MyPy type invariant compliance.

---

### Step 5: ASW Swarm Disciplines & AI Slop Elimination (vendor/antigravity-swarm)
Adopt the evidence-driven ASW swarm lifecycle (`asw-plan` -> `start-work` -> `asw` -> `asw-review`):
1. **Binding Success Contract**:
   - Define exact observable criteria (happy path, edge case, regression) before modifying code.
   - Lock current behavior with regression or characterization tests first.
2. **AI Slop & Boilerplate Elimination**:
   - Strip redundant comments restating the code.
   - Remove hollow docstrings on self-explanatory functions.
   - Prevent over-defensive boilerplate that obscures core algorithms.
3. **Local SLM Pre-Flight Critic Review**:
   - Run the candidate implementation through the local Critic Model:
     ```python
     from anse.guard.critic import CodeCritic

     result = CodeCritic().evaluate(code, prompt_context="Task context")
     assert result.is_accepted, f"Critic Rejected: {result.reason}"
     ```
   - Rejects code immediately with an energy penalty ($E = 10^6$) if stubs or fake data are found.
4. **Final Swarm Review**:
   - Verify that test output is real, non-synthetic, and produces zero diff leakage in public packages.

