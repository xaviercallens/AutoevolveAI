fn main() {
    let n = std::hint::black_box(256);
    // 1D discrete Laplacian: -u'' = f with Dirichlet boundary conditions
    let mut diag = vec![2.0f64; n];
    let off = -1.0f64;
    let b: Vec<f64> = (0..n).map(|i| ((i + 1) as f64 / n as f64).sin()).collect();

    let mat_vec = |x: &[f64]| -> Vec<f64> {
        let mut y = vec![0.0; n];
        for i in 0..n {
            y[i] = diag[i] * x[i];
            if i > 0 { y[i] += off * x[i - 1]; }
            if i + 1 < n { y[i] += off * x[i + 1]; }
        }
        y
    };

    let dot = |u: &[f64], v: &[f64]| -> f64 {
        u.iter().zip(v.iter()).map(|(a, b)| a * b).sum()
    };

    // Preconditioner M^{-1} = 1.0 / diag
    let mut x = vec![0.0f64; n];
    let mut r = b.clone();
    let mut z: Vec<f64> = (0..n).map(|i| r[i] / diag[i]).collect();
    let mut p = z.clone();
    let mut rz_old = dot(&r, &z);
    let initial_r_norm = dot(&r, &r).sqrt();

    for _iter in 0..500 {
        let ap = mat_vec(&p);
        let alpha = rz_old / dot(&p, &ap);
        for i in 0..n {
            x[i] += alpha * p[i];
            r[i] -= alpha * ap[i];
        }
        let r_norm = dot(&r, &r).sqrt();
        if r_norm / initial_r_norm < 1e-8 {
            break;
        }
        for i in 0..n { z[i] = r[i] / diag[i]; }
        let rz_new = dot(&r, &z);
        let beta = rz_new / rz_old;
        for i in 0..n {
            p[i] = z[i] + beta * p[i];
        }
        rz_old = rz_new;
    }

    let ax = mat_vec(&x);
    let mut final_res = 0.0f64;
    for i in 0..n {
        let diff = (ax[i] - b[i]).abs();
        if diff > final_res { final_res = diff; }
    }

    println!("INVARIANT_CHECK: {}", if final_res < 1e-6 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", final_res);
}