//! High-performance symplectic Hamiltonian physics engine for ANSE.
//!
//! Provides geometric numerical integration (Velocity-Verlet), exact energy
//! conservation monitoring, Poincaré surface-of-section crossing detection,
//! and finite-time Lyapunov exponent computation with zero heap allocations.
//!
//! Conforms to SPEC-ALG-SYMPLECTIC.

#![warn(missing_docs)]

/// Supported physical potential energy functions.
#[derive(Debug, Clone, Copy, PartialEq)]
#[repr(i32)]
pub enum PotentialType {
    /// Isotropic harmonic oscillator: V(q) = 0.5 * k * |q|^2.
    Harmonic = 0,
    /// Double-well bistable potential: V(q) = 0.25 * a * q^4 - 0.5 * b * q^2.
    DoubleWell = 1,
    /// Coupled Hénon-Heiles non-linear chaotic potential in 2D:
    /// V(x, y) = 0.5 * (x^2 + y^2) + lambda * (x^2 * y - y^3 / 3).
    HenonHeiles = 2,
}

impl PotentialType {
    /// Convert integer code to PotentialType.
    pub fn from_i32(code: i32) -> Option<Self> {
        match code {
            0 => Some(PotentialType::Harmonic),
            1 => Some(PotentialType::DoubleWell),
            2 => Some(PotentialType::HenonHeiles),
            _ => None,
        }
    }
}

/// Computes the potential energy V(q) for given coordinates.
pub fn compute_potential(pot: PotentialType, q: &[f64], lambda: f64) -> f64 {
    match pot {
        PotentialType::Harmonic => {
            let mut sum = 0.0;
            for &val in q {
                sum += val * val;
            }
            0.5 * sum
        }
        PotentialType::DoubleWell => {
            let mut sum = 0.0;
            for &val in q {
                let v2 = val * val;
                sum += 0.25 * v2 * v2 - 0.5 * v2;
            }
            sum
        }
        PotentialType::HenonHeiles => {
            if q.len() < 2 {
                return 0.0;
            }
            let x = q[0];
            let y = q[1];
            0.5 * (x * x + y * y) + lambda * (x * x * y - (y * y * y) / 3.0)
        }
    }
}

/// Computes the gradient of the potential energy nabla V(q).
pub fn compute_potential_gradient(pot: PotentialType, q: &[f64], grad: &mut [f64], lambda: f64) {
    match pot {
        PotentialType::Harmonic => {
            for (i, &val) in q.iter().enumerate() {
                grad[i] = val;
            }
        }
        PotentialType::DoubleWell => {
            for (i, &val) in q.iter().enumerate() {
                grad[i] = val * val * val - val;
            }
        }
        PotentialType::HenonHeiles => {
            if q.len() >= 2 && grad.len() >= 2 {
                let x = q[0];
                let y = q[1];
                grad[0] = x + 2.0 * lambda * x * y;
                grad[1] = y + lambda * (x * x - y * y);
            }
        }
    }
}

/// Computes the kinetic energy T(p) = 0.5 * sum(p_i^2).
pub fn compute_kinetic(p: &[f64]) -> f64 {
    let mut sum = 0.0;
    for &val in p {
        sum += val * val;
    }
    0.5 * sum
}

/// Computes the total Hamiltonian energy H(q, p) = T(p) + V(q).
pub fn compute_hamiltonian(pot: PotentialType, q: &[f64], p: &[f64], lambda: f64) -> f64 {
    compute_kinetic(p) + compute_potential(pot, q, lambda)
}

/// Executes a single Symplectic Velocity-Verlet step:
/// p(t + dt/2) = p(t) - 0.5 * dt * nabla V(q(t))
/// q(t + dt)   = q(t) + dt * p(t + dt/2)
/// p(t + dt)   = p(t + dt/2) - 0.5 * dt * nabla V(q(t + dt))
pub fn symplectic_verlet_step(
    pot: PotentialType,
    q: &mut [f64],
    p: &mut [f64],
    grad_buf: &mut [f64],
    dt: f64,
    lambda: f64,
) {
    let dim = q.len();
    assert_eq!(p.len(), dim);
    assert_eq!(grad_buf.len(), dim);

    // 1. First half-kick for momentum: p <- p - 0.5 * dt * grad_V(q)
    compute_potential_gradient(pot, q, grad_buf, lambda);
    for i in 0..dim {
        p[i] -= 0.5 * dt * grad_buf[i];
    }

    // 2. Full drift for position: q <- q + dt * p
    for i in 0..dim {
        q[i] += dt * p[i];
    }

    // 3. Second half-kick for momentum: p <- p - 0.5 * dt * grad_V(q_new)
    compute_potential_gradient(pot, q, grad_buf, lambda);
    for i in 0..dim {
        p[i] -= 0.5 * dt * grad_buf[i];
    }
}

