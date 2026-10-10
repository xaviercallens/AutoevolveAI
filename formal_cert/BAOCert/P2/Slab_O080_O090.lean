import BAOCert.P2.T_O080
import BAOCert.P2.T_O090
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O080_O090
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(28986722944399 / 125000000000000 : ℚ), (118384506516013 / 500000000000000 : ℚ)⟩, ⟨(15213486928201 / 40000000000000 : ℚ), (778532538530097 / 2000000000000000 : ℚ)⟩, ⟨(22365377347 / 40000000000 : ℚ), (29089632737 / 50000000000 : ℚ)⟩, ⟨(961051039877803 / 2000000000000000 : ℚ), (493871423062781 / 1000000000000000 : ℚ)⟩, ⟨(116961916351 / 250000000000 : ℚ), (48957514769 / 100000000000 : ℚ)⟩, ⟨(1155450839378023 / 2000000000000000 : ℚ), (119169394773473 / 200000000000000 : ℚ)⟩, ⟨(388941280031 / 1000000000000 : ℚ), (408688589783 / 1000000000000 : ℚ)⟩, ⟨(1418132529168937 / 2000000000000000 : ℚ), (5873542851321 / 8000000000000 : ℚ)⟩, ⟨(296786999683 / 1000000000000 : ℚ), (62614272201 / 200000000000 : ℚ)⟩, ⟨(377523535578741 / 500000000000000 : ℚ), (782736398367621 / 1000000000000000 : ℚ)⟩, ⟨(53655326587 / 200000000000 : ℚ), (283278927089 / 1000000000000 : ℚ)⟩, ⟨(43301205259 / 250000000000 : ℚ), (11460497691 / 62500000000 : ℚ)⟩, ⟨(468461477358309 / 500000000000000 : ℚ), (39004533252531 / 40000000000000 : ℚ)⟩]

/-- For every Om in [4/5, 9/10] and every real K, χ²_DESI DR2(Om, K) ≥ 647.47. -/
theorem chi2_slab : ∀ Om : ℝ, (((4 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) ≤ Om → Om ≤ (((9 : ℕ) : ℝ) / ((10 : ℕ) : ℝ)) → ∀ K : ℝ, ((64747 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((4 : ℕ) : ℝ) / ((5 : ℕ) : ℝ)) := by positivity
  have hb1 : (((9 : ℕ) : ℝ) / ((10 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(28986722944399 / 125000000000000 : ℚ), (118384506516013 / 500000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O080.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(15213486928201 / 40000000000000 : ℚ), (778532538530097 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O080.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(22365377347 / 40000000000 : ℚ), (29089632737 / 50000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O080.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(961051039877803 / 2000000000000000 : ℚ), (493871423062781 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O080.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(116961916351 / 250000000000 : ℚ), (48957514769 / 100000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O080.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1155450839378023 / 2000000000000000 : ℚ), (119169394773473 / 200000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O080.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(388941280031 / 1000000000000 : ℚ), (408688589783 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O080.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1418132529168937 / 2000000000000000 : ℚ), (5873542851321 / 8000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O080.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(296786999683 / 1000000000000 : ℚ), (62614272201 / 200000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O080.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(377523535578741 / 500000000000000 : ℚ), (782736398367621 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O080.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(53655326587 / 200000000000 : ℚ), (283278927089 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O080.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(43301205259 / 250000000000 : ℚ), (11460497691 / 62500000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O080.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(468461477358309 / 500000000000000 : ℚ), (39004533252531 / 40000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O080.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (1679437910 / 43319929 : ℚ) _ _ henv (64747 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O080_O090
