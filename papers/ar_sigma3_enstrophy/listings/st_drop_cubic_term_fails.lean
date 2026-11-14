-- Autoresearch_Enstrophy.lean (prior round) lines 84-86
theorem drop_cubic_term_fails :
    ¬ (2 * 1 * enstrophy 0 (fun n => if n = 0 then (1 : ℂ) else if n = 1 then -Complex.I else 0)
        ≤ ham3 1 0 (fun n => if n = 0 then (1 : ℂ) else if n = 1 then -Complex.I else 0)) := ...
