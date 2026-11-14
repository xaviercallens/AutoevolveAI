"""Writes eye_review.json: the by-eye verdicts typed in during the review (data, not computation)."""

import json
from pathlib import Path

LANE = Path(__file__).resolve().parent
B = "Solution file OAI/Analysis/Brenier/Basic.lean imports only Mathlib (no OAI instances/notation visible); open lines identical on both sides; every renaming in the map is a binder on both sides (read)."
K = "Solution file OAI/Combinatorics/KServer/Basic.lean imports only Mathlib; context identical (open scoped BigOperators, universe u)."
N = "Textually identical; OAI/Analysis/Naimark/Basic.lean imports only Mathlib; context identical (universe u v w)."
O = "Textually identical; context identical; the OAI instances visible at the solution declaration (visible_instances.json) are all on OAI-local types (Coins, SwitchSamples, Tabloid, Shapes); none touches a type used here."
R = (
    "Textually identical. context_differs: the solution adds `open scoped InnerProductSpace CStarAlgebra` and `open ContinuousLinearMap`. No identifier here uses inner-product or C*-notation; "
    "mathlib_scan.json finds no ContinuousLinearMap.<ident> for any free identifier (1175 ContinuousLinearMap.* declarations extracted from 312 files, so the parser does see that namespace; a raw-text grep of decl lines inside `namespace ContinuousLinearMap` files for these identifiers also finds none; LeanMaster's Mathlib rev 85e3a25e, not upstream's pin d13f23b7); the only visible OAI instance line is a `local instance` in another file (not visible). Read as unable to change meaning."
)
S = (
    "Textually identical. context_differs: the solution is inside `noncomputable section`, adds non-scoped `open MeasureTheory TopologicalSpace Set` and `open MatrixAnalysis TensorMatrix`, and names its instance variables "
    "([contextInstance31_23 : Fintype R] vs anonymous [Fintype R]). The set of scoped opens is the same. Every free identifier resolves to the same OAI constant on both sides (eye_aid resolution_differences empty), "
    "and mathlib_scan finds no capture under MeasureTheory/Set/TopologicalSpace. The instance binder names change only binder names in the elaborated type; whether Comparator's type check is name-sensitive is a D2 question."
)
EYE = {
    "OAI.Problem358.E": ("MATCHES", B, True),
    "OAI.Problem358.uniformMeasure": ("MATCHES", B, True),
    "OAI.Problem358.IsSupported": (
        "EQUIVALENT_BY_READING",
        "Mechanical DIFFERS is a lexer artefact: `containerᶜ` vs `Yᶜ` were each lexed as one identifier (U+1D9C is in \\w), but Lean lexes `Y` followed by the postfix `ᶜ`. With container->Y (a bound renaming) the bodies are identical. " + B,
        True,
    ),
    "OAI.Problem358.IsCoupling": ("MATCHES", B, True),
    "OAI.Problem358.quadraticPlanCost": ("MATCHES", B, True),
    "OAI.Problem358.wasserstein2": ("MATCHES", B, True),
    "OAI.Problem358.graphPlan": ("MATCHES", B, True),
    "OAI.Problem358.IsQuadraticOptimalMap": ("MATCHES", B, True),
    "OAI.Problem358.IsUniqueQuadraticOptimalMap": ("MATCHES", B, True),
    "OAI.Problem358.mapL2Dist": ("MATCHES", B, True),
    "OAI.Problem358.cube": ("MATCHES", B, True),
    "OAI.Problem358.HasExactlyThreeAtoms": (
        "EQUIVALENT_BY_READING",
        "The only difference (eye_aid: 2 inserted tokens) is redundant parentheses: solution `(w i) • Measure.dirac (y i)` vs challenge `weights index • Measure.dirac (atoms index)`. Application binds tighter than •, so the parse is the same. " + B,
        True,
    ),
    "OAI.DefocusingNLS.sobolevProduct": (
        "SORRIED_IN_CHALLENGE",
        "Genuine hole. The challenge's `by sorry` sits only in the Memℓp membership proof (a Prop). The data part `fun n => (sobolevProductWeight k n : ℂ) * sobolevProductCoefficient k f g n` is token-identical to the solution's (up to _hk->hk), so by proof irrelevance the value would agree. The preregistration still treats SORRIED holes as unpinned. The solution proof uses sobolevProductMajorant and weighted_sobolevProduct_le_majorant, which do not exist in the challenge.",
        False,
    ),
    "OAI.DefocusingNLS.schrodingerFlow": (
        "EQUIVALENT_BY_READING",
        "All 7 differing spans (eye_aid) lie in proof fields: the Memℓp proof inside toFun (a tactic block vs `(lp.memℓp f).mono' (by intro n; simp)`) and the norm_map' tactic proof, plus the absorbed trailing `run_cmd` line (instrument defect). The data `fun n => schrodingerMultiplier t n * f n`, map_add' and map_smul' are token-identical. The differing fields are Prop-valued, so by reading the structures are definitionally equal (proof irrelevance). Not elaborated.",
        True,
    ),
    "OAI.DefocusingNLS.sobolevOddPower": (
        "EQUIVALENT_BY_READING",
        "The only difference is the column-0 `run_cmd Lean.modifyEnv ...` line after the challenge definition. The extractor wrongly absorbed it (run_cmd is missing from COMMAND_STARTS). The equation-compiler bodies are token-identical. Free identifiers (sobolevProduct, fourierConjugate, FourierL2) resolve to the same OAI constants.",
        True,
    ),
    "OAI.elementaryPositivityWitness": (
        "SORRIED_IN_CHALLENGE",
        "Genuine hole, `:= by sorry` (sorry-only). theorem_names is empty, so the challenge's whole claim is that the type `G.PermutationWitness` (a structure: theta plus an e-expansion of G.chromatic r over nondescent permutations) is inhabited for every natural unit interval graph. Comparator's type check is therefore the meaningful check: any inhabitant witnesses the claim, so the body cannot change what is certified. The solution builds it from Encodable.choose on exists_successful_table, using four FiniteSearch helpers that are not in the challenge. Flagged, not resolved.",
        False,
    ),
    "OAI.EuclideanFiveColor.ProperColoring": ("MATCHES", "Bodies identical up to colorCount->k, coloring->c, point->x, otherPoint->y (all binders). The solution file Coloring.lean imports only Mathlib; context identical (empty).", True),
    "OAI.KServer.Configuration": ("MATCHES", "Textually identical abbrev. " + K, True),
    "OAI.KServer.LabelDistribution": ("MATCHES", "Subtype binder probability->p and ∑ binder label->i. " + K, True),
    "OAI.KServer.Policy": ("MATCHES", "Textually identical abbrev. " + K, True),
    "OAI.KServer.serve": ("MATCHES", "Explicit binders label->i, request->r. " + K, True),
    "OAI.KServer.serviceCost": (
        "EQUIVALENT_BY_READING",
        "All 7 differing spans are bound renamings that the single-bijection rule rejects: the challenge uses `requests` both as the arrow binder `(requests : List X) →` (->σ) and as the match tail variable (->rs). Also labels->j and index->i. Read in full: `| request :: requests, labels => dist (s (labels 0)) request + serviceCost (serve s (labels 0) request) requests (fun index => labels index.succ)` is alpha-equivalent to `| r :: rs, j => dist (s (j 0)) r + serviceCost (serve s (j 0) r) rs (fun i => j i.succ)`. " + K,
        True,
    ),
    "OAI.KServer.pathProbability": (
        "EQUIVALENT_BY_READING",
        "Same cause as serviceCost (requests -> σ in the arrow binder and -> rs in the pattern; history->h, labels->j, index->i). `(A history request).val (labels 0) * pathProbability A (history ++ [(request, labels 0)]) requests (fun index => labels index.succ)` is alpha-equivalent to the solution's. " + K,
        True,
    ),
    "OAI.KServer.expectedCost": ("MATCHES", "requests->σ, labels->j (∑ binder). " + K, True),
    "OAI.KServer.optimalCost": ("MATCHES", "requests->σ. " + K, True),
    "OAI.KServer.MainStatement": (
        "MATCHES",
        "Bound renamings embedding->e, requests->σ. context_differs: the solution (Main.lean:123) adds `open Finset` and `open GlobalEndpoint FiniteMetricTransport`. The eye aid resolves the latter two under OAI.KServer, and no free identifier resolves differently (resolution_differences empty). mathlib_scan finds no Finset.<ident> (LeanMaster's Mathlib rev, not upstream's pin). All 207 instance/notation lines visible at Main.lean:123 (visible_instances.json) were triaged. 12 are `local`/`scoped instance` in other files, so they are not visible. 176 are `attribute [local instance] Classical.propDecidable/decEq` (or keyDecEq/poolDecEq). 174 of these are in other files and so not visible. Main.lean:12 is closed by `end KServer.FiniteMetricTransport` at line 82. The remaining global instances are all on OAI-local types (Inventory, LevelKeys.Tape, Alphabet, refresh, factorTest, absoluteTest, LabelDistribution, Vertex, Tree.Child, reset, Law). One same-file exception is active at the declaration: Main.lean:95 `attribute [local instance] Classical.propDecidable Classical.decEq`, inside `noncomputable section` / `namespace KServer`. MainStatement has no decidability-dependent subterm (no if/decide/filter), so by reading this instance does not enter the term. Not elaborated. This matches the earlier OPENAI_MATH_STUDY.md reading.",
        True,
    ),
    "OAI.NaimarkZFC.IsSimpleCStar": ("MATCHES", N, True),
    "OAI.NaimarkZFC.IsState": ("MATCHES", N, True),
    "OAI.NaimarkZFC.IsFaithfulTracialState": ("MATCHES", N, True),
    "OAI.NaimarkZFC.IsIrreducible": ("MATCHES", N, True),
    "OAI.NaimarkZFC.UnitarilyEquivalent": ("MATCHES", N, True),
    "OAI.NaimarkZFC.HasUniqueIrreducibleRepresentation": ("MATCHES", N, True),
    "OAI.NaimarkZFC.IsIsomorphicToCompacts": ("MATCHES", N, True),
    "OAI.CubeShuffle.UnitaryFinite.IsUnitary": ("MATCHES", "Textually identical; variable lines identical; the solution file imports only Mathlib.", True),
    "OAI.CubeShuffle.Specht.hilbertSpace": ("MATCHES", O, True),
    "OAI.CubeShuffle.Specht.unitaryRepresentation": ("MATCHES", O, True),
    "OAI.CubeShuffle.Specht.relabelledUnitary": ("MATCHES", O, True),
    "OAI.RowColumn.OccupiedOverlapEndpoint": ("MATCHES", "Read both sources side by side (challenge :237, solution RowColumn/Basic.lean:68): identical abbrev. " + O, True),
    "OAI.Rokhlin.timeMap": ("MATCHES", R, True),
    "OAI.Rokhlin.IsMixing": ("MATCHES", R, True),
    "OAI.Rokhlin.layoutTime": ("MATCHES", R, True),
    "OAI.Rokhlin.MixingOfOrder": ("MATCHES", R, True),
    "OAI.SpinAngle.TypeAngle.row": ("MATCHES", S, True),
    "OAI.SpinAngle.TypeAngle.column": ("MATCHES", S, True),
    "OAI.SpinAngle.TypeAngle.phi": ("MATCHES", S + " phi's missingCellProductFactor and missingInRow are non-hole constants with the same full name on both sides.", True),
}


def main() -> int:
    out = {k: {"verdict": v, "note": n, "meaning_pinned": p} for k, (v, n, p) in EYE.items()}
    (LANE / "eye_review.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
