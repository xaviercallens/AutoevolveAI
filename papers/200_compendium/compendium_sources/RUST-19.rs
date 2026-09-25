fn main() {
    let n_states = std::hint::black_box(2);
    let start_p = [0.6, 0.4];
    let trans_p = [[0.7, 0.3], [0.4, 0.6]];
    let emit_p = [[0.5, 0.4, 0.1], [0.1, 0.3, 0.6]];
    let obs = [0, 1, 2, 0, 2];
    let t_len = obs.len();

    let mut viterbi = vec![[0.0f64; 2]; t_len];
    let mut backpointer = vec![[0usize; 2]; t_len];

    for s in 0..n_states {
        viterbi[0][s] = start_p[s] * emit_p[s][obs[0]];
    }

    for t in 1..t_len {
        for s in 0..n_states {
            let mut max_prob = -1.0;
            let mut best_prev = 0;
            for prev in 0..n_states {
                let prob = viterbi[t - 1][prev] * trans_p[prev][s] * emit_p[s][obs[t]];
                if prob > max_prob {
                    max_prob = prob;
                    best_prev = prev;
                }
            }
            viterbi[t][s] = max_prob;
            backpointer[t][s] = best_prev;
        }
    }

    let mut max_final_prob = -1.0;
    for s in 0..n_states {
        if viterbi[t_len - 1][s] > max_final_prob {
            max_final_prob = viterbi[t_len - 1][s];
        }
    }

    let mut true_max_prob = -1.0;
    for code in 0..(1 << t_len) {
        let mut path = [0; 5];
        for bit in 0..t_len { path[bit] = (code >> bit) & 1; }
        let mut prob = start_p[path[0]] * emit_p[path[0]][obs[0]];
        for step in 1..t_len {
            prob *= trans_p[path[step - 1]][path[step]] * emit_p[path[step]][obs[step]];
        }
        if prob > true_max_prob { true_max_prob = prob; }
    }
    let err = (max_final_prob - true_max_prob).abs();
    println!("INVARIANT_CHECK: {}", if err < 1e-12 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", err);
}