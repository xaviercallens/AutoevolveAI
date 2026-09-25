fn main() {
    // 3 nodes triangle: (0,0), (1,0), (0,1)
    let area = 0.5;
    // Local stiffness matrix K = B^T B * Area
    // grad phi_1 = (-1, -1), grad phi_2 = (1, 0), grad phi_3 = (0, 1)
    let k = [
        [ 2.0 * area, -1.0 * area, -1.0 * area],
        [-1.0 * area,  1.0 * area,  0.0 * area],
        [-1.0 * area,  0.0 * area,  1.0 * area]
    ];
    // Invariant: Null space of Laplacian on constant vector (1, 1, 1)
    let mut null_res = 0.0;
    for i in 0..3 {
        let row_sum: f64 = k[i].iter().sum();
        null_res += row_sum.abs();
    }
    println!("INVARIANT_CHECK: {}", if null_res < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", null_res);
}