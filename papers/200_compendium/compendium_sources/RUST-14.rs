fn main() {
    let n = std::hint::black_box(8);
    let mut a = vec![0.0f64; n * n];
    for i in 0..n {
        for j in 0..n {
            a[i * n + j] = ((i * 7 + j * 11) % 10) as f64 * 0.1;
        }
        a[i * n + i] += 15.0;
    }
    for i in 0..n {
        for j in (i+1)..n {
            let avg = 0.5 * (a[i * n + j] + a[j * n + i]);
            a[i * n + j] = avg;
            a[j * n + i] = avg;
        }
    }
    let a_orig = a.clone();
    let mut l = vec![0.0f64; n * n];
    for i in 0..n {
        for j in 0..=i {
            let mut sum = 0.0;
            for k in 0..j { sum += l[i * n + k] * l[j * n + k]; }
            if i == j {
                let val = a[i * n + i] - sum;
                assert!(val > 0.0);
                l[i * n + j] = val.sqrt();
            } else {
                l[i * n + j] = (a[i * n + j] - sum) / l[j * n + j];
            }
        }
    }
    let mut max_diff = 0.0f64;
    for i in 0..n {
        for j in 0..n {
            let mut recon = 0.0;
            for k in 0..n { recon += l[i * n + k] * l[j * n + k]; }
            let diff = (recon - a_orig[i * n + j]).abs();
            if diff > max_diff { max_diff = diff; }
        }
    }
    println!("INVARIANT_CHECK: {}", if max_diff < 1e-10 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_diff);
}