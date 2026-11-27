import BAOCert.P2.T_O020
import BAOCert.P2.T_O022
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O020_O022
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(273864920181525 : ℚ) / (1000000000000000 : ℚ), (275594749745831 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(923964102432585 : ℚ) / (2000000000000000 : ℚ), (931395170453413 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(806491156906 : ℚ) / (1000000000000 : ℚ), (819619763942 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1225110238206873 : ℚ) / (2000000000000000 : ℚ), (1238366135141899 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(730814374509 : ℚ) / (1000000000000 : ℚ), (746801047623 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1539430761469886 : ℚ) / (2000000000000000 : ℚ), (1560520367238234 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(649371641337 : ℚ) / (1000000000000 : ℚ), (667145745429 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1994879407652596 : ℚ) / (2000000000000000 : ℚ), (2030179053848535 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(532191204004 : ℚ) / (1000000000000 : ℚ), (550426473069 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2161480077594460 : ℚ) / (2000000000000000 : ℚ), (2202711619073594 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(490767091350 : ℚ) / (1000000000000 : ℚ), (508632051367 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(335130577144 : ℚ) / (1000000000000 : ℚ), (349530562504 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2847875706500913 : ℚ) / (2000000000000000 : ℚ), (2916707854923812 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [20/100, 22/100] and every real K, χ²_DESI DR2(Om, K) ≥ 63.74. -/
theorem chi2_slab : ∀ Om : ℝ, (((20 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((22 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((3187 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((20 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((22 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(273864920181525 : ℚ) / (1000000000000000 : ℚ), (275594749745831 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O020.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(923964102432585 : ℚ) / (2000000000000000 : ℚ), (931395170453413 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O020.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(806491156906 : ℚ) / (1000000000000 : ℚ), (819619763942 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O020.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1225110238206873 : ℚ) / (2000000000000000 : ℚ), (1238366135141899 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O020.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(730814374509 : ℚ) / (1000000000000 : ℚ), (746801047623 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O020.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1539430761469886 : ℚ) / (2000000000000000 : ℚ), (1560520367238234 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O020.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(649371641337 : ℚ) / (1000000000000 : ℚ), (667145745429 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O020.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1994879407652596 : ℚ) / (2000000000000000 : ℚ), (2030179053848535 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O020.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(532191204004 : ℚ) / (1000000000000 : ℚ), (550426473069 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O020.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2161480077594460 : ℚ) / (2000000000000000 : ℚ), (2202711619073594 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O020.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(490767091350 : ℚ) / (1000000000000 : ℚ), (508632051367 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O020.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(335130577144 : ℚ) / (1000000000000 : ℚ), (349530562504 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O020.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2847875706500913 : ℚ) / (2000000000000000 : ℚ), (2916707854923812 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O022.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O020.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (7073444519 / 258854787 : ℚ) _ _ henv (3187 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O020_O022
