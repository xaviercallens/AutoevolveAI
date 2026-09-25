fn main() {
    let pos = [[0.0f64, 0.0], [0.2, 0.1], [-0.1, 0.3], [0.15, -0.2]];
    let rho = [1.0f64, 1.05, 0.98, 1.02];
    let p = [1.2f64, 1.3, 1.1, 1.25];
    let mass = 0.1f64;
    let h = 0.5f64;

    let mut total_fx = 0.0f64;
    let mut total_fy = 0.0f64;
    let n = pos.len();
    for i in 0..n {
        for j in (i+1)..n {
            let dx = pos[i][0] - pos[j][0];
            let dy = pos[i][1] - pos[j][1];
            let dist = (dx * dx + dy * dy).sqrt();
            if dist < h && dist > 1e-8 {
                let q = dist / h;
                let dw_dr = - (45.0 / (std::f64::consts::PI * h.powi(4))) * (1.0 - q).powi(2);
                let grad_x = dw_dr * (dx / dist);
                let grad_y = dw_dr * (dy / dist);
                let f_pair = mass * mass * (p[i] / (rho[i] * rho[i]) + p[j] / (rho[j] * rho[j]));
                let fij_x = - f_pair * grad_x;
                let fij_y = - f_pair * grad_y;
                let fji_x = - fij_x;
                let fji_y = - fij_y;
                total_fx += fij_x + fji_x;
                total_fy += fij_y + fji_y;
            }
        }
    }
    let p_drift = total_fx.abs() + total_fy.abs();
    println!("INVARIANT_CHECK: {}", if p_drift < 1e-14 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", p_drift);
}