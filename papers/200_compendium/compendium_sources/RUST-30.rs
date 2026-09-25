fn main() {
    let size = std::hint::black_box(16);
    let n_cells = size * size;
    let mut state = vec![[0u8; 4]; n_cells];
    for i in 0..n_cells {
        if i % 3 == 0 { state[i][0] = 1; }
        if i % 4 == 0 { state[i][1] = 1; }
        if i % 5 == 0 { state[i][2] = 1; }
        if i % 7 == 0 { state[i][3] = 1; }
    }
    let count_particles = |s: &Vec<[u8; 4]>| -> (usize, isize, isize) {
        let mut total_n = 0; let mut total_px = 0isize; let mut total_py = 0isize;
        for cell in s {
            total_n += (cell[0] + cell[1] + cell[2] + cell[3]) as usize;
            total_py += cell[0] as isize - cell[2] as isize;
            total_px += cell[1] as isize - cell[3] as isize;
        }
        (total_n, total_px, total_py)
    };
    let (n0, px0, py0) = count_particles(&state);
    for _step in 0..10 {
        for cell in state.iter_mut() {
            if cell[0] == 1 && cell[2] == 1 && cell[1] == 0 && cell[3] == 0 {
                cell[0] = 0; cell[2] = 0; cell[1] = 1; cell[3] = 1;
            } else if cell[1] == 1 && cell[3] == 1 && cell[0] == 0 && cell[2] == 0 {
                cell[1] = 0; cell[3] = 0; cell[0] = 1; cell[2] = 1;
            }
        }
        let mut next_state = vec![[0u8; 4]; n_cells];
        for y in 0..size {
            for x in 0..size {
                let idx = y * size + x;
                let y_north = (y + 1) % size;
                let x_east = (x + 1) % size;
                let y_south = (y + size - 1) % size;
                let x_west = (x + size - 1) % size;
                next_state[y_north * size + x][0] = state[idx][0];
                next_state[y * size + x_east][1] = state[idx][1];
                next_state[y_south * size + x][2] = state[idx][2];
                next_state[y * size + x_west][3] = state[idx][3];
            }
        }
        state = next_state;
    }
    let (n_end, px_end, py_end) = count_particles(&state);
    let n_drift = (n_end as isize - n0 as isize).abs();
    let p_drift = (px_end - px0).abs() + (py_end - py0).abs();
    let total_drift = (n_drift + p_drift) as f64;
    println!("INVARIANT_CHECK: {}", if total_drift == 0.0 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", total_drift);
}