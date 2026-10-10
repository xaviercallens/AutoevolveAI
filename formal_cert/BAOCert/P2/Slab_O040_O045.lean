import BAOCert.P2.T_O040
import BAOCert.P2.T_O045
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O040_O045
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(128363048793039 / 500000000000000 : ℚ), (260179715961631 / 1000000000000000 : ℚ)⟩, ⟨(854054951369329 / 2000000000000000 : ℚ), (867774591282777 / 2000000000000000 : ℚ)⟩, ⟨(172544001139 / 250000000000 : ℚ), (8889695079 / 12500000000 : ℚ)⟩, ⟨(221242435498267 / 400000000000000 : ℚ), (1128627182871007 / 2000000000000000 : ℚ)⟩, ⟨(14982308711 / 25000000000 : ℚ), (310920171349 / 500000000000 : ℚ)⟩, ⟨(169871476841663 / 250000000000000 : ℚ), (278354606975577 / 400000000000000 : ℚ)⟩, ⟨(512636399419 / 1000000000000 : ℚ), (267508250721 / 500000000000 : ℚ)⟩, ⟨(342090825960477 / 400000000000000 : ℚ), (1759908467535509 / 2000000000000000 : ℚ)⟩, ⟨(402373113813 / 1000000000000 : ℚ), (422526998099 / 1000000000000 : ℚ)⟩, ⟨(1835611750968131 / 2000000000000000 : ℚ), (378297285845337 / 400000000000000 : ℚ)⟩, ⟨(45805335211 / 125000000000 : ℚ), (192724863409 / 500000000000 : ℚ)⟩, ⟨(120677522321 / 500000000000 : ℚ), (255068721919 / 1000000000000 : ℚ)⟩, ⟨(18704233532533 / 16000000000000 : ℚ), (605368037879469 / 500000000000000 : ℚ)⟩]

/-- For every Om in [2/5, 9/20] and every real K, χ²_DESI DR2(Om, K) ≥ -4.95. -/
theorem chi2_slab : ∀ Om : ℝ, (((2 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) ≤ Om → Om ≤ (((9 : ℕ) : ℝ) / ((20 : ℕ) : ℝ)) → ∀ K : ℝ, ((-99 / 20 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((2 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) := by positivity
  have hb1 : (((9 : ℕ) : ℝ) / ((20 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(128363048793039 / 500000000000000 : ℚ), (260179715961631 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O040.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(854054951369329 / 2000000000000000 : ℚ), (867774591282777 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O040.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(172544001139 / 250000000000 : ℚ), (8889695079 / 12500000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O040.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(221242435498267 / 400000000000000 : ℚ), (1128627182871007 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O040.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(14982308711 / 25000000000 : ℚ), (310920171349 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O040.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(169871476841663 / 250000000000000 : ℚ), (278354606975577 / 400000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O040.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(512636399419 / 1000000000000 : ℚ), (267508250721 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O040.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(342090825960477 / 400000000000000 : ℚ), (1759908467535509 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O040.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(402373113813 / 1000000000000 : ℚ), (422526998099 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O040.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1835611750968131 / 2000000000000000 : ℚ), (378297285845337 / 400000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O040.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(45805335211 / 125000000000 : ℚ), (192724863409 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O040.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(120677522321 / 500000000000 : ℚ), (255068721919 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O040.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(18704233532533 / 16000000000000 : ℚ), (605368037879469 / 500000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O040.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (31961172042 / 993495305 : ℚ) _ _ henv (-99 / 20 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O040_O045
