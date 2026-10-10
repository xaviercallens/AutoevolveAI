import BAOCert.P2.T_FitFine
import BAOCert.P2.Data

namespace BAOCert.P2.Fit
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(1672854005331 / 6250000000000 : ℚ), (16728821891881 / 62500000000000 : ℚ)⟩, ⟨(1122511718015549 / 2500000000000000 : ℚ), (561270794470793 / 1250000000000000 : ℚ)⟩, ⟨(47564537619 / 62500000000 : ℚ), (152206520381 / 200000000000 : ℚ)⟩, ⟨(11796466787192679 / 20000000000000000 : ℚ), (11796789403948199 / 20000000000000000 : ℚ)⟩, ⟨(3386916293 / 5000000000 : ℚ), (677383258601 / 1000000000000 : ℚ)⟩, ⟨(3671359680044939 / 5000000000000000 : ℚ), (14685846800417121 / 20000000000000000 : ℚ)⟩, ⟨(118383956263 / 200000000000 : ℚ), (147979945329 / 250000000000 : ℚ)⟩, ⟨(187946814148023 / 200000000000000 : ℚ), (18795205840426801 / 20000000000000000 : ℚ)⟩, ⟨(475574401919 / 1000000000000 : ℚ), (743085003 / 1562500000 : ℚ)⟩, ⟨(20279130785876203 / 20000000000000000 : ℚ), (20279694817175477 / 20000000000000000 : ℚ)⟩, ⟨(217984365203 / 500000000000 : ℚ), (435968730407 / 1000000000000 : ℚ)⟩, ⟨(73133558969 / 250000000000 : ℚ), (292534235877 / 1000000000000 : ℚ)⟩, ⟨(1644933498989059 / 1250000000000000 : ℚ), (6579910862408917 / 5000000000000000 : ℚ)⟩]

/-- χ² of DESI DR2 at Om = 0.29743, h r_d = 101.543 Mpc (K = 299792458/10154300) lies in [10.2525, 10.2897]. -/
theorem chi2_fit : ((4101 / 400 : ℚ) : ℝ) ≤ Data.chi2DESI (((29743 : ℕ) : ℝ) / ((100000 : ℕ) : ℝ)) (((299792458 / 10154300 : ℚ)) : ℝ) ∧
    Data.chi2DESI (((29743 : ℕ) : ℝ) / ((100000 : ℕ) : ℝ)) (((299792458 / 10154300 : ℚ)) : ℝ) ≤ ((102897 / 10000 : ℚ) : ℝ) := by
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
  have henv := env_ok envs (Data.xsOf (((29743 : ℕ) : ℝ) / ((100000 : ℕ) : ℝ))) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  have hm := chi2_mem_at_K0 Data.Pent Data.dR (299792458 / 10154300) _ _ henv
  have hlo : (4101 / 400 : ℚ) ≤ ((cEx Data.Pent Data.dR (299792458 / 10154300)).ieval (envOf envs)).lo := by decide +kernel
  have hhi : ((cEx Data.Pent Data.dR (299792458 / 10154300)).ieval (envOf envs)).hi ≤ (102897 / 10000 : ℚ) := by decide +kernel
  have hlo' := (Rat.cast_le (K := ℝ)).2 hlo
  have hhi' := (Rat.cast_le (K := ℝ)).2 hhi
  exact ⟨by push_cast at hlo' ⊢; exact hlo'.trans hm.1, by push_cast at hhi' ⊢; exact hm.2.trans hhi'⟩

end BAOCert.P2.Fit
