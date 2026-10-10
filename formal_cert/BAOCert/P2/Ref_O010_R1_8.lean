import BAOCert.P2.T_O010
import BAOCert.P2.T_R1_8
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_O010_R1_8
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(282289172337818 : ℚ) / (1000000000000000 : ℚ), (284687960083656 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(960661901867684 : ℚ) / (2000000000000000 : ℚ), (971483558225744 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(875252527124 : ℚ) / (1000000000000 : ℚ), (896475251132 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1292523070291610 : ℚ) / (2000000000000000 : ℚ), (1313190300945877 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(817682951845 : ℚ) / (1000000000000 : ℚ), (846206507440 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1649825526433066 : ℚ) / (2000000000000000 : ℚ), (1685160675774826 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(749693635469 : ℚ) / (1000000000000 : ℚ), (784854686055 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2186996480428860 : ℚ) / (2000000000000000 : ℚ), (2252479733089892 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(640458061010 : ℚ) / (1000000000000 : ℚ), (681941654995 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2388864332914797 : ℚ) / (2000000000000000 : ℚ), (2468108610575883 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(598591609769 : ℚ) / (1000000000000 : ℚ), (641145314950 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(426760270732 : ℚ) / (1000000000000 : ℚ), (466627698349 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(3245813090310324 : ℚ) / (2000000000000000 : ℚ), (3396305258099584 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [10/100, 1/8] and every real K, χ²_DESI DR2(Om, K) ≥ 710.9. -/
theorem chi2_slab : ∀ Om : ℝ, (((10 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((1 : ℕ) : ℝ) / ((8 : ℕ) : ℝ)) → ∀ K : ℝ, ((7109 / 10 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((10 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((1 : ℕ) : ℝ) / ((8 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(282289172337818 : ℚ) / (1000000000000000 : ℚ), (284687960083656 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O010.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(960661901867684 : ℚ) / (2000000000000000 : ℚ), (971483558225744 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O010.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(875252527124 : ℚ) / (1000000000000 : ℚ), (896475251132 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O010.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1292523070291610 : ℚ) / (2000000000000000 : ℚ), (1313190300945877 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O010.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(817682951845 : ℚ) / (1000000000000 : ℚ), (846206507440 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O010.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1649825526433066 : ℚ) / (2000000000000000 : ℚ), (1685160675774826 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O010.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(749693635469 : ℚ) / (1000000000000 : ℚ), (784854686055 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O010.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(2186996480428860 : ℚ) / (2000000000000000 : ℚ), (2252479733089892 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O010.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(640458061010 : ℚ) / (1000000000000 : ℚ), (681941654995 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O010.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2388864332914797 : ℚ) / (2000000000000000 : ℚ), (2468108610575883 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O010.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(598591609769 : ℚ) / (1000000000000 : ℚ), (641145314950 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O010.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(426760270732 : ℚ) / (1000000000000 : ℚ), (466627698349 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O010.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(3245813090310324 : ℚ) / (2000000000000000 : ℚ), (3396305258099584 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R1_8.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O010.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (1583186423 / 65584032 : ℚ) _ _ henv (7109 / 10 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_O010_R1_8
