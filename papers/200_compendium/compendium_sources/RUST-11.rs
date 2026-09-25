fn main() {
    let mut a: [[f64; 4]; 4] = [[4.0, 1.0, -2.0, 2.0], [1.0, 2.0, 0.0, 1.0], [-2.0, 0.0, 3.0, -2.0], [2.0, 1.0, -2.0, -1.0]];
    let a_orig = a;
    let mut u: [[f64; 4]; 4] = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]];
    let mut v: [[f64; 4]; 4] = u;
    for _sweep in 0..30 {
        for p in 0..4 {
            for q in (p+1)..4 {
                let mut app: f64 = 0.0; let mut aqq: f64 = 0.0; let mut apq: f64 = 0.0;
                for k in 0..4 {
                    app += a[k][p] * a[k][p];
                    aqq += a[k][q] * a[k][q];
                    apq += a[k][p] * a[k][q];
                }
                if apq.abs() > 1e-12 {
                    let tau: f64 = (aqq - app) / (2.0 * apq);
                    let t: f64 = if tau >= 0.0 { 1.0 / (tau + (1.0 + tau * tau).sqrt()) } else { -1.0 / (-tau + (1.0 + tau * tau).sqrt()) };
                    let c: f64 = 1.0 / (1.0 + t * t).sqrt();
                    let s: f64 = t * c;
                    for k in 0..4 {
                        let akp = a[k][p]; let akq = a[k][q];
                        a[k][p] = c * akp - s * akq;
                        a[k][q] = s * akp + c * akq;
                        let vkp = v[k][p]; let vkq = v[k][q];
                        v[k][p] = c * vkp - s * vkq;
                        v[k][q] = s * vkp + c * vkq;
                    }
                }
            }
        }
    }
    let mut sigma: [f64; 4] = [0.0; 4];
    for j in 0..4 {
        let mut norm: f64 = 0.0;
        for i in 0..4 { norm += a[i][j] * a[i][j]; }
        sigma[j] = norm.sqrt();
        if sigma[j] > 1e-12 {
            for i in 0..4 { u[i][j] = a[i][j] / sigma[j]; }
        }
    }
    let mut max_err: f64 = 0.0;
    for i in 0..4 {
        for j in 0..4 {
            let mut recon: f64 = 0.0;
            for k in 0..4 { recon += u[i][k] * sigma[k] * v[j][k]; }
            let diff: f64 = (recon - a_orig[i][j]).abs();
            if diff > max_err { max_err = diff; }
        }
    }
    println!("INVARIANT_CHECK: {}", if max_err < 1e-8 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_err);
}