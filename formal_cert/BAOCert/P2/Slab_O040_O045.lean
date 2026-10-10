import BAOCert.P2.T_O040
import BAOCert.P2.T_O045
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O040_O045
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(256726097586078 : ℚ) / (1000000000000000 : ℚ), (260179715961631 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(854054951369329 : ℚ) / (2000000000000000 : ℚ), (867774591282777 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(690176004556 : ℚ) / (1000000000000 : ℚ), (711175606320 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1106212177491335 : ℚ) / (2000000000000000 : ℚ), (1128627182871007 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(599292348440 : ℚ) / (1000000000000 : ℚ), (621840342698 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1358971814733304 : ℚ) / (2000000000000000 : ℚ), (1391773034877885 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(512636399419 : ℚ) / (1000000000000 : ℚ), (535016501442 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1710454129802385 : ℚ) / (2000000000000000 : ℚ), (1759908467535509 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(402373113813 : ℚ) / (1000000000000 : ℚ), (422526998099 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1835611750968131 : ℚ) / (2000000000000000 : ℚ), (1891486429226685 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(366442681688 : ℚ) / (1000000000000 : ℚ), (385449726818 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(241355044642 : ℚ) / (1000000000000 : ℚ), (255068721919 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2338029191566625 : ℚ) / (2000000000000000 : ℚ), (2421472151517876 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [40/100, 45/100] and every real K, χ²_DESI DR2(Om, K) ≥ -4.95. -/
theorem chi2_slab : ∀ Om : ℝ, (((40 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((45 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((-99 / 20 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((40 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((45 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(256726097586078 : ℚ) / (1000000000000000 : ℚ), (260179715961631 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O040.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(854054951369329 : ℚ) / (2000000000000000 : ℚ), (867774591282777 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O040.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(690176004556 : ℚ) / (1000000000000 : ℚ), (711175606320 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O040.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1106212177491335 : ℚ) / (2000000000000000 : ℚ), (1128627182871007 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O040.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(599292348440 : ℚ) / (1000000000000 : ℚ), (621840342698 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O040.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1358971814733304 : ℚ) / (2000000000000000 : ℚ), (1391773034877885 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O040.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(512636399419 : ℚ) / (1000000000000 : ℚ), (535016501442 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O040.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1710454129802385 : ℚ) / (2000000000000000 : ℚ), (1759908467535509 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O040.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(402373113813 : ℚ) / (1000000000000 : ℚ), (422526998099 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O040.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1835611750968131 : ℚ) / (2000000000000000 : ℚ), (1891486429226685 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O040.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(366442681688 : ℚ) / (1000000000000 : ℚ), (385449726818 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O040.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(241355044642 : ℚ) / (1000000000000 : ℚ), (255068721919 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O040.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2338029191566625 : ℚ) / (2000000000000000 : ℚ), (2421472151517876 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O045.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O040.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (31961172042 / 993495305 : ℚ) _ _ henv (-99 / 20 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O040_O045
