import BAOCert.P2.T_O035
import BAOCert.P2.T_O036
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O035_O036
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(262961617335823 / 1000000000000000 : ℚ), (263739994219923 / 1000000000000000 : ℚ)⟩, ⟨(878855616729179 / 2000000000000000 : ℚ), (882057807553549 / 2000000000000000 : ℚ)⟩, ⟨(182357316393 / 250000000000 : ℚ), (734216597161 / 1000000000000 : ℚ)⟩, ⟨(573589641919891 / 1000000000000000 : ℚ), (576232069644879 / 1000000000000000 : ℚ)⟩, ⟨(641834063821 / 1000000000000 : ℚ), (323570626759 / 500000000000 : ℚ)⟩, ⟨(1419452591367357 / 2000000000000000 : ℚ), (1427283252274259 / 2000000000000000 : ℚ)⟩, ⟨(69399633373 / 125000000000 : ℚ), (560609373907 / 1000000000000 : ℚ)⟩, ⟨(180253624625829 / 200000000000000 : ℚ), (907272624187523 / 1000000000000000 : ℚ)⟩, ⟨(441029784851 / 1000000000000 : ℚ), (223024066617 / 500000000000 : ℚ)⟩, ⟨(1939952585416841 / 2000000000000000 : ℚ), (1953596020462847 / 2000000000000000 : ℚ)⟩, ⟨(402987058153 / 1000000000000 : ℚ), (203879287701 / 500000000000 : ℚ)⟩, ⟨(16743717217 / 62500000000 : ℚ), (54284303051 / 200000000000 : ℚ)⟩, ⟨(2495323077581431 / 2000000000000000 : ℚ), (2516079599069911 / 2000000000000000 : ℚ)⟩]

/-- For every Om in [7/20, 9/25] and every real K, χ²_DESI DR2(Om, K) ≥ 26.43. -/
theorem chi2_slab : ∀ Om : ℝ, (((7 : ℕ) : ℝ) / ((20 : ℕ) : ℝ)) ≤ Om → Om ≤ (((9 : ℕ) : ℝ) / ((25 : ℕ) : ℝ)) → ∀ K : ℝ, ((2643 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((7 : ℕ) : ℝ) / ((20 : ℕ) : ℝ)) := by positivity
  have hb1 : (((9 : ℕ) : ℝ) / ((25 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(262961617335823 / 1000000000000000 : ℚ), (263739994219923 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O035.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(878855616729179 / 2000000000000000 : ℚ), (882057807553549 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O035.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(182357316393 / 250000000000 : ℚ), (734216597161 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O035.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(573589641919891 / 1000000000000000 : ℚ), (576232069644879 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O035.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(641834063821 / 1000000000000 : ℚ), (323570626759 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O035.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1419452591367357 / 2000000000000000 : ℚ), (1427283252274259 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O035.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(69399633373 / 125000000000 : ℚ), (560609373907 / 1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O035.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(180253624625829 / 200000000000000 : ℚ), (907272624187523 / 1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O035.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(441029784851 / 1000000000000 : ℚ), (223024066617 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O035.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1939952585416841 / 2000000000000000 : ℚ), (1953596020462847 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O035.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(402987058153 / 1000000000000 : ℚ), (203879287701 / 500000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O035.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(16743717217 / 62500000000 : ℚ), (54284303051 / 200000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O035.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2495323077581431 / 2000000000000000 : ℚ), (2516079599069911 / 2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O036.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O035.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (2403823508 / 78092985 : ℚ) _ _ henv (2643 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O035_O036
