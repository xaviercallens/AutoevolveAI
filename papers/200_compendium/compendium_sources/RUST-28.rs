fn main() {
    let n = std::hint::black_box(31);
    let h = 1.0 / ((n + 1) as f64);
    let mut f = vec![0.0f64; n];
    for i in 0..n {
        let x = (i + 1) as f64 * h;
        f[i] = (std::f64::consts::PI * x).sin() * h * h;
    }
    let mut u = vec![0.0f64; n];
    let calc_res = |sol: &[f64]| -> f64 {
        let mut norm2 = 0.0f64;
        for i in 0..n {
            let left = if i > 0 { sol[i - 1] } else { 0.0 };
            let right = if i + 1 < n { sol[i + 1] } else { 0.0 };
            let diff = f[i] - (2.0 * sol[i] - left - right);
            norm2 += diff * diff;
        }
        norm2.sqrt()
    };
    let res_0 = calc_res(&u);
    let omega = 1.8f64;
    for _it in 0..80 {
        for i in 0..n {
            let left = if i > 0 { u[i - 1] } else { 0.0 };
            let right = if i + 1 < n { u[i + 1] } else { 0.0 };
            let gs = 0.5 * (f[i] + left + right);
            u[i] = (1.0 - omega) * u[i] + omega * gs;
        }
    }
    let res_end = calc_res(&u);
    let contraction = res_end / res_0;
    println!("INVARIANT_CHECK: {}", if contraction < 1e-3 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", contraction);
}