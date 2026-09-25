fn main() {
    let n = std::hint::black_box(32);
    let mut a = vec![0.0f64; n * n];
    let mut b = vec![0.0f64; n];

    // Build diagonally dominant SPD matrix
    for i in 0..n {
        let mut row_sum = 0.0;
        for j in 0..n {
            let val = ((i * 17 + j * 31) % 50) as f64 / 10.0;
            a[i * n + j] = val;
            row_sum += val.abs();
        }
        a[i * n + i] += row_sum + 10.0;
        b[i] = (i + 1) as f64;
    }

    let a_orig = a.clone();
    let b_orig = b.clone();

    // LUP Factorization
    let mut p: Vec<usize> = (0..n).collect();
    for i in 0..n {
        let mut max_val = 0.0f64;
        let mut max_row = i;
        for k in i..n {
            let val = a[k * n + i].abs();
            if val > max_val {
                max_val = val;
                max_row = k;
            }
        }
        if max_row != i {
            p.swap(i, max_row);
            for col in 0..n {
                let temp = a[i * n + col];
                a[i * n + col] = a[max_row * n + col];
                a[max_row * n + col] = temp;
            }
        }
        let pivot = a[i * n + i];
        for j in (i + 1)..n {
            a[j * n + i] /= pivot;
            let factor = a[j * n + i];
            for k in (i + 1)..n {
                a[j * n + k] -= factor * a[i * n + k];
            }
        }
    }

    // Forward substitution Ly = Pb
    let mut y = vec![0.0f64; n];
    for i in 0..n {
        let mut sum = b_orig[p[i]];
        for j in 0..i {
            sum -= a[i * n + j] * y[j];
        }
        y[i] = sum;
    }

    // Backward substitution Ux = y
    let mut x = vec![0.0f64; n];
    for i in (0..n).rev() {
        let mut sum = y[i];
        for j in (i + 1)..n {
            sum -= a[i * n + j] * x[j];
        }
        x[i] = sum / a[i * n + i];
    }

    // Compute residual ||Ax - b||
    let mut max_res = 0.0f64;
    for i in 0..n {
        let mut ax_i = 0.0;
        for j in 0..n {
            ax_i += a_orig[i * n + j] * x[j];
        }
        let res = (ax_i - b_orig[i]).abs();
        if res > max_res { max_res = res; }
    }

    println!("INVARIANT_CHECK: {}", if max_res < 1e-8 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_res);
}