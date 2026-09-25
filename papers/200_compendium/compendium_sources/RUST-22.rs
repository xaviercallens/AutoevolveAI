fn main() {
    let n = std::hint::black_box(4);
    let mut a: Vec<f64> = vec![
        4.0, 1.0, 0.5, 0.2,
        1.0, 5.0, 1.2, 0.3,
        0.5, 1.2, 6.0, 1.5,
        0.2, 0.3, 1.5, 7.0,
    ];
    let a_orig = a.clone();
    let mut v = vec![0.0f64; n * n];
    for i in 0..n { v[i * n + i] = 1.0; }

    for _sweep in 0..50 {
        let mut max_off = 0.0f64;
        let mut p = 0;
        let mut q = 1;
        for i in 0..n {
            for j in (i + 1)..n {
                let val = a[i * n + j].abs();
                if val > max_off { max_off = val; p = i; q = j; }
            }
        }
        if max_off < 1e-13 { break; }
        let app = a[p * n + p];
        let aqq = a[q * n + q];
        let apq = a[p * n + q];
        let theta = (aqq - app) / (2.0 * apq);
        let t = if theta >= 0.0 { 1.0 / (theta + (theta * theta + 1.0f64).sqrt()) } else { -1.0 / (-theta + (theta * theta + 1.0f64).sqrt()) };
        let c = 1.0 / (t * t + 1.0f64).sqrt();
        let s = t * c;
        for i in 0..n {
            if i != p && i != q {
                let aip = a[i * n + p];
                let aiq = a[i * n + q];
                a[i * n + p] = c * aip - s * aiq;
                a[p * n + i] = a[i * n + p];
                a[i * n + q] = s * aip + c * aiq;
                a[q * n + i] = a[i * n + q];
            }
        }
        a[p * n + p] = c * c * app - 2.0 * s * c * apq + s * s * aqq;
        a[q * n + q] = s * s * app + 2.0 * s * c * apq + c * c * aqq;
        a[p * n + q] = 0.0;
        a[q * n + p] = 0.0;
        for i in 0..n {
            let vip = v[i * n + p];
            let viq = v[i * n + q];
            v[i * n + p] = c * vip - s * viq;
            v[i * n + q] = s * vip + c * viq;
        }
    }
    let mut off_norm = 0.0f64;
    for i in 0..n {
        for j in 0..n {
            if i != j {
                let mut elem = 0.0f64;
                for k in 0..n {
                    for l in 0..n { elem += v[k * n + i] * a_orig[k * n + l] * v[l * n + j]; }
                }
                off_norm += elem * elem;
            }
        }
    }
    let err = off_norm.sqrt();
    println!("INVARIANT_CHECK: {}", if err < 1e-10 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}