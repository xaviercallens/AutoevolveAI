import BAOCert.P2.T_FitFine
import BAOCert.P2.Data_Tamper

namespace BAOCert.P2.Fit_Tamper
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(267656640852960 : ℚ) / (1000000000000000 : ℚ), (267661150270096 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(8980093744124392 : ℚ) / (20000000000000000 : ℚ), (8980332711532688 : ℚ) / (20000000000000000 : ℚ)⟩, ⟨(761032601904 : ℚ) / (1000000000000 : ℚ), (761032601905 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(11796466787192679 : ℚ) / (20000000000000000 : ℚ), (11796789403948199 : ℚ) / (20000000000000000 : ℚ)⟩, ⟨(677383258600 : ℚ) / (1000000000000 : ℚ), (677383258601 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(14685438720179756 : ℚ) / (20000000000000000 : ℚ), (14685846800417121 : ℚ) / (20000000000000000 : ℚ)⟩, ⟨(591919781315 : ℚ) / (1000000000000 : ℚ), (591919781316 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(18794681414802300 : ℚ) / (20000000000000000 : ℚ), (18795205840426801 : ℚ) / (20000000000000000 : ℚ)⟩, ⟨(475574401919 : ℚ) / (1000000000000 : ℚ), (475574401920 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(20279130785876203 : ℚ) / (20000000000000000 : ℚ), (20279694817175477 : ℚ) / (20000000000000000 : ℚ)⟩, ⟨(435968730406 : ℚ) / (1000000000000 : ℚ), (435968730407 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(292534235876 : ℚ) / (1000000000000 : ℚ), (292534235877 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(26318935983824944 : ℚ) / (20000000000000000 : ℚ), (26319643449635668 : ℚ) / (20000000000000000 : ℚ)⟩]

/-- χ² of DESI DR2 at Om = 0.29743, h r_d = 101.543 Mpc (K = 299792458/10154300) lies in [122.697, 122.7513]. -/
theorem chi2_fit : ((122697 / 1000 : ℚ) : ℝ) ≤ Data_Tamper.chi2DESI (((29743 : ℕ) : ℝ) / ((100000 : ℕ) : ℝ)) (((299792458 / 10154300 : ℚ)) : ℝ) ∧
    Data_Tamper.chi2DESI (((29743 : ℕ) : ℝ) / ((100000 : ℕ) : ℝ)) (((299792458 / 10154300 : ℚ)) : ℝ) ≤ ((1227513 / 10000 : ℚ) : ℝ) := by
  have h0 := BAOCert.P2.T_FitFine.wV_z0295
  have h1 := BAOCert.P2.T_FitFine.chi_z0510
  have h2 := BAOCert.P2.T_FitFine.invE_z0510
  have h3 := BAOCert.P2.T_FitFine.chi_z0706
  have h4 := BAOCert.P2.T_FitFine.invE_z0706
  have h5 := BAOCert.P2.T_FitFine.chi_z0934
  have h6 := BAOCert.P2.T_FitFine.invE_z0934
  have h7 := BAOCert.P2.T_FitFine.chi_z1321
  have h8 := BAOCert.P2.T_FitFine.invE_z1321
  have h9 := BAOCert.P2.T_FitFine.chi_z1484
  have h10 := BAOCert.P2.T_FitFine.invE_z1484
  have h11 := BAOCert.P2.T_FitFine.invE_z2330
  have h12 := BAOCert.P2.T_FitFine.chi_z2330
  have henv := env_ok envs (Data_Tamper.xsOf (((29743 : ℕ) : ℝ) / ((100000 : ℕ) : ℝ))) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  have hm := chi2_mem_at_K0 Data_Tamper.Pent Data_Tamper.dR (299792458 / 10154300) _ _ henv
  have hlo : (122697 / 1000 : ℚ) ≤ ((cEx Data_Tamper.Pent Data_Tamper.dR (299792458 / 10154300)).ieval (envOf envs)).lo := by decide +kernel
  have hhi : ((cEx Data_Tamper.Pent Data_Tamper.dR (299792458 / 10154300)).ieval (envOf envs)).hi ≤ (1227513 / 10000 : ℚ) := by decide +kernel
  have hlo' := (Rat.cast_le (K := ℝ)).2 hlo
  have hhi' := (Rat.cast_le (K := ℝ)).2 hhi
  exact ⟨hlo'.trans hm.1, hm.2.trans hhi'⟩

end BAOCert.P2.Fit_Tamper
