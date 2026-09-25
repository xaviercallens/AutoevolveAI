fn main() {
    let n = std::hint::black_box(8);
    let mut a = vec![0.0f64; n * n];
    for i in 0..n {
        for j in 0..n {
            a[i * n + j] = ((i * 13 + j * 29) % 37) as f64 / 10.0 + if i == j { 5.0 } else { 0.0 };
        }
    }
    let a_orig = a.clone();
    let mut q = vec![0.0f64; n * n];
    for i in 0..n { q[i * n + i] = 1.0; }

    for k in 0..(n - 1) {
        let mut norm_x = 0.0;
        for i in k..n { norm_x += a[i * n + k] * a[i * n + k]; }
        norm_x = norm_x.sqrt();
        let alpha = if a[k * n + k] >= 0.0 { -norm_x } else { norm_x };
        let mut v = vec![0.0f64; n];
        v[k] = a[k * n + k] - alpha;
        for i in (k + 1)..n { v[i] = a[i * n + k]; }
        let mut v_norm_sq = 0.0;
        for i in k..n { v_norm_sq += v[i] * v[i]; }
        if v_norm_sq > 1e-14 {
            let beta = 2.0 / v_norm_sq;
            for j in k..n {
                let mut v_dot_col = 0.0;
                for i in k..n { v_dot_col += v[i] * a[i * n + j]; }
                for i in k..n { a[i * n + j] -= beta * v_dot_col * v[i]; }
            }
            for j in 0..n {
                let mut v_dot_col = 0.0;
                for i in k..n { v_dot_col += v[i] * q[i * n + j]; }
                for i in k..n { q[i * n + j] -= beta * v_dot_col * v[i]; }
            }
        }
    }
    let mut max_err = 0.0f64;
    for i in 0..n {
        for j in 0..n {
            let mut val = 0.0;
            for k in 0..n {
                let r_kj = if k <= j { a[k * n + j] } else { 0.0 };
                val += q[k * n + i] * r_kj;
            }
            let diff = (val - a_orig[i * n + j]).abs();
            if diff > max_err { max_err = diff; }
        }
    }
    println!("INVARIANT_CHECK: {}", if max_err < 1e-9 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_err);
}