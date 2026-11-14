import BAOCert.P2.T_O070
import BAOCert.P2.T_O080
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O070_O080
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(236680208713263 : ℚ) / (1000000000000000 : ℚ), (241918046649606 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(778114331183816 : ℚ) / (2000000000000000 : ℚ), (797562132597372 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(581792654739 : ℚ) / (1000000000000 : ℚ), (607449375914 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(987232421271839 : ℚ) / (2000000000000000 : ℚ), (1016770594237812 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(489575147689 : ℚ) / (1000000000000 : ℚ), (514641207224 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1191102636322644 : ℚ) / (2000000000000000 : ℚ), (1231729564218422 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(408688589782 : ℚ) / (1000000000000 : ℚ), (431785451563 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1467698784188612 : ℚ) / (2000000000000000 : ℚ), (1524815767167965 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(313071361004 : ℚ) / (1000000000000 : ℚ), (332368547236 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1564756075659362 : ℚ) / (2000000000000000 : ℚ), (1627953282049736 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(283278927088 : ℚ) / (1000000000000 : ℚ), (301116850670 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(183367963055 : ℚ) / (1000000000000 : ℚ), (195559485438 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1949410030584945 : ℚ) / (2000000000000000 : ℚ), (2037690003057424 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [70/100, 80/100] and every real K, χ²_DESI DR2(Om, K) ≥ 423.02. -/
theorem chi2_slab : ∀ Om : ℝ, (((70 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((80 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((21151 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((70 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((80 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(236680208713263 : ℚ) / (1000000000000000 : ℚ), (241918046649606 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O070.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(778114331183816 : ℚ) / (2000000000000000 : ℚ), (797562132597372 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O070.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(581792654739 : ℚ) / (1000000000000 : ℚ), (607449375914 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O070.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(987232421271839 : ℚ) / (2000000000000000 : ℚ), (1016770594237812 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O070.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(489575147689 : ℚ) / (1000000000000 : ℚ), (514641207224 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O070.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1191102636322644 : ℚ) / (2000000000000000 : ℚ), (1231729564218422 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O070.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(408688589782 : ℚ) / (1000000000000 : ℚ), (431785451563 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O070.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1467698784188612 : ℚ) / (2000000000000000 : ℚ), (1524815767167965 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O070.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(313071361004 : ℚ) / (1000000000000 : ℚ), (332368547236 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O070.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1564756075659362 : ℚ) / (2000000000000000 : ℚ), (1627953282049736 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O070.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(283278927088 : ℚ) / (1000000000000 : ℚ), (301116850670 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O070.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(183367963055 : ℚ) / (1000000000000 : ℚ), (195559485438 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O070.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(1949410030584945 : ℚ) / (2000000000000000 : ℚ), (2037690003057424 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O080.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O070.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (37267848234 / 996205775 : ℚ) _ _ henv (21151 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O070_O080
