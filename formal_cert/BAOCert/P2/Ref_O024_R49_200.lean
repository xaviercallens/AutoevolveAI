import BAOCert.P2.T_O024
import BAOCert.P2.T_R49_200
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_O024_R49_200
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(271796237456332 : ℚ) / (1000000000000000 : ℚ), (272243418894492 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(915215331083897 : ℚ) / (2000000000000000 : ℚ), (917144230450471 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(790934566303 : ℚ) / (1000000000000 : ℚ), (793973870118 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1209609343105248 : ℚ) / (2000000000000000 : ℚ), (1212930267236330 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(712203936957 : ℚ) / (1000000000000 : ℚ), (715812293318 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1514984291986941 : ℚ) / (2000000000000000 : ℚ), (1520115885849447 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(629031237299 : ℚ) / (1000000000000 : ℚ), (632946427918 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1954486192010596 : ℚ) / (2000000000000000 : ℚ), (1962789988591541 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(511757462246 : ℚ) / (1000000000000 : ℚ), (515655952876 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2114508484892183 : ℚ) / (2000000000000000 : ℚ), (2124106608755676 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(470876681535 : ℚ) / (1000000000000 : ℚ), (474661332195 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(319407662143 : ℚ) / (1000000000000 : ℚ), (322375261268 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2770682882000825 : ℚ) / (2000000000000000 : ℚ), (2786157717659568 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [24/100, 49/200] and every real K, χ²_DESI DR2(Om, K) ≥ 48.58. -/
theorem chi2_slab : ∀ Om : ℝ, (((24 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((49 : ℕ) : ℝ) / ((200 : ℕ) : ℝ)) → ∀ K : ℝ, ((2429 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((24 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((49 : ℕ) : ℝ) / ((200 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(271796237456332 : ℚ) / (1000000000000000 : ℚ), (272243418894492 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O024.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(915215331083897 : ℚ) / (2000000000000000 : ℚ), (917144230450471 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O024.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(790934566303 : ℚ) / (1000000000000 : ℚ), (793973870118 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O024.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1209609343105248 : ℚ) / (2000000000000000 : ℚ), (1212930267236330 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O024.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(712203936957 : ℚ) / (1000000000000 : ℚ), (715812293318 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O024.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1514984291986941 : ℚ) / (2000000000000000 : ℚ), (1520115885849447 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O024.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(629031237299 : ℚ) / (1000000000000 : ℚ), (632946427918 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O024.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1954486192010596 : ℚ) / (2000000000000000 : ℚ), (1962789988591541 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O024.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(511757462246 : ℚ) / (1000000000000 : ℚ), (515655952876 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O024.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2114508484892183 : ℚ) / (2000000000000000 : ℚ), (2124106608755676 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O024.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(470876681535 : ℚ) / (1000000000000 : ℚ), (474661332195 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O024.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(319407662143 : ℚ) / (1000000000000 : ℚ), (322375261268 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O024.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2770682882000825 : ℚ) / (2000000000000000 : ℚ), (2786157717659568 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R49_200.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O024.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (28077757921 / 995909535 : ℚ) _ _ henv (2429 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_O024_R49_200
