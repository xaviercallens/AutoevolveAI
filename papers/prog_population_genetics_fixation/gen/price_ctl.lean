theorem ctl_pos_three_types :
    wmean (Finset.univ : Finset (Fin 3)) ![1, 2, 3] ![1, 2, 4]
        * (zbarNext Finset.univ ![1, 2, 3] ![1, 2, 4] ![1, 1, 2]
          - wmean Finset.univ ![1, 2, 3] ![0, 1, 3]) = (-13 / 36 : ℚ) ∧
    wcov (Finset.univ : Finset (Fin 3)) ![1, 2, 3] ![1, 2, 4] ![0, 1, 3]
        + wmean Finset.univ ![1, 2, 3]
          (fun i => (![1, 2, 4] : Fin 3 → ℚ) i * ((![1, 1, 2] : Fin 3 → ℚ) i - (![0, 1, 3] : Fin 3 → ℚ) i))
        = (-13 / 36 : ℚ) := -- proof elided

theorem ctl_neg_transmission_bias :
    zbarNext (Finset.univ : Finset (Fin 2)) ![1, 1] ![1, 2] ![1, 1]
        - wmean Finset.univ ![1, 1] ![1, 2] = (-1 / 2 : ℚ) ∧
    wvar (Finset.univ : Finset (Fin 2)) ![1, 1] ![1, 2] / wmean Finset.univ ![1, 1] ![1, 2]
        = (1 / 6 : ℚ) ∧
    wmean (Finset.univ : Finset (Fin 2)) ![1, 1] ![1, 2]
        * (zbarNext Finset.univ ![1, 1] ![1, 2] ![1, 1] - wmean Finset.univ ![1, 1] ![1, 2])
        = (-3 / 4 : ℚ) ∧
    wcov (Finset.univ : Finset (Fin 2)) ![1, 1] ![1, 2] ![1, 2]
        + wmean Finset.univ ![1, 1]
          (fun i => (![1, 2] : Fin 2 → ℚ) i * ((![1, 1] : Fin 2 → ℚ) i - (![1, 2] : Fin 2 → ℚ) i))
        = (-3 / 4 : ℚ) := -- proof elided

theorem ctl_neg_missing_wbar :
    wbarNext (Finset.univ : Finset (Fin 2)) ![1, 1] ![1, 2] - wmean Finset.univ ![1, 1] ![1, 2]
        = (1 / 6 : ℚ) ∧
    wvar (Finset.univ : Finset (Fin 2)) ![1, 1] (![1, 2] : Fin 2 → ℚ) = 1 / 4 ∧
    wvar (Finset.univ : Finset (Fin 2)) ![1, 1] (![1, 2] : Fin 2 → ℚ)
      ≠ wbarNext Finset.univ ![1, 1] ![1, 2] - wmean Finset.univ ![1, 1] ![1, 2] := -- proof elided
