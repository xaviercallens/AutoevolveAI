import BAOCert.P2.T_O100
import BAOCert.P2.Data

namespace BAOCert.P2.EdS
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(227432269060185 : ℚ) / (1000000000000000 : ℚ), (227532776534225 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(744615671485113 : ℚ) / (2000000000000000 : ℚ), (745076738731980 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(538932754153 : ℚ) / (1000000000000 : ℚ), (538932754154 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(937264061313053 : ℚ) / (2000000000000000 : ℚ), (937815283416796 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(448777897669 : ℚ) / (1000000000000 : ℚ), (448777897670 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1123402012381779 : ℚ) / (2000000000000000 : ℚ), (1124030207324104 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(371805059543 : ℚ) / (1000000000000 : ℚ), (371805059544 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1374078593358857 : ℚ) / (2000000000000000 : ℚ), (1374795788227496 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(282805134003 : ℚ) / (1000000000000 : ℚ), (282805134004 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1461671145857298 : ℚ) / (2000000000000000 : ℚ), (1462415715443054 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(255430417212 : ℚ) / (1000000000000 : ℚ), (255430417213 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(164563550856 : ℚ) / (1000000000000 : ℚ), (164563550857 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1807595843779660 : ℚ) / (2000000000000000 : ℚ), (1808431280233464 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [1/1, 1/1] and every real K, χ²_DESI DR2(Om, K) ≥ 1415.82. -/
theorem chi2_slab : ∀ Om : ℝ, (((1 : ℕ) : ℝ) / ((1 : ℕ) : ℝ)) ≤ Om → Om ≤ (((1 : ℕ) : ℝ) / ((1 : ℕ) : ℝ)) → ∀ K : ℝ, ((70791 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((1 : ℕ) : ℝ) / ((1 : ℕ) : ℝ)) := by positivity
  have hb1 : (((1 : ℕ) : ℝ) / ((1 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(227432269060185 : ℚ) / (1000000000000000 : ℚ), (227532776534225 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O100.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(744615671485113 : ℚ) / (2000000000000000 : ℚ), (745076738731980 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O100.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(538932754153 : ℚ) / (1000000000000 : ℚ), (538932754154 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O100.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(937264061313053 : ℚ) / (2000000000000000 : ℚ), (937815283416796 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O100.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(448777897669 : ℚ) / (1000000000000 : ℚ), (448777897670 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O100.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1123402012381779 : ℚ) / (2000000000000000 : ℚ), (1124030207324104 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O100.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(371805059543 : ℚ) / (1000000000000 : ℚ), (371805059544 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O100.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1374078593358857 : ℚ) / (2000000000000000 : ℚ), (1374795788227496 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O100.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(282805134003 : ℚ) / (1000000000000 : ℚ), (282805134004 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O100.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1461671145857298 : ℚ) / (2000000000000000 : ℚ), (1462415715443054 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O100.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(255430417212 : ℚ) / (1000000000000 : ℚ), (255430417213 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O100.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(164563550856 : ℚ) / (1000000000000 : ℚ), (164563550857 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O100.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(1807595843779660 : ℚ) / (2000000000000000 : ℚ), (1808431280233464 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O100.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O100.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (27204731265 / 669084328 : ℚ) _ _ henv (70791 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.EdS
