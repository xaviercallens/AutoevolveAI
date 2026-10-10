import BAOCert.P2.T_O060
import BAOCert.P2.T_O070
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O060_O070
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(120918013392873 / 500000000000000 : ℚ), (30936196577629 / 125000000000000 : ℚ)⟩, ⟨(159433916394453 / 400000000000000 : ℚ), (818500805655257 / 2000000000000000 : ℚ)⟩, ⟨(607449375913 / 1000000000000 : ℚ), (318415110609 / 500000000000 : ℚ)⟩, ⟨(1016285235443623 / 2000000000000000 : ℚ), (1311620818257 / 2500000000000 : ℚ)⟩, ⟨(514641207223 / 1000000000000 : ℚ), (8499983281 / 15625000000 : ℚ)⟩, ⟨(307790337417029 / 500000000000000 : ℚ), (638632407573691 / 1000000000000000 : ℚ)⟩, ⟨(215892725781 / 500000000000 : ℚ), (114825059149 / 250000000000 : ℚ)⟩, ⟨(762074067856279 / 1000000000000000 : ℚ), (1590056556172573 / 2000000000000000 : ℚ)⟩, ⟨(66473709447 / 200000000000 : ℚ), (44467394621 / 125000000000 : ℚ)⟩, ⟨(1627254398897437 / 2000000000000000 : ℚ), (1700537900368847 / 2000000000000000 : ℚ)⟩, ⟨(301116850669 / 1000000000000 : ℚ), (161406678587 / 500000000000 : ℚ)⟩, ⟨(195559485437 / 1000000000000 : ℚ), (210558410837 / 1000000000000 : ℚ)⟩, ⟨(2036885562538201 / 2000000000000000 : ℚ), (1070428665756343 / 1000000000000000 : ℚ)⟩]

/-- For every Om in [3/5, 7/10] and every real K, χ²_DESI DR2(Om, K) ≥ 197.59. -/
theorem chi2_slab : ∀ Om : ℝ, (((3 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) ≤ Om → Om ≤ (((7 : ℕ) : ℝ) / ((10 : ℕ) : ℝ)) → ∀ K : ℝ, ((19759 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((3 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) := by positivity
  have hb1 : (((7 : ℕ) : ℝ) / ((10 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(120918013392873 / 500000000000000 : ℚ), (30936196577629 / 125000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O060.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(159433916394453 / 400000000000000 : ℚ), (818500805655257 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O060.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(607449375913 / 1000000000000 : ℚ), (318415110609 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O060.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1016285235443623 / 2000000000000000 : ℚ), (1311620818257 / 2500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O060.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(514641207223 / 1000000000000 : ℚ), (8499983281 / 15625000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O060.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(307790337417029 / 500000000000000 : ℚ), (638632407573691 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O060.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(215892725781 / 500000000000 : ℚ), (114825059149 / 250000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O060.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(762074067856279 / 1000000000000000 : ℚ), (1590056556172573 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O060.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(66473709447 / 200000000000 : ℚ), (44467394621 / 125000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O060.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1627254398897437 / 2000000000000000 : ℚ), (1700537900368847 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O060.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(301116850669 / 1000000000000 : ℚ), (161406678587 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O060.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(195559485437 / 1000000000000 : ℚ), (210558410837 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O060.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2036885562538201 / 2000000000000000 : ℚ), (1070428665756343 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O070.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O060.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (22593812058 / 628415215 : ℚ) _ _ henv (19759 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O060_O070
