fn main() {
    let w1 = -0.117767998417887e1;
    let w2 = 0.235573213359357e1;
    let w3 = 0.784513610477560e0;
    let w0 = 1.0 - 2.0 * (w1 + w2 + w3);
    let weights = [w3, w2, w1, w0, w1, w2, w3];
    let mut q = 1.0f64;
    let mut p = 0.0f64;
    let h0 = 0.5 * (p * p + q * q);
    let dt = 0.005;
    for _step in 0..500 {
        for &w in &weights {
            let h = w * dt;
            let q_next = q + h * p - 0.5 * h * h * q;
            p = p - 0.5 * h * (q + q_next);
            q = q_next;
        }
    }
    let h_end = 0.5 * (p * p + q * q);
    let drift = (h_end - h0).abs() / h0;
    println!("INVARIANT_CHECK: {}", if drift < 1e-4 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", drift);
}