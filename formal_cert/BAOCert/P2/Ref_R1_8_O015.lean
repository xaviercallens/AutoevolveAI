import BAOCert.P2.T_O015
import BAOCert.P2.T_R1_8
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_R1_8_O015
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(279979971231642 : ℚ) / (1000000000000000 : ℚ), (282310926014985 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(950419998464599 : ℚ) / (2000000000000000 : ℚ), (960786649341580 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(855469037588 : ℚ) / (1000000000000 : ℚ), (875252527125 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1273290057108789 : ℚ) / (2000000000000000 : ℚ), (1292705387341177 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(791862053426 : ℚ) / (1000000000000 : ℚ), (817682951846 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1617591104760781 : ℚ) / (2000000000000000 : ℚ), (1650075832799465 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(718870800524 : ℚ) / (1000000000000 : ℚ), (749693635470 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2129062705653991 : ℚ) / (2000000000000000 : ℚ), (2187356022370492 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(605727150307 : ℚ) / (1000000000000 : ℚ), (640458061011 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2319536452638647 : ℚ) / (2000000000000000 : ℚ), (2389265741307996 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(563522280312 : ℚ) / (1000000000000 : ℚ), (598591609770 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(395627768173 : ℚ) / (1000000000000 : ℚ), (426760270733 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(3119638345011805 : ℚ) / (2000000000000000 : ℚ), (3246386330044252 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [1/8, 15/100] and every real K, χ²_DESI DR2(Om, K) ≥ 414.89. -/
theorem chi2_slab : ∀ Om : ℝ, (((1 : ℕ) : ℝ) / ((8 : ℕ) : ℝ)) ≤ Om → Om ≤ (((15 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((41489 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((1 : ℕ) : ℝ) / ((8 : ℕ) : ℝ)) := by positivity
  have hb1 : (((15 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(279979971231642 : ℚ) / (1000000000000000 : ℚ), (282310926014985 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_R1_8.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(950419998464599 : ℚ) / (2000000000000000 : ℚ), (960786649341580 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_R1_8.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(855469037588 : ℚ) / (1000000000000 : ℚ), (875252527125 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_R1_8.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1273290057108789 : ℚ) / (2000000000000000 : ℚ), (1292705387341177 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_R1_8.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(791862053426 : ℚ) / (1000000000000 : ℚ), (817682951846 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_R1_8.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1617591104760781 : ℚ) / (2000000000000000 : ℚ), (1650075832799465 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_R1_8.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(718870800524 : ℚ) / (1000000000000 : ℚ), (749693635470 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_R1_8.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(2129062705653991 : ℚ) / (2000000000000000 : ℚ), (2187356022370492 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_R1_8.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(605727150307 : ℚ) / (1000000000000 : ℚ), (640458061011 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_R1_8.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2319536452638647 : ℚ) / (2000000000000000 : ℚ), (2389265741307996 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_R1_8.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(563522280312 : ℚ) / (1000000000000 : ℚ), (598591609770 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_R1_8.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(395627768173 : ℚ) / (1000000000000 : ℚ), (426760270733 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_R1_8.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(3119638345011805 : ℚ) / (2000000000000000 : ℚ), (3246386330044252 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O015.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_R1_8.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (14441286225 / 576004246 : ℚ) _ _ henv (41489 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_R1_8_O015
