fn main() {
    let mut l1 = 1.0f64;
    let mut l2 = 0.5f64;
    let mut l3 = 0.2f64;
    let casimir_0 = l1 * l1 + l2 * l2 + l3 * l3;
    let dt = 0.001;
    
    for _ in 0..500 {
        // dL/dt = L x Omega
        let dl1 = l2 * l3 * 0.5;
        let dl2 = -l1 * l3 * 0.5;
        let dl3 = 0.0;
        l1 += dt * dl1;
        l2 += dt * dl2;
        l3 += dt * dl3;
    }
    let casimir_end = l1 * l1 + l2 * l2 + l3 * l3;
    let err = (casimir_end - casimir_0).abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-3 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}