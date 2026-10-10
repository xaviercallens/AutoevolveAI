import BAOCert.P2.T_O010
import BAOCert.P2.T_O015
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O010_O015
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(139989985615821 / 500000000000000 : ℚ), (35585995010457 / 125000000000000 : ℚ)⟩, ⟨(950419998464599 / 2000000000000000 : ℚ), (60717722389109 / 125000000000000 : ℚ)⟩, ⟨(213867259397 / 250000000000 : ℚ), (224118812783 / 250000000000 : ℚ)⟩, ⟨(1273290057108789 / 2000000000000000 : ℚ), (1313190300945877 / 2000000000000000 : ℚ)⟩, ⟨(395931026713 / 500000000000 : ℚ), (10577581343 / 12500000000 : ℚ)⟩, ⟨(1617591104760781 / 2000000000000000 : ℚ), (842580337887413 / 1000000000000000 : ℚ)⟩, ⟨(179717700131 / 250000000000 : ℚ), (156970937211 / 200000000000 : ℚ)⟩, ⟨(2129062705653991 / 2000000000000000 : ℚ), (563119933272473 / 500000000000000 : ℚ)⟩, ⟨(605727150307 / 1000000000000 : ℚ), (136388330999 / 200000000000 : ℚ)⟩, ⟨(2319536452638647 / 2000000000000000 : ℚ), (2468108610575883 / 2000000000000000 : ℚ)⟩, ⟨(70440285039 / 125000000000 : ℚ), (12822906299 / 20000000000 : ℚ)⟩, ⟨(395627768173 / 1000000000000 : ℚ), (466627698349 / 1000000000000 : ℚ)⟩, ⟨(623927669002361 / 400000000000000 : ℚ), (26533634828903 / 15625000000000 : ℚ)⟩]

/-- For every Om in [1/10, 3/20] and every real K, χ²_DESI DR2(Om, K) ≥ 21.57. -/
theorem chi2_slab : ∀ Om : ℝ, (((1 : ℕ) : ℝ) / ((10 : ℕ) : ℝ)) ≤ Om → Om ≤ (((3 : ℕ) : ℝ) / ((20 : ℕ) : ℝ)) → ∀ K : ℝ, ((2157 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((1 : ℕ) : ℝ) / ((10 : ℕ) : ℝ)) := by positivity
  have hb1 : (((3 : ℕ) : ℝ) / ((20 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(139989985615821 / 500000000000000 : ℚ), (35585995010457 / 125000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O010.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(950419998464599 / 2000000000000000 : ℚ), (60717722389109 / 125000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O010.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(213867259397 / 250000000000 : ℚ), (224118812783 / 250000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O010.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1273290057108789 / 2000000000000000 : ℚ), (1313190300945877 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O010.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(395931026713 / 500000000000 : ℚ), (10577581343 / 12500000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O010.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1617591104760781 / 2000000000000000 : ℚ), (842580337887413 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O010.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(179717700131 / 250000000000 : ℚ), (156970937211 / 200000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O010.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(2129062705653991 / 2000000000000000 : ℚ), (563119933272473 / 500000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O010.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(605727150307 / 1000000000000 : ℚ), (136388330999 / 200000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O010.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2319536452638647 / 2000000000000000 : ℚ), (2468108610575883 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O010.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(70440285039 / 125000000000 : ℚ), (12822906299 / 20000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O010.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(395627768173 / 1000000000000 : ℚ), (466627698349 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O010.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(623927669002361 / 400000000000000 : ℚ), (26533634828903 / 15625000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O010.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (7214557496 / 293049207 : ℚ) _ _ henv (2157 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O010_O015
