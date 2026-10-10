import BAOCert.P2.T_O040
import BAOCert.P2.T_R17_40
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_O040_R17_40
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(258404570700405 : ℚ) / (1000000000000000 : ℚ), (260179715961631 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(860667225131069 : ℚ) / (2000000000000000 : ℚ), (867774591282777 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(700439823164 : ℚ) / (1000000000000 : ℚ), (711175606320 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1117018799225749 : ℚ) / (2000000000000000 : ℚ), (1128627182871007 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(610254149180 : ℚ) / (1000000000000 : ℚ), (621840342698 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1374773661065264 : ℚ) / (2000000000000000 : ℚ), (1391773034877885 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(523467980785 : ℚ) / (1000000000000 : ℚ), (535016501442 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1734240767275318 : ℚ) / (2000000000000000 : ℚ), (1759908467535509 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(412080886089 : ℚ) / (1000000000000 : ℚ), (422526998099 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1862471003147129 : ℚ) / (2000000000000000 : ℚ), (1891486429226685 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(375585980010 : ℚ) / (1000000000000 : ℚ), (385449726818 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(247927880044 : ℚ) / (1000000000000 : ℚ), (255068721919 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2378060289951422 : ℚ) / (2000000000000000 : ℚ), (2421472151517876 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [40/100, 17/40] and every real K, χ²_DESI DR2(Om, K) ≥ 59.66. -/
theorem chi2_slab : ∀ Om : ℝ, (((40 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((17 : ℕ) : ℝ) / ((40 : ℕ) : ℝ)) → ∀ K : ℝ, ((2983 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((40 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((17 : ℕ) : ℝ) / ((40 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(258404570700405 : ℚ) / (1000000000000000 : ℚ), (260179715961631 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O040.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(860667225131069 : ℚ) / (2000000000000000 : ℚ), (867774591282777 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O040.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(700439823164 : ℚ) / (1000000000000 : ℚ), (711175606320 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O040.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1117018799225749 : ℚ) / (2000000000000000 : ℚ), (1128627182871007 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O040.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(610254149180 : ℚ) / (1000000000000 : ℚ), (621840342698 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O040.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1374773661065264 : ℚ) / (2000000000000000 : ℚ), (1391773034877885 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O040.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(523467980785 : ℚ) / (1000000000000 : ℚ), (535016501442 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O040.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1734240767275318 : ℚ) / (2000000000000000 : ℚ), (1759908467535509 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O040.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(412080886089 : ℚ) / (1000000000000 : ℚ), (422526998099 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O040.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1862471003147129 : ℚ) / (2000000000000000 : ℚ), (1891486429226685 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O040.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(375585980010 : ℚ) / (1000000000000 : ℚ), (385449726818 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O040.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(247927880044 : ℚ) / (1000000000000 : ℚ), (255068721919 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O040.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2378060289951422 : ℚ) / (2000000000000000 : ℚ), (2421472151517876 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R17_40.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O040.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (15221007701 / 476670166 : ℚ) _ _ henv (2983 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_O040_R17_40
