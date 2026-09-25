fn main() {
    let n = std::hint::black_box(24);
    let matvec = |v: &[f64]| -> Vec<f64> {
        let mut av = vec![0.0f64; n];
        for i in 0..n {
            let left = if i > 0 { v[i - 1] } else { 0.0 };
            let right = if i + 1 < n { v[i + 1] } else { 0.0 };
            av[i] = 2.0 * v[i] - left - right;
        }
        av
    };
    let m = std::hint::black_box(20);
    let mut q = vec![vec![0.0f64; n]; m + 1];
    let mut alpha = vec![0.0f64; m];
    let mut beta = vec![0.0f64; m + 1];
    for i in 0..n { q[1][i] = if i % 2 == 0 { 1.0 } else { -1.0 } / (n as f64).sqrt(); }
    for j in 1..=m {
        let mut v = matvec(&q[j]);
        for i in 0..n { v[i] -= beta[j - 1] * q[j - 1][i]; }
        let mut a_j = 0.0f64;
        for i in 0..n { a_j += q[j][i] * v[i]; }
        alpha[j - 1] = a_j;
        for i in 0..n { v[i] -= a_j * q[j][i]; }
        let mut b_j = 0.0f64;
        for i in 0..n { b_j += v[i] * v[i]; }
        b_j = b_j.sqrt();
        beta[j] = b_j;
        if b_j < 1e-12 || j == m { break; }
        for i in 0..n { q[j + 1][i] = v[i] / b_j; }
    }
    let exact_max = 4.0 * ((n as f64) * std::f64::consts::PI / (2.0 * (n as f64 + 1.0))).sin().powi(2);
    let mut approx_lambda = 0.0f64;
    for k in 0..m { if alpha[k] > approx_lambda { approx_lambda = alpha[k]; } }
    let err = (exact_max - approx_lambda).abs() / exact_max;
    println!("INVARIANT_CHECK: {}", if err < 0.05 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}