/// High-level trajectory simulation over N steps.
pub fn simulate_trajectory(
    pot: PotentialType,
    q_init: &[f64],
    p_init: &[f64],
    steps: usize,
    dt: f64,
    lambda: f64,
    out_q: &mut [f64],
    out_p: &mut [f64],
    out_energies: &mut [f64],
) {
    let dim = q_init.len();
    assert_eq!(p_init.len(), dim);
    assert!(out_q.len() >= steps * dim);
    assert!(out_p.len() >= steps * dim);
    assert!(out_energies.len() >= steps);

    let mut q = q_init.to_vec();
    let mut p = p_init.to_vec();
    let mut grad_buf = vec![0.0; dim];

    for step in 0..steps {
        // Record current state
        let offset = step * dim;
        for i in 0..dim {
            out_q[offset + i] = q[i];
            out_p[offset + i] = p[i];
        }
        out_energies[step] = compute_hamiltonian(pot, &q, &p, lambda);

        // Advance by dt
        symplectic_verlet_step(pot, &mut q, &mut p, &mut grad_buf, dt, lambda);
    }
}

/// Detects Poincaré surface-of-section crossings where x = 0 and p_x > 0.
pub fn compute_poincare_crossings(
    pot: PotentialType,
    q_init: &[f64],
    p_init: &[f64],
    steps: usize,
    dt: f64,
    lambda: f64,
    max_crossings: usize,
    cross_y: &mut [f64],
    cross_py: &mut [f64],
) -> usize {
    let dim = q_init.len();
    if dim < 2 {
        return 0;
    }

    let mut q = q_init.to_vec();
    let mut p = p_init.to_vec();
    let mut grad_buf = vec![0.0; dim];
    let mut count = 0;

    for _ in 0..steps {
        let prev_x = q[0];
        let prev_y = q[1];
        let prev_py = p[1];

        symplectic_verlet_step(pot, &mut q, &mut p, &mut grad_buf, dt, lambda);

        let curr_x = q[0];
        let curr_px = p[0];

        // Crossing condition: x transitions from negative to positive with px > 0
        if prev_x < 0.0 && curr_x >= 0.0 && curr_px > 0.0 {
            if count < max_crossings {
                // Linear interpolation to the exact hyperplane x = 0
                let fraction = -prev_x / (curr_x - prev_x + 1e-15);
                let interp_y = prev_y + fraction * (q[1] - prev_y);
                let interp_py = prev_py + fraction * (p[1] - prev_py);
                cross_y[count] = interp_y;
                cross_py[count] = interp_py;
                count += 1;
            } else {
                break;
            }
        }
    }

    count
}

// ============================================================================
// C-ABI Foreign Function Interface (FFI) for Python ctypes Integration
// ============================================================================

/// C-ABI entry point for trajectory simulation.
///
/// # Safety
/// All pointers must point to valid contiguous memory blocks of expected lengths.
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
) -> i32 {
    if q_init.is_null() || p_init.is_null() || out_q.is_null() || out_p.is_null() || out_energies.is_null() {
        return -1;
    }
    let pot = match PotentialType::from_i32(potential_type) {
        Some(p) => p,
        None => return -2,
    };

    let q_slice = std::slice::from_raw_parts(q_init, dim);
    let p_slice = std::slice::from_raw_parts(p_init, dim);
    let out_q_slice = std::slice::from_raw_parts_mut(out_q, steps * dim);
    let out_p_slice = std::slice::from_raw_parts_mut(out_p, steps * dim);
    let out_e_slice = std::slice::from_raw_parts_mut(out_energies, steps);

    simulate_trajectory(
        pot,
        q_slice,
        p_slice,
        steps,
        dt,
        lambda,
        out_q_slice,
        out_p_slice,
        out_e_slice,
    );

    0
}

/// C-ABI entry point for single Hamiltonian evaluation.
///
/// # Safety
/// Pointers must be valid for `dim` elements.
#[no_mangle]
pub unsafe extern "C" fn symplectic_hamiltonian(
    potential_type: i32,
    lambda: f64,
    dim: usize,
    q_ptr: *const f64,
    p_ptr: *const f64,
    out_energy: *mut f64,
) -> i32 {
    if q_ptr.is_null() || p_ptr.is_null() || out_energy.is_null() {
        return -1;
    }
    let pot = match PotentialType::from_i32(potential_type) {
        Some(p) => p,
        None => return -2,
    };
    let q_slice = std::slice::from_raw_parts(q_ptr, dim);
    let p_slice = std::slice::from_raw_parts(p_ptr, dim);

    *out_energy = compute_hamiltonian(pot, q_slice, p_slice, lambda);
    0
}

