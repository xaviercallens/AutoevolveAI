fn main() {
    let n = std::hint::black_box(64);
    let mut a = vec![0.0f64; n * n];
    let mut b = vec![0.0f64; n * n];
    let mut c_naive = vec![0.0f64; n * n];
    let mut c_tiled = vec![0.0f64; n * n];

    for i in 0..n {
        for j in 0..n {
            a[i * n + j] = ((i * 37 + j * 17) % 100) as f64 / 10.0;
            b[i * n + j] = ((i * 13 + j * 43) % 100) as f64 / 10.0;
        }
    }

    // Naive O(N^3)
    for i in 0..n {
        for k in 0..n {
            let aik = a[i * n + k];
            for j in 0..n {
                c_naive[i * n + j] += aik * b[k * n + j];
            }
        }
    }

    // Cache-blocked / Tiled with unrolling
    let block = std::hint::black_box(16);
    for bi in (0..n).step_by(block) {
        for bk in (0..n).step_by(block) {
            for bj in (0..n).step_by(block) {
                let imax = (bi + block).min(n);
                let kmax = (bk + block).min(n);
                let jmax = (bj + block).min(n);
                for i in bi..imax {
                    for k in bk..kmax {
                        let aik = a[i * n + k];
                        let mut j = bj;
                        while j + 4 <= jmax {
                            c_tiled[i * n + j] += aik * b[k * n + j];
                            c_tiled[i * n + j + 1] += aik * b[k * n + j + 1];
                            c_tiled[i * n + j + 2] += aik * b[k * n + j + 2];
                            c_tiled[i * n + j + 3] += aik * b[k * n + j + 3];
                            j += 4;
                        }
                        while j < jmax {
                            c_tiled[i * n + j] += aik * b[k * n + j];
                            j += 1;
                        }
                    }
                }
            }
        }
    }

    let mut max_diff = 0.0f64;
    for idx in 0..(n * n) {
        let diff = (c_naive[idx] - c_tiled[idx]).abs();
        if diff > max_diff {
            max_diff = diff;
        }
    }

    println!("INVARIANT_CHECK: {}", if max_diff < 1e-9 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_diff);
}