struct Ray { ox: f64, oy: f64, oz: f64, dx: f64, dy: f64, dz: f64 }
struct Sphere { cx: f64, cy: f64, cz: f64, r: f64 }
fn hit_sphere(r: &Ray, s: &Sphere) -> Option<f64> {
    let oc_x = r.ox - s.cx;
    let oc_y = r.oy - s.cy;
    let oc_z = r.oz - s.cz;
    let a = r.dx * r.dx + r.dy * r.dy + r.dz * r.dz;
    let half_b = oc_x * r.dx + oc_y * r.dy + oc_z * r.dz;
    let c = oc_x * oc_x + oc_y * oc_y + oc_z * oc_z - s.r * s.r;
    let discriminant = half_b * half_b - a * c;
    if discriminant < 0.0 { None } else {
        let sqrtd = discriminant.sqrt();
        let mut root = (-half_b - sqrtd) / a;
        if root <= 1e-3 {
            root = (-half_b + sqrtd) / a;
            if root <= 1e-3 { return None; }
        }
        Some(root)
    }
}
fn main() {
    let s = Sphere { cx: 0.0, cy: 0.0, cz: -5.0, r: 2.0 };
    let mut hits = 0;
    let mut max_geom_err = 0.0f64;
    for i in -5..=5 {
        for j in -5..=5 {
            let u = i as f64 * 0.2;
            let v = j as f64 * 0.2;
            let len = (u * u + v * v + 1.0).sqrt();
            let ray = Ray { ox: 0.0, oy: 0.0, oz: 0.0, dx: u / len, dy: v / len, dz: -1.0 / len };
            if let Some(t) = hit_sphere(&ray, &s) {
                hits += 1;
                let hx = ray.ox + t * ray.dx;
                let hy = ray.oy + t * ray.dy;
                let hz = ray.oz + t * ray.dz;
                let dist_to_center = ((hx - s.cx).powi(2) + (hy - s.cy).powi(2) + (hz - s.cz).powi(2)).sqrt();
                let err = (dist_to_center - s.r).abs();
                if err > max_geom_err { max_geom_err = err; }
            }
        }
    }
    println!("INVARIANT_CHECK: {}", if hits > 0 && max_geom_err < 1e-10 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_geom_err);
}