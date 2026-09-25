fn main() {
    let h = [
        (1.0 + 3.0f64.sqrt()) / (4.0 * 2.0f64.sqrt()),
        (3.0 + 3.0f64.sqrt()) / (4.0 * 2.0f64.sqrt()),
        (3.0 - 3.0f64.sqrt()) / (4.0 * 2.0f64.sqrt()),
        (1.0 - 3.0f64.sqrt()) / (4.0 * 2.0f64.sqrt())
    ];
    // Invariant: Filter orthogonality sum(h_i^2) == 1
    let energy: f64 = h.iter().map(|x| x * x).sum();
    let err = (energy - 1.0).abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}