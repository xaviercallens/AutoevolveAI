import BAOCert.P2.T_O015
import BAOCert.P2.T_R7_40
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_O015_R7_40
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(277738770214927 : ℚ) / (1000000000000000 : ℚ), (280005523911213 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(940615670346745 : ℚ) / (2000000000000000 : ℚ), (950564529428031 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(836969135513 : ℚ) / (1000000000000 : ℚ), (855469037589 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1255193637283159 : ℚ) / (2000000000000000 : ℚ), (1273498195056775 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(768342309084 : ℚ) / (1000000000000 : ℚ), (791862053427 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1587823118574502 : ℚ) / (2000000000000000 : ℚ), (1617872233962125 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(691561693882 : ℚ) / (1000000000000 : ℚ), (718870800525 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2076980494854265 : ℚ) / (2000000000000000 : ℚ), (2129456978506326 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(576095614652 : ℚ) / (1000000000000 : ℚ), (605727150308 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2257795233009073 : ℚ) / (2000000000000000 : ℚ), (2319972930361303 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(533972753262 : ℚ) / (1000000000000 : ℚ), (563522280313 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(370445166303 : ℚ) / (1000000000000 : ℚ), (395627768174 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(3011074501919054 : ℚ) / (2000000000000000 : ℚ), (3120242717248292 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [15/100, 7/40] and every real K, χ²_DESI DR2(Om, K) ≥ 224.52. -/
theorem chi2_slab : ∀ Om : ℝ, (((15 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((7 : ℕ) : ℝ) / ((40 : ℕ) : ℝ)) → ∀ K : ℝ, ((5613 / 25 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((15 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((7 : ℕ) : ℝ) / ((40 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(277738770214927 : ℚ) / (1000000000000000 : ℚ), (280005523911213 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O015.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(940615670346745 : ℚ) / (2000000000000000 : ℚ), (950564529428031 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O015.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(836969135513 : ℚ) / (1000000000000 : ℚ), (855469037589 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O015.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1255193637283159 : ℚ) / (2000000000000000 : ℚ), (1273498195056775 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O015.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(768342309084 : ℚ) / (1000000000000 : ℚ), (791862053427 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O015.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1587823118574502 : ℚ) / (2000000000000000 : ℚ), (1617872233962125 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O015.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(691561693882 : ℚ) / (1000000000000 : ℚ), (718870800525 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O015.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(2076980494854265 : ℚ) / (2000000000000000 : ℚ), (2129456978506326 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O015.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(576095614652 : ℚ) / (1000000000000 : ℚ), (605727150308 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O015.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2257795233009073 : ℚ) / (2000000000000000 : ℚ), (2319972930361303 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O015.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(533972753262 : ℚ) / (1000000000000 : ℚ), (563522280313 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O015.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(370445166303 : ℚ) / (1000000000000 : ℚ), (395627768174 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O015.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(3011074501919054 : ℚ) / (2000000000000000 : ℚ), (3120242717248292 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R7_40.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O015.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (24721460201 / 954082024 : ℚ) _ _ henv (5613 / 25 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_O015_R7_40
