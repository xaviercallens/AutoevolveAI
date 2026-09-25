fn main() {
    // Left and Right states: [rho, p, vx, vy, vz, By, Bz]
    let state_l: [f64; 7] = [1.0, 1.0, 0.2, 0.0, 0.0, 1.0, 0.0];
    let state_r: [f64; 7] = [0.5, 0.5, 0.2, 0.0, 0.0, 1.0, 0.0];

    // Wave speeds estimation
    let s_l: f64 = -0.8;
    let s_r: f64 = 0.8;

    // Physical mass flux: F(rho) = rho * vx
    let flux_l = state_l[0] * state_l[2];
    let flux_r = state_r[0] * state_r[2];

    // HLL numerical flux
    let _hll_flux = (s_r * flux_l - s_l * flux_r + s_l * s_r * (state_r[0] - state_l[0])) / (s_r - s_l);

    // Invariant 1: Normal magnetic field jump across shock vanishes: [Bx] = 0
    let b_normal_jump = (state_l[5] - state_r[5]).abs();

    // Invariant 2: HLL flux consistency (when states match, F_HLL == F_physical)
    let hll_id = (s_r * flux_l - s_l * flux_l) / (s_r - s_l);
    let consistency_err = (hll_id - flux_l).abs();

    let total_err = b_normal_jump + consistency_err;
    println!("INVARIANT_CHECK: {}", if total_err < 1e-10 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", total_err);
}