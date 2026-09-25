fn main() {
    // Cycle graph C_4: Laplacian rows sum to 0
    let l = [
        [ 2.0, -1.0,  0.0, -1.0],
        [-1.0,  2.0, -1.0,  0.0],
        [ 0.0, -1.0,  2.0, -1.0],
        [-1.0,  0.0, -1.0,  2.0]
    ];
    // Invariant: Constant eigenvector eigenvalue == 0
    let mut max_drift = 0.0f64;
    for i in 0..4 {
        let row_sum: f64 = l[i].iter().sum();
        max_drift = max_drift.max(row_sum.abs());
    }
    println!("INVARIANT_CHECK: {}", if max_drift < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_drift);
}