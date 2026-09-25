fn main() {
    // Butcher tableau for Radau IIA order 5: c = [(4-sqrt(6))/10, (4+sqrt(6))/10, 1]
    let sq6 = 6.0f64.sqrt();
    let c = [(4.0 - sq6) / 10.0, (4.0 + sq6) / 10.0, 1.0];
    let b = [(16.0 - sq6) / 36.0, (16.0 + sq6) / 36.0, 1.0 / 9.0];
    
    // Invariant: Order condition sum(b_i) == 1.0
    let b_sum: f64 = b.iter().sum();
    let order_err = (b_sum - 1.0).abs();
    
    // Invariant: sum(b_i * c_i) == 1/2
    let bc_sum: f64 = b.iter().zip(c.iter()).map(|(bi, ci)| bi * ci).sum();
    let moment_err = (bc_sum - 0.5).abs();
    let err = order_err + moment_err;
    println!("INVARIANT_CHECK: {}", if err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}