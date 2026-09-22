# Antigravity IDE v2 Session Hardening & Verification Protocol

## Active Hardening Level: MAXIMUM (Tier 1 Rigor)

In this Antigravity IDE v2 session, the following zero-trust hardness invariants are strictly enforced:

### 1. Anti-Stub & Zero-Simulation Mandate
- **Zero Placeholder Code:** Functions and methods must contain concrete, operational logic. `pass`, `...` (Ellipsis), `raise NotImplementedError`, and `# TODO` comments are strictly rejected.
- **Zero Fake Data:** Variables named `mock_*`, `dummy_*`, `fake_*`, or `sample_*` are banned outside `tests/`.
- **AST Whistleblower:** Any Python modification is automatically audited post-edit via `.agents/scripts/post_tool_guard.py`.

### 2. Physical Energy Invariant ($E$)
- Every algorithm, data structure, or neural operator must satisfy the thermodynamic boundary:
  $$E = \text{Duration (ms)} + \text{Peak RAM (MB)}$$
- Proposed optimizations are evaluated under the strict condition $\Delta E = E_{\text{candidate}} - E_{\text{baseline}} < 0$.
- Sandbox failure or timeout incurs Maximum Pain ($E = 10^6$) and causes immediate rejection.

### 3. Formal Lean 4 Mathematical Invariant
- Every logical rule, state transition, or theorem modification must be backed by a sound proof in `formal/ANSE/`.
- `cd formal && lake build` must succeed without `sorry` declarations.

### 4. Zero-Trust Cryptographic Proof of Execution
- Natural language declarations of task completion are considered non-binding.
- Tasks are completed only upon generating a signed attestation token:
  ```bash
  python execution_attestation.py <target_module> <test_path>
  ```
- Output must display: `[PROOF_TOKEN: <token>]`.

### 5. Multi-Tool Hardened Gate Pipeline
Before finalizing tasks, code must pass:
1. **Radon:** Cyclomatic Complexity $\le 10$ across all methods.
2. **Bandit:** Zero high/medium security vulnerabilities.
3. **Ruff:** Clean lint and style compliance.
4. **Vulture:** Zero unreachable dead code.
5. **MyPy:** Strict type safety invariants.
