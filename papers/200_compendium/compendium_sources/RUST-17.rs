fn main() {
    let nx = std::hint::black_box(32); let ny = std::hint::black_box(16);
    let w = [4.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/9.0, 1.0/36.0, 1.0/36.0, 1.0/36.0, 1.0/36.0];
    let cx = [0, 1, 0, -1, 0, 1, -1, -1, 1];
    let cy = [0, 0, 1, 0, -1, 1, 1, -1, -1];
    let mut f = vec![0.0f64; nx * ny * 9];
    for y in 0..ny {
        for x in 0..nx {
            for i in 0..9 { f[(y * nx + x) * 9 + i] = w[i]; }
        }
    }
    let calc_total_mass = |arr: &[f64]| -> f64 { arr.iter().sum() };
    let mass_0 = calc_total_mass(&f);
    let tau = 0.8;
    for _step in 0..10 {
        let mut f_coll = f.clone();
        for y in 0..ny {
            for x in 0..nx {
                let base = (y * nx + x) * 9;
                let mut rho = 0.0;
                let mut ux = 0.0;
                let mut uy = 0.0;
                for i in 0..9 {
                    let val = f[base + i];
                    rho += val;
                    ux += val * cx[i] as f64;
                    uy += val * cy[i] as f64;
                }
                ux /= rho; uy /= rho;
                for i in 0..9 {
                    let ci_u = cx[i] as f64 * ux + cy[i] as f64 * uy;
                    let u_sq = ux * ux + uy * uy;
                    let feq = w[i] * rho * (1.0 + 3.0 * ci_u + 4.5 * ci_u * ci_u - 1.5 * u_sq);
                    f_coll[base + i] = f[base + i] - (1.0 / tau) * (f[base + i] - feq);
                }
            }
        }
        for y in 0..ny {
            for x in 0..nx {
                for i in 0..9 {
                    let xp = ((x as isize - cx[i] + nx as isize) % nx as isize) as usize;
                    let yp = ((y as isize - cy[i] + ny as isize) % ny as isize) as usize;
                    f[(y * nx + x) * 9 + i] = f_coll[(yp * nx + xp) * 9 + i];
                }
            }
        }
    }
    let mass_end = calc_total_mass(&f);
    let mass_diff = (mass_end - mass_0).abs() / mass_0;
    println!("INVARIANT_CHECK: {}", if mass_diff < 1e-11 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", mass_diff);
}