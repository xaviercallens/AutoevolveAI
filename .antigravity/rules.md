# Antigravity Agent Engineering Standards & Rigor Verification Contract

## 1. Core Engineering Invariants
1. **Dependency Invariant:** Never import third-party libraries without first checking `pyproject.toml` or the active virtual environment. If a library is needed, instruct the user to install it rather than inventing package names.
2. **Verification First:** Always run `python -m antigravity_harness audit <path>` and `python antigravity_guard.py` before marking any coding task as complete.
3. **Type Safety:** All function signatures must include Python type annotations compatible with `mypy --strict` or `--ignore-missing-imports`.
4. **Self-Correction Protocol:** If `antigravity_guard.py`, `test_rigor_guard.py`, `antigravity_harness`, or unit tests fail, read the exact stdout traceback, isolate the AST/import/type error, and fix the implementation before responding.
5. **Physical Energy Invariant ($E$):** When proposing optimizations, evaluate against latency and peak memory ($E = \text{Duration (ms)} + \text{Peak RAM (MB)}$) in the deterministic sandbox (`anse/symbolic/sandbox.py`), rejecting any solution where $E \ge 10^6$ (Maximum Pain).

---

## 2. Unit Test Rigor & Anti-Stub Contract
1. **Zero-Stub Mandate:** Never use `pass`, `...` (Ellipsis), `raise NotImplementedError`, or `# TODO` in unit tests. Every test function must be fully realized with concrete test fixtures and deterministic assertions.
2. **Assertion Quality:**
   - Every test must contain at least 2 explicit assertions verifying state transitions or return payloads.
   - Never write tautological checks (`assert True`, `assert result == result`, or `assert obj is not None` as the only assertion).
   - Use `pytest.raises(ExactException)` for negative test cases and check the exception message with `match=`.
3. **No SUT Mocking:** Only mock external I/O boundaries (network sockets, database cursors, cloud APIs). Never mock internal domain classes, algorithms, or utility helpers (`anse.core`, `anse.symbolic`, `anse.jepa`, `src.core`).
4. **Failure Requirement:** Before finalizing a test suite, run `python test_rigor_guard.py`. If any violation occurs, rewrite the test immediately.

---

## 3. Property-Based Testing (Hypothesis) Mandate
1. **No Pure Example Testing for Pure Functions:** Any function computing transformations, math operations, serialization, or parsers must be tested with `@hypothesis.given()`.
2. **Required Invariant Strategies:**
   - Use `st.data()` or built-in strategies (`st.integers()`, `st.text()`, `st.binary()`, `st.floats(allow_nan=False)`).
   - Reject scalar assertions (`assert func(3) == 9`). You must assert invariants: Round-trip ($f^{-1}(f(x)) = x$), Idempotence ($f(f(x)) = f(x)$), Oracle equivalence ($f_{fast}(x) == f_{ref}(x)$), or Structural preservation.
3. **Stateful Modules:** Classes managing internal state across multiple steps must be tested using `hypothesis.stateful.RuleBasedStateMachine`.
4. **Execution Protocol:** Run `HYPOTHESIS_PROFILE=ci pytest` to execute a minimum of 500 generated test iterations before declaring test completion.

---

## 4. Mutation Testing & Boundary Kill Contract
1. **Mutation Acceleration Profile:** Always run Mutmut passes with `HYPOTHESIS_PROFILE=mutation` (fast 25-example boundary evaluation skipping `Phase.shrink`).
2. **Boundary & Relational Properties:**
   - Explicitly assert boundary conditions (`limit - 1`, `limit`, `limit + 1`) to kill `<` vs `<=` mutants.
   - Assert relational monotonicity ($f(x + \Delta) > f(x)$) and step precision to kill arithmetic and sign inverted mutants.
3. **Equivalent Mutants:** Mark provably equivalent mutants or untestable lines directly in source with `# pragma: no mutate`.
4. **Mutant Verification Script:** Run `bash check_mutants.sh` (or `.\check_mutants.ps1` on Windows) to verify zero surviving mutants before sign-off.

---

