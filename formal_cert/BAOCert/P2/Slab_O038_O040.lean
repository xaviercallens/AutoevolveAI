import BAOCert.P2.T_O038
import BAOCert.P2.T_O040
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O038_O040
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(10404933539133 / 40000000000000 : ℚ), (261582845664831 / 1000000000000000 : ℚ)⟩, ⟨(216871441722019 / 500000000000000 : ℚ), (436688610240601 / 1000000000000000 : ℚ)⟩, ⟨(711175606319 / 1000000000000 : ℚ), (90016123179 / 125000000000 : ℚ)⟩, ⟨(282062255803073 / 500000000000000 : ℚ), (1137927866528431 / 2000000000000000 : ℚ)⟩, ⟨(621840342697 / 1000000000000 : ℚ), (631599984013 / 1000000000000 : ℚ)⟩, ⟨(695654025688729 / 1000000000000000 : ℚ), (281112327536489 / 400000000000000 : ℚ)⟩, ⟨(535016501441 / 1000000000000 : ℚ), (272413336803 / 500000000000 : ℚ)⟩, ⟨(351866198906193 / 400000000000000 : ℚ), (1781001446050089 / 2000000000000000 : ℚ)⟩, ⟨(211263499049 / 500000000000 : ℚ), (21574056851 / 50000000000 : ℚ)⟩, ⟨(945435939475267 / 1000000000000000 : ℚ), (1915421365299273 / 2000000000000000 : ℚ)⟩, ⟨(385449726817 / 1000000000000 : ℚ), (12310184767 / 31250000000 : ℚ)⟩, ⟨(127534360959 / 500000000000 : ℚ), (65312021161 / 250000000000 : ℚ)⟩, ⟨(1210363610117567 / 1000000000000000 : ℚ), (2457716828204111 / 2000000000000000 : ℚ)⟩]

/-- For every Om in [19/50, 2/5] and every real K, χ²_DESI DR2(Om, K) ≥ 42.75. -/
theorem chi2_slab : ∀ Om : ℝ, (((19 : ℕ) : ℝ) / ((50 : ℕ) : ℝ)) ≤ Om → Om ≤ (((2 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) → ∀ K : ℝ, ((171 / 4 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((19 : ℕ) : ℝ) / ((50 : ℕ) : ℝ)) := by positivity
  have hb1 : (((2 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(10404933539133 / 40000000000000 : ℚ), (261582845664831 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O038.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(216871441722019 / 500000000000000 : ℚ), (436688610240601 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O038.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(711175606319 / 1000000000000 : ℚ), (90016123179 / 125000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O038.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(282062255803073 / 500000000000000 : ℚ), (1137927866528431 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O038.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(621840342697 / 1000000000000 : ℚ), (631599984013 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O038.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(695654025688729 / 1000000000000000 : ℚ), (281112327536489 / 400000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O038.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(535016501441 / 1000000000000 : ℚ), (272413336803 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O038.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(351866198906193 / 400000000000000 : ℚ), (1781001446050089 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O038.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(211263499049 / 500000000000 : ℚ), (21574056851 / 50000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O038.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(945435939475267 / 1000000000000000 : ℚ), (1915421365299273 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O038.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(385449726817 / 1000000000000 : ℚ), (12310184767 / 31250000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O038.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(127534360959 / 500000000000 : ℚ), (65312021161 / 250000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O038.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(1210363610117567 / 1000000000000000 : ℚ), (2457716828204111 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O040.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O038.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (27809297673 / 883038547 : ℚ) _ _ henv (171 / 4 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O038_O040
