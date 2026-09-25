fn f(x: f64) -> f64 { x * x.sin() }
fn simpson(a: f64, b: f64) -> f64 {
    let c = 0.5 * (a + b);
    (b - a) / 6.0 * (f(a) + 4.0 * f(c) + f(b))
}
fn adaptive_simpson(a: f64, b: f64, eps: f64, whole: f64) -> f64 {
    let c = 0.5 * (a + b);
    let left = simpson(a, c);
    let right = simpson(c, b);
    if (left + right - whole).abs() <= 15.0 * eps {
        left + right + (left + right - whole) / 15.0
    } else {
        adaptive_simpson(a, c, eps * 0.5, left) + adaptive_simpson(c, b, eps * 0.5, right)
    }
}
fn main() {
    let a = 0.0f64;
    let b = std::f64::consts::PI;
    let whole = simpson(a, b);
    let approx = adaptive_simpson(a, b, 1e-9, whole);
    let exact = std::f64::consts::PI;
    let err = (approx - exact).abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-8 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}