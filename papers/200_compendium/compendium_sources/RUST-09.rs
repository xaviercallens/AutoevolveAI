fn main() {
    let n = std::hint::black_box(1000);
    // Tridiagonal matrix in CSR format
    let mut row_ptr = Vec::with_capacity(n + 1);
    let mut col_ind = Vec::new();
    let mut values = Vec::new();

    row_ptr.push(0);
    for i in 0..n {
        if i > 0 {
            col_ind.push(i - 1);
            values.push(-1.0f64);
        }
        col_ind.push(i);
        values.push(2.0f64);
        if i + 1 < n {
            col_ind.push(i + 1);
            values.push(-1.0f64);
        }
        row_ptr.push(values.len());
    }

    let x: Vec<f64> = (0..n).map(|i| (i as f64 * 0.01).cos()).collect();
    let mut y_spmv = vec![0.0f64; n];

    // CSR SpMV kernel
    for i in 0..n {
        let start = row_ptr[i];
        let end = row_ptr[i + 1];
        let mut sum = 0.0;
        for idx in start..end {
            sum += values[idx] * x[col_ind[idx]];
        }
        y_spmv[i] = sum;
    }

    // Dense ground truth check
    let mut max_err = 0.0f64;
    for i in 0..n {
        let mut y_true = 2.0 * x[i];
        if i > 0 { y_true -= x[i - 1]; }
        if i + 1 < n { y_true -= x[i + 1]; }
        let err = (y_spmv[i] - y_true).abs();
        if err > max_err { max_err = err; }
    }

    println!("INVARIANT_CHECK: {}", if max_err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_err);
}