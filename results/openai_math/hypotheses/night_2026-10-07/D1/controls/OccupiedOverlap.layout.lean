/- header /- nested -/ comment -/
import Mathlib

namespace OAI

namespace CubeShuffle.Specht

open scoped BigOperators Classical

abbrev Cell (μ : YoungDiagram) := {x : ℕ × ℕ // x ∈ μ.cells}
def row {μ : YoungDiagram} (x : Cell μ) : ℕ := x.1.1
def col {μ : YoungDiagram} (x : Cell μ) : ℕ := x.1.2

lemma row_lt_colLen {μ : YoungDiagram} (x : Cell μ) : row x < μ.colLen (col x) :=
    YoungDiagram.mem_iff_lt_colLen.mp x.2  -- control comment
noncomputable def rowIndex {μ : YoungDiagram} (x : Cell μ) : Fin (μ.colLen 0) :=
    ⟨row x, (row_lt_colLen x).trans_le (μ.colLen_anti 0 (col x) (Nat.zero_le _))⟩  -- control comment

abbrev Tabloid (μ : YoungDiagram) :=
    {f : Cell μ → Fin (μ.colLen 0) // ∃ p : Equiv.Perm (Cell μ), f = rowIndex ∘ p}  -- control comment

noncomputable instance (μ : YoungDiagram) : Fintype (Tabloid μ) := Fintype.ofFinite _

noncomputable def baseTabloid (μ : YoungDiagram) : Tabloid μ := ⟨rowIndex, 1, rfl⟩

noncomputable def tabloidAct {μ : YoungDiagram} (p : Equiv.Perm (Cell μ)) :
    Equiv.Perm (Tabloid μ) where  -- control comment
    toFun f := ⟨fun x => f.1 (p⁻¹ x), by  -- control comment
    obtain ⟨q,hq⟩ := f.2  -- control comment
    refine ⟨q*p⁻¹, ?_⟩  -- control comment
    funext x  -- control comment
    simp only [hq,Function.comp_apply,Equiv.Perm.mul_apply]⟩  -- control comment
    invFun f := ⟨fun x => f.1 (p x), by  -- control comment
    obtain ⟨q,hq⟩ := f.2  -- control comment
    refine ⟨q*p, ?_⟩  -- control comment
    funext x  -- control comment
    simp only [hq,Function.comp_apply,Equiv.Perm.mul_apply]⟩  -- control comment
    left_inv f := by apply Subtype.ext; funext x; simp  -- control comment
    right_inv f := by apply Subtype.ext; funext x; simp  -- control comment

@[simp] lemma tabloidAct_apply {μ : YoungDiagram} (p : Equiv.Perm (Cell μ))
    (f : Tabloid μ) (x : Cell μ) : (tabloidAct p f).1 x = f.1 (p⁻¹ x) := rfl  -- control comment

@[simp] lemma tabloidAct_one (μ : YoungDiagram) : tabloidAct (1 : Equiv.Perm (Cell μ)) = 1 := by
    ext f x  -- control comment
    rfl  -- control comment

@[simp] lemma tabloidAct_mul {μ : YoungDiagram} (p q : Equiv.Perm (Cell μ)) :
    tabloidAct (p*q) = tabloidAct p * tabloidAct q := by  -- control comment
    ext f x  -- control comment
    simp only [tabloidAct_apply, mul_inv_rev,Equiv.Perm.mul_apply]  -- control comment

@[simp] lemma tabloidAct_inv {μ : YoungDiagram} (p : Equiv.Perm (Cell μ)) :
    tabloidAct p⁻¹ = (tabloidAct p)⁻¹ := by  -- control comment
    ext f x  -- control comment
    simp [tabloidAct,Equiv.Perm.inv_def]  -- control comment

noncomputable def tabloidRep (μ : YoungDiagram) :
    Representation ℂ (Equiv.Perm (Cell μ)) (Tabloid μ → ℂ) where  -- control comment
    toFun p :=  -- control comment
    { toFun := fun v f => v (tabloidAct p⁻¹ f)  -- control comment
    map_add' := by intros; rfl  -- control comment
    map_smul' := by intros; rfl }  -- control comment
    map_one' := by ext v f; simp  -- control comment
    map_mul' p q := by  -- control comment
    ext v f  -- control comment
    simp only [mul_inv_rev,tabloidAct_mul,Equiv.Perm.mul_apply]  -- control comment
    rfl  -- control comment

@[simp] lemma tabloidRep_apply {μ : YoungDiagram} (p : Equiv.Perm (Cell μ))
    (v : Tabloid μ → ℂ) (f : Tabloid μ) : tabloidRep μ p v f = v (tabloidAct p⁻¹ f) := rfl  -- control comment

noncomputable def delta {μ : YoungDiagram} (f : Tabloid μ) : Tabloid μ → ℂ :=
    fun g => if g=f then 1 else 0  -- control comment

noncomputable def colGroup (μ : YoungDiagram) : Subgroup (Equiv.Perm (Cell μ)) where
    carrier := {p | ∀ x, col (p x) = col x}  -- control comment
    one_mem' := by intro x; rfl  -- control comment
    mul_mem' := by intro p q hp hq x; exact (hp (q x)).trans (hq x)  -- control comment
    inv_mem' := by intro p hp x; simpa using (hp (p⁻¹ x)).symm  -- control comment

noncomputable def permSign {α : Type*} [Fintype α] [DecidableEq α] (p : Equiv.Perm α) : ℂ :=
    ((Equiv.Perm.sign p : ℤ) : ℂ)  -- control comment
section Alternator
variable {α V : Type*} [Fintype α] [DecidableEq α] [AddCommGroup V] [Module ℂ V]

noncomputable def alternator (C : Subgroup (Equiv.Perm α))
    (ρ : Representation ℂ (Equiv.Perm α) V) : Module.End ℂ V := by  -- control comment
    classical  -- control comment
    exact ∑ c : C, permSign (c : Equiv.Perm α) • ρ c  -- control comment

end Alternator

noncomputable def polytabloid (μ : YoungDiagram) : Tabloid μ → ℂ :=
    alternator (colGroup μ) (tabloidRep μ) (delta (baseTabloid μ))  -- control comment

noncomputable def space (μ : YoungDiagram) : Submodule ℂ (Tabloid μ → ℂ) :=
    Submodule.span ℂ (Set.range (fun p : Equiv.Perm (Cell μ) => tabloidRep μ p (polytabloid μ)))  -- control comment

lemma orbit_mem_space (μ : YoungDiagram) (p : Equiv.Perm (Cell μ)) :
    tabloidRep μ p (polytabloid μ) ∈ space μ := Submodule.subset_span ⟨p,rfl⟩  -- control comment

lemma action_mem_space (μ : YoungDiagram) (p : Equiv.Perm (Cell μ))
    (v : Tabloid μ → ℂ) (hv : v ∈ space μ) : tabloidRep μ p v ∈ space μ := by  -- control comment
    induction hv using Submodule.span_induction with  -- control comment
    | mem v hv =>  -- control comment
    obtain ⟨q,rfl⟩ := hv  -- control comment
    change ((tabloidRep μ p)*(tabloidRep μ q)) (polytabloid μ) ∈ space μ  -- control comment
    rw [←map_mul]  -- control comment
    exact orbit_mem_space μ (p*q)  -- control comment
    | zero => simp  -- control comment
    | add v w hv hw ihv ihw => simpa using (space μ).add_mem ihv ihw  -- control comment
    | smul a v hv ih => simpa using (space μ).smul_mem a ih  -- control comment

noncomputable def subrepresentation (μ : YoungDiagram) : Subrepresentation (tabloidRep μ) :=
    ⟨space μ, fun p v hv => action_mem_space μ p v hv⟩  -- control comment

noncomputable def representation (μ : YoungDiagram) :
    Representation ℂ (Equiv.Perm (Cell μ)) (space μ) :=  -- control comment
    (subrepresentation μ).toRepresentation  -- control comment

end CubeShuffle.Specht

namespace CubeShuffle.PermutationHilbert

open scoped BigOperators ComplexConjugate Classical
open Complex

variable {X : Type*} [Fintype X]

abbrev H (X : Type*) [Fintype X] := EuclideanSpace ℂ X

end CubeShuffle.PermutationHilbert

namespace CubeShuffle.Specht

open scoped BigOperators Classical

noncomputable def hilbertEquiv (μ : YoungDiagram) :
    (Tabloid μ → ℂ) ≃ₗ[ℂ] PermutationHilbert.H (Tabloid μ) :=  -- control comment
    (WithLp.linearEquiv 2 ℂ (Tabloid μ → ℂ)).symm  -- control comment

noncomputable def hilbertSpace (μ : YoungDiagram) :
    Submodule ℂ (PermutationHilbert.H (Tabloid μ)) := (space μ).map (hilbertEquiv μ).toLinearMap  -- control comment

noncomputable def spaceHilbertEquiv (μ : YoungDiagram) : space μ ≃ₗ[ℂ] hilbertSpace μ :=
    (hilbertEquiv μ).submoduleMap (space μ)  -- control comment

noncomputable def unitaryRepresentation (μ : YoungDiagram) :
    Representation ℂ (Equiv.Perm (Cell μ)) (hilbertSpace μ) :=  -- control comment
    ((spaceHilbertEquiv μ).conjAlgEquiv ℂ).toMonoidHom.comp (representation μ)  -- control comment

variable {α ι : Type*} [Fintype α] [Fintype ι]

noncomputable def relabelledUnitary (μ : YoungDiagram) (e : α ≃ Cell μ) :
    Representation ℂ (Equiv.Perm α) (hilbertSpace μ) :=  -- control comment
    (unitaryRepresentation μ).comp e.permCongrHom.toMonoidHom  -- control comment

end CubeShuffle.Specht

namespace CubeShuffle.UnitaryFinite

open scoped BigOperators ComplexConjugate Classical

variable {G : Type*} [Group G] [Fintype G]
variable {V W : Type*} [NormedAddCommGroup V] [InnerProductSpace ℂ V]
    [FiniteDimensional ℂ V] [NormedAddCommGroup W] [InnerProductSpace ℂ W]  -- control comment
    [FiniteDimensional ℂ W]  -- control comment

def IsUnitary (ρ : Representation ℂ G V) : Prop :=
    ∀ g v w, inner ℂ (ρ g v) (ρ g w) = inner ℂ v w  -- control comment

end CubeShuffle.UnitaryFinite

noncomputable section

open scoped BigOperators Classical

namespace RowColumn
open CubeShuffle CubeShuffle.Specht CubeShuffle.UnitaryFinite

/-- Permutations preserving each fibre of a given line map. -/
def lineGroup {α β : Type*} (f : α → β) : Subgroup (Equiv.Perm α) where
    carrier := {g | ∀ x, f (g x) = f x}  -- control comment
    one_mem' := by intro x; rfl  -- control comment
    mul_mem' := by  -- control comment
    intro a b ha hb x  -- control comment
    exact (ha (b x)).trans (hb x)  -- control comment
    inv_mem' := by  -- control comment
    intro a ha x  -- control comment
    simpa using (ha (a⁻¹ x)).symm  -- control comment

abbrev Board (m n : ℕ) := Fin m × Fin n
abbrev rowGroup {m n : ℕ} (Ω : Finset (Board m n)) :=
    lineGroup (fun x : Ω => x.1.1)  -- control comment
abbrev columnGroup {m n : ℕ} (Ω : Finset (Board m n)) :=
    lineGroup (fun x : Ω => x.1.2)  -- control comment

/-- Zero-based form of the manuscript's (h,h)-hook. -/
def InHook (a : YoungDiagram) (h : ℕ) : Prop :=
    ∀ c ∈ a.cells, c.1 < h ∨ c.2 < h  -- control comment

section Copies
variable {G V W : Type*} [Group G]
    [NormedAddCommGroup V] [InnerProductSpace ℂ V] [FiniteDimensional ℂ V]  -- control comment
    [NormedAddCommGroup W] [InnerProductSpace ℂ W] [FiniteDimensional ℂ W]  -- control comment

/-- An actual equivariant inclusion, not an unspecified overlap matrix. -/
def Intertwines (ρ : Representation ℂ G V) (τ : Representation ℂ G W)
    (I : V →ₗ[ℂ] W) : Prop :=  -- control comment
    ∀ g v, I (ρ g v) = τ g (I v)  -- control comment

/-- All orthogonal multiplicity copies of one irreducible type. The completeness
condition quantifies over genuine intertwiners, i.e. it is exactly the isotypic
space condition. -/
def CompleteCopies (ρ : Representation ℂ G V) (τ : Representation ℂ G W)
    {u : ℕ} (I : Fin u → V →ₗᵢ[ℂ] W) : Prop :=  -- control comment
    (∀ i, Intertwines ρ τ (I i).toLinearMap) ∧  -- control comment
    (∀ i j, i ≠ j → ∀ v w, inner ℂ (I i v) (I j w) = 0) ∧  -- control comment
    ∀ J : V →ₗ[ℂ] W, Intertwines ρ τ J →  -- control comment
    LinearMap.range J ≤ ⨆ i, LinearMap.range (I i).toLinearMap  -- control comment

end Copies

/-- The all-copy operator-overlap sum, with each squared operator norm. -/
def allCopyOverlap {V W X : Type*}
    [NormedAddCommGroup V] [InnerProductSpace ℂ V] [FiniteDimensional ℂ V]  -- control comment
    [NormedAddCommGroup W] [InnerProductSpace ℂ W] [FiniteDimensional ℂ W]  -- control comment
    [NormedAddCommGroup X] [InnerProductSpace ℂ X] [FiniteDimensional ℂ X]  -- control comment
    {u v : ℕ} (I : Fin u → V →ₗᵢ[ℂ] X) (J : Fin v → W →ₗᵢ[ℂ] X) : ℝ :=  -- control comment
    ∑ i, ∑ j, ‖((I i).toContinuousLinearMap.adjoint).comp  -- control comment
    (J j).toContinuousLinearMap‖ ^ 2  -- control comment

/-- Exact occupied-board main. Carriers are in orthonormal coordinates; arbitrary
unitary irreducibles of the two actual line groups are quantified over (equivalently,
the tuples of line partitions in the manuscript). Labelling `e` chooses the action
of the Specht module on the occupied cells and forces |a| = |Ω|. -/
abbrev OccupiedOverlapEndpoint : Prop :=
    ∃ C : ℝ, 0 < C ∧ ∀ (m n : ℕ) (Ω : Finset (Board m n))  -- control comment
    (a : YoungDiagram) (e : Ω ≃ Cell a) (h : ℕ),  -- control comment
    1 ≤ h → h ≤ m * n → InHook a h →  -- control comment
    ∀ (r c u v : ℕ)  -- control comment
    (ρ : Representation ℂ (rowGroup Ω) (EuclideanSpace ℂ (Fin r)))  -- control comment
    (τ : Representation ℂ (columnGroup Ω) (EuclideanSpace ℂ (Fin c))),  -- control comment
    Representation.IsIrreducible ρ → Representation.IsIrreducible τ →  -- control comment
    IsUnitary ρ → IsUnitary τ →  -- control comment
    ∀ (I : Fin u → EuclideanSpace ℂ (Fin r) →ₗᵢ[ℂ] hilbertSpace a)  -- control comment
    (J : Fin v → EuclideanSpace ℂ (Fin c) →ₗᵢ[ℂ] hilbertSpace a),  -- control comment
    CompleteCopies (V := EuclideanSpace ℂ (Fin r)) (W := hilbertSpace a) ρ ((relabelledUnitary a e).comp (rowGroup Ω).subtype) I →  -- control comment
    CompleteCopies (V := EuclideanSpace ℂ (Fin c)) (W := hilbertSpace a) τ ((relabelledUnitary a e).comp (columnGroup Ω).subtype) J →  -- control comment
    allCopyOverlap (V := EuclideanSpace ℂ (Fin r)) (W := EuclideanSpace ℂ (Fin c))  -- control comment
    (X := hilbertSpace a) I J ≤  -- control comment
    Real.exp (C * (((m + n + 1 : ℕ) : ℝ) * (h : ℝ)^2 *  -- control comment
    Real.log ((m * n : ℕ) + 2) + (m * n - Ω.card : ℕ))) *  -- control comment
    min 1 ((r : ℝ) * c / Module.finrank ℂ (space a))  -- control comment

end RowColumn

end

theorem RowColumn.occupied_overlap_endpoint : RowColumn.OccupiedOverlapEndpoint := by
    sorry  -- control comment

theorem RowColumn.occupied_overlap : RowColumn.OccupiedOverlapEndpoint := by
    sorry  -- control comment

end OAI
