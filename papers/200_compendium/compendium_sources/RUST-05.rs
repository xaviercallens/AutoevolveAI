use std::f64::consts::PI;

fn approx_erf(x: f64) -> f64 {
    let a1 = 0.254829592f64;
    let a2 = -0.284496736f64;
    let a3 = 1.421413741f64;
    let a4 = -1.453152027f64;
    let a5 = 1.061405429f64;
    let p = 0.3275911f64;
    let sign = if x < 0.0 { -1.0 } else { 1.0 };
    let abs_x = x.abs();
    let t = 1.0 / (1.0 + p * abs_x);
    let y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * (-abs_x * abs_x).exp();
    sign * y
}

fn normal_cdf(x: f64) -> f64 {
    0.5 * (1.0 + approx_erf(x / 2.0f64.sqrt()))
}

// Xorshift64 PRNG
struct XorShift64(u64);
impl XorShift64 {
    fn next_u64(&mut self) -> u64 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 7;
        self.0 ^= self.0 << 17;
        self.0
    }
    fn next_f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 * (1.0 / 9007199254740992.0)
    }
    fn next_gaussian(&mut self) -> f64 {
        let u1 = self.next_f64().max(1e-15);
        let u2 = self.next_f64();
        (-2.0 * u1.ln()).sqrt() * (2.0 * PI * u2).cos()
    }
}

fn main() {
    let s0: f64 = 100.0;
    let k: f64 = 100.0;
    let r: f64 = 0.05;
    let sigma: f64 = 0.2;
    let t: f64 = 1.0;
    let n_paths: usize = 500_000;

    // Analytical price
    let d1 = ((s0 / k).ln() + (r + 0.5 * sigma * sigma) * t) / (sigma * t.sqrt());
    let d2 = d1 - sigma * t.sqrt();
    let bs_analytic = s0 * normal_cdf(d1) - k * (-r * t).exp() * normal_cdf(d2);

    // Monte Carlo with Antithetic Variates
    let mut rng = XorShift64(88172645463325252);
    let drift = (r - 0.5 * sigma * sigma) * t;
    let vol = sigma * t.sqrt();
    let discount = (-r * t).exp();

    let mut sum_payoff = 0.0f64;
    for _ in 0..(n_paths / 2) {
        let z = rng.next_gaussian();
        let s_t1 = s0 * (drift + vol * z).exp();
        let s_t2 = s0 * (drift - vol * z).exp();
        let payoff1 = (s_t1 - k).max(0.0);
        let payoff2 = (s_t2 - k).max(0.0);
        sum_payoff += 0.5 * (payoff1 + payoff2);
    }
    let mc_price = discount * (sum_payoff / (n_paths / 2) as f64);
    let abs_err = (mc_price - bs_analytic).abs();

    println!("INVARIANT_CHECK: {}", if abs_err < 0.15 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", abs_err);
}