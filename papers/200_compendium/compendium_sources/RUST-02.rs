use std::f64::consts::PI;

#[derive(Clone, Copy)]
struct Complex {
    re: f64,
    im: f64,
}

impl Complex {
    fn new(re: f64, im: f64) -> Self { Self { re, im } }
    fn add(self, o: Self) -> Self { Self::new(self.re + o.re, self.im + o.im) }
    fn sub(self, o: Self) -> Self { Self::new(self.re - o.re, self.im - o.im) }
    fn mul(self, o: Self) -> Self {
        Self::new(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)
    }
    fn norm_sq(self) -> f64 { self.re * self.re + self.im * self.im }
}

fn fft_radix2(buf: &mut [Complex]) {
    let n = buf.len();
    assert!(n.is_power_of_two());
    let mut j = 0;
    for i in 0..n {
        if i < j { buf.swap(i, j); }
        let mut bit = n >> 1;
        while j & bit != 0 {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
    }

    let mut len = 2;
    while len <= n {
        let angle = -2.0 * PI / (len as f64);
        let wlen = Complex::new(angle.cos(), angle.sin());
        for i in (0..n).step_by(len) {
            let mut w = Complex::new(1.0, 0.0);
            for k in 0..(len / 2) {
                let u = buf[i + k];
                let v = buf[i + k + len / 2].mul(w);
                buf[i + k] = u.add(v);
                buf[i + k + len / 2] = u.sub(v);
                w = w.mul(wlen);
            }
        }
        len <<= 1;
    }
}

fn main() {
    let n = std::hint::black_box(512);
    let mut signal = Vec::with_capacity(n);
    let mut time_energy = 0.0f64;
    for i in 0..n {
        let t = i as f64 / n as f64;
        let v = (2.0 * PI * 5.0 * t).sin() + 0.5 * (2.0 * PI * 20.0 * t).cos();
        let c = Complex::new(v, 0.0);
        time_energy += c.norm_sq();
        signal.push(c);
    }

    fft_radix2(&mut signal);

    let mut freq_energy = 0.0f64;
    for c in &signal {
        freq_energy += c.norm_sq();
    }
    freq_energy /= n as f64;

    let parseval_error = (time_energy - freq_energy).abs() / time_energy;
    println!("INVARIANT_CHECK: {}", if parseval_error < 1e-9 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", parseval_error);
}