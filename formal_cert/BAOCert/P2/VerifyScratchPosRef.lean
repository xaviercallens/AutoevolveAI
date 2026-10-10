import BAOCert.P2.T_R101_400
import BAOCert.P2.T_R51_200
import BAOCert.P2.Data

namespace BAOCert.P2.VerifyScratchPosRef
open BAOCert BAOCert.P2

def envs : List Iv := [⟨(270984582200712 : ℚ) / (1000000000000000 : ℚ), (271226270121370 : ℚ) / (1000000000000000 : ℚ)⟩, ⟨(911808568710926 : ℚ) / (2000000000000000 : ℚ), (912869003586111 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(784959219526 : ℚ) / (1000000000000 : ℚ), (786440351992 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1203626862860423 : ℚ) / (2000000000000000 : ℚ), (1205404394300953 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(705147961279 : ℚ) / (1000000000000 : ℚ), (706892278369 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1505632209582844 : ℚ) / (2000000000000000 : ℚ), (1508325240007226 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(621413990115 : ℚ) / (1000000000000 : ℚ), (623292333457 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(1939209977904629 : ℚ) / (2000000000000000 : ℚ), (1943478707215019 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(504218598435 : ℚ) / (1000000000000 : ℚ), (506072042033 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2096810860292726 : ℚ) / (2000000000000000 : ℚ), (2101715328553605 : ℚ) / (2000000000000000 : ℚ)⟩, ⟨(463571265026 : ℚ) / (1000000000000 : ℚ), (465365702106 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(313710311895 : ℚ) / (1000000000000 : ℚ), (315106026141 : ℚ) / (1000000000000 : ℚ)⟩, ⟨(2741968987955238 : ℚ) / (2000000000000000 : ℚ), (2749725612512278 : ℚ) / (2000000000000000 : ℚ)⟩]

/-- For every Om in [101/400, 51/200] and every real K, χ²_DESI DR2(Om, K) ≥ 36.02. -/
theorem chi2_slab : ∀ Om : ℝ, (((101 : ℕ) : ℝ) / ((400 : ℕ) : ℝ)) ≤ Om → Om ≤ (((51 : ℕ) : ℝ) / ((200 : ℕ) : ℝ)) → ∀ K : ℝ, ((1801 / 50 : ℚ) : ℝ) ≤ Data.chi2DESI Om K := by
  intro Om hOa hOb
  have ha0 : (0 : ℝ) ≤ (((101 : ℕ) : ℝ) / ((400 : ℕ) : ℝ)) := by positivity
  have hb1 : (((51 : ℕ) : ℝ) / ((200 : ℕ) : ℝ)) ≤ 1 := by norm_num
  have hO0 : 0 ≤ Om := ha0.trans hOa
  have hO1 : Om ≤ 1 := hOb.trans hb1
  have hz0 : (0 : ℝ) ≤ (((590 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h0 : (⟨(270984582200712 : ℚ) / (1000000000000000 : ℚ), (271226270121370 : ℚ) / (1000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.wV_z0295).1.trans (wV_anti_Om hO0 hOb hb1 hz0),
     (wV_anti_Om ha0 hOa hO1 hz0).trans (BAOCert.P2.T_R101_400.wV_z0295).2⟩
  have hz1 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h1 : (⟨(911808568710926 : ℚ) / (2000000000000000 : ℚ), (912869003586111 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.chi_z0510).1.trans (chi_anti_Om hO0 hOb hb1 hz1),
     (chi_anti_Om ha0 hOa hO1 hz1).trans (BAOCert.P2.T_R101_400.chi_z0510).2⟩
  have hz2 : (0 : ℝ) ≤ (((1020 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h2 : (⟨(784959219526 : ℚ) / (1000000000000 : ℚ), (786440351992 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.invE_z0510).1.trans (invE_anti_Om hO0 hOb hb1 hz2),
     (invE_anti_Om ha0 hOa hO1 hz2).trans (BAOCert.P2.T_R101_400.invE_z0510).2⟩
  have hz3 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h3 : (⟨(1203626862860423 : ℚ) / (2000000000000000 : ℚ), (1205404394300953 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.chi_z0706).1.trans (chi_anti_Om hO0 hOb hb1 hz3),
     (chi_anti_Om ha0 hOa hO1 hz3).trans (BAOCert.P2.T_R101_400.chi_z0706).2⟩
  have hz4 : (0 : ℝ) ≤ (((1412 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h4 : (⟨(705147961279 : ℚ) / (1000000000000 : ℚ), (706892278369 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.invE_z0706).1.trans (invE_anti_Om hO0 hOb hb1 hz4),
     (invE_anti_Om ha0 hOa hO1 hz4).trans (BAOCert.P2.T_R101_400.invE_z0706).2⟩
  have hz5 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h5 : (⟨(1505632209582844 : ℚ) / (2000000000000000 : ℚ), (1508325240007226 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.chi_z0934).1.trans (chi_anti_Om hO0 hOb hb1 hz5),
     (chi_anti_Om ha0 hOa hO1 hz5).trans (BAOCert.P2.T_R101_400.chi_z0934).2⟩
  have hz6 : (0 : ℝ) ≤ (((1868 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h6 : (⟨(621413990115 : ℚ) / (1000000000000 : ℚ), (623292333457 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.invE_z0934).1.trans (invE_anti_Om hO0 hOb hb1 hz6),
     (invE_anti_Om ha0 hOa hO1 hz6).trans (BAOCert.P2.T_R101_400.invE_z0934).2⟩
  have hz7 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h7 : (⟨(1939209977904629 : ℚ) / (2000000000000000 : ℚ), (1943478707215019 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.chi_z1321).1.trans (chi_anti_Om hO0 hOb hb1 hz7),
     (chi_anti_Om ha0 hOa hO1 hz7).trans (BAOCert.P2.T_R101_400.chi_z1321).2⟩
  have hz8 : (0 : ℝ) ≤ (((2642 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h8 : (⟨(504218598435 : ℚ) / (1000000000000 : ℚ), (506072042033 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.invE_z1321).1.trans (invE_anti_Om hO0 hOb hb1 hz8),
     (invE_anti_Om ha0 hOa hO1 hz8).trans (BAOCert.P2.T_R101_400.invE_z1321).2⟩
  have hz9 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h9 : (⟨(2096810860292726 : ℚ) / (2000000000000000 : ℚ), (2101715328553605 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.chi_z1484).1.trans (chi_anti_Om hO0 hOb hb1 hz9),
     (chi_anti_Om ha0 hOa hO1 hz9).trans (BAOCert.P2.T_R101_400.chi_z1484).2⟩
  have hz10 : (0 : ℝ) ≤ (((2968 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h10 : (⟨(463571265026 : ℚ) / (1000000000000 : ℚ), (465365702106 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.invE_z1484).1.trans (invE_anti_Om hO0 hOb hb1 hz10),
     (invE_anti_Om ha0 hOa hO1 hz10).trans (BAOCert.P2.T_R101_400.invE_z1484).2⟩
  have hz11 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h11 : (⟨(313710311895 : ℚ) / (1000000000000 : ℚ), (315106026141 : ℚ) / (1000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.invE_z2330).1.trans (invE_anti_Om hO0 hOb hb1 hz11),
     (invE_anti_Om ha0 hOa hO1 hz11).trans (BAOCert.P2.T_R101_400.invE_z2330).2⟩
  have hz12 : (0 : ℝ) ≤ (((4660 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) := by positivity
  have h12 : (⟨(2741968987955238 : ℚ) / (2000000000000000 : ℚ), (2749725612512278 : ℚ) / (2000000000000000 : ℚ)⟩ : Iv).mem _ :=
    ⟨(BAOCert.P2.T_R51_200.chi_z2330).1.trans (chi_anti_Om hO0 hOb hb1 hz12),
     (chi_anti_Om ha0 hOa hO1 hz12).trans (BAOCert.P2.T_R101_400.chi_z2330).2⟩
  have henv := env_ok envs (Data.xsOf Om) (List.Forall₂.cons h0 (List.Forall₂.cons h1 (List.Forall₂.cons h2 (List.Forall₂.cons h3 (List.Forall₂.cons h4 (List.Forall₂.cons h5 (List.Forall₂.cons h6 (List.Forall₂.cons h7 (List.Forall₂.cons h8 (List.Forall₂.cons h9 (List.Forall₂.cons h10 (List.Forall₂.cons h11 (List.Forall₂.cons h12 List.Forall₂.nil)))))))))))))
  exact chi2_lower_of_env Data.Pent Data.dR (26468476066 / 929431031 : ℚ) _ _ henv (1801 / 50 : ℚ) (by decide +kernel) (by decide +kernel)

end BAOCert.P2.VerifyScratchPosRef
