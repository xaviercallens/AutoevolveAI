fn main() {
    let nx = std::hint::black_box(32); let ny = std::hint::black_box(32);
    let dx = 2.0 / (nx as f64);
    let dy = 2.0 / (ny as f64);
    let mut phi = vec![0.0f64; nx * ny];
    for j in 0..ny {
        let y = -1.0 + (j as f64 + 0.5) * dy;
        for i in 0..nx {
            let x = -1.0 + (i as f64 + 0.5) * dx;
            phi[j * nx + i] = x * x + y * y - 0.25;
        }
    }
    let mut max_grad_err = 0.0f64;
    let r_target = 0.5f64;
    for j in 4..(ny - 4) {
        let y = -1.0 + (j as f64 + 0.5) * dy;
        for i in 4..(nx - 4) {
            let x = -1.0 + (i as f64 + 0.5) * dx;
            let r = (x * x + y * y).sqrt();
            let exact_sdf = r - r_target;
            let diff = (phi[j * nx + i] / (2.0 * r.max(0.1)) - exact_sdf).abs();
            if diff > max_grad_err && (r - r_target).abs() < 0.2 { max_grad_err = diff; }
        }
    }
    let passed = max_grad_err < 0.08;
    println!("INVARIANT_CHECK: {}", if passed { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_grad_err);
}