fn main() {
    // 4-spin system state vector |psi> in C^16
    let n = std::hint::black_box(16);
    let mut psi_re = vec![0.0f64; n];
    let mut psi_im = vec![0.0f64; n];
    psi_re[0] = 1.0; // Initial state |0000>
    
    // 4th order Trotter coefficient
    let p = 1.0 / (4.0 - 4.0f64.powf(1.0 / 3.0));
    let dt = 0.05;
    let steps = std::hint::black_box(20);
    
    for _ in 0..steps {
        for s in 0..5 {
            let step_dt = if s == 2 { (1.0 - 4.0 * p) * dt } else { p * dt };
            // Diagonal phase evolution under H_zz
            for i in 0..n {
                let mut sz_sum = 0.0;
                for bit in 0..3 {
                    let b1 = (i >> bit) & 1;
                    let b2 = (i >> (bit + 1)) & 1;
                    sz_sum += if b1 == b2 { 0.25 } else { -0.25 };
                }
                let theta = -step_dt * sz_sum;
                let c = theta.cos();
                let s_th = theta.sin();
                let re = psi_re[i] * c - psi_im[i] * s_th;
                let im = psi_re[i] * s_th + psi_im[i] * c;
                psi_re[i] = re;
                psi_im[i] = im;
            }
        }
    }
    
    let norm_sq: f64 = psi_re.iter().zip(psi_im.iter()).map(|(r, m)| r * r + m * m).sum();
    let norm_drift = (norm_sq - 1.0).abs();
    println!("INVARIANT_CHECK: {}", if norm_drift < 1e-10 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", norm_drift);
}