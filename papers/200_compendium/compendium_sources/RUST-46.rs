fn main() {
    let u_coarse_left = 1.5f64;
    let u_coarse_right = 0.5f64;
    let dy_coarse = 2.0f64;
    let f_coarse = (0.5 * (u_coarse_left + u_coarse_right) - 0.25 * (u_coarse_right - u_coarse_left)) * dy_coarse;

    let dy_fine = 1.0f64;
    let u_fine_left1 = 1.5f64;
    let u_fine_left2 = 1.5f64;
    let f_fine1 = (0.5 * (u_fine_left1 + u_coarse_right) - 0.25 * (u_coarse_right - u_fine_left1)) * dy_fine;
    let f_fine2 = (0.5 * (u_fine_left2 + u_coarse_right) - 0.25 * (u_coarse_right - u_fine_left2)) * dy_fine;
    let conservation_err = (f_coarse - (f_fine1 + f_fine2)).abs();
    println!("INVARIANT_CHECK: {}", if conservation_err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", conservation_err);
}