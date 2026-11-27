import BAOCert.P2.T_R141_400
import BAOCert.P2.T_R71_200
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_R141_400_R71_200
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(263324356231033 : ℚ) / (1000000000000000 : ℚ), (263557759717422 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(880318949257009 : ℚ) / (2000000000000000 : ℚ), (881321250411470 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(731811187541 : ℚ) / (1000000000000 : ℚ), (733010932319 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1149634841903582 : ℚ) / (2000000000000000 : ℚ), (1151224628415287 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(644471270079 : ℚ) / (1000000000000 : ℚ), (645802122326 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1423129475485873 : ℚ) / (2000000000000000 : ℚ), (1425422695179217 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(557883531100 : ℚ) / (1000000000000 : ℚ), (559241470224 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1808228908765679 : ℚ) / (2000000000000000 : ℚ), (1811656511737130 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(443517667211 : ℚ) / (1000000000000 : ℚ), (444777501610 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1946436406558802 : ℚ) / (2000000000000000 : ℚ), (1950302976234513 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(405351755686 : ℚ) / (1000000000000 : ℚ), (406549822403 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(269643245262 : ℚ) / (1000000000000 : ℚ), (270527996924 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2505262583707765 : ℚ) / (2000000000000000 : ℚ), (2511017406527087 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [141/400, 71/200] and every real K, χ²_DESI DR2(Om, K) ≥ 40.0. -/
theorem chi2_slab : ∀ Om : ℝ, (((141 : ℕ) : ℝ) / ((400 : ℕ) : ℝ)) ≤ Om → Om ≤ (((71 : ℕ) : ℝ) / ((200 : ℕ) : ℝ)) → ∀ K : ℝ, ((40 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((141 : ℕ) : ℝ) / ((400 : ℕ) : ℝ)) := by positivity
  have hb1 : (((71 : ℕ) : ℝ) / ((200 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(263324356231033 : ℚ) / (1000000000000000 : ℚ), (263557759717422 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_R141_400.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(880318949257009 : ℚ) / (2000000000000000 : ℚ), (881321250411470 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_R141_400.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(731811187541 : ℚ) / (1000000000000 : ℚ), (733010932319 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_R141_400.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1149634841903582 : ℚ) / (2000000000000000 : ℚ), (1151224628415287 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_R141_400.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(644471270079 : ℚ) / (1000000000000 : ℚ), (645802122326 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_R141_400.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1423129475485873 : ℚ) / (2000000000000000 : ℚ), (1425422695179217 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_R141_400.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(557883531100 : ℚ) / (1000000000000 : ℚ), (559241470224 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_R141_400.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1808228908765679 : ℚ) / (2000000000000000 : ℚ), (1811656511737130 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_R141_400.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(443517667211 : ℚ) / (1000000000000 : ℚ), (444777501610 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_R141_400.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1946436406558802 : ℚ) / (2000000000000000 : ℚ), (1950302976234513 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_R141_400.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(405351755686 : ℚ) / (1000000000000 : ℚ), (406549822403 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_R141_400.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(269643245262 : ℚ) / (1000000000000 : ℚ), (270527996924 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_R141_400.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2505262583707765 : ℚ) / (2000000000000000 : ℚ), (2511017406527087 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R71_200.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_R141_400.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (23307025285 / 757817176 : ℚ) _ _ henv (40 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_R141_400_R71_200
