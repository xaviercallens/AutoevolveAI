fn main() {
    let theta: f64 = 0.7853981633974483; // pi / 4
    let x: f64 = theta.cos();
    
    // P_0^0, P_1^0, P_2^0 recurrence
    let p00 = 1.0;
    let p10 = x;
    let p20 = 0.5 * (3.0 * x * x - 1.0);
    let p30 = 0.5 * (5.0 * x * x * x - 3.0 * x);
    
    // Invariant: Legendre differential equation residual at degree l=2
    // (1 - x^2) y'' - 2x y' + l(l+1) y = 0
    let y = p20;
    let dy = 3.0 * x;
    let d2y = 3.0;
    let ode_res: f64 = (1.0 - x * x) * d2y - 2.0 * x * dy + 6.0 * y;
    let err: f64 = ode_res.abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}