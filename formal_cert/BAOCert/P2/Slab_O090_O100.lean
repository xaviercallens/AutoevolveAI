import BAOCert.P2.T_O090
import BAOCert.P2.T_O100
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O090_O100
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(45486453812037 / 200000000000000 : ℚ), (46397743719357 / 200000000000000 : ℚ)⟩, ⟨(744615671485113 / 2000000000000000 : ℚ), (152223042395479 / 400000000000000 : ℚ)⟩, ⟨(538932754153 / 1000000000000 : ℚ), (139783608419 / 250000000000 : ℚ)⟩, ⟨(937264061313053 / 2000000000000000 : ℚ), (961583192213811 / 2000000000000000 : ℚ)⟩, ⟨(448777897669 / 1000000000000 : ℚ), (93569533081 / 200000000000 : ℚ)⟩, ⟨(1123402012381779 / 2000000000000000 : ℚ), (57803094904993 / 100000000000000 : ℚ)⟩, ⟨(371805059543 / 1000000000000 : ℚ), (12154415001 / 31250000000 : ℚ)⟩, ⟨(1374078593358857 / 2000000000000000 : ℚ), (177354467771487 / 250000000000000 : ℚ)⟩, ⟨(282805134003 / 1000000000000 : ℚ), (74196749921 / 250000000000 : ℚ)⟩, ⟨(730835572928649 / 1000000000000000 : ℚ), (1510825865684997 / 2000000000000000 : ℚ)⟩, ⟨(63857604303 / 250000000000 : ℚ), (33534579117 / 125000000000 : ℚ)⟩, ⟨(20570443857 / 125000000000 : ℚ), (173204821037 / 1000000000000 : ℚ)⟩, ⟨(90379792188983 / 100000000000000 : ℚ), (93733635230843 / 100000000000000 : ℚ)⟩]

/-- For every Om in [9/10, 1/1] and every real K, χ²_DESI DR2(Om, K) ≥ 865.67. -/
theorem chi2_slab : ∀ Om : ℝ, (((9 : ℕ) : ℝ) / ((10 : ℕ) : ℝ)) ≤ Om → Om ≤ (((1 : ℕ) : ℝ) / ((1 : ℕ) : ℝ)) → ∀ K : ℝ, ((86567 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((9 : ℕ) : ℝ) / ((10 : ℕ) : ℝ)) := by positivity
  have hb1 : (((1 : ℕ) : ℝ) / ((1 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(45486453812037 / 200000000000000 : ℚ), (46397743719357 / 200000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O090.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(744615671485113 / 2000000000000000 : ℚ), (152223042395479 / 400000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O090.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(538932754153 / 1000000000000 : ℚ), (139783608419 / 250000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O090.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(937264061313053 / 2000000000000000 : ℚ), (961583192213811 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O090.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(448777897669 / 1000000000000 : ℚ), (93569533081 / 200000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O090.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1123402012381779 / 2000000000000000 : ℚ), (57803094904993 / 100000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O090.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(371805059543 / 1000000000000 : ℚ), (12154415001 / 31250000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O090.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1374078593358857 / 2000000000000000 : ℚ), (177354467771487 / 250000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O090.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(282805134003 / 1000000000000 : ℚ), (74196749921 / 250000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O090.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(730835572928649 / 1000000000000000 : ℚ), (1510825865684997 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O090.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(63857604303 / 250000000000 : ℚ), (33534579117 / 125000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O090.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(20570443857 / 125000000000 : ℚ), (173204821037 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O090.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(90379792188983 / 100000000000000 : ℚ), (93733635230843 / 100000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O090.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (10558213959 / 263648993 : ℚ) _ _ henv (86567 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O090_O100
