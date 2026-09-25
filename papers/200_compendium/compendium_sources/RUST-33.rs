fn main() {
    let mut x: f64 = 2.0; let mut y: f64 = 0.0; let mut z: f64 = 0.0;
    let mut vx: f64 = 0.0; let mut vy: f64 = 0.8; let mut vz: f64 = 0.2;
    let dt: f64 = 0.001;
    let steps = std::hint::black_box(1000);
    let e0: f64 = 0.5 * (vx * vx + vy * vy + vz * vz);
    
    for _ in 0..steps {
        let r = (x * x + y * y + z * z).sqrt();
        let r5 = r.powi(5);
        let bx = -3.0 * x * z / r5;
        let by = -3.0 * y * z / r5;
        let bz = (r * r - 3.0 * z * z) / r5;
        
        let fx = vy * bz - vz * by;
        let fy = vz * bx - vx * bz;
        let fz = vx * by - vy * bx;
        
        vx += 0.5 * dt * fx;
        vy += 0.5 * dt * fy;
        vz += 0.5 * dt * fz;
        
        x += dt * vx;
        y += dt * vy;
        z += dt * vz;
        
        vx += 0.5 * dt * fx;
        vy += 0.5 * dt * fy;
        vz += 0.5 * dt * fz;
    }
    
    let e_end = 0.5 * (vx * vx + vy * vy + vz * vz);
    let de = (e_end - e0).abs() / e0;
    println!("INVARIANT_CHECK: {}", if de < 1e-4 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", de);
}