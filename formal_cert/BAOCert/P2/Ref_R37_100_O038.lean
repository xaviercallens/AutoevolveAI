import BAOCert.P2.T_O038
import BAOCert.P2.T_R37_100
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_R37_100_O038
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(261528544416602 : ℚ) / (1000000000000000 : ℚ), (262294777815340 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(873097349465613 : ℚ) / (2000000000000000 : ℚ), (876232967946190 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(720128985431 : ℚ) / (1000000000000 : ℚ), (724734374041 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1137559466511031 : ℚ) / (2000000000000000 : ℚ), (1142692861279587 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(631599984012 : ℚ) / (1000000000000 : ℚ), (636655340838 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1405106464354182 : ℚ) / (2000000000000000 : ℚ), (1412658631564206 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(544826673605 : ℚ) / (1000000000000 : ℚ), (549938549503 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1780432927184466 : ℚ) / (2000000000000000 : ℚ), (1791917839808770 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(431481137019 : ℚ) / (1000000000000 : ℚ), (436177092027 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1914815291208848 : ℚ) / (2000000000000000 : ℚ), (1927829587787195 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(393925912543 : ℚ) / (1000000000000 : ℚ), (398379220166 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(261248084643 : ℚ) / (1000000000000 : ℚ), (264511079793 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2456978076284094 : ℚ) / (2000000000000000 : ℚ), (2476610800103776 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [37/100, 38/100] and every real K, χ²_DESI DR2(Om, K) ≥ 48.74. -/
theorem chi2_slab : ∀ Om : ℝ, (((37 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((38 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((2437 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((37 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((38 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(261528544416602 : ℚ) / (1000000000000000 : ℚ), (262294777815340 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_R37_100.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(873097349465613 : ℚ) / (2000000000000000 : ℚ), (876232967946190 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_R37_100.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(720128985431 : ℚ) / (1000000000000 : ℚ), (724734374041 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_R37_100.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1137559466511031 : ℚ) / (2000000000000000 : ℚ), (1142692861279587 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_R37_100.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(631599984012 : ℚ) / (1000000000000 : ℚ), (636655340838 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_R37_100.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1405106464354182 : ℚ) / (2000000000000000 : ℚ), (1412658631564206 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_R37_100.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(544826673605 : ℚ) / (1000000000000 : ℚ), (549938549503 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_R37_100.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1780432927184466 : ℚ) / (2000000000000000 : ℚ), (1791917839808770 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_R37_100.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(431481137019 : ℚ) / (1000000000000 : ℚ), (436177092027 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_R37_100.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1914815291208848 : ℚ) / (2000000000000000 : ℚ), (1927829587787195 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_R37_100.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(393925912543 : ℚ) / (1000000000000 : ℚ), (398379220166 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_R37_100.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(261248084643 : ℚ) / (1000000000000 : ℚ), (264511079793 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_R37_100.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2456978076284094 : ℚ) / (2000000000000000 : ℚ), (2476610800103776 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O038.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_R37_100.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (14247434459 / 456760844 : ℚ) _ _ henv (2437 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_R37_100_O038
