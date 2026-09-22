# Technical Specification: SPEC-ALG-SYMPLECTIC
## Multi-Task Hamiltonian Symplectic Dynamics & Chaos Engine (Rust + Python)

### 1. Mathematical & Physical Foundations
A classical dynamical system with coordinates $q \in \mathbb{R}^d$ and conjugate momenta $p \in \mathbb{R}^d$ is governed by a Hamiltonian function $H(q, p) = T(p) + V(q)$, yielding Hamilton's canonical equations of motion:
$$\dot{q} = \frac{\partial H}{\partial p} = \mathbf{M}^{-1} p$$
$$\dot{p} = -\frac{\partial H}{\partial q} = -\nabla V(q)$$

Standard non-symplectic numerical integrators (e.g. standard explicit Euler or classical Runge-Kutta RK4) introduce artificial dissipation or secular energy drift over long horizons $T \gg 1$.
In contrast, a **Symplectic Integrator** (such as the Velocity Verlet algorithm) preserves the differential 2-form:
$$\omega = \sum_{i=1}^d dq_i \wedge dp_i$$
preserving phase-space volume (Liouville's theorem) and ensuring that the discrete numerical trajectory lies on the invariant manifold of a shadowed Hamiltonian $\tilde{H} = H + O(\Delta t^2)$, yielding bounded energy oscillation without secular drift.

### 2. Supported Hamiltonian Potentials
1. **Harmonic Oscillator**:
   $$V(q) = \frac{1}{2} k q^2, \quad \nabla V(q) = k q$$
2. **Double-Well Potential (Bistable System)**:
   $$V(q) = \frac{a}{4} q^4 - \frac{b}{2} q^2, \quad \nabla V(q) = a q^3 - b q$$
3. **Coupled Hénon-Heiles Non-Linear Chaotic Potential ($d=2$)**:
   $$V(x, y) = \frac{1}{2}(x^2 + y^2) + \lambda \left(x^2 y - \frac{1}{3} y^3\right)$$
   $$\nabla V(x, y) = \begin{bmatrix} x + 2\lambda x y \\ y + \lambda(x^2 - y^2) \end{bmatrix}$$

### 3. Multi-Task Core Operations
- **Task 1: Symplectic Velocity-Verlet Step**:
  $$p_{n+1/2} = p_n - \frac{\Delta t}{2} \nabla V(q_n)$$
  $$q_{n+1} = q_n + \Delta t \, \mathbf{M}^{-1} p_{n+1/2}$$
  $$p_{n+1} = p_{n+1/2} - \frac{\Delta t}{2} \nabla V(q_{n+1})$$
- **Task 2: Energy Conservation & Drift Verification**:
  Computes $H_n = T(p_n) + V(q_n)$ at every step. Asserts relative drift:
  $$\max_n \left|\frac{H_n - H_0}{H_0}\right| < 10^{-3} \quad (\text{for } \Delta t \le 0.01)$$
- **Task 3: Poincaré Surface-of-Section**:
  Detects transversal crossings of a phase space plane (e.g. $x = 0$ with $p_x > 0$) using linear interpolation:
  $$t^* = t_n + \Delta t \cdot \frac{-x_n}{x_{n+1} - x_n}$$
- **Task 4: Finite-Time Lyapunov Exponent (FTLE) & Chaos Diagnosis**:
  Tracks two trajectories initialized with an infinitesimal separation $\delta_0 = 10^{-8}$.
  Computes the divergence rate $\lambda(t) = \frac{1}{t} \ln \frac{\|\delta(t)\|}{\|\delta_0\|}$.

### 4. Rust C-ABI Interface (`crates/anse_physics`)
```rust
#[no_mangle]
pub unsafe extern "C" fn symplectic_integrate(
    potential_type: i32,     // 0: Harmonic, 1: Double-well, 2: Henon-Heiles
    lambda: f64,             // Coupling parameter for Henon-Heiles
    dim: usize,              // Dimensionality d
    steps: usize,            // Total integration steps N
    dt: f64,                 // Time step Delta t
    q_init: *const f64,      // Initial position vector (length dim)
    p_init: *const f64,      // Initial momentum vector (length dim)
    out_q: *mut f64,         // Output positions array (N * dim)
    out_p: *mut f64,         // Output momenta array (N * dim)
    out_energies: *mut f64,  // Output total Hamiltonian energy (length N)
) -> i32;
```

### 5. Thermodynamic Criteria & Invariants
1. **Time Reversibility**: Reversing $p \to -p$ and integrating $N$ steps returns to $(q_0, -p_0)$ with error $< 10^{-11}$.
2. **Computational Speedup**: Rust SIMD kernel must achieve $> 10\times$ speedup over interpreted Python loop, satisfying $\Delta E < 0$.
3. **Zero-Stub Enforcement**: Both Rust and Python implementations contain zero stub markers, mock data, or unhandled exceptions.
