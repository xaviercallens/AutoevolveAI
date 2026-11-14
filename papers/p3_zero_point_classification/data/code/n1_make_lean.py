"""N1: assemble the a-sweep records (n1_certify2.py outputs) into the Lean certificate
formal_cert/Programmes/ZeroPointClass/Cert.lean and a summary JSON.

usage: python -I n1_make_lean.py OUT_LEAN OUT_SUMMARY RUN1.json [RUN2.json ...]

Records are sorted by a_lo. They must tile a set of segments: maximal runs of consecutive records with the same
certified sign ("pos" / "neg") and hi = next lo. The expected pattern on [A0, A1] is pos | gap | neg | gap | pos,
where each gap is either an uncertified record (sign "none") or several, whose union is the root enclosure. A record
with sign "none" never enters a Lean list. Every enclosure endpoint is copied verbatim (outward rounded rationals).
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction


def lean_q(x: Fraction) -> str:
    if x.denominator == 1:
        return f"({x.numerator} : ℚ)"
    return f"(({x.numerator} : ℚ) / {x.denominator})"


def piece_bounds(r: dict, p: Fraction, q: Fraction) -> tuple[Fraction, Fraction]:
    """(qlo + cmin, qhi + cmax) on the sub-interval [p, q], exactly as Lean's Rec.cmin / Rec.cmax compute them."""
    ac = Fraction(r["a_c"])
    qlo = Fraction(r["Q"]["lo"]) + Fraction(r["R"]["lo"])
    qhi = Fraction(r["Q"]["hi"]) + Fraction(r["R"]["hi"])
    dlo, dhi = Fraction(r["D"]["lo"]), Fraction(r["D"]["hi"])
    corners = [(p - ac) * dlo, (p - ac) * dhi, (q - ac) * dlo, (q - ac) * dhi]
    return qlo + min(corners), qhi + max(corners)


def sign_of(r: dict, p: Fraction, q: Fraction) -> str:
    lo, hi = piece_bounds(r, p, q)
    return "pos" if lo > 0 else ("neg" if hi < 0 else "none")


def split_run(r: dict, grid: int = 10**7) -> list[dict]:
    """Certified pieces of one run: the whole interval if it has a sign, else the longest certified prefix and
    suffix (endpoints on the 1/grid lattice, found by bisection; the middle is left uncertified)."""
    lo, hi = Fraction(r["a_lo"]), Fraction(r["a_hi"])
    if not r.get("ok"):
        return []
    sg = sign_of(r, lo, hi)
    if sg != "none":
        return [{"run": r, "lo": lo, "hi": hi, "sign": sg}]
    out = []
    first = sign_of(r, lo, lo)
    if first != "none":
        a, b = lo, hi
        for _ in range(60):
            m = Fraction(round((a + b) / 2 * grid), grid)
            if m <= a or m >= b:
                break
            if sign_of(r, lo, m) == first:
                a = m
            else:
                b = m
        if a > lo:
            out.append({"run": r, "lo": lo, "hi": a, "sign": first})
    last = sign_of(r, hi, hi)
    if last != "none":
        a, b = lo, hi
        for _ in range(60):
            m = Fraction(round((a + b) / 2 * grid), grid)
            if m <= a or m >= b:
                break
            if sign_of(r, m, hi) == last:
                b = m
            else:
                a = m
        if b < hi:
            out.append({"run": r, "lo": b, "hi": hi, "sign": last})
    return out