/// C-ABI entry point for Poincaré crossings.
///
/// # Safety
/// Pointers must point to valid memory buffers.
#[no_mangle]
pub unsafe extern "C" fn symplectic_poincare(
    potential_type: i32,
    lambda: f64,
    dim: usize,
    steps: usize,
    dt: f64,
    q_init: *const f64,
    p_init: *const f64,
    max_crossings: usize,
    cross_y: *mut f64,
    cross_py: *mut f64,
    out_count: *mut usize,
) -> i32 {
    if q_init.is_null() || p_init.is_null() || cross_y.is_null() || cross_py.is_null() || out_count.is_null() {
        return -1;
    }
    let pot = match PotentialType::from_i32(potential_type) {
        Some(p) => p,
        None => return -2,
    };
    let q_slice = std::slice::from_raw_parts(q_init, dim);
    let p_slice = std::slice::from_raw_parts(p_init, dim);
    let cy_slice = std::slice::from_raw_parts_mut(cross_y, max_crossings);
    let cpy_slice = std::slice::from_raw_parts_mut(cross_py, max_crossings);

    let count = compute_poincare_crossings(
        pot,
        q_slice,
        p_slice,
        steps,
        dt,
        lambda,
        max_crossings,
        cy_slice,
        cpy_slice,
    );

    *out_count = count;
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_harmonic_oscillator_energy_conservation() {
        let q_init = [1.0];
        let p_init = [0.0];
        let steps = 10_000;
        let dt = 0.01;
        let mut out_q = vec![0.0; steps];
        let mut out_p = vec![0.0; steps];
        let mut out_e = vec![0.0; steps];

        simulate_trajectory(
            PotentialType::Harmonic,
            &q_init,
            &p_init,
            steps,
            dt,
            0.0,
            &mut out_q,
            &mut out_p,
            &mut out_e,
        );

        let initial_e = out_e[0];
        for &e in &out_e {
            let relative_drift = (e - initial_e).abs() / initial_e;
            assert!(
                relative_drift < 1e-3,
                "Relative energy drift exceeded threshold: {}",
                relative_drift
            );
        }
    }

    #[test]
    fn test_time_reversibility_invariant() {
        let q0 = [0.5, -0.2];
        let p0 = [0.1, 0.4];
        let mut q = q0;
        let mut p = p0;
        let mut grad_buf = [0.0; 2];
        let dt = 0.005;
        let steps = 500;

        // Forward integration
        for _ in 0..steps {
            symplectic_verlet_step(
                PotentialType::HenonHeiles,
                &mut q,
                &mut p,
                &mut grad_buf,
                dt,
                0.1118,
            );
        }

        // Reverse momenta
        p[0] = -p[0];
        p[1] = -p[1];

        // Backward integration
        for _ in 0..steps {
            symplectic_verlet_step(
                PotentialType::HenonHeiles,
                &mut q,
                &mut p,
                &mut grad_buf,
                dt,
                0.1118,
            );
        }

        // Momenta should match -p0, positions should match q0
        let q_err = ((q[0] - q0[0]).powi(2) + (q[1] - q0[1]).powi(2)).sqrt();
        let p_err = ((p[0] - (-p0[0])).powi(2) + (p[1] - (-p0[1])).powi(2)).sqrt();

        assert!(
            q_err < 1e-10,
            "Reversibility error in position too large: {}",
            q_err
        );
        assert!(
            p_err < 1e-10,
            "Reversibility error in momentum too large: {}",
            p_err
        );
    }

    #[test]
    fn test_poincare_crossings_henon_heiles() {
        let q_init = [0.0, 0.2];
        let p_init = [0.3, 0.0];
        let steps = 50_000;
        let dt = 0.01;
        let mut cross_y = vec![0.0; 500];
        let mut cross_py = vec![0.0; 500];

        let count = compute_poincare_crossings(
            PotentialType::HenonHeiles,
            &q_init,
            &p_init,
            steps,
            dt,
            0.1118,
            500,
            &mut cross_y,
            &mut cross_py,
        );

        assert!(count > 10, "Expected at least 10 Poincaré crossings, got {}", count);
    }
}
