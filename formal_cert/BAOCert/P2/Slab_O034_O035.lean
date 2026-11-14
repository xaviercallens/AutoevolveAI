import BAOCert.P2.T_O034
import BAOCert.P2.T_O035
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O034_O035
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(263688915455329 : ℚ) / (1000000000000000 : ℚ), (264473535173424 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(881792024149689 : ℚ) / (2000000000000000 : ℚ), (885028791418270 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(734216597160 : ℚ) / (1000000000000 : ℚ), (739099442674 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1152111280541863 : ℚ) / (2000000000000000 : ℚ), (1157475556243921 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(647141253517 : ℚ) / (1000000000000 : ℚ), (652582310686 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1426843861646297 : ℚ) / (2000000000000000 : ℚ), (1434821833691828 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(560609373906 : ℚ) / (1000000000000 : ℚ), (566183115607 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1813991296505637 : ℚ) / (2000000000000000 : ℚ), (1826280393859533 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(446048133233 : ℚ) / (1000000000000 : ℚ), (451241781800 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1953003779035280 : ℚ) / (2000000000000000 : ℚ), (1966984509300153 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(407758575401 : ℚ) / (1000000000000 : ℚ), (412703697535 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(271421515254 : ℚ) / (1000000000000 : ℚ), (275086221909 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2515351020580505 : ℚ) / (2000000000000000 : ℚ), (2536716089499934 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [34/100, 35/100] and every real K, χ²_DESI DR2(Om, K) ≥ 17.42. -/
theorem chi2_slab : ∀ Om : ℝ, (((34 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((35 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((871 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((34 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((35 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(263688915455329 : ℚ) / (1000000000000000 : ℚ), (264473535173424 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O034.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(881792024149689 : ℚ) / (2000000000000000 : ℚ), (885028791418270 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O034.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(734216597160 : ℚ) / (1000000000000 : ℚ), (739099442674 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O034.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1152111280541863 : ℚ) / (2000000000000000 : ℚ), (1157475556243921 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O034.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(647141253517 : ℚ) / (1000000000000 : ℚ), (652582310686 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O034.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1426843861646297 : ℚ) / (2000000000000000 : ℚ), (1434821833691828 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O034.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(560609373906 : ℚ) / (1000000000000 : ℚ), (566183115607 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O034.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1813991296505637 : ℚ) / (2000000000000000 : ℚ), (1826280393859533 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O034.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(446048133233 : ℚ) / (1000000000000 : ℚ), (451241781800 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O034.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1953003779035280 : ℚ) / (2000000000000000 : ℚ), (1966984509300153 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O034.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(407758575401 : ℚ) / (1000000000000 : ℚ), (412703697535 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O034.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(271421515254 : ℚ) / (1000000000000 : ℚ), (275086221909 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O034.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2515351020580505 : ℚ) / (2000000000000000 : ℚ), (2536716089499934 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O035.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O034.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (22616051576 / 739775995 : ℚ) _ _ henv (871 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O034_O035
