"""N1: assemble certified records (n1_certify2.py outputs: thin points a_lo = a_hi, and a-intervals) into the Lean
certificate formal_cert/Programmes/ZeroPointClass/Cert.lean, plus a summary JSON.

usage: python -I n1_make_cert.py OUT_LEAN OUT_SUMMARY AM1 AM2 AP1 AP2 RUN1.json [RUN2.json ...]
  AM1 < AM2: thin points bracketing a-  (F(AM1) > 0 > F(AM2) must be certified)
  AP1 < AP2: thin points bracketing a+  (F(AP1) < 0 < F(AP2) must be certified)

Every certified run (sign pos / neg over its whole interval) becomes one Lean `Rec`
⟨lo, hi, a_c, (Q+R).lo, (Q+R).hi, D.lo, D.hi⟩; runs whose interval has no sign are listed in the summary and never
enter Lean. The Lean kernel re-checks every sign by `decide` (allPos / allNeg). Endpoints are copied verbatim.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction


def lean_q(x: Fraction) -> str:
    if x.denominator == 1:
        return f"({x.numerator} : ℚ)"
    return f"(({x.numerator} : ℚ) / {x.denominator})"


def rec_vals(r: dict) -> tuple[Fraction, ...]:
    return (Fraction(r["a_lo"]), Fraction(r["a_hi"]), Fraction(r["a_c"]),
            Fraction(r["Q"]["lo"]) + Fraction(r["R"]["lo"]), Fraction(r["Q"]["hi"]) + Fraction(r["R"]["hi"]),
            Fraction(r["D"]["lo"]), Fraction(r["D"]["hi"]))


def bounds(r: dict) -> tuple[Fraction, Fraction]:
    lo, hi, ac, qlo, qhi, dlo, dhi = rec_vals(r)
    c = [(lo - ac) * dlo, (lo - ac) * dhi, (hi - ac) * dlo, (hi - ac) * dhi]
    return qlo + min(c), qhi + max(c)


def main() -> None:
    out_lean, out_sum = sys.argv[1], sys.argv[2]
    am1, am2, ap1, ap2 = (Fraction(x) for x in sys.argv[3:7])
    runs: dict[tuple[Fraction, Fraction], dict] = {}
    for p in sys.argv[7:]:
        for r in json.load(open(p)):
            if r.get("engine") == "n1_certify2":
                runs[(Fraction(r["a_lo"]), Fraction(r["a_hi"]))] = r
    pos, neg, none = [], [], []
    for k in sorted(runs):
        r = runs[k]
        if not r["ok"]:
            none.append(r)
            continue
        lo, hi = bounds(r)
        (pos if lo > 0 else neg if hi < 0 else none).append(r)
    names: dict[tuple[Fraction, Fraction], str] = {}
    lines = []
    for i, r in enumerate(pos + neg):
        nm = f"r{i}"
        names[(Fraction(r["a_lo"]), Fraction(r["a_hi"]))] = nm
        lines.append(f"/-- a ∈ [{r['a_lo']}, {r['a_hi']}] ({'F > 0' if r in pos else 'F < 0'}); run {r['N']}/{r['depth']}/"
                     f"{r['tol']}, {r['stats']['cells']} cells, {r['seconds']} s. -/")
        lines.append(f"def {nm} : Rec := ⟨" + ", ".join(lean_q(x) for x in rec_vals(r)) + "⟩")
    need = {"AM1": (am1, pos), "AM2": (am2, neg), "AP1": (ap1, neg), "AP2": (ap2, pos)}
    for key, (a, lst) in need.items():
        if not any(Fraction(r["a_lo"]) == a == Fraction(r["a_hi"]) for r in lst):
            raise SystemExit(f"bracket point {key} = {a} is not a certified thin point of the right sign")
    def key(r: dict) -> tuple[Fraction, Fraction]:
        return (Fraction(r["a_lo"]), Fraction(r["a_hi"]))

    def segments(lst: list[dict]) -> tuple[list[list[dict]], list[dict]]:
        """Maximal chains (>= 2 records) of contiguous interval records; the rest."""
        segs, cur = [], []
        for r in [x for x in lst if key(x)[0] < key(x)[1]]:
            lo, hi = key(r)
            if lo < hi and cur and key(cur[-1])[1] == lo:
                cur.append(r)
            else:
                if len(cur) >= 2:
                    segs.append(cur)
                cur = [r] if lo < hi else []
        if len(cur) >= 2:
            segs.append(cur)
        used = {key(r) for sg in segs for r in sg}
        return segs, [r for r in lst if key(r) not in used]

    seg_lines, seg_thms, seg_prints, seg_summary = [], [], [], []

    def build(lst: list[dict], tag: str, sign: str) -> str:
        segs, rest = segments(lst)
        parts = []
        for i, sg in enumerate(segs):
            nmL = f"L{tag}seg{i}"
            parts.append(nmL)
            lo, hi = key(sg[0])[0], key(sg[-1])[1]
            seg_lines.append(f"/-- chained {sign} segment [{lo}, {hi}], {len(sg)} records. -/")
            seg_lines.append(f"def {nmL} : List Rec := [{', '.join(names[key(r)] for r in sg)}]")
            ext = "".join(".right" for _ in range(i)) + ".left"
            sgn = "allPos" if sign == "pos" else "allNeg"
            sgn_ext = f"{sgn}_left " + "".join(f"({sgn}_right " for _ in range(i)) + f"sign_{tag}" + ")" * i
            lem = "pos_on_of_chain" if sign == "pos" else "neg_on_of_chain"
            concl = "0 < F a t" if sign == "pos" else "F a t < 0"
            seg_thms.append(f"""theorem chain_{tag}{i} : chainFrom {lean_q(lo)} {lean_q(hi)} {nmL} = true := by decide +kernel

