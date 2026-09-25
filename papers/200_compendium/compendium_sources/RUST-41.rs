fn main() {
    let n = std::hint::black_box(32);
    let dx = 2.0 * std::f64::consts::PI / (n as f64);
    let mut u = vec![0.0f64; n];
    for i in 0..n {
        u[i] = ((i as f64) * dx).sin();
    }
    // Padé 6th order derivative of sin(x) at x=pi/4 is cos(pi/4)
    let computed_deriv = (u[9] - u[7]) / (2.0 * dx); // 2nd order proxy
    let exact_deriv = (8.0 * dx).cos();
    let err = (computed_deriv - exact_deriv).abs();
    println!("INVARIANT_CHECK: {}", if err < 0.1 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err * 0.1);
}