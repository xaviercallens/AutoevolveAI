fn main() {
    let mut vx = 0.6f64;
    let mut vy = 0.8f64;
    let vz = 0.0f64;
    let v2_initial = vx * vx + vy * vy + vz * vz;
    
    // Boris rotation: pure magnetic rotation preserves |v|^2
    let bz = 1.0f64;
    let dt = 0.01f64;
    let t = bz * dt * 0.5;
    let s = 2.0 * t / (1.0 + t * t);
    
    let v_prime_x = vx + vy * t;
    let v_prime_y = vy - vx * t;
    vx += v_prime_y * s;
    vy -= v_prime_x * s;
    
    let v2_final = vx * vx + vy * vy + vz * vz;
    let err = (v2_final - v2_initial).abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}