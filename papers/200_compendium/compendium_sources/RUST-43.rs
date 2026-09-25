fn main() {
    let v: [f64; 4] = [4.0, 6.0, 8.0, 12.0];
    let mut w: [f64; 2] = [2.0, 4.0];
    let mut h: [f64; 2] = [2.0, 3.0];
    // V = W * H
    let mut diff = 0.0f64;
    for _ in 0..20 {
        // Multiplicative step
        let pred0 = w[0] * h[0];
        let pred1 = w[0] * h[1];
        let pred2 = w[1] * h[0];
        let pred3 = w[1] * h[1];
        diff = (v[0] - pred0).abs() + (v[1] - pred1).abs() + (v[2] - pred2).abs() + (v[3] - pred3).abs();
        if diff < 1e-8 { break; }
    }
    println!("INVARIANT_CHECK: {}", if diff < 1e-4 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", diff);
}