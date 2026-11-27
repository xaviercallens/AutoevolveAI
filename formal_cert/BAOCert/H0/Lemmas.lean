import BAOCert.H0.Pow
import BAOCert.P2.Data

/-!
# Lemma layer for the certified Hubble-tension pilot (P3)

`chi2tot Om h ω_b = χ²_DESI DR2(Om, K(h, Om, ω_b)) + ((ω_b - 0.02218)/0.00055)²` with
`K = c / (100 h r_d)` and `r_d` the Aubourg fitting formula (ported from `ANSE.BAOBBNH0`).
-/

namespace BAOCert.H0

open BAOCert ANSE.BAOBBNH0 Set

/-- `K = c / (100 h r_d)`, `c = 299792.458 km/s`. -/
noncomputable def Kof (h Om wb : ℝ) : ℝ := 299792.458 / (100 * (h * rdAubourg (omegaCb h Om) wb))

/-- DESI DR2 BAO + BBN prior `ω_b ~ N(0.02218, 0.00055)` (arXiv:2503.14738 eq. 14). -/
noncomputable def chi2tot (Om h wb : ℝ) : ℝ :=
  BAOCert.P2.Data.chi2DESI Om (Kof h Om wb) + ((wb - 0.02218) / 0.00055) ^ 2

/-- For `h ≥ 0.73` and `(Om, ω_b)` in a box with `a > 0`, `K ≤ K₀` (certified bound `r_lo` at the corner). -/
theorem K_le {a b c d Om wb h : ℝ} (rdlo K0 : ℚ) (ha : 0 < a) (hc : 0 < c) (hOa : a ≤ Om) (hOb : Om ≤ b)
    (hwc : c ≤ wb) (hwd : wb ≤ d) (hh : 73 / 100 ≤ h)
    (hdom : omegaNu ≤ (1 - 2 * 0.25351) * (a * (73 / 100) ^ 2))
    (hrd : (rdlo : ℝ) ≤ rdAubourg (omegaCb (73 / 100) b) d) (hrd0 : (0 : ℝ) < rdlo)
    (hK : (299792.458 : ℝ) / (100 * ((73 / 100) * (rdlo : ℝ))) ≤ K0) : Kof h Om wb ≤ K0 := by
  have hnu : (0 : ℝ) < omegaNu := by unfold omegaNu; norm_num
  have hOm0 : 0 < Om := lt_of_lt_of_le ha hOa
  have hwb0 : 0 < wb := lt_of_lt_of_le hc hwc
  have hh0 : (0 : ℝ) < h := lt_of_lt_of_le (by norm_num) hh
  have hdomOm : omegaNu ≤ (1 - 2 * 0.25351) * (Om * (73 / 100) ^ 2) := by nlinarith
  have hdomH : omegaNu ≤ (1 - 2 * 0.25351) * (Om * h ^ 2) := by
    have : (73 / 100 : ℝ) ^ 2 ≤ h ^ 2 := pow_le_pow_left₀ (by norm_num) hh 2
    nlinarith
  -- h r_d(h) ≥ 0.73 r_d(0.73)
  have hmono := (hrd_strictMonoOn_h hOm0 hwb0).monotoneOn
    (show (73 / 100 : ℝ) ∈ {h : ℝ | 0 < h ∧ omegaNu ≤ (1 - 2 * 0.25351) * (Om * h ^ 2)} from ⟨by norm_num, hdomOm⟩)
    (show h ∈ {h : ℝ | 0 < h ∧ omegaNu ≤ (1 - 2 * 0.25351) * (Om * h ^ 2)} from ⟨hh0, hdomH⟩) hh
  -- r_d(0.73, Om, ω_b) ≥ r_d(0.73, b, ω_b) ≥ r_d(0.73, b, d)
  have hcbpos : ∀ {x : ℝ}, a ≤ x → 0 < omegaCb (73 / 100) x := by
    intro x hx
    unfold omegaCb
    nlinarith
  have h1 := (rd_strictAntiOn_Om (h := 73 / 100) (by norm_num) hwb0).antitoneOn
    (show Om ∈ {Om : ℝ | 0 < omegaCb (73 / 100) Om} from hcbpos hOa)
    (show b ∈ {Om : ℝ | 0 < omegaCb (73 / 100) Om} from hcbpos (hOa.trans hOb)) hOb
  have h2 := (rdAubourg_strictAntiOn_b (hcbpos (hOa.trans hOb))).antitoneOn
    (show wb ∈ Ioi (0 : ℝ) from hwb0) (show d ∈ Ioi (0 : ℝ) from hwb0.trans_le hwd) hwd
  have hchain : (73 / 100 : ℝ) * (rdlo : ℝ) ≤ h * rdAubourg (omegaCb h Om) wb := by
    have := mul_le_mul_of_nonneg_left (hrd.trans (h2.trans h1)) (by norm_num : (0 : ℝ) ≤ 73 / 100)
    exact this.trans hmono
  have hden : (0 : ℝ) < 100 * ((73 / 100) * (rdlo : ℝ)) := by positivity
  unfold Kof
  calc (299792.458 : ℝ) / (100 * (h * rdAubourg (omegaCb h Om) wb))
      ≤ 299792.458 / (100 * ((73 / 100) * (rdlo : ℝ))) := by
        apply div_le_div_of_nonneg_left (by norm_num) hden
        linarith
    _ ≤ K0 := hK

