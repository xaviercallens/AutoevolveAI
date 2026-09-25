#[derive(Clone, Copy)]
struct Body { x: f64, y: f64, vx: f64, vy: f64, m: f64 }

fn main() {
    let n = std::hint::black_box(50);
    let mut bodies = Vec::with_capacity(n);
    for i in 0..n {
        let angle = i as f64 * (2.0 * std::f64::consts::PI / n as f64);
        let r = 5.0 + ((i * 13) % 7) as f64 * 0.5;
        let v = (1.0 / r).sqrt();
        bodies.push(Body {
            x: r * angle.cos(),
            y: r * angle.sin(),
            vx: -v * angle.sin(),
            vy: v * angle.cos(),
            m: 1.0,
        });
    }
    let calc_energy = |b: &[Body]| -> f64 {
        let mut ke = 0.0;
        let mut pe = 0.0;
        for i in 0..b.len() {
            ke += 0.5 * b[i].m * (b[i].vx * b[i].vx + b[i].vy * b[i].vy);
            for j in (i+1)..b.len() {
                let dx = b[j].x - b[i].x;
                let dy = b[j].y - b[i].y;
                let dist = (dx * dx + dy * dy + 0.1).sqrt();
                pe -= (b[i].m * b[j].m) / dist;
            }
        }
        ke + pe
    };
    let e0 = calc_energy(&bodies);
    let dt = 0.005;
    for _ in 0..20 {
        let mut ax = vec![0.0f64; n];
        let mut ay = vec![0.0f64; n];
        for i in 0..n {
            for j in 0..n {
                if i == j { continue; }
                let dx = bodies[j].x - bodies[i].x;
                let dy = bodies[j].y - bodies[i].y;
                let r3 = (dx * dx + dy * dy + 0.1).powf(1.5);
                ax[i] += bodies[j].m * dx / r3;
                ay[i] += bodies[j].m * dy / r3;
            }
        }
        for i in 0..n {
            bodies[i].vx += ax[i] * dt;
            bodies[i].vy += ay[i] * dt;
            bodies[i].x += bodies[i].vx * dt;
            bodies[i].y += bodies[i].vy * dt;
        }
    }
    let e1 = calc_energy(&bodies);
    let de = (e1 - e0).abs() / e0.abs();
    println!("INVARIANT_CHECK: {}", if de < 0.05 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", de);
}