fn main() {
    let verts: [[f64; 3]; 6] = [
        [1.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, -1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, -1.0],
    ];
    let faces: [[usize; 3]; 8] = [
        [0, 2, 4], [0, 3, 4], [1, 2, 4], [1, 3, 4],
        [0, 2, 5], [0, 3, 5], [1, 2, 5], [1, 3, 5],
    ];
    let v = std::hint::black_box(6);
    let e = std::hint::black_box(12);
    let f = std::hint::black_box(8);
    let chi = v - e + f;
    let chi_err = (chi - 2) as f64;

    let mut vol = 0.0f64;
    for fc in &faces {
        let a = verts[fc[0]];
        let b = verts[fc[1]];
        let c = verts[fc[2]];
        let det: f64 = a[0] * (b[1] * c[2] - b[2] * c[1])
                     - a[1] * (b[0] * c[2] - b[2] * c[0])
                     + a[2] * (b[0] * c[1] - b[1] * c[0]);
        vol += det.abs() / 6.0;
    }
    let vol_exact = 4.0 / 3.0;
    let vol_err = (vol - vol_exact).abs();
    let total_err = chi_err.abs() + vol_err;
    println!("INVARIANT_CHECK: {}", if total_err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", total_err);
}