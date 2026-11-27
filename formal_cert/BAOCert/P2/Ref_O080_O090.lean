import BAOCert.P2.T_O080
import BAOCert.P2.T_O090
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_O080_O090
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(231893783555192 : ℚ) / (1000000000000000 : ℚ), (236769013032026 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(760674346410050 : ℚ) / (2000000000000000 : ℚ), (778532538530097 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(559134433675 : ℚ) / (1000000000000 : ℚ), (581792654740 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(961051039877803 : ℚ) / (2000000000000000 : ℚ), (987742846125562 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(467847665404 : ℚ) / (1000000000000 : ℚ), (489575147690 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1155450839378023 : ℚ) / (2000000000000000 : ℚ), (1191693947734730 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(388941280031 : ℚ) / (1000000000000 : ℚ), (408688589783 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1418132529168937 : ℚ) / (2000000000000000 : ℚ), (1468385712830250 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(296786999683 : ℚ) / (1000000000000 : ℚ), (313071361005 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1510094142314964 : ℚ) / (2000000000000000 : ℚ), (1565472796735242 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(268276632935 : ℚ) / (1000000000000 : ℚ), (283278927089 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(173204821036 : ℚ) / (1000000000000 : ℚ), (183367963056 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1873845909433236 : ℚ) / (2000000000000000 : ℚ), (1950226662626550 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [80/100, 90/100] and every real K, χ²_DESI DR2(Om, K) ≥ 647.47. -/
theorem chi2_slab : ∀ Om : ℝ, (((80 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((90 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((64747 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((80 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((90 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(231893783555192 : ℚ) / (1000000000000000 : ℚ), (236769013032026 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O080.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(760674346410050 : ℚ) / (2000000000000000 : ℚ), (778532538530097 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O080.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(559134433675 : ℚ) / (1000000000000 : ℚ), (581792654740 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O080.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(961051039877803 : ℚ) / (2000000000000000 : ℚ), (987742846125562 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O080.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(467847665404 : ℚ) / (1000000000000 : ℚ), (489575147690 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O080.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1155450839378023 : ℚ) / (2000000000000000 : ℚ), (1191693947734730 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O080.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(388941280031 : ℚ) / (1000000000000 : ℚ), (408688589783 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O080.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1418132529168937 : ℚ) / (2000000000000000 : ℚ), (1468385712830250 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O080.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(296786999683 : ℚ) / (1000000000000 : ℚ), (313071361005 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O080.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(1510094142314964 : ℚ) / (2000000000000000 : ℚ), (1565472796735242 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O080.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(268276632935 : ℚ) / (1000000000000 : ℚ), (283278927089 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O080.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(173204821036 : ℚ) / (1000000000000 : ℚ), (183367963056 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O080.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(1873845909433236 : ℚ) / (2000000000000000 : ℚ), (1950226662626550 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O090.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O080.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (1679437910 / 43319929 : ℚ) _ _ henv (64747 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_O080_O090
