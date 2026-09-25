#[derive(Clone, Copy, Debug, PartialEq)]
struct Point {
    x: f64,
    y: f64,
}

fn orientation(p: Point, q: Point, r: Point) -> f64 {
    // Cross product: > 0 => counter-clockwise, < 0 => clockwise, 0 => collinear
    (q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x)
}

fn convex_hull(mut points: Vec<Point>) -> Vec<Point> {
    points.sort_by(|a, b| {
        a.x.partial_cmp(&b.x).unwrap().then(a.y.partial_cmp(&b.y).unwrap())
    });
    points.dedup();
    if points.len() <= 2 { return points; }

    let mut lower = Vec::new();
    for &p in &points {
        while lower.len() >= 2 && orientation(lower[lower.len() - 2], lower[lower.len() - 1], p) <= 0.0 {
            lower.pop();
        }
        lower.push(p);
    }

    let mut upper = Vec::new();
    for &p in points.iter().rev() {
        while upper.len() >= 2 && orientation(upper[upper.len() - 2], upper[upper.len() - 1], p) <= 0.0 {
            upper.pop();
        }
        upper.push(p);
    }

    lower.pop();
    upper.pop();
    lower.extend(upper);
    lower
}

fn main() {
    let n = std::hint::black_box(500);
    let mut pts = Vec::with_capacity(n);
    for i in 0..n {
        let x = ((i * 47) % 1000) as f64 / 10.0;
        let y = ((i * 79) % 1000) as f64 / 10.0;
        pts.push(Point { x, y });
    }

    let hull = convex_hull(pts.clone());

    // Invariant: all points must lie in the half-planes defined by the hull edges
    let mut max_violation = 0.0f64;
    let m = hull.len();
    for p in &pts {
        for i in 0..m {
            let p1 = hull[i];
            let p2 = hull[(i + 1) % m];
            let cross = orientation(p1, p2, *p);
            if cross < -1e-8 {
                let viol = cross.abs();
                if viol > max_violation { max_violation = viol; }
            }
        }
    }

    println!("INVARIANT_CHECK: {}", if max_violation < 1e-7 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", max_violation);
}