theorem price_equation (s : Finset ι) (n w z z' : ι → K)
    (hN : ∑ i ∈ s, n i ≠ 0) (hW : ∑ i ∈ s, n i * w i ≠ 0) :
    wmean s n w * (zbarNext s n w z' - wmean s n z)
      = wcov s n w z + wmean s n (fun i => w i * (z' i - z i)) := -- proof elided

theorem wcov_eq_moment (s : Finset ι) (n f g : ι → K) (hN : ∑ i ∈ s, n i ≠ 0) :
    wcov s n f g = wmean s n (fun i => f i * g i) - wmean s n f * wmean s n g := -- proof elided

theorem fisher_haploid (s : Finset ι) (n w : ι → K)
    (hN : ∑ i ∈ s, n i ≠ 0) (hW : ∑ i ∈ s, n i * w i ≠ 0) :
    wmean s n w * (wbarNext s n w - wmean s n w) = wvar s n w := -- proof elided

theorem fisher_haploid_div (s : Finset ι) (n w : ι → K)
    (hN : ∑ i ∈ s, n i ≠ 0) (hW : ∑ i ∈ s, n i * w i ≠ 0) :
    wbarNext s n w - wmean s n w = wvar s n w / wmean s n w := -- proof elided

theorem fisher_haploid_nondecreasing (s : Finset ι) (n w : ι → ℝ)
    (hn : ∀ i ∈ s, 0 ≤ n i) (hN : 0 < ∑ i ∈ s, n i) (hW : 0 < ∑ i ∈ s, n i * w i) :
    wmean s n w ≤ wbarNext s n w := -- proof elided

theorem price_equation_pos (s : Finset ι) (n w z z' : ι → ℝ) (hs : s.Nonempty)
    (hn : ∀ i ∈ s, 0 < n i) (hw : ∀ i ∈ s, 0 < w i) :
    wmean s n w * (zbarNext s n w z' - wmean s n z)
      = wcov s n w z + wmean s n (fun i => w i * (z' i - z i)) := -- proof elided
