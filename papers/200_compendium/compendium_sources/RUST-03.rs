fn lorenz_deriv(y: &[f64; 3]) -> [f64; 3] {
    let sigma = 10.0;
    let rho = 28.0;
    let beta = 8.0 / 3.0;
    [
        sigma * (y[1] - y[0]),
        y[0] * (rho - y[2]) - y[1],
        y[0] * y[1] - beta * y[2],
    ]
}

fn rkf45_step(y: &[f64; 3], h: f64) -> ([f64; 3], f64) {
    let k1 = lorenz_deriv(y);
    let mut y2 = [0.0; 3];
    for i in 0..3 { y2[i] = y[i] + h * (1.0/4.0 * k1[i]); }
    let k2 = lorenz_deriv(&y2);

    let mut y3 = [0.0; 3];
    for i in 0..3 { y3[i] = y[i] + h * (3.0/32.0 * k1[i] + 9.0/32.0 * k2[i]); }
    let k3 = lorenz_deriv(&y3);

    let mut y4 = [0.0; 3];
    for i in 0..3 { y4[i] = y[i] + h * (1932.0/2197.0 * k1[i] - 7200.0/2197.0 * k2[i] + 7296.0/2197.0 * k3[i]); }
    let k4 = lorenz_deriv(&y4);

    let mut y5 = [0.0; 3];
    for i in 0..3 { y5[i] = y[i] + h * (439.0/216.0 * k1[i] - 8.0 * k2[i] + 3680.0/513.0 * k3[i] - 845.0/4104.0 * k4[i]); }
    let k5 = lorenz_deriv(&y5);

    let mut y6 = [0.0; 3];
    for i in 0..3 { y6[i] = y[i] + h * (-8.0/27.0 * k1[i] + 2.0 * k2[i] - 3544.0/2565.0 * k3[i] + 1859.0/4104.0 * k4[i] - 11.0/40.0 * k5[i]); }
    let k6 = lorenz_deriv(&y6);

    let mut y_next = [0.0; 3];
    let mut error = 0.0f64;
    for i in 0..3 {
        let sol4 = y[i] + h * (25.0/216.0 * k1[i] + 1408.0/2565.0 * k3[i] + 2197.0/4104.0 * k4[i] - 1.0/5.0 * k5[i]);
        let sol5 = y[i] + h * (16.0/135.0 * k1[i] + 6656.0/12825.0 * k3[i] + 28561.0/56430.0 * k4[i] - 9.0/50.0 * k5[i] + 2.0/55.0 * k6[i]);
        y_next[i] = sol5;
        let diff = (sol5 - sol4).abs();
        if diff > error { error = diff; }
    }
    (y_next, error)
}

fn main() {
    let mut y = [1.0, 1.0, 1.0];
    let mut t = 0.0;
    let t_end = 2.0;
    let mut h = 0.01;
    let tol = 1e-5;
    let mut max_error_observed = 0.0f64;

    while t < t_end {
        if t + h > t_end { h = t_end - t; }
        let (y_cand, err) = rkf45_step(&y, h);
        if err <= tol || h <= 1e-6 {
            y = y_cand;
            t += h;
            if err > max_error_observed { max_error_observed = err; }
        }
        let scale = 0.84 * (tol / (err + 1e-12)).powf(0.25);
        h = (h * scale.clamp(0.1, 4.0)).clamp(1e-5, 0.1);
    }

    println!("INVARIANT_CHECK: {}", if max_error_observed <= tol { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_error_observed);
}