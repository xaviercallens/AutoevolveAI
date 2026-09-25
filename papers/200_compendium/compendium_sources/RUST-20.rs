struct XorShift32(u32);
impl XorShift32 {
    fn next_f64(&mut self) -> f64 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 17;
        self.0 ^= self.0 << 5;
        (self.0 as f64) / (u32::MAX as f64)
    }
}
fn griewank(x: &[f64; 2]) -> f64 {
    let sum = (x[0] * x[0] + x[1] * x[1]) / 4000.0;
    let prod = (x[0]).cos() * (x[1] / 2.0f64.sqrt()).cos();
    sum - prod + 1.0
}
fn main() {
    let mut rng = XorShift32(123456789);
    let mut current_x = [5.0, -5.0];
    let initial_e = griewank(&current_x);
    let mut current_e = initial_e;
    let mut best_e = current_e;
    let mut t = 2.0;
    let cooling = 0.9998;

    for _ in 0..50000 {
        let cand_x = [
            current_x[0] + (rng.next_f64() - 0.5) * 0.8 * t,
            current_x[1] + (rng.next_f64() - 0.5) * 0.8 * t,
        ];
        let cand_e = griewank(&cand_x);
        let delta = cand_e - current_e;
        if delta < 0.0 || rng.next_f64() < (-delta / t).exp() {
            current_x = cand_x;
            current_e = cand_e;
            if current_e < best_e { best_e = current_e; }
        }
        t *= cooling;
    }
    let energy_reduction = initial_e - best_e;
    let passed = best_e < 0.5 && energy_reduction > 0.5;
    println!("INVARIANT_CHECK: {}", if passed { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", best_e);
}