def main() -> None:
    out_lean, out_sum = sys.argv[1], sys.argv[2]
    runs = []
    for p in sys.argv[3:]:
        for r in json.load(open(p)):
            if r.get("engine") == "n1_certify2" and Fraction(r["a_lo"]) < Fraction(r["a_hi"]):
                runs.append(r)
    runs.sort(key=lambda r: (Fraction(r["a_lo"]), Fraction(r["a_hi"])))
    # keep, per interval, the last run (a rerun with more depth replaces a failed one)
    uniq: dict[tuple[Fraction, Fraction], dict] = {}
    for r in runs:
        uniq[(Fraction(r["a_lo"]), Fraction(r["a_hi"]))] = r
    runs = [uniq[k] for k in sorted(uniq)]
    holes = [(str(x["a_hi"]), str(y["a_lo"])) for x, y in zip(runs, runs[1:]) if Fraction(x["a_hi"]) != Fraction(y["a_lo"])]
    pieces = [pc for r in runs for pc in split_run(r)]
    segs: list[dict] = []
    for pc in pieces:
        if segs and segs[-1]["sign"] == pc["sign"] and segs[-1]["hi"] == pc["lo"]:
            segs[-1]["recs"].append(pc)
            segs[-1]["hi"] = pc["hi"]
        else:
            segs.append({"sign": pc["sign"], "lo": pc["lo"], "hi": pc["hi"], "recs": [pc]})
    all_segs = [(s["sign"], str(s["lo"]), str(s["hi"])) for s in segs]
    # the longest negative segment, and the nearest positive segment on each side of it; the gaps between them must
    # be covered by runs (no hole may be bridged)
    negs = [i for i, s in enumerate(segs) if s["sign"] == "neg"]
    if not negs:
        raise SystemExit(f"no negative segment: {all_segs}")
    k = max(negs, key=lambda i: segs[i]["hi"] - segs[i]["lo"])
    if not (k >= 1 and k + 1 < len(segs) and segs[k - 1]["sign"] == "pos" and segs[k + 1]["sign"] == "pos"):
        raise SystemExit(f"no pos|neg|pos pattern around the main negative segment: {all_segs}")
    for g_lo, g_hi in ((segs[k - 1]["hi"], segs[k]["lo"]), (segs[k]["hi"], segs[k + 1]["lo"])):
        for h_lo, h_hi in holes:
            if g_lo <= Fraction(h_lo) < g_hi:
                raise SystemExit(f"root gap [{g_lo}, {g_hi}] contains an uncovered hole [{h_lo}, {h_hi}]")
    dropped = [x for i, x in enumerate(all_segs) if i not in (k - 1, k, k + 1)]
    segs = [segs[k - 1], segs[k], segs[k + 1]]
    names = ["Lpos1", "Lneg", "Lpos2"]
    lines = []
    for nm, s in zip(names, segs):
        items = []
        for pc in s["recs"]:
            r = pc["run"]
            vals = (pc["lo"], pc["hi"], Fraction(r["a_c"]), Fraction(r["Q"]["lo"]) + Fraction(r["R"]["lo"]),
                    Fraction(r["Q"]["hi"]) + Fraction(r["R"]["hi"]), Fraction(r["D"]["lo"]), Fraction(r["D"]["hi"]))
            items.append("⟨" + ", ".join(lean_q(x) for x in vals) + "⟩")
        lines.append(f"/-- {s['sign']} segment [{s['lo']}, {s['hi']}], {len(items)} records. -/")
        lines.append(f"def {nm} : List Rec := [\n  " + ",\n  ".join(items) + "]")
        lines.append("")
    A0, aLm, aRm, aLp, aRp, A1 = segs[0]["lo"], segs[0]["hi"], segs[1]["lo"], segs[1]["hi"], segs[2]["lo"], segs[2]["hi"]
    pts = {"A0": A0, "aLm": aLm, "aRm": aRm, "aLp": aLp, "aRp": aRp, "A1": A1}
    defs = "\n".join(f"def {k} : ℚ := {lean_q(v)}" for k, v in pts.items())
    src = f"""import Programmes.ZeroPointClass.Basic

/-!
# N1 certificate data (generated by `results/proposal3/2026-10-26/N1/code/n1_make_lean.py`; do not edit)

Records `⟨lo, hi, a_c, qlo, qhi, dlo, dhi⟩` (see `Rec`): for every `a ∈ [lo, hi]` and `|t| ≤ t₀ = 10⁻⁸` the exact
second variation `F a t` of the zero-point energy along the shear path satisfies `F a t - (a - a_c) d ∈ [qlo, qhi]`
for some `d ∈ [dlo, dhi]` (Arb ball arithmetic, `n1_certify2.py`, Tier C-ball). The kernel checks by `decide` that
the intervals chain and that the corner bounds have the claimed signs.
-/

namespace ProgZeroPointClass

open Set

/-- Window half-width. -/
noncomputable def t0 : ℝ := 1 / 100000000

{defs}

{chr(10).join(lines)}
theorem chain_pos1 : chainFrom A0 aLm Lpos1 = true := by decide +kernel
theorem chain_neg : chainFrom aRm aLp Lneg = true := by decide +kernel
theorem chain_pos2 : chainFrom aRp A1 Lpos2 = true := by decide +kernel
theorem sign_pos1 : allPos Lpos1 = true := by decide +kernel
theorem sign_neg : allNeg Lneg = true := by decide +kernel
theorem sign_pos2 : allPos Lpos2 = true := by decide +kernel
theorem gaps_ordered : A0 < aLm ∧ aLm < aRm ∧ aRm < aLp ∧ aLp < aRp ∧ aRp < A1 := by decide +kernel

/-- **N1, the certified classification of the sign of the zero-point curvature (logic Tier A; the enclosure
hypotheses are Tier C-ball, the continuity in `a` Tier C-human).** `F a t` is the second `t`-derivative of the
zero-point energy along the shear path for the Gaussian `exp(-π a r²)`. Then: `F > 0` on `[A0, aLm] × [-t₀, t₀]`,
`F < 0` on `[aRm, aLp] × [-t₀, t₀]`, `F > 0` on `[aRp, A1] × [-t₀, t₀]`, `a ↦ F a 0` has a zero in each gap
`(aLm, aRm)`, `(aLp, aRp)`, and every zero of `a ↦ F a t` in `[A0, A1]` lies in one of the two gaps. -/
theorem classification (F : ℝ → ℝ → ℝ) (h1 : Encloses F t0 Lpos1) (h2 : Encloses F t0 Lneg)
    (h3 : Encloses F t0 Lpos2) (hcont : ContinuousOn (fun a => F a 0) (Icc (A0 : ℝ) (A1 : ℝ))) :
    (∀ a : ℝ, (A0 : ℝ) ≤ a → a ≤ (aLm : ℝ) → ∀ t : ℝ, |t| ≤ t0 → 0 < F a t) ∧
    (∀ a : ℝ, (aRm : ℝ) ≤ a → a ≤ (aLp : ℝ) → ∀ t : ℝ, |t| ≤ t0 → F a t < 0) ∧
    (∀ a : ℝ, (aRp : ℝ) ≤ a → a ≤ (A1 : ℝ) → ∀ t : ℝ, |t| ≤ t0 → 0 < F a t) ∧
    (∃ a ∈ Ioo (aLm : ℝ) (aRm : ℝ), F a 0 = 0) ∧ (∃ a ∈ Ioo (aLp : ℝ) (aRp : ℝ), F a 0 = 0) ∧
    (∀ a : ℝ, (A0 : ℝ) ≤ a → a ≤ (A1 : ℝ) → ∀ t : ℝ, |t| ≤ t0 → F a t = 0 →
      a ∈ Ioo (aLm : ℝ) (aRm : ℝ) ∪ Ioo (aLp : ℝ) (aRp : ℝ)) := by
  have ho := gaps_ordered
  have o1 : (A0 : ℝ) < aLm := by exact_mod_cast ho.1
  have o2 : (aLm : ℝ) < aRm := by exact_mod_cast ho.2.1
  have o3 : (aRm : ℝ) < aLp := by exact_mod_cast ho.2.2.1
  have o4 : (aLp : ℝ) < aRp := by exact_mod_cast ho.2.2.2.1
  have o5 : (aRp : ℝ) < A1 := by exact_mod_cast ho.2.2.2.2
  have t00 : |(0 : ℝ)| ≤ t0 := by rw [abs_zero]; norm_num [t0]
  have P1 : ∀ a : ℝ, (A0 : ℝ) ≤ a → a ≤ (aLm : ℝ) → ∀ t : ℝ, |t| ≤ t0 → 0 < F a t := by
    intro a ha hb t ht
    obtain ⟨c, hc, hF⟩ := pos_on_of_chain F t0 Lpos1 A0 aLm chain_pos1 sign_pos1 h1 a ha hb
    have : (0 : ℝ) < c := by exact_mod_cast hc
    linarith [hF t ht]
  have N : ∀ a : ℝ, (aRm : ℝ) ≤ a → a ≤ (aLp : ℝ) → ∀ t : ℝ, |t| ≤ t0 → F a t < 0 := by
    intro a ha hb t ht
    obtain ⟨c, hc, hF⟩ := neg_on_of_chain F t0 Lneg aRm aLp chain_neg sign_neg h2 a ha hb
    have : (c : ℝ) < 0 := by exact_mod_cast hc
    linarith [hF t ht]
  have P2 : ∀ a : ℝ, (aRp : ℝ) ≤ a → a ≤ (A1 : ℝ) → ∀ t : ℝ, |t| ≤ t0 → 0 < F a t := by
    intro a ha hb t ht
    obtain ⟨c, hc, hF⟩ := pos_on_of_chain F t0 Lpos2 aRp A1 chain_pos2 sign_pos2 h3 a ha hb
    have : (0 : ℝ) < c := by exact_mod_cast hc
    linarith [hF t ht]
  refine ⟨P1, N, P2, ?_, ?_, ?_⟩
  · exact root_in_gap (fun a => F a 0) o2 (hcont.mono (Icc_subset_Icc o1.le (by linarith)))
      (P1 _ o1.le le_rfl 0 t00) (N _ le_rfl o3.le 0 t00)
  · exact root_in_gap' (fun a => F a 0) o4 (hcont.mono (Icc_subset_Icc (by linarith) o5.le))
      (N _ o3.le le_rfl 0 t00) (P2 _ le_rfl o5.le 0 t00)
  · intro a ha hb t ht hz
    by_cases c1 : a ≤ (aLm : ℝ)
    · exact absurd hz (ne_of_gt (P1 a ha c1 t ht))
    by_cases c2 : a < (aRm : ℝ)
    · exact Or.inl ⟨lt_of_not_ge c1, c2⟩
    by_cases c3 : a ≤ (aLp : ℝ)
    · exact absurd hz (ne_of_lt (N a (le_of_not_gt c2) c3 t ht))
    by_cases c4 : a < (aRp : ℝ)
    · exact Or.inr ⟨lt_of_not_ge c3, c4⟩
    · exact absurd hz (ne_of_gt (P2 a (le_of_not_gt c4) hb t ht))

/-- **N1, along-path consequences (logic Tier A).** If, for each `a`, `t ↦ E a t` (the zero-point energy along the
shear path) has derivative `E' a` and second derivative `F a` on `[-t₀, t₀]` (Tier C-human: differentiation under
the Brillouin-zone integral) and is even in `t` (mirror symmetry, B2 §2.4), then on `[aRm, aLp]` the triangular point
is not a local minimum along the path and `E a t < E a 0` for `0 < t ≤ t₀`, while on `[A0, aLm]` and `[aRp, A1]`
it is a strict minimum along the path on `0 < |t| ≤ t₀`. -/
theorem along_path (E E' F : ℝ → ℝ → ℝ) (h1 : Encloses F t0 Lpos1) (h2 : Encloses F t0 Lneg)
    (h3 : Encloses F t0 Lpos2) (hcont : ContinuousOn (fun a => F a 0) (Icc (A0 : ℝ) (A1 : ℝ)))
    (hE : ∀ a : ℝ, (A0 : ℝ) ≤ a → a ≤ (A1 : ℝ) → ∀ t ∈ Icc (-t0) t0, HasDerivAt (E a) (E' a t) t)
    (hE' : ∀ a : ℝ, (A0 : ℝ) ≤ a → a ≤ (A1 : ℝ) → ∀ t ∈ Icc (-t0) t0, HasDerivAt (E' a) (F a t) t)
    (hsym : ∀ a t : ℝ, E a (-t) = E a t) :
    (∀ a : ℝ, (aRm : ℝ) ≤ a → a ≤ (aLp : ℝ) → ¬ IsLocalMin (E a) 0 ∧ ∀ t, 0 < t → t ≤ t0 → E a t < E a 0) ∧
    (∀ a : ℝ, ((A0 : ℝ) ≤ a ∧ a ≤ (aLm : ℝ)) ∨ ((aRp : ℝ) ≤ a ∧ a ≤ (A1 : ℝ)) →
      ∀ t, t ≠ 0 → |t| ≤ t0 → E a 0 < E a t) := by
  have ho := gaps_ordered
  have o1 : (A0 : ℝ) < aLm := by exact_mod_cast ho.1
  have o2 : (aLm : ℝ) < aRm := by exact_mod_cast ho.2.1
  have o3 : (aRm : ℝ) < aLp := by exact_mod_cast ho.2.2.1
  have o4 : (aLp : ℝ) < aRp := by exact_mod_cast ho.2.2.2.1
  have o5 : (aRp : ℝ) < A1 := by exact_mod_cast ho.2.2.2.2
  have ht0 : (0 : ℝ) < t0 := by norm_num [t0]
  have mem : ∀ t ∈ Icc (-t0) t0, |t| ≤ t0 := fun t ht => abs_le.2 ⟨ht.1, ht.2⟩
  refine ⟨?_, ?_⟩
  · intro a ha hb
    have hA0 : (A0 : ℝ) ≤ a := by linarith
    have hA1 : a ≤ (A1 : ℝ) := by linarith
    obtain ⟨c, hc, hF⟩ := neg_on_of_chain F t0 Lneg aRm aLp chain_neg sign_neg h2 a ha hb
    have hc' : (c : ℝ) < 0 := by exact_mod_cast hc
    exact not_localMin_of_curv_neg ht0 hc' (hE a hA0 hA1) (hE' a hA0 hA1) (fun t ht => hF t (mem t ht))
      (fun t => hsym a t)
  · intro a ha
    have hrange : (A0 : ℝ) ≤ a ∧ a ≤ (A1 : ℝ) := by
      rcases ha with ⟨p, q⟩ | ⟨p, q⟩
      · exact ⟨p, by linarith⟩
      · exact ⟨by linarith, q⟩
    obtain ⟨c, hc, hF⟩ : ∃ c : ℚ, 0 < c ∧ ∀ t : ℝ, |t| ≤ t0 → (c : ℝ) ≤ F a t := by
      rcases ha with ⟨p, q⟩ | ⟨p, q⟩
      · exact pos_on_of_chain F t0 Lpos1 A0 aLm chain_pos1 sign_pos1 h1 a p q
      · exact pos_on_of_chain F t0 Lpos2 aRp A1 chain_pos2 sign_pos2 h3 a p q
    have hc' : (0 : ℝ) < c := by exact_mod_cast hc
    exact strict_gt_of_curv_pos hc' (hE a hrange.1 hrange.2) (hE' a hrange.1 hrange.2)
      (fun t ht => hF t (mem t ht)) (fun t => hsym a t)

end ProgZeroPointClass

#print axioms ProgZeroPointClass.chain_pos1
#print axioms ProgZeroPointClass.chain_neg
#print axioms ProgZeroPointClass.chain_pos2
#print axioms ProgZeroPointClass.sign_pos1
#print axioms ProgZeroPointClass.sign_neg
#print axioms ProgZeroPointClass.sign_pos2
#print axioms ProgZeroPointClass.gaps_ordered
#print axioms ProgZeroPointClass.classification
#print axioms ProgZeroPointClass.along_path
"""
    open(out_lean, "w").write(src)
    summary = {k: str(v) for k, v in pts.items()}
    summary.update({k + "_float": float(v) for k, v in pts.items()})
    summary["segments"] = [{"sign": s["sign"], "lo": str(s["lo"]), "hi": str(s["hi"]), "n_records": len(s["recs"]),
                            "pieces": [{"lo": str(pc["lo"]), "hi": str(pc["hi"]),
                                        "F_bounds": [float(x) for x in piece_bounds(pc["run"], pc["lo"], pc["hi"])]}
                                       for pc in s["recs"]]} for s in segs]
    summary["runs"] = len(runs)
    summary["holes_between_runs"] = holes
    summary["all_segments"] = all_segs
    summary["dropped_segments"] = dropped
    summary["root_enclosures"] = {"a_minus": [str(aLm), str(aRm), float(aLm), float(aRm)],
                                  "a_plus": [str(aLp), str(aRp), float(aLp), float(aRp)]}
    json.dump(summary, open(out_sum, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