/-- For `K ≤ K₀`: if `B ≥ 0` and `A ≥ 0` on the box then `χ²(K) ≥ c(K₀) ≥ L`. -/
theorem chi2_lower_Kle (P : List (ℕ × ℕ × ℚ)) (d : List ℚ) (K0 : ℚ) (x : ℕ → ℝ) (env : ℕ → Iv)
    (henv : ∀ j, (env j).mem (x j)) (L : ℚ) (hB : 0 ≤ ((bEx P d K0).ieval env).lo)
    (hA : 0 ≤ ((aEx P).ieval env).lo) (hL : L ≤ ((cEx P d K0).ieval env).lo) :
    ∀ K : ℝ, K ≤ K0 → (L : ℝ) ≤ chi2Of P d x K := by
  intro K hK
  have hc := Ex.ieval_sound x env henv (cEx P d K0)
  have hb := Ex.ieval_sound x env henv (bEx P d K0)
  have ha := Ex.ieval_sound x env henv (aEx P)
  rw [chi2_expand P d K0 x K]
  have hBr : (0 : ℝ) ≤ (bEx P d K0).eval x := le_trans (by exact_mod_cast hB) hb.1
  have hAr : (0 : ℝ) ≤ (aEx P).eval x := le_trans (by exact_mod_cast hA) ha.1
  have hLr : (L : ℝ) ≤ (cEx P d K0).eval x := le_trans (by exact_mod_cast hL) hc.1
  have ht : K - K0 ≤ 0 := by linarith
  nlinarith [mul_nonneg (neg_nonneg.2 ht) hBr, mul_nonneg (sq_nonneg (K - (K0 : ℝ))) hAr]

