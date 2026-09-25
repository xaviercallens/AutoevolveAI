#[derive(Clone, Copy)]
struct Point3D {
    coords: [f64; 3],
    id: usize,
}

impl Point3D {
    fn dist_sq(&self, other: &Point3D) -> f64 {
        let dx = self.coords[0] - other.coords[0];
        let dy = self.coords[1] - other.coords[1];
        let dz = self.coords[2] - other.coords[2];
        dx * dx + dy * dy + dz * dz
    }
}

struct KdNode {
    point: Point3D,
    left: Option<Box<KdNode>>,
    right: Option<Box<KdNode>>,
    axis: usize,
}

fn build_kdtree(mut points: Vec<Point3D>, depth: usize) -> Option<Box<KdNode>> {
    if points.is_empty() { return None; }
    let axis = depth % 3;
    points.sort_by(|a, b| a.coords[axis].partial_cmp(&b.coords[axis]).unwrap());
    let median = points.len() / 2;
    let node_point = points[median];
    let left_pts = points[..median].to_vec();
    let right_pts = points[(median + 1)..].to_vec();

    Some(Box::new(KdNode {
        point: node_point,
        left: build_kdtree(left_pts, depth + 1),
        right: build_kdtree(right_pts, depth + 1),
        axis,
    }))
}

fn knn_search(node: &Option<Box<KdNode>>, target: &Point3D, best_point: &mut Point3D, best_dist_sq: &mut f64) {
    if let Some(n) = node {
        let d2 = n.point.dist_sq(target);
        if d2 < *best_dist_sq {
            *best_dist_sq = d2;
            *best_point = n.point;
        }
        let axis = n.axis;
        let delta = target.coords[axis] - n.point.coords[axis];
        let (first, second) = if delta <= 0.0 { (&n.left, &n.right) } else { (&n.right, &n.left) };

        knn_search(first, target, best_point, best_dist_sq);
        if delta * delta < *best_dist_sq {
            knn_search(second, target, best_point, best_dist_sq);
        }
    }
}

fn main() {
    let n = std::hint::black_box(1000);
    let mut points = Vec::with_capacity(n);
    for i in 0..n {
        let x = ((i * 17) % 1000) as f64 / 100.0;
        let y = ((i * 31) % 1000) as f64 / 100.0;
        let z = ((i * 53) % 1000) as f64 / 100.0;
        points.push(Point3D { coords: [x, y, z], id: i });
    }

    let tree = build_kdtree(points.clone(), 0);

    let mut total_discrepancies = 0;
    for q in 0..50 {
        let target = Point3D {
            coords: [
                ((q * 73) % 1000) as f64 / 100.0,
                ((q * 109) % 1000) as f64 / 100.0,
                ((q * 137) % 1000) as f64 / 100.0,
            ],
            id: usize::MAX,
        };

        // Brute-force ground truth
        let mut bf_best_pt = points[0];
        let mut bf_best_dist = points[0].dist_sq(&target);
        for p in &points[1..] {
            let d = p.dist_sq(&target);
            if d < bf_best_dist {
                bf_best_dist = d;
                bf_best_pt = *p;
            }
        }

        // KD-Tree query
        let mut kd_best_pt = points[0];
        let mut kd_best_dist = f64::INFINITY;
        knn_search(&tree, &target, &mut kd_best_pt, &mut kd_best_dist);

        if (bf_best_dist - kd_best_dist).abs() > 1e-9 {
            total_discrepancies += 1;
        }
    }

    let error = total_discrepancies as f64;
    println!("INVARIANT_CHECK: {}", if total_discrepancies == 0 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", error);
}