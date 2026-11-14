import BAOCert.P2.T_O035
import BAOCert.P2.T_R141_400
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_O035_R141_400
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(263506407282128 : ℚ) / (1000000000000000 : ℚ), (263739994219923 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(881054261342768 : ℚ) / (2000000000000000 : ℚ), (882057807553549 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(733010932318 : ℚ) / (1000000000000 : ℚ), (734216597161 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1150870430536200 : ℚ) / (2000000000000000 : ℚ), (1152464139289758 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(645802122325 : ℚ) / (1000000000000 : ℚ), (647141253518 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1424981936647572 : ℚ) / (2000000000000000 : ℚ), (1427283252274259 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(559241470223 : ℚ) / (1000000000000 : ℚ), (560609373907 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1811101289236097 : ℚ) / (2000000000000000 : ℚ), (1814545248375046 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(444777501609 : ℚ) / (1000000000000 : ℚ), (446048133234 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1949709526053947 : ℚ) / (2000000000000000 : ℚ), (1953596020462847 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(406549822402 : ℚ) / (1000000000000 : ℚ), (407758575402 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(270527996923 : ℚ) / (1000000000000 : ℚ), (271421515255 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2510287934519350 : ℚ) / (2000000000000000 : ℚ), (2516079599069911 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [35/100, 141/400] and every real K, χ²_DESI DR2(Om, K) ≥ 37.34. -/
theorem chi2_slab : ∀ Om : ℝ, (((35 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((141 : ℕ) : ℝ) / ((400 : ℕ) : ℝ)) → ∀ K : ℝ, ((1867 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((35 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((141 : ℕ) : ℝ) / ((400 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(263506407282128 : ℚ) / (1000000000000000 : ℚ), (263739994219923 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O035.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(881054261342768 : ℚ) / (2000000000000000 : ℚ), (882057807553549 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O035.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(733010932318 : ℚ) / (1000000000000 : ℚ), (734216597161 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O035.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1150870430536200 : ℚ) / (2000000000000000 : ℚ), (1152464139289758 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O035.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(645802122325 : ℚ) / (1000000000000 : ℚ), (647141253518 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O035.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1424981936647572 : ℚ) / (2000000000000000 : ℚ), (1427283252274259 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O035.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(559241470223 : ℚ) / (1000000000000 : ℚ), (560609373907 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O035.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1811101289236097 : ℚ) / (2000000000000000 : ℚ), (1814545248375046 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O035.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(444777501609 : ℚ) / (1000000000000 : ℚ), (446048133234 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O035.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1949709526053947 : ℚ) / (2000000000000000 : ℚ), (1953596020462847 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O035.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(406549822402 : ℚ) / (1000000000000 : ℚ), (407758575402 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O035.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(270527996923 : ℚ) / (1000000000000 : ℚ), (271421515255 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O035.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2510287934519350 : ℚ) / (2000000000000000 : ℚ), (2516079599069911 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R141_400.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O035.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (3772896437 / 122883009 : ℚ) _ _ henv (1867 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_O035_R141_400
