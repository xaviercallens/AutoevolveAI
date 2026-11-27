import BAOCert.P2.T_O029
import BAOCert.P2.T_O030
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O029_O030
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(267438343018685 : ℚ) / (1000000000000000 : ℚ), (268256015237569 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(897086597045568 : ℚ) / (2000000000000000 : ℚ), (900510538668234 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(759652709466 : ℚ) / (1000000000000 : ℚ), (765064635505 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1178101451076983 : ℚ) / (2000000000000000 : ℚ), (1183904842073156 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(675805094253 : ℚ) / (1000000000000 : ℚ), (682008755918 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1466218154407356 : ℚ) / (2000000000000000 : ℚ), (1475026836560546 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(590265443243 : ℚ) / (1000000000000 : ℚ), (596781941008 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1875827053066080 : ℚ) / (2000000000000000 : ℚ), (1889733698912103 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(473992387043 : ℚ) / (1000000000000 : ℚ), (480238744362 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2023748688398082 : ℚ) / (2000000000000000 : ℚ), (2039691650827091 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(434451157277 : ℚ) / (1000000000000 : ℚ), (440447200222 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(291385346507 : ℚ) / (1000000000000 : ℚ), (295933756612 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2625413994688255 : ℚ) / (2000000000000000 : ℚ), (2650403989822663 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [29/100, 30/100] and every real K, χ²_DESI DR2(Om, K) ≥ 0.33. -/
theorem chi2_slab : ∀ Om : ℝ, (((29 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((30 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((33 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((29 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((30 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(267438343018685 : ℚ) / (1000000000000000 : ℚ), (268256015237569 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O029.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(897086597045568 : ℚ) / (2000000000000000 : ℚ), (900510538668234 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O029.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(759652709466 : ℚ) / (1000000000000 : ℚ), (765064635505 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O029.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1178101451076983 : ℚ) / (2000000000000000 : ℚ), (1183904842073156 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O029.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(675805094253 : ℚ) / (1000000000000 : ℚ), (682008755918 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O029.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1466218154407356 : ℚ) / (2000000000000000 : ℚ), (1475026836560546 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O029.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(590265443243 : ℚ) / (1000000000000 : ℚ), (596781941008 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O029.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1875827053066080 : ℚ) / (2000000000000000 : ℚ), (1889733698912103 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O029.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(473992387043 : ℚ) / (1000000000000 : ℚ), (480238744362 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O029.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2023748688398082 : ℚ) / (2000000000000000 : ℚ), (2039691650827091 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O029.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(434451157277 : ℚ) / (1000000000000 : ℚ), (440447200222 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O029.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(291385346507 : ℚ) / (1000000000000 : ℚ), (295933756612 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O029.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2625413994688255 : ℚ) / (2000000000000000 : ℚ), (2650403989822663 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O030.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O029.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (25825047772 / 876375247 : ℚ) _ _ henv (33 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O029_O030
