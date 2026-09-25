fn main() {
    // Harmonic oscillator ground state psi(x) = exp(-alpha * x^2 / 2)
    // E_L(x) = alpha + x^2 (1 - alpha^2)
    // When alpha=1, E_L(x) = 1.0 for all x (zero-variance principle)
    let alpha = 1.0f64;
    let x_vals = [-1.5, -0.5, 0.0, 0.7, 1.8];
    let mut var = 0.0f64;
    for &x in &x_vals {
        let e_l = alpha + x * x * (1.0 - alpha * alpha);
        var += (e_l - 1.0).powi(2);
    }
    let zero_var_err = var / (x_vals.len() as f64);
    println!("INVARIANT_CHECK: {}", if zero_var_err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", zero_var_err);
}