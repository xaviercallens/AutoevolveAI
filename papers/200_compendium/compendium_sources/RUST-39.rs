fn main() {
    // min 0.5 * (x1^2 + x2^2) subject to x1 + x2 >= 2
    // Optimal: x1* = 1, x2* = 1, lambda* = 1
    let mut x1 = 0.0f64;
    let mut x2 = 0.0f64;
    let mut lambda = 0.0f64;
    let alpha = 0.1f64;
    for _ in 0..300 {
        let gx1 = x1 - lambda;
        let gx2 = x2 - lambda;
        x1 -= alpha * gx1;
        x2 -= alpha * gx2;
        let c = 2.0 - (x1 + x2);
        lambda = (lambda + alpha * c).max(0.0);
    }

    let kkt_stationarity = (x1 - lambda).abs() + (x2 - lambda).abs();
    let kkt_primal_feasibility = (x1 + x2 - 2.0).abs();
    let err = kkt_stationarity + kkt_primal_feasibility;
    println!("INVARIANT_CHECK: {}", if err < 1e-5 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}