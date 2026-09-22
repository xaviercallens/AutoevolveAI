# Technical Specification: Closed Loop v2 (SPEC-ANSE-LOOP-V2)
## Multi-Task Neuro-Symbolic Self-Evolution, C-ABI Symplectic Physics, and Zero-Trust RL Alignment

---

### 1. Executive Summary & Architectural Paradigm
Closed Loop v2 establishes the autonomous self-improving loop of the **Autopoietic Neuro-Symbolic Energy-based Model (ANSE)**. In this architecture, AI code generation is not judged by subjective human preference or syntactic plausibility, but by the physical laws of computation:
1. **Thermodynamic Energy Function ($E$):** Every optimization, algorithm, or neural module executed in the deterministic sandbox (`anse/symbolic/sandbox.py`) is mapped to an energy scalar:
   $$E = \text{duration\_ms} + \text{peak\_ram\_mb}$$
   An algorithmic candidate is accepted for autopoietic promotion if and only if it satisfies the strict monotonicity condition:
   $$\Delta E = E_{\text{candidate}} - E_{\text{baseline}} < 0$$
2. **Physical Symplectic Invariants:** For dynamical systems, numerical discretization must preserve the symplectic 2-form $\omega = \sum dq \wedge dp$. Energy drift must remain bounded without secular divergence:
   $$\max_{n \in [0, N]} \left|\frac{H_n - H_0}{H_0}\right| < 10^{-3}$$
3. **Zero-Trust Hardness & AST Attestation:** The system strictly rejects hallucinated stubs, mock variables (`fake_`, `mock_`, `test_data_`), empty `pass` blocks, or unhandled exceptions. Code must achieve 100% AST integrity attested by `execution_attestation.py`.
4. **Dual-Track RL Closed Loop (DPO + GRPO):** Validated physics implementations form the chosen pairs ($y_w$) and flawed, non-symplectic Euler implementations form the rejected pairs ($y_l$), producing an ongoing training corpus for local SLM critics (e.g. Qwen 2.5 Coder 3B) and online policy gradient advantage estimation.
5. **Antigravity Swarm Command Deck (ASCD):** Real-time SCADA telemetry dashboard broadcasting 60 FPS state, active agents, token throughput, thermodynamic energy, and live DAG execution over WebSockets.

---

### 2. The Multi-Task Computational Physics Engine (`crates/anse_physics` + Python)

#### 2.1 Hamiltonian Dynamics Foundations
Let $q \in \mathbb{R}^d$ denote generalized coordinates and $p \in \mathbb{R}^d$ conjugate momenta. The total Hamiltonian is $H(q, p) = T(p) + V(q) = \frac{1}{2} p^T \mathbf{M}^{-1} p + V(q)$.
Hamilton's equations:
$$\dot{q} = \frac{\partial H}{\partial p}, \quad \dot{p} = -\frac{\partial H}{\partial q} = -\nabla V(q)$$

The engine supports three fundamental Hamiltonian potentials:
1. **Harmonic Oscillator (Linear Baseline):**
   $$V(q) = \frac{1}{2} k q^2, \quad \nabla V(q) = k q$$
2. **Double-Well Bistable Potential (Symmetry Breaking):**
   $$V(q) = \frac{a}{4} q^4 - \frac{b}{2} q^2, \quad \nabla V(q) = a q^3 - b q$$
3. **Coupled Hénon-Heiles Non-Linear Chaotic Potential ($d=2$):**
   $$V(x, y) = \frac{1}{2}(x^2 + y^2) + \lambda \left(x^2 y - \frac{1}{3} y^3\right)$$
   $$\nabla V(x, y) = \begin{bmatrix} x + 2\lambda x y \\ y + \lambda(x^2 - y^2) \end{bmatrix}$$

#### 2.2 Symplectic Velocity-Verlet Integration
To prevent the artificial dissipation and secular exponential energy drift of standard explicit integrators, the engine uses the second-order symplectic Velocity-Verlet operator:
$$p_{n+1/2} = p_n - \frac{\Delta t}{2} \nabla V(q_n)$$
$$q_{n+1} = q_n + \Delta t \, \mathbf{M}^{-1} p_{n+1/2}$$
$$p_{n+1} = p_{n+1/2} - \frac{\Delta t}{2} \nabla V(q_{n+1})$$

#### 2.3 Diagnostic Tasks
- **Poincaré Surface of Section:** Tracks transversal hyper-plane intersections ($x = 0$ with $p_x > 0$) with linear sub-step interpolation:
  $$t^* = t_n + \Delta t \cdot \frac{-x_n}{x_{n+1} - x_n}, \quad y^* = y_n + \frac{t^* - t_n}{\Delta t}(y_{n+1} - y_n)$$
- **Finite-Time Lyapunov Exponent (FTLE):** Tracks shadow trajectory separated by $\delta_0 = 10^{-8}$ to measure chaotic divergence:
  $$\lambda(t) = \frac{1}{t} \ln \left(\frac{\|\delta(t)\|}{\|\delta_0\|}\right)$$