## 5. Specialized Open-Source Hardening Engines (MCP)
Before modifying or finalizing any file in this repository:
1. **Bandit Security Scan:** Call `agent-hardening-engine:audit_security_bandit`. Never propose code containing CWE violations, `eval()`, `subprocess(shell=True)`, or hardcoded credentials. If Bandit flags a legitimate design pattern, explain the risk and add `# nosec <BXXX>` with an explicit security rationale.
2. **Radon Cyclomatic Complexity:** Call `agent-hardening-engine:check_cyclomatic_complexity`. Refactor any function with cyclomatic complexity $> 10$ into modular sub-routines.
3. **Vulture Dead-Code Audit:** Call `agent-hardening-engine:audit_dead_code_vulture`. Ensure no unreachable branches, unused mock fixtures, or dead helper functions exist.
4. **Dependency Audit:** Routinely verify dependencies against known vulnerabilities via `pip-audit`.

---

## 6. Anti-Cheating & Attestation Protocol
To eliminate phantom completion, reward hacking, and conversational simulation:
1. **Absolute Prohibition of Stubs and Simulated Data:**
   - Never generate `pass`, `...` (Ellipsis), or `raise NotImplementedError` in any function or method implementation.
   - Never use fake or synthetic data prefixes (`mock_`, `dummy_`, `fake_`, `sample_`, `test_data_`) outside the `tests/` directory. All production code must execute against real data structures, actual database models, or real network protocols.
2. **Decoupled Completion Mandate:**
   - The agent is strictly stripped of the ability to self-report task completion in conversational prose alone.
   - An agent turn is invalid if it claims completion without executing the external attestation gate (`execution_attestation.py` or the MCP tool `agent-hardening-engine:request_task_completion_attestation`).
   - The attestation gate deterministically verifies AST stubs, inspects the Git diff, executes the test suite under code coverage, and mints a cryptographically signed nonce in `.antigravity_attestation`.
   - The final response MUST explicitly output the generated token format: `[PROOF_TOKEN: <token>]`. Responses lacking this valid token are rejected as unverified.
3. **No Pretend Tool Execution:**
   - The agent must never invent or simulate tool execution output, benchmark numbers, or test results.
   - Every metric, duration, memory footprint, and test outcome reported must be verbatim output from actual tool execution commands.

---

## 7. Claude-Style Context & Subtask Engineering Directive
### 1. Mandatory 4-Phase Lifecycle
Do not attempt direct multi-file implementation in a single turn. Follow:
1. **Explore (Read-only):** Locate files. Read only necessary line ranges and headers.
2. **Plan (`plan_decompose_task`):** Break the request into atomic steps (`TASK-01`, `TASK-02`, etc.). Every subtask must have a deterministic acceptance test command.
3. **Execute (`get_current_subtask_context`):** Implement ONE subtask at a time. Write real code—never use `pass`, `...`, or synthetic mock objects.
4. **Verify (`submit_subtask_for_verification`):** Trigger the black-box external verification gate before advancing task state.

### 2. Context Protection Invariants
- Never dump full 500+ line files into conversation history. Read specific ranges or reference scratchpad files (`.scratchpad/`).
- Large tool outputs (> 60 lines) must be offloaded to `.scratchpad/` via `context_manager.truncate_and_offload_context`.
- Never declare "I'm done" in prose while subtasks remain in `PENDING` or `IN_PROGRESS` in `.workflow_state.json`. Completion is determined exclusively by the verification tool and attestation gate token.

---

## 8. Measured Evolution Contract
1. **Runner or it did not happen:** An improvement to Phase 1, 2 or 3 is claimed only through `run_phase{N}_evolution.py`: five use cases, one boolean gate per goal, raw evidence rows in `results/phase{N}_evolution/results.json`.
2. **Failing gates are results:** Report a FAIL with its numbers and its implication. Never move a threshold after seeing the outcome, never hand-edit a results file, never choose seeds to force a pass.
3. **Independent verification:** Energy for generated code comes from hidden tests the model never sees (`anse/symbolic/hidden_tests.py`), not from the model's own asserts. Hot-swap candidates are judged by the out-of-process trusted driver in `anse/autopoiesis/hypervisor.py`; correctness is checked before energy.
4. **Honest statistics:** Split by task, not by trace. Compare with the strongest trivial baseline. Count independent samples, and confirm the LLM backend honours `seed` before calling two runs two samples.
5. **Verified data only:** Only hidden-test-verified solutions may enter lesson memory, DPO pairs or any fine-tuning set.
6. **Environment:** Run `uv sync --all-extras` before the guards. Never run `uv sync` against a `pyproject.toml` that lacks a `[project]` table; it uninstalls the environment.