/-- Whole-interval sign on the chained segment `[{lo}, {hi}]` (logic Tier A, enclosures Tier C-ball). -/
theorem segment_{tag}{i} (F : ℝ → ℝ → ℝ) (h : Encloses F t0 L{tag}) :
    ∀ a : ℝ, (({lean_q(lo)} : ℚ) : ℝ) ≤ a → a ≤ (({lean_q(hi)} : ℚ) : ℝ) → ∀ t : ℝ, |t| ≤ t0 → {concl} := by
  intro a h1 h2 t ht
  obtain ⟨c, hc, hF⟩ := {lem} F t0 {nmL} _ _ chain_{tag}{i} ({sgn_ext}) (h{ext}) a h1 h2
  have hc' : {"(0 : ℝ) < (c : ℝ)" if sign == "pos" else "(c : ℝ) < 0"} := by exact_mod_cast hc
  linarith [hF t ht]
""")
            if sign == "neg":
                path_concl = "¬ IsLocalMin (E a) 0 ∧ ∀ t, 0 < t → t ≤ t0 → E a t < E a 0"
                path_proof = ("not_localMin_of_curv_neg ht0 hc' (fun t ht => hE a t ht) (fun t ht => hE' a t ht)\n"
                              "    (fun t ht => hF t (mem t ht)) (fun t => hsym a t)")
                hc_txt = "(c : ℝ) < 0"
            else:
                path_concl = "∀ t, t ≠ 0 → |t| ≤ t0 → E a 0 < E a t"
                path_proof = ("strict_gt_of_curv_pos hc' (fun t ht => hE a t ht) (fun t ht => hE' a t ht)\n"
                              "    (fun t ht => hF t (mem t ht)) (fun t => hsym a t)")
                hc_txt = "(0 : ℝ) < (c : ℝ)"
            seg_thms.append(f"""/-- Along-path consequence on the whole segment `[{lo}, {hi}]` (logic Tier A; hypotheses as `along_path`). -/
