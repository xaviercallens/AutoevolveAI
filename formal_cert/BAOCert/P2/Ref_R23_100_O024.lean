import BAOCert.P2.T_O024
import BAOCert.P2.T_R23_100
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_R23_100_O024
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(272205410017168 : ℚ) / (1000000000000000 : ℚ), (273067266660400 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(916938204319568 : ℚ) / (2000000000000000 : ℚ), (920623720700093 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(793973870117 : ℚ) / (1000000000000 : ℚ), (800159092565 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1212646079528235 : ℚ) / (2000000000000000 : ℚ), (1219090284571492 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(715812293317 : ℚ) / (1000000000000 : ℚ), (723196658171 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1519748832275496 : ℚ) / (2000000000000000 : ℚ), (1529821016587275 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(632946427917 : ℚ) / (1000000000000 : ℚ), (641001256797 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1962305644541774 : ℚ) / (2000000000000000 : ℚ), (1978801732878264 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(515655952875 : ℚ) / (1000000000000 : ℚ), (523727909525 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2123581270084902 : ℚ) / (2000000000000000 : ℚ), (2142716226015448 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(474661332194 : ℚ) / (1000000000000 : ℚ), (482512731241 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(322375261267 : ℚ) / (1000000000000 : ℚ), (328567374418 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2785480092916175 : ℚ) / (2000000000000000 : ℚ), (2816683033090159 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [23/100, 24/100] and every real K, χ²_DESI DR2(Om, K) ≥ 48.61. -/
theorem chi2_slab : ∀ Om : ℝ, (((23 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((24 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((4861 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((23 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((24 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(272205410017168 : ℚ) / (1000000000000000 : ℚ), (273067266660400 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_R23_100.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(916938204319568 : ℚ) / (2000000000000000 : ℚ), (920623720700093 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_R23_100.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(793973870117 : ℚ) / (1000000000000 : ℚ), (800159092565 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_R23_100.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1212646079528235 : ℚ) / (2000000000000000 : ℚ), (1219090284571492 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_R23_100.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(715812293317 : ℚ) / (1000000000000 : ℚ), (723196658171 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_R23_100.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1519748832275496 : ℚ) / (2000000000000000 : ℚ), (1529821016587275 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_R23_100.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(632946427917 : ℚ) / (1000000000000 : ℚ), (641001256797 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_R23_100.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1962305644541774 : ℚ) / (2000000000000000 : ℚ), (1978801732878264 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_R23_100.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(515655952875 : ℚ) / (1000000000000 : ℚ), (523727909525 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_R23_100.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2123581270084902 : ℚ) / (2000000000000000 : ℚ), (2142716226015448 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_R23_100.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(474661332194 : ℚ) / (1000000000000 : ℚ), (482512731241 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_R23_100.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(322375261267 : ℚ) / (1000000000000 : ℚ), (328567374418 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_R23_100.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2785480092916175 : ℚ) / (2000000000000000 : ℚ), (2816683033090159 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O024.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_R23_100.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (26729102808 / 954646067 : ℚ) _ _ henv (4861 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_R23_100_O024
