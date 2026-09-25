#[derive(Clone, Copy)]
struct Body { x: f64, y: f64, z: f64, m: f64 }
fn main() {
    let n = std::hint::black_box(16);
    let mut bodies = Vec::with_capacity(n);
    bodies.push(Body { x: 0.0, y: 0.0, z: 0.0, m: 1.0 });
    for i in 1..n {
        let theta = (i as f64) * 0.4;
        let r = 0.5 * (i as f64 / n as f64);
        bodies.push(Body { x: 10.0 + r * theta.cos(), y: r * theta.sin(), z: 0.0, m: 1.0 });
    }
    let g = 1.0;
    let mut direct_fx = 0.0f64;
    let mut direct_fy = 0.0f64;
    for j in 1..n {
        let dx = bodies[j].x - bodies[0].x;
        let dy = bodies[j].y - bodies[0].y;
        let dist = (dx * dx + dy * dy).sqrt();
        let f = g * bodies[0].m * bodies[j].m / (dist * dist * dist);
        direct_fx += f * dx;
        direct_fy += f * dy;
    }
    let mut cm_m = 0.0f64; let mut cm_x = 0.0; let mut cm_y = 0.0;
    for j in 1..n {
        cm_m += bodies[j].m;
        cm_x += bodies[j].m * bodies[j].x;
        cm_y += bodies[j].m * bodies[j].y;
    }
    cm_x /= cm_m; cm_y /= cm_m;
    let dx = cm_x - bodies[0].x;
    let dy = cm_y - bodies[0].y;
    let dist = (dx * dx + dy * dy).sqrt();
    let f = g * bodies[0].m * cm_m / (dist * dist * dist);
    let approx_fx = f * dx;
    let approx_fy = f * dy;
    let dfx = direct_fx - approx_fx;
    let dfy = direct_fy - approx_fy;
    let direct_f_mag = (direct_fx * direct_fx + direct_fy * direct_fy).sqrt();
    let rel_err = (dfx * dfx + dfy * dfy).sqrt() / direct_f_mag;
    let passed = rel_err < 1e-2;
    println!("INVARIANT_CHECK: {}", if passed { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", rel_err);
}