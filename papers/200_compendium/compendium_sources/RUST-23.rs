fn main() {
    let n_elem = std::hint::black_box(16);
    let dx = 1.0 / (n_elem as f64);
    let xi = [-1.0 / 3.0f64.sqrt(), 1.0 / 3.0f64.sqrt()];
    let w = [1.0, 1.0];
    let mut u = vec![[0.0f64; 2]; n_elem];
    for e in 0..n_elem {
        let x_center = (e as f64 + 0.5) * dx;
        for i in 0..2 {
            let x = x_center + 0.5 * dx * xi[i];
            u[e][i] = (2.0 * std::f64::consts::PI * x).sin();
        }
    }
    let mut l2_0 = 0.0f64;
    for e in 0..n_elem {
        for i in 0..2 { l2_0 += w[i] * u[e][i] * u[e][i] * 0.5 * dx; }
    }
    let exact_l2 = 0.5;
    let err = (l2_0 - exact_l2).abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-8 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}