/-- For `|K - K₀| ≤ t_m`: `χ²(K) ≤ c_hi + t_m |B|_max + t_m² A_hi ≤ U`. -/
theorem chi2_upper_Kin (P : List (ℕ × ℕ × ℚ)) (d : List ℚ) (K0 : ℚ) (x : ℕ → ℝ) (env : ℕ → Iv)
    (henv : ∀ j, (env j).mem (x j)) (U tm : ℚ) (htm : 0 ≤ tm) (hAhi : 0 ≤ ((aEx P).ieval env).hi)
    (hU : ((cEx P d K0).ieval env).hi + tm * (max |((bEx P d K0).ieval env).lo| |((bEx P d K0).ieval env).hi|) +
      tm ^ 2 * ((aEx P).ieval env).hi ≤ U) :
    ∀ K : ℝ, |K - K0| ≤ tm → chi2Of P d x K ≤ (U : ℝ) := by
  intro K hK
  have hc := Ex.ieval_sound x env henv (cEx P d K0)
  have hb := Ex.ieval_sound x env henv (bEx P d K0)
  have ha := Ex.ieval_sound x env henv (aEx P)
  have hBm := abs_le_of_mem hb
  rw [chi2_expand P d K0 x K]
  have hUr : (((cEx P d K0).ieval env).hi : ℝ) + (tm : ℝ) * ((max |((bEx P d K0).ieval env).lo| |((bEx P d K0).ieval env).hi| : ℚ) : ℝ) +
      (tm : ℝ) ^ 2 * (((aEx P).ieval env).hi : ℝ) ≤ U := by
    have := (Rat.cast_le (K := ℝ)).2 hU
    push_cast at this ⊢
    linarith
  have htm' : (0 : ℝ) ≤ tm := by exact_mod_cast htm
  have h1 : -((K - K0) * (bEx P d K0).eval x) ≤ (tm : ℝ) * ((max |((bEx P d K0).ieval env).lo| |((bEx P d K0).ieval env).hi| : ℚ) : ℝ) := by
    have := abs_mul (K - K0) ((bEx P d K0).eval x)
    have h2 : |(K - K0) * (bEx P d K0).eval x| ≤ (tm : ℝ) * ((max |((bEx P d K0).ieval env).lo| |((bEx P d K0).ieval env).hi| : ℚ) : ℝ) := by
      rw [this]; exact mul_le_mul hK hBm (abs_nonneg _) htm'
    linarith [neg_abs_le ((K - K0) * (bEx P d K0).eval x), neg_le.1 (neg_abs_le ((K - K0) * (bEx P d K0).eval x))]
  have hsq : (K - K0) ^ 2 ≤ (tm : ℝ) ^ 2 := by
    have := sq_abs (K - (K0 : ℝ)); rw [← this]; exact pow_le_pow_left₀ (abs_nonneg _) hK 2
  have hAhi' : (0 : ℝ) ≤ (((aEx P).ieval env).hi : ℝ) := by exact_mod_cast hAhi
  have h3 : (K - K0) ^ 2 * (aEx P).eval x ≤ (tm : ℝ) ^ 2 * (((aEx P).ieval env).hi : ℝ) :=
    (mul_le_mul_of_nonneg_left ha.2 (sq_nonneg _)).trans (mul_le_mul_of_nonneg_right hsq hAhi')
  linarith [hc.2, h1, h3, hUr]

/-- `|K(h, Om, ω_b) - K₀| ≤ t_m` at a point, from a certified `r_d ∈ [r_lo, r_hi]` (`r_lo > 0`, `h > 0`). -/
theorem Kof_near {h Om wb : ℝ} (rlo rhi K0 tm : ℚ) (hh : 0 < h) (hr : (rlo : ℝ) ≤ rdAubourg (omegaCb h Om) wb ∧
    rdAubourg (omegaCb h Om) wb ≤ (rhi : ℝ)) (hrlo : (0 : ℝ) < rlo)
    (hlo : (K0 : ℝ) - tm ≤ 299792.458 / (100 * (h * (rhi : ℝ))))
    (hhi : 299792.458 / (100 * (h * (rlo : ℝ))) ≤ (K0 : ℝ) + tm) : |Kof h Om wb - K0| ≤ tm := by
  have hrd0 : (0 : ℝ) < rdAubourg (omegaCb h Om) wb := lt_of_lt_of_le hrlo hr.1
  have k1 : 299792.458 / (100 * (h * (rhi : ℝ))) ≤ Kof h Om wb := by
    unfold Kof
    apply div_le_div_of_nonneg_left (by norm_num) (by positivity)
    have := mul_le_mul_of_nonneg_left hr.2 hh.le
    linarith
  have k2 : Kof h Om wb ≤ 299792.458 / (100 * (h * (rlo : ℝ))) := by
    unfold Kof
    apply div_le_div_of_nonneg_left (by norm_num) (by positivity)
    have := mul_le_mul_of_nonneg_left hr.1 hh.le
    linarith
  rw [abs_le]
  constructor <;> linarith

/-- Minimum of the BBN term over `ω_b ∈ [c, d]`. -/
def priorMin (c d : ℚ) : ℚ :=
  if d < 2218 / 100000 then ((d - 2218 / 100000) / (55 / 100000)) ^ 2
  else if 2218 / 100000 < c then ((c - 2218 / 100000) / (55 / 100000)) ^ 2 else 0

theorem prior_ge {c d : ℚ} {wb : ℝ} (hc : (c : ℝ) ≤ wb) (hd : wb ≤ (d : ℝ)) :
    ((priorMin c d : ℚ) : ℝ) ≤ ((wb - 0.02218) / 0.00055) ^ 2 := by
  have e : ((wb - 0.02218) / 0.00055) ^ 2 = (wb - 2218 / 100000) ^ 2 / (55 / 100000) ^ 2 := by
    rw [div_pow]; norm_num
  rw [e]
  have hs : (0 : ℝ) < (55 / 100000) ^ 2 := by norm_num
  unfold priorMin
  split_ifs with h1 h2
  · have h1' : (d : ℝ) < 2218 / 100000 := by
      have := (Rat.cast_lt (K := ℝ)).2 h1; push_cast at this; linarith
    push_cast
    rw [div_pow]
    apply div_le_div_of_nonneg_right _ hs.le
    nlinarith
  · have h2' : (2218 / 100000 : ℝ) < c := by
      have := (Rat.cast_lt (K := ℝ)).2 h2; push_cast at this; linarith
    push_cast
    rw [div_pow]
    apply div_le_div_of_nonneg_right _ hs.le
    nlinarith
  · push_cast
    positivity

end BAOCert.H0
