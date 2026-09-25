fn rosenbrock(x: &[f64; 2]) -> f64 {
    (1.0 - x[0]).powi(2) + 100.0 * (x[1] - x[0].powi(2)).powi(2)
}

fn rosenbrock_grad(x: &[f64; 2]) -> [f64; 2] {
    [
        -2.0 * (1.0 - x[0]) - 400.0 * x[0] * (x[1] - x[0].powi(2)),
        200.0 * (x[1] - x[0].powi(2)),
    ]
}

fn main() {
    let mut x = [0.0f64, 0.0f64];
    let mut h = [[1.0f64, 0.0f64], [0.0f64, 1.0f64]];

    let mut grad = rosenbrock_grad(&x);
    for _iter in 0..500 {
        let grad_norm = (grad[0] * grad[0] + grad[1] * grad[1]).sqrt();
        if grad_norm < 1e-5 { break; }

        let p = [
            -(h[0][0] * grad[0] + h[0][1] * grad[1]),
            -(h[1][0] * grad[0] + h[1][1] * grad[1]),
        ];

        let mut alpha = 1.0f64;
        let c1 = 1e-4f64;
        let fx = rosenbrock(&x);
        let dir_deriv = grad[0] * p[0] + grad[1] * p[1];
        if dir_deriv >= 0.0 {
            h = [[1.0, 0.0], [0.0, 1.0]];
            continue;
        }

        while alpha > 1e-12 {
            let x_cand = [x[0] + alpha * p[0], x[1] + alpha * p[1]];
            if rosenbrock(&x_cand) <= fx + c1 * alpha * dir_deriv {
                break;
            }
            alpha *= 0.5;
        }

        let s = [alpha * p[0], alpha * p[1]];
        let x_next = [x[0] + s[0], x[1] + s[1]];
        let grad_next = rosenbrock_grad(&x_next);
        let y = [grad_next[0] - grad[0], grad_next[1] - grad[1]];

        let ys = y[0] * s[0] + y[1] * s[1];
        if ys > 1e-10 {
            let rho = 1.0 / ys;
            let v = [
                h[0][0] * y[0] + h[0][1] * y[1],
                h[1][0] * y[0] + h[1][1] * y[1],
            ];
            let y_hy = y[0] * v[0] + y[1] * v[1];

            for i in 0..2 {
                for j in 0..2 {
                    let t1 = (s[i] * v[j]) * rho;
                    let t2 = (v[i] * s[j]) * rho;
                    let t3 = (1.0 + rho * y_hy) * (s[i] * s[j]) * rho;
                    h[i][j] = h[i][j] - t1 - t2 + t3;
                }
            }
        }

        x = x_next;
        grad = grad_next;
    }

    let error_from_optimum = ((x[0] - 1.0).powi(2) + (x[1] - 1.0).powi(2)).sqrt();
    println!("INVARIANT_CHECK: {}", if error_from_optimum < 1e-4 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", error_from_optimum);
}