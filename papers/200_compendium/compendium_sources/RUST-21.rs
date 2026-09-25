fn main() {
    let n_qubits = std::hint::black_box(8);
    let n = 1 << n_qubits;
    let mut re = vec![0.0f64; n];
    let mut im = vec![0.0f64; n];
    re[0] = 1.0;
    let inv_sqrt2 = 1.0 / 2.0f64.sqrt();
    for q in 0..n_qubits {
        let step = 1 << (q + 1);
        let half_step = 1 << q;
        for i in (0..n).step_by(step) {
            for j in 0..half_step {
                let u_idx = i + j;
                let v_idx = i + j + half_step;
                let u_re = re[u_idx];
                let u_im = im[u_idx];
                let v_re = re[v_idx];
                let v_im = im[v_idx];
                re[u_idx] = inv_sqrt2 * (u_re + v_re);
                im[u_idx] = inv_sqrt2 * (u_im + v_im);
                re[v_idx] = inv_sqrt2 * (u_re - v_re);
                im[v_idx] = inv_sqrt2 * (u_im - v_im);
            }
        }
    }
    for i in 0..n {
        let mut rev = 0;
        for b in 0..n_qubits {
            if (i >> b) & 1 == 1 { rev |= 1 << (n_qubits - 1 - b); }
        }
        if rev > i { re.swap(i, rev); im.swap(i, rev); }
    }
    let mut norm_sq = 0.0f64;
    let mut max_diff = 0.0f64;
    let expected_prob = 1.0 / (n as f64);
    for i in 0..n {
        let prob = re[i] * re[i] + im[i] * im[i];
        norm_sq += prob;
        let diff = (prob - expected_prob).abs();
        if diff > max_diff { max_diff = diff; }
    }
    let total_err = (norm_sq - 1.0).abs() + max_diff;
    println!("INVARIANT_CHECK: {}", if total_err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", total_err);
}