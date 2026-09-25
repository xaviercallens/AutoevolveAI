fn main() {
    let mut r = 1.0f64;
    let dt = 0.0005f64;
    for _ in 0..400 {
        r -= dt / r;
    }
    let r_exact = (1.0 - 2.0 * 0.2f64).sqrt();
    let err = (r - r_exact).abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-3 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}