fn main() {
    // Degree N=4 GLL nodes on [-1, 1]
    let xi = [-1.0, -0.6546536707079771, 0.0, 0.6546536707079771, 1.0];
    let w = [0.1, 0.5444444444444444, 0.7111111111111111, 0.5444444444444444, 0.1];
    
    // Invariant 1: Sum of quadrature weights == 2.0 (length of interval)
    let weight_sum: f64 = w.iter().sum();
    let weight_err = (weight_sum - 2.0).abs();
    
    // Invariant 2: Integration of exact 6th order polynomial x^2 -> 2/3
    let mut int_x2 = 0.0;
    for i in 0..5 {
        int_x2 += w[i] * xi[i] * xi[i];
    }
    let poly_err = (int_x2 - 2.0 / 3.0).abs();
    let err = weight_err + poly_err;
    println!("INVARIANT_CHECK: {}", if err < 1e-10 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}