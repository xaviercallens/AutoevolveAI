import BAOCert.P2.T_O020
import BAOCert.P2.T_R7_40
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_R7_40_O020
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(275562056225953 : ℚ) / (1000000000000000 : ℚ), (277767966188690 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(931214790216334 : ℚ) / (2000000000000000 : ℚ), (940778701212252 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(819619763941 : ℚ) / (1000000000000 : ℚ), (836969135514 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1238112936188109 : ℚ) / (2000000000000000 : ℚ), (1255425294975487 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(746801047622 : ℚ) / (1000000000000 : ℚ), (768342309085 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1560187512981794 : ℚ) / (2000000000000000 : ℚ), (1588131556882488 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(667145745428 : ℚ) / (1000000000000 : ℚ), (691561693883 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2029729480318961 : ℚ) / (2000000000000000 : ℚ), (2077404399242255 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(550426473068 : ℚ) / (1000000000000 : ℚ), (576095614653 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2202220251121992 : ℚ) / (2000000000000000 : ℚ), (2258261260258779 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(508632051366 : ℚ) / (1000000000000 : ℚ), (533972753263 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(349530562503 : ℚ) / (1000000000000 : ℚ), (370445166304 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2916057385481655 : ℚ) / (2000000000000000 : ℚ), (3011704056757411 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [7/40, 20/100] and every real K, χ²_DESI DR2(Om, K) ≥ 103.1. -/
theorem chi2_slab : ∀ Om : ℝ, (((7 : ℕ) : ℝ) / ((40 : ℕ) : ℝ)) ≤ Om → Om ≤ (((20 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((1031 / 10 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((7 : ℕ) : ℝ) / ((40 : ℕ) : ℝ)) := by positivity
  have hb1 : (((20 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(275562056225953 : ℚ) / (1000000000000000 : ℚ), (277767966188690 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_R7_40.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(931214790216334 : ℚ) / (2000000000000000 : ℚ), (940778701212252 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_R7_40.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(819619763941 : ℚ) / (1000000000000 : ℚ), (836969135514 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_R7_40.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1238112936188109 : ℚ) / (2000000000000000 : ℚ), (1255425294975487 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_R7_40.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(746801047622 : ℚ) / (1000000000000 : ℚ), (768342309085 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_R7_40.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1560187512981794 : ℚ) / (2000000000000000 : ℚ), (1588131556882488 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_R7_40.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(667145745428 : ℚ) / (1000000000000 : ℚ), (691561693883 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_R7_40.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(2029729480318961 : ℚ) / (2000000000000000 : ℚ), (2077404399242255 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_R7_40.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(550426473068 : ℚ) / (1000000000000 : ℚ), (576095614653 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_R7_40.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2202220251121992 : ℚ) / (2000000000000000 : ℚ), (2258261260258779 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_R7_40.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(508632051366 : ℚ) / (1000000000000 : ℚ), (533972753263 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_R7_40.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(349530562503 : ℚ) / (1000000000000 : ℚ), (370445166304 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_R7_40.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2916057385481655 : ℚ) / (2000000000000000 : ℚ), (3011704056757411 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_R7_40.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (1217241315 / 45622097 : ℚ) _ _ henv (1031 / 10 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_R7_40_O020
