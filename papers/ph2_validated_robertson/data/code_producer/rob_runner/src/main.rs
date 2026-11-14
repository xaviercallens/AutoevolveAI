// Runs rusty-SUNDIALS cvode crate (Rust port; BDF, Newton, dense LU, analytic Jacobian) on Robertson.
// usage: rob_runner RTOL ATOL T1 T2 ...   prints one JSON line per output time (shortest round-trip floats).
use cvode::{Cvode, Method, Task};
use nvector::SerialVector;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a: Vec<String> = std::env::args().collect();
    let rtol: f64 = a[1].parse()?;
    let atol: f64 = a[2].parse()?;
    let times: Vec<f64> = a[3..].iter().map(|s| s.parse().unwrap()).collect();
    let rhs = |_t: f64, y: &[f64], d: &mut [f64]| -> Result<(), String> {
        d[0] = -0.04 * y[0] + 1e4 * y[1] * y[2];
        d[1] = 0.04 * y[0] - 1e4 * y[1] * y[2] - 3e7 * y[1] * y[1];
        d[2] = 3e7 * y[1] * y[1];
        Ok(())
    };
    let y0 = SerialVector::from_slice(&[1.0, 0.0, 0.0]);
    let mut s = Cvode::builder(Method::Bdf)
        .rtol(rtol)
        .atol(atol)
        .max_steps(50_000_000)
        .jacobian(
            |_t: f64,
             y: &[f64],
             j: &mut sundials_core::generated::sundials_dense::DenseMat|
             -> Result<(), String> {
                j.cols[0][0] = -0.04;
                j.cols[1][0] = 1e4 * y[2];
                j.cols[2][0] = 1e4 * y[1];
                j.cols[0][1] = 0.04;
                j.cols[1][1] = -1e4 * y[2] - 6e7 * y[1];
                j.cols[2][1] = -1e4 * y[1];
                j.cols[0][2] = 0.0;
                j.cols[1][2] = 6e7 * y[1];
                j.cols[2][2] = 0.0;
                Ok(())
            },
        )
        .build(rhs, 0.0, y0)?;
    for &tout in &times {
        let (t, y) = s.solve(tout, Task::Normal)?;
        let (y1, y2, y3) = (y[0], y[1], y[2]);
        drop(y);
        println!(
            "{{\"rtol\":{:e},\"atol\":{:e},\"tout\":{:e},\"t\":{:e},\"y\":[{:e},{:e},{:e}],\"steps\":{},\"rhs\":{},\"order\":{}}}",
            rtol, atol, tout, t, y1, y2, y3, s.num_steps(), s.num_rhs_evals(), s.order()
        );
    }
    Ok(())
}
