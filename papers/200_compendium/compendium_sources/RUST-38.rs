fn main() {
    let mut x = 0.5f64;
    let mut y = 0.25f64;
    let mut dx = 0.0f64;
    let mut dy = 0.0f64;
    for _ in 0..300 {
        let gx = -400.0 * x * (y - x * x) - 2.0 * (1.0 - x);
        let gy = 200.0 * (y - x * x);
        dx = 0.9 * dx - 0.002 * gx;
        dy = 0.9 * dy - 0.002 * gy;
        x += dx;
        y += dy;
    }
    // Distance from global optimum (1, 1)
    let dist = (x - 1.0).hypot(y - 1.0);
    println!("INVARIANT_CHECK: {}", if dist < 0.1 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", dist);
}