#### 2.4 High-Performance Rust C-ABI Kernel
The inner integration loop is implemented in Rust with AVX2/SIMD alignment (`crates/anse_physics/src/lib.rs`) and exposed via C-ABI:
```rust
#[no_mangle]
pub unsafe extern "C" fn symplectic_integrate(
    potential_type: i32,
    lambda: f64,
    dim: usize,
    steps: usize,
    dt: f64,
    q_init: *const f64,
    p_init: *const f64,
    out_q: *mut f64,
    out_p: *mut f64,
    out_energies: *mut f64,
) -> i32;
```
Python bindings in `anse/algorithms/symplectic.py` bind directly to `libanse_physics.so` with fallback to pure Python Velocity-Verlet.

---

### 3. Zero-Trust Hardness & AST Attestation
All generated code is audited by `supergravity-guard` before execution:
1. **Anti-Stub AST Inspection:** Prohibits `ast.Pass`, empty functions, and docstring-only bodies.
2. **Anti-Mock / Anti-Simulation:** Prohibits mock libraries (`unittest.mock`, `MagicMock`), dummy arrays, or hardcoded answers.
3. **Deterministic Sandbox Isolation:** Enforces 5000ms timeouts, resource limits via `setrlimit` (CPU time, memory), and cleans temporary artifacts.

---

### 4. Reinforcement Learning Closed Loop (DPO & GRPO)

#### 4.1 DPO Dataset Specification (`results/dpo_multitask_dataset.jsonl`)
Each record contains:
- `prompt`: Standard ChatML format specifying rigorous algorithmic and physics requirements.
- `chosen`: Verified, zero-stub, SIMD-accelerated or heap-optimal implementation passing unit tests and physical invariants.
- `rejected`: Naive, non-symplectic, unindexed, or stubbed implementation exhibiting secular drift, infinite loops, or $O(N)$ bottlenecks.
- `metadata`: Contains `use_case_id`, `speedup`, `energy_delta`, `thermodynamic_pass`, and failure root-causes.

#### 4.2 GRPO Advantage & Reward Computation
For each group of generated solutions $\{y_1, y_2, \dots, y_G\}$:
1. **Code Hygiene Reward:** $r_{\text{hygiene}} \in [-1.0, +1.0]$ based on AST complexity, zero stubs, and docstrings.
2. **Execution Verdict Reward:** $r_{\text{verdict}} = +1.0$ (passed) or $-1.0$ (runtime failure / invariant breach).
3. **Computational Physics Reward:**
   $$r_{\text{phys}} = \ln(\max(1.0, \text{speedup})) - \frac{\Delta E}{1000.0}$$
4. **Composite Reward:**
   $$R_i = r_{\text{verdict}} + r_{\text{hygiene}} + 0.5 \cdot r_{\text{phys}}$$
5. **Group Relative Advantage:**
   $$A_i = \frac{R_i - \text{mean}(\{R_j\})}{\text{std}(\{R_j\}) + \epsilon}$$

---

### 5. Swarm Control Center (ASCD) Web Architecture
- **Web API:** FastAPI app running on `PORT=5000` (`web/server.py`).
- **Telemetry Endpoints:**
  - `GET /api/ascd/telemetry`: Returns active agents, token throughput, host CPU/RAM, thermodynamic energy $E$, and DPO counts.
  - `POST /api/ascd/halt`: God-mode emergency halt / resume switch.
  - `POST /api/ascd/dpo-feedback`: Direct injection of human or automated preference judgments into the DPO pipeline.
  - `GET /api/ascd/physics-telemetry`: Symplectic physics benchmarking data and phase space portraits.
  - `WebSocket /ws/ascd`: High-frequency 60 FPS virtualized event stream.
- **Frontend Dashboard:** Dark-mode glassmorphism interface in `web/index.html` featuring interactive tabs for Concepts, Evolution Lab, PR Factory, and the ASCD Command Deck.

---

### 6. Verification and Success Gates
1. **Physics Gate:** Velocity-Verlet relative energy drift $< 10^{-3}$ over $50,000$ steps; explicit Euler drift $> 10^{-1}$ (confirming clear preference distinction).
2. **Thermodynamic Gate:** Native Rust SIMD achieves $> 1.5\times$ speedup and $\Delta E < 0$.
3. **Code Quality Gate:** 100% pytest pass on `tests/algorithms/test_symplectic.py` and zero lint/AST violations.
4. **Data Pipeline Gate:** `results/dpo_multitask_dataset.jsonl` contains all 6 core neuro-symbolic tasks (UC1 through UC6), successfully evaluated by `scripts/run_multitask_rl_eval.py`.
5. **Web Gateway Gate:** UI renders telemetry HUD, agent statuses, and physics metrics with zero console errors.
