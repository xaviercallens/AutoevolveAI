import BAOCert.P2.T_O015
import BAOCert.P2.T_O020
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O015_O020
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(275562056225953 / 1000000000000000 : ℚ), (280005523911213 / 1000000000000000 : ℚ)⟩, ⟨(465607395108167 / 1000000000000000 : ℚ), (950564529428031 / 2000000000000000 : ℚ)⟩, ⟨(819619763941 / 1000000000000 : ℚ), (855469037589 / 1000000000000 : ℚ)⟩, ⟨(1238112936188109 / 2000000000000000 : ℚ), (50939927802271 / 80000000000000 : ℚ)⟩, ⟨(373400523811 / 500000000000 : ℚ), (791862053427 / 1000000000000 : ℚ)⟩, ⟨(780093756490897 / 1000000000000000 : ℚ), (12942977871697 / 16000000000000 : ℚ)⟩, ⟨(166786436357 / 250000000000 : ℚ), (28754832021 / 40000000000 : ℚ)⟩, ⟨(2029729480318961 / 2000000000000000 : ℚ), (1064728489253163 / 1000000000000000 : ℚ)⟩, ⟨(137606618267 / 250000000000 : ℚ), (151431787577 / 250000000000 : ℚ)⟩, ⟨(275277531390249 / 250000000000000 : ℚ), (2319972930361303 / 2000000000000000 : ℚ)⟩, ⟨(254316025683 / 500000000000 : ℚ), (563522280313 / 1000000000000 : ℚ)⟩, ⟨(349530562503 / 1000000000000 : ℚ), (197813884087 / 500000000000 : ℚ)⟩, ⟨(583211477096331 / 400000000000000 : ℚ), (780060679312073 / 500000000000000 : ℚ)⟩]

/-- For every Om in [3/20, 1/5] and every real K, χ²_DESI DR2(Om, K) ≥ -116.5. -/
theorem chi2_slab : ∀ Om : ℝ, (((3 : ℕ) : ℝ) / ((20 : ℕ) : ℝ)) ≤ Om → Om ≤ (((1 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) → ∀ K : ℝ, ((-233 / 2 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((3 : ℕ) : ℝ) / ((20 : ℕ) : ℝ)) := by positivity
  have hb1 : (((1 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(275562056225953 / 1000000000000000 : ℚ), (280005523911213 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O015.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(465607395108167 / 1000000000000000 : ℚ), (950564529428031 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O015.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(819619763941 / 1000000000000 : ℚ), (855469037589 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O015.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1238112936188109 / 2000000000000000 : ℚ), (50939927802271 / 80000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O015.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(373400523811 / 500000000000 : ℚ), (791862053427 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O015.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(780093756490897 / 1000000000000000 : ℚ), (12942977871697 / 16000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O015.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(166786436357 / 250000000000 : ℚ), (28754832021 / 40000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O015.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(2029729480318961 / 2000000000000000 : ℚ), (1064728489253163 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O015.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(137606618267 / 250000000000 : ℚ), (151431787577 / 250000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O015.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(275277531390249 / 250000000000000 : ℚ), (2319972930361303 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O015.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(254316025683 / 500000000000 : ℚ), (563522280313 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O015.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(349530562503 / 1000000000000 : ℚ), (197813884087 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O015.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(583211477096331 / 400000000000000 : ℚ), (780060679312073 / 500000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O020.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O015.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (10967220865 / 416943934 : ℚ) _ _ henv (-233 / 2 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O015_O020
