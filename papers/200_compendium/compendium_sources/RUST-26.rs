fn main() {
    let p_order = std::hint::black_box(8);
    let n_sources = std::hint::black_box(16);
    let mut z_src = Vec::with_capacity(n_sources);
    let mut q_src = Vec::with_capacity(n_sources);
    for i in 0..n_sources {
        let r = 0.2 * (i as f64 / n_sources as f64);
        let theta = (i as f64) * 0.3927;
        z_src.push((r * theta.cos(), r * theta.sin()));
        q_src.push(1.0f64 / (n_sources as f64));
    }
    let mut a_coeffs = vec![(0.0f64, 0.0f64); p_order + 1];
    for i in 0..n_sources {
        a_coeffs[0].0 += q_src[i];
        let (zx, zy) = z_src[i];
        let mut zk = (zx, zy);
        for k in 1..=p_order {
            a_coeffs[k].0 -= (q_src[i] / (k as f64)) * zk.0;
            a_coeffs[k].1 -= (q_src[i] / (k as f64)) * zk.1;
            let n_re = zk.0 * zx - zk.1 * zy;
            let n_im = zk.0 * zy + zk.1 * zx;
            zk = (n_re, n_im);
        }
    }
    let target = (4.0f64, 4.0f64);
    let mut direct_pot = 0.0f64;
    for i in 0..n_sources {
        let dx = target.0 - z_src[i].0;
        let dy = target.1 - z_src[i].1;
        direct_pot += q_src[i] * (dx * dx + dy * dy).sqrt().ln();
    }
    let target_r = (target.0 * target.0 + target.1 * target.1).sqrt();
    let mut fmm_pot = a_coeffs[0].0 * target_r.ln();
    let inv_denom = target.0 * target.0 + target.1 * target.1;
    let z_inv = (target.0 / inv_denom, -target.1 / inv_denom);
    let mut z_inv_k = z_inv;
    for k in 1..=p_order {
        fmm_pot += a_coeffs[k].0 * z_inv_k.0 - a_coeffs[k].1 * z_inv_k.1;
        let n_re = z_inv_k.0 * z_inv.0 - z_inv_k.1 * z_inv.1;
        let n_im = z_inv_k.0 * z_inv.1 + z_inv_k.1 * z_inv.0;
        z_inv_k = (n_re, n_im);
    }
    let err = (fmm_pot - direct_pot).abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-8 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}