theorem segment_{tag}{i}_path (E E' F : ℝ → ℝ → ℝ) (h : Encloses F t0 L{tag})
    (hE : ∀ a t : ℝ, t ∈ Icc (-t0) t0 → HasDerivAt (E a) (E' a t) t)
    (hE' : ∀ a t : ℝ, t ∈ Icc (-t0) t0 → HasDerivAt (E' a) (F a t) t)
    (hsym : ∀ a t : ℝ, E a (-t) = E a t) :
    ∀ a : ℝ, (({lean_q(lo)} : ℚ) : ℝ) ≤ a → a ≤ (({lean_q(hi)} : ℚ) : ℝ) → {path_concl} := by
  intro a h1 h2
  have ht0 : (0 : ℝ) < t0 := by norm_num [t0]
  have mem : ∀ t ∈ Icc (-t0) t0, |t| ≤ t0 := fun t ht => abs_le.2 ⟨ht.1, ht.2⟩
  obtain ⟨c, hc, hF⟩ := {lem} F t0 {nmL} _ _ chain_{tag}{i} ({sgn_ext}) (h{ext}) a h1 h2
  have hc' : {hc_txt} := by exact_mod_cast hc
  exact {path_proof}
""")
            seg_prints.extend([f"#print axioms ProgZeroPointClass.chain_{tag}{i}", f"#print axioms ProgZeroPointClass.segment_{tag}{i}",
                               f"#print axioms ProgZeroPointClass.segment_{tag}{i}_path"])
            seg_summary.append({"sign": sign, "lo": str(lo), "hi": str(hi), "lo_float": float(lo), "hi_float": float(hi),
                                "n_records": len(sg)})
        restL = "[" + ", ".join(names[key(r)] for r in rest) + "]"
        expr = restL
        for nmL in reversed(parts):
            expr = f"{nmL} ++ ({expr})"
        return expr

    pos_expr = build(pos, "pos", "pos")
    neg_expr = build(neg, "neg", "neg")
    nm = {k: names[(a, a)] for k, (a, _) in need.items()}
    src = f"""import Programmes.ZeroPointClass.Basic

/-!
# N1 certificate data (generated by `results/proposal3/2026-10-26/N1/code/n1_make_cert.py`; do not edit)

Records `⟨lo, hi, a_c, qlo, qhi, dlo, dhi⟩` (see `Rec`): for every `a ∈ [lo, hi]` and `|t| ≤ t₀ = 10⁻⁸` the exact
second variation `F a t` of the zero-point energy along the shear path satisfies `F a t - (a - a_c) d ∈ [qlo, qhi]`
for some `d ∈ [dlo, dhi]` (Arb ball arithmetic, `n1_certify2.py`; Tier C-ball). A record with `lo = hi` is a thin
point. The kernel checks by `decide` that every record of `Lpos` has a positive lower corner bound and every record of
`Lneg` a negative upper corner bound, and that the bracket points are ordered.
-/

namespace ProgZeroPointClass

open Set

/-- Window half-width. -/
noncomputable def t0 : ℝ := 1 / 100000000

{chr(10).join(lines)}

-- Records certifying `F > 0` (chained segments first).
{chr(10).join(seg_lines)}

def Lpos : List Rec := {pos_expr}
-- Records certifying `F < 0`.
def Lneg : List Rec := {neg_expr}

theorem sign_pos : allPos Lpos = true := by decide +kernel
theorem sign_neg : allNeg Lneg = true := by decide +kernel

{chr(10).join(seg_thms)}theorem brackets_ordered : {nm['AM1']}.lo < {nm['AM2']}.lo ∧ {nm['AM2']}.lo < {nm['AP1']}.lo ∧ {nm['AP1']}.lo < {nm['AP2']}.lo ∧
    {nm['AM1']}.lo = {nm['AM1']}.hi ∧ {nm['AM2']}.lo = {nm['AM2']}.hi ∧ {nm['AP1']}.lo = {nm['AP1']}.hi ∧
    {nm['AP2']}.lo = {nm['AP2']}.hi := by decide +kernel

/-- **N1, certified signs and root brackets (logic Tier A; the enclosure hypotheses are Tier C-ball, the continuity
of `a ↦ F a 0` Tier C-human).** `F a t` is the second `t`-derivative of the zero-point energy along the shear path for
the Gaussian `exp(-π a r²)`. Then `F > 0` on every record of `Lpos`, `F < 0` on every record of `Lneg` (whole
`a`-intervals for interval records, the point for thin records, always for all `|t| ≤ t₀`), and `a ↦ F a 0` has a
zero strictly between the bracket points `{nm['AM1']}.lo < {nm['AM2']}.lo` (a₋) and `{nm['AP1']}.lo < {nm['AP2']}.lo` (a₊). -/
theorem classification (F : ℝ → ℝ → ℝ) (hp : Encloses F t0 Lpos) (hn : Encloses F t0 Lneg)
    (hcm : ContinuousOn (fun a => F a 0) (Icc ({nm['AM1']}.lo : ℝ) ({nm['AM2']}.lo : ℝ)))
    (hcp : ContinuousOn (fun a => F a 0) (Icc ({nm['AP1']}.lo : ℝ) ({nm['AP2']}.lo : ℝ))) :
    (∀ r ∈ Lpos, ∀ a : ℝ, (r.lo : ℝ) ≤ a → a ≤ (r.hi : ℝ) → ∀ t : ℝ, |t| ≤ t0 → 0 < F a t) ∧
    (∀ r ∈ Lneg, ∀ a : ℝ, (r.lo : ℝ) ≤ a → a ≤ (r.hi : ℝ) → ∀ t : ℝ, |t| ≤ t0 → F a t < 0) ∧
    (∃ a ∈ Ioo ({nm['AM1']}.lo : ℝ) ({nm['AM2']}.lo : ℝ), F a 0 = 0) ∧
    (∃ a ∈ Ioo ({nm['AP1']}.lo : ℝ) ({nm['AP2']}.lo : ℝ), F a 0 = 0) := by
  have P := pos_of_mem F t0 Lpos sign_pos hp
  have N := neg_of_mem F t0 Lneg sign_neg hn
  have ho := brackets_ordered
  have t00 : |(0 : ℝ)| ≤ t0 := by rw [abs_zero]; norm_num [t0]
  have mAM1 : {nm['AM1']} ∈ Lpos := by simp [Lpos]
  have mAP2 : {nm['AP2']} ∈ Lpos := by simp [Lpos]
  have mAM2 : {nm['AM2']} ∈ Lneg := by simp [Lneg]
  have mAP1 : {nm['AP1']} ∈ Lneg := by simp [Lneg]
  have o1 : ({nm['AM1']}.lo : ℝ) < {nm['AM2']}.lo := by exact_mod_cast ho.1
  have o3 : ({nm['AP1']}.lo : ℝ) < {nm['AP2']}.lo := by exact_mod_cast ho.2.2.1
  have e1 : ({nm['AM1']}.lo : ℝ) ≤ {nm['AM1']}.hi := by exact_mod_cast ho.2.2.2.1.le
  have e2 : ({nm['AM2']}.lo : ℝ) ≤ {nm['AM2']}.hi := by exact_mod_cast ho.2.2.2.2.1.le
  have e3 : ({nm['AP1']}.lo : ℝ) ≤ {nm['AP1']}.hi := by exact_mod_cast ho.2.2.2.2.2.1.le
  have e4 : ({nm['AP2']}.lo : ℝ) ≤ {nm['AP2']}.hi := by exact_mod_cast ho.2.2.2.2.2.2.le
  refine ⟨P, N, ?_, ?_⟩
  · exact root_in_gap (fun a => F a 0) o1 hcm (P _ mAM1 _ le_rfl e1 0 t00) (N _ mAM2 _ le_rfl e2 0 t00)
  · exact root_in_gap' (fun a => F a 0) o3 hcp (N _ mAP1 _ le_rfl e3 0 t00) (P _ mAP2 _ le_rfl e4 0 t00)

/-- **N1, along-path consequences (logic Tier A).** If for each certified `a` the energy `t ↦ E a t` along the shear
path has derivative `E' a` and second derivative `F a` on `[-t₀, t₀]` (Tier C-human: differentiation under the
Brillouin-zone integral) and is even in `t` (mirror symmetry, B2 §2.4), then for every `a` of a negative record the
triangular point is not a local minimum along the path and `E a t < E a 0` for `0 < t ≤ t₀`, and for every `a` of a
positive record `E a 0 < E a t` for `0 < |t| ≤ t₀`. -/
theorem along_path (E E' F : ℝ → ℝ → ℝ) (hp : Encloses F t0 Lpos) (hn : Encloses F t0 Lneg)
    (hE : ∀ a t : ℝ, t ∈ Icc (-t0) t0 → HasDerivAt (E a) (E' a t) t)
    (hE' : ∀ a t : ℝ, t ∈ Icc (-t0) t0 → HasDerivAt (E' a) (F a t) t)
    (hsym : ∀ a t : ℝ, E a (-t) = E a t) :
    (∀ r ∈ Lneg, ∀ a : ℝ, (r.lo : ℝ) ≤ a → a ≤ (r.hi : ℝ) →
      ¬ IsLocalMin (E a) 0 ∧ ∀ t, 0 < t → t ≤ t0 → E a t < E a 0) ∧
    (∀ r ∈ Lpos, ∀ a : ℝ, (r.lo : ℝ) ≤ a → a ≤ (r.hi : ℝ) → ∀ t, t ≠ 0 → |t| ≤ t0 → E a 0 < E a t) := by
  have ht0 : (0 : ℝ) < t0 := by norm_num [t0]
  have mem : ∀ t ∈ Icc (-t0) t0, |t| ≤ t0 := fun t ht => abs_le.2 ⟨ht.1, ht.2⟩
  refine ⟨?_, ?_⟩
  · intro r hr a h1 h2
    have hc : r.qhi + r.cmax < 0 := by
      have := List.all_eq_true.1 sign_neg r hr
      simpa using this
    have hc' : ((r.qhi + r.cmax : ℚ) : ℝ) < 0 := by exact_mod_cast hc
    exact not_localMin_of_curv_neg ht0 hc' (fun t ht => hE a t ht) (fun t ht => hE' a t ht)
      (fun t ht => rec_upper F t0 r h1 h2 (hn r hr a h1 h2 t (mem t ht))) (fun t => hsym a t)
  · intro r hr a h1 h2
    have hc : 0 < r.qlo + r.cmin := by
      have := List.all_eq_true.1 sign_pos r hr
      simpa using this
    have hc' : (0 : ℝ) < ((r.qlo + r.cmin : ℚ) : ℝ) := by exact_mod_cast hc
    exact strict_gt_of_curv_pos hc' (fun t ht => hE a t ht) (fun t ht => hE' a t ht)
      (fun t ht => rec_lower F t0 r h1 h2 (hp r hr a h1 h2 t (mem t ht))) (fun t => hsym a t)

end ProgZeroPointClass

#print axioms ProgZeroPointClass.sign_pos
#print axioms ProgZeroPointClass.sign_neg
#print axioms ProgZeroPointClass.brackets_ordered
#print axioms ProgZeroPointClass.classification
#print axioms ProgZeroPointClass.along_path
{chr(10).join(seg_prints)}
"""
    open(out_lean, "w").write(src)
    summ = {
        "brackets": {"a_minus": [str(am1), str(am2), float(am1), float(am2)],
                     "a_plus": [str(ap1), str(ap2), float(ap1), float(ap2)]},
        "positive": [{"a_lo": r["a_lo"], "a_hi": r["a_hi"], "F": [float(x) for x in bounds(r)]} for r in pos],
        "negative": [{"a_lo": r["a_lo"], "a_hi": r["a_hi"], "F": [float(x) for x in bounds(r)]} for r in neg],
        "uncertified": [{"a_lo": r["a_lo"], "a_hi": r["a_hi"], "ok": r["ok"],
                         "F": [float(x) for x in bounds(r)] if r["ok"] else None} for r in none],
    }
    summ["chained_segments"] = seg_summary
    summ["inputs"] = sys.argv[7:]
    json.dump(summ, open(out_sum, "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
