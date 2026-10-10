import BAOCert.P2.T_O000
import BAOCert.P2.T_O005
import BAOCert.P2.Data

namespace BAOCert.P2.Slab_O000_O005
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(289664380725332 : ℚ) / (1000000000000000 : ℚ), (295000000000295 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(994427498354835 : ℚ) / (2000000000000000 : ℚ), (1020000000001020 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(944006570725 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1358634663648511 : ℚ) / (2000000000000000 : ℚ), (1412000000001412 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(913533408480 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1766152265567395 : ℚ) / (2000000000000000 : ℚ), (1868000000001868 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(873140221720 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2412811340212208 : ℚ) / (2000000000000000 : ℚ), (2642000000002642 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(796777057780 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2667094146816183 : ℚ) / (2000000000000000 : ℚ), (2968000000002968 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(763304116959 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(598009350915 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(3815212107469492 : ℚ) / (2000000000000000 : ℚ), (4660000000004660 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [0/1, 5/100] and every real K, χ²_DESI DR2(Om, K) ≥ -3347.79. -/
theorem chi2_slab : ∀ Om : ℝ, (((0 : ℕ) : ℝ) / ((1 : ℕ) : ℝ)) ≤ Om → Om ≤ (((5 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) → ∀ K : ℝ, ((-334779 / 100 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((0 : ℕ) : ℝ) / ((1 : ℕ) : ℝ)) := by positivity
  have hb1 : (((5 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(289664380725332 : ℚ) / (1000000000000000 : ℚ), (295000000000295 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O000.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(994427498354835 : ℚ) / (2000000000000000 : ℚ), (1020000000001020 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O000.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(944006570725 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O000.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1358634663648511 : ℚ) / (2000000000000000 : ℚ), (1412000000001412 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O000.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(913533408480 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O000.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1766152265567395 : ℚ) / (2000000000000000 : ℚ), (1868000000001868 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O000.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(873140221720 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O000.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(2412811340212208 : ℚ) / (2000000000000000 : ℚ), (2642000000002642 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O000.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(796777057780 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O000.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2667094146816183 : ℚ) / (2000000000000000 : ℚ), (2968000000002968 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O000.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(763304116959 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O000.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(598009350915 : ℚ) / (1000000000000 : ℚ), (1000000000001 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O000.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(3815212107469492 : ℚ) / (2000000000000000 : ℚ), (4660000000004660 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_O005.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O000.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (19173158639 / 995184032 : ℚ) _ _ henv (-334779 / 100 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Slab_O000_O005
