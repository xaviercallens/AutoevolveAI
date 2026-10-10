import BAOCert.P2.T_O022
import BAOCert.P2.T_O024
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O022_O024
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(17012838126073 / 62500000000000 : ℚ), (68475078236263 / 250000000000000 : ℚ)⟩, ⟨(57308637769973 / 125000000000000 : ℚ), (924157611276699 / 2000000000000000 : ℚ)⟩, ⟨(793973870117 / 1000000000000 : ℚ), (806491156907 / 1000000000000 : ℚ)⟩, ⟨(242529215905647 / 400000000000000 : ℚ), (76586213989611 / 125000000000000 : ℚ)⟩, ⟨(715812293317 / 1000000000000 : ℚ), (73081437451 / 100000000000 : ℚ)⟩, ⟨(189968604034437 / 250000000000000 : ℚ), (1539781389830417 / 2000000000000000 : ℚ)⟩, ⟨(632946427917 / 1000000000000 : ℚ), (324685820669 / 500000000000 : ℚ)⟩, ⟨(981152822270887 / 1000000000000000 : ℚ), (997673608225617 / 1000000000000000 : ℚ)⟩, ⟨(4125247623 / 8000000000 : ℚ), (106438240801 / 200000000000 : ℚ)⟩, ⟨(1061790635042451 / 1000000000000000 : ℚ), (1080994655253039 / 1000000000000000 : ℚ)⟩, ⟨(237330666097 / 500000000000 : ℚ), (490767091351 / 1000000000000 : ℚ)⟩, ⟨(322375261267 / 1000000000000 : ℚ), (67026115429 / 200000000000 : ℚ)⟩, ⟨(111419203716647 / 80000000000000 : ℚ), (2848540575928429 / 2000000000000000 : ℚ)⟩]

/-- For every Om in [11/50, 6/25] and every real K, χ²_DESI DR2(Om, K) ≥ 22.05. -/
theorem chi2_slab : ∀ Om : ℝ, (((11 : ℕ) : ℝ) / ((50 : ℕ) : ℝ)) ≤ Om → Om ≤ (((6 : ℕ) : ℝ) / ((25 : ℕ) : ℝ)) → ∀ K : ℝ, ((441 / 20 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((11 : ℕ) : ℝ) / ((50 : ℕ) : ℝ)) := by positivity
  have hb1 : (((6 : ℕ) : ℝ) / ((25 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(17012838126073 / 62500000000000 : ℚ), (68475078236263 / 250000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O022.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(57308637769973 / 125000000000000 : ℚ), (924157611276699 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O022.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(793973870117 / 1000000000000 : ℚ), (806491156907 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O022.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(242529215905647 / 400000000000000 : ℚ), (76586213989611 / 125000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O022.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(715812293317 / 1000000000000 : ℚ), (73081437451 / 100000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O022.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(189968604034437 / 250000000000000 : ℚ), (1539781389830417 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O022.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(632946427917 / 1000000000000 : ℚ), (324685820669 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O022.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(981152822270887 / 1000000000000000 : ℚ), (997673608225617 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O022.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(4125247623 / 8000000000 : ℚ), (106438240801 / 200000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O022.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1061790635042451 / 1000000000000000 : ℚ), (1080994655253039 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O022.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(237330666097 / 500000000000 : ℚ), (490767091351 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O022.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(322375261267 / 1000000000000 : ℚ), (67026115429 / 200000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O022.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(111419203716647 / 80000000000000 : ℚ), (2848540575928429 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O022.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (15132806811 / 543024149 : ℚ) _ _ henv (441 / 20 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O022_O024
