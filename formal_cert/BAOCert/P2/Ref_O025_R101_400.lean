import BAOCert.P2.T_O025
import BAOCert.P2.T_R101_400
import BAOCert.P2.Data

namespace BAOCert.P2.Ref_O025_R101_400
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(271186666589620 : ℚ) / (1000000000000000 : ℚ), (271428589153347 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(912655443937082 : ℚ) / (2000000000000000 : ℚ), (913717584299932 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(786440351991 : ℚ) / (1000000000000 : ℚ), (787929900430 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1205111286577909 : ℚ) / (2000000000000000 : ℚ), (1206894478191316 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(706892278368 : ℚ) / (1000000000000 : ℚ), (708649604529 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1507948532338814 : ℚ) / (2000000000000000 : ℚ), (1510654020634929 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(623292333456 : ℚ) / (1000000000000 : ℚ), (625187813384 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1942984779254409 : ℚ) / (2000000000000000 : ℚ), (1947280853036657 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(506072042032 : ℚ) / (1000000000000 : ℚ), (507946076123 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2101180694252742 : ℚ) / (2000000000000000 : ℚ), (2106119358165861 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(465365702105 : ℚ) / (1000000000000 : ℚ), (467181140071 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(315106026140 : ℚ) / (1000000000000 : ℚ), (316520536524 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2749040718533758 : ℚ) / (2000000000000000 : ℚ), (2756866228073726 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [25/100, 101/400] and every real K, χ²_DESI DR2(Om, K) ≥ 39.68. -/
theorem chi2_slab : ∀ Om : ℝ, (((25 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) ≤ Om → Om ≤ (((101 : ℕ) : ℝ) / ((400 : ℕ) : ℝ)) → ∀ K : ℝ, ((992 / 25 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((25 : ℕ) : ℝ) / ((100 : ℕ) : ℝ)) := by positivity
  have hb1 : (((101 : ℕ) : ℝ) / ((400 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(271186666589620 : ℚ) / (1000000000000000 : ℚ), (271428589153347 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_O025.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(912655443937082 : ℚ) / (2000000000000000 : ℚ), (913717584299932 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_O025.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(786440351991 : ℚ) / (1000000000000 : ℚ), (787929900430 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_O025.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1205111286577909 : ℚ) / (2000000000000000 : ℚ), (1206894478191316 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_O025.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(706892278368 : ℚ) / (1000000000000 : ℚ), (708649604529 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_O025.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1507948532338814 : ℚ) / (2000000000000000 : ℚ), (1510654020634929 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_O025.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(623292333456 : ℚ) / (1000000000000 : ℚ), (625187813384 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_O025.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1942984779254409 : ℚ) / (2000000000000000 : ℚ), (1947280853036657 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_O025.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(506072042032 : ℚ) / (1000000000000 : ℚ), (507946076123 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_O025.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2101180694252742 : ℚ) / (2000000000000000 : ℚ), (2106119358165861 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_O025.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(465365702105 : ℚ) / (1000000000000 : ℚ), (467181140071 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_O025.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(315106026140 : ℚ) / (1000000000000 : ℚ), (316520536524 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_O025.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2749040718533758 : ℚ) / (2000000000000000 : ℚ), (2756866228073726 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R101_400.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_O025.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (26433892345 / 930266031 : ℚ) _ _ henv (992 / 25 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.Ref_O025_R101_400
