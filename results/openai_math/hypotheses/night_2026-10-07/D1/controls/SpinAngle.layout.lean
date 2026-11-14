/- header /- nested -/ comment -/
import Mathlib

namespace OAI

noncomputable section

open scoped BigOperators ComplexConjugate InnerProductSpace Matrix TensorProduct

open scoped Matrix.Norms.L2Operator MatrixOrder ComplexOrder

namespace SpinAngle.Specht

variable {G : Type*} [Group G]
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]

def cyclic (ρ : Representation ℂ G E) (e : E) : Subrepresentation ρ where
    toSubmodule := Submodule.span ℂ (Set.range fun g => ρ g e)  -- control comment
    apply_mem_toSubmodule g := by  -- control comment
    intro v hv  -- control comment
    induction hv using Submodule.span_induction with  -- control comment
    | mem v hv =>  -- control comment
    obtain ⟨h, rfl⟩ := hv  -- control comment
    exact Submodule.subset_span ⟨g * h, by simp⟩  -- control comment
    | zero => simp  -- control comment
    | add x y hx hy ihx ihy =>  -- control comment
    simpa using (Submodule.span ℂ (Set.range fun h => ρ h e)).add_mem ihx ihy  -- control comment
    | smul a x hx ih =>  -- control comment
    simpa using (Submodule.span ℂ (Set.range fun h => ρ h e)).smul_mem a ih  -- control comment

end SpinAngle.Specht

namespace SpinAngle.TensorRep
variable {ι n : Type*} [Fintype ι] [DecidableEq ι] [Fintype n] [DecidableEq n]

def tensor (a : ι → Matrix n n ℂ) : Matrix (ι → n) (ι → n) ℂ :=
    fun x y => ∏ i, a i (x i) (y i)  -- control comment

lemma tensor_mul
    {ι : Type*} {n : Type*}  -- control comment
    [Fintype ι]  -- control comment
    [DecidableEq ι]  -- control comment
    [Fintype n]  -- control comment
    [DecidableEq n] (a b : ι → Matrix n n ℂ) :  -- control comment
    tensor (fun i => a i * b i) = tensor a * tensor b := by  -- control comment
    ext x y  -- control comment
    simp only [tensor, Matrix.mul_apply, ← Finset.prod_mul_distrib]  -- control comment
    symm  -- control comment
    simpa using (Finset.sum_prod_piFinset (ι := ι) Finset.univ  -- control comment
    (fun i j => a i (x i) j * b i j (y i)))  -- control comment

lemma tensor_one
    {ι : Type*} {n : Type*}  -- control comment
    [Fintype ι]  -- control comment
    [DecidableEq ι]  -- control comment
    [Fintype n]  -- control comment
    [DecidableEq n] : tensor (fun _ : ι => (1 : Matrix n n ℂ)) = 1 := by  -- control comment
    ext x y  -- control comment
    classical  -- control comment
    by_cases h : x = y  -- control comment
    · subst y  -- control comment
    simp [tensor]  -- control comment
    · obtain ⟨i, hi⟩ := Function.ne_iff.mp h  -- control comment
    simp only [tensor, Matrix.one_apply, ite_eq_right h]  -- control comment
    apply Finset.prod_eq_zero (Finset.mem_univ i)  -- control comment
    simp [hi]  -- control comment

lemma toEuclideanLin_mul
    {ι : Type*} {n : Type*}  -- control comment
    [Fintype ι]  -- control comment
    [DecidableEq ι]  -- control comment
    [Fintype n]  -- control comment
    [DecidableEq n] (a b : Matrix n n ℂ) :  -- control comment
    Matrix.toEuclideanLin (a * b) =  -- control comment
    Matrix.toEuclideanLin a * Matrix.toEuclideanLin b := by  -- control comment
    ext v x  -- control comment
    change ((a * b) *ᵥ (WithLp.ofLp v)) x = (a *ᵥ (b *ᵥ (WithLp.ofLp v))) x  -- control comment
    rw [Matrix.mulVec_mulVec]  -- control comment

lemma toEuclideanLin_one
    {ι : Type*} {n : Type*}  -- control comment
    [Fintype ι]  -- control comment
    [DecidableEq ι]  -- control comment
    [Fintype n]  -- control comment
    [DecidableEq n] : Matrix.toEuclideanLin (1 : Matrix n n ℂ) = 1 := by  -- control comment
    ext v x  -- control comment
    change ((1 : Matrix n n ℂ) *ᵥ (WithLp.ofLp v)) x = v x  -- control comment
    simp  -- control comment

def action : Matrix n n ℂ →* Module.End ℂ (EuclideanSpace ℂ (ι → n)) where
    toFun a := Matrix.toEuclideanLin (tensor (fun _ : ι => a))  -- control comment
    map_one' := by rw [tensor_one, toEuclideanLin_one (ι := ι)]  -- control comment
    map_mul' a b := by rw [tensor_mul, toEuclideanLin_mul (ι := ι)]  -- control comment

def rep : Representation ℂ (Matrix.unitaryGroup n ℂ) (EuclideanSpace ℂ (ι → n)) :=
    action.comp (Matrix.unitaryGroup n ℂ).subtype  -- control comment

lemma tensor_reindex
    {ι : Type*} {n : Type*}  -- control comment
    [Fintype ι]  -- control comment
    [DecidableEq ι]  -- control comment
    [Fintype n]  -- control comment
    [DecidableEq n] (a : Matrix n n ℂ) (σ : Equiv.Perm ι) (x y : ι → n) :  -- control comment
    tensor (fun _ : ι => a) (x ∘ σ) (y ∘ σ) = tensor (fun _ : ι => a) x y := by  -- control comment
    exact Equiv.prod_comp σ (fun i => a (x i) (y i))  -- control comment

end SpinAngle.TensorRep

namespace SpinAngle.Specht
open scoped Classical
variable {G : Type*} [Group G]
namespace PermutationSpace
open scoped Classical

variable {X : Type*} [Fintype X] [MulAction G X]

def rep : Representation ℂ G (EuclideanSpace ℂ X) where
    toFun g := {  -- control comment
    toFun v := WithLp.toLp 2 (fun x => v (g⁻¹ • x))  -- control comment
    map_add' := by intro v w; rfl  -- control comment
    map_smul' := by intro a v; rfl }  -- control comment
    map_one' := by ext v x; simp  -- control comment
    map_mul' := by  -- control comment
    intro g h  -- control comment
    ext v x  -- control comment
    change v ((g * h)⁻¹ • x) = v (h⁻¹ • g⁻¹ • x)  -- control comment
    simp [mul_smul]  -- control comment

variable {H : Type*} [Group H] [Fintype H]

def alternator (ι : H →* G) (χ : H →* ℂ) : Module.End ℂ (EuclideanSpace ℂ X) :=
    ∑ h, χ h • rep (ι h)  -- control comment

omit [Fintype X] in
lemma alternator_apply (ι : H →* G) (χ : H →* ℂ) (v : EuclideanSpace ℂ X) :
    alternator ι χ v = ∑ h, χ h • rep (ι h) v := by  -- control comment
    simp [alternator, LinearMap.sum_apply]  -- control comment

lemma rep_alternator
    {G : Type*} {H : Type*} {X : Type*}  -- control comment
    [Group G]  -- control comment
    [Group H]  -- control comment
    [Fintype H]  -- control comment
    [Fintype X]  -- control comment
    [MulAction G X] (ι : H →* G) (χ : H →* ℂ) (a : H)  -- control comment
    (v : EuclideanSpace ℂ X) :  -- control comment
    rep (ι a) (alternator ι χ v) = χ a⁻¹ • alternator ι χ v := by  -- control comment
    rw [alternator_apply, map_sum, Finset.smul_sum]  -- control comment
    have he := Equiv.sum_comp (Equiv.mulLeft a)  -- control comment
    (fun h => χ a⁻¹ • (χ h • (rep (ι h) v : EuclideanSpace ℂ X)))  -- control comment
    rw [← he]  -- control comment
    apply Finset.sum_congr rfl  -- control comment
    intro h _  -- control comment
    simp only [Equiv.coe_mulLeft, smul_smul, map_mul, map_smul]  -- control comment
    rw [show χ a⁻¹ * (χ a * χ h) = χ h by  -- control comment
    rw [← mul_assoc, ← map_mul, inv_mul_cancel, map_one, one_mul]]  -- control comment
    rfl  -- control comment

end PermutationSpace

variable {α : Type*} [Fintype α]

def complexSign : Equiv.Perm α →* ℂ where
    toFun g := ((Equiv.Perm.sign g : ℤˣ) : ℤ)  -- control comment
    map_one' := by simp  -- control comment
    map_mul' := by intro g h; simp  -- control comment

@[simp] lemma complexSign_inv (g : Equiv.Perm α) : complexSign g⁻¹ = complexSign g := by
    simp [complexSign]  -- control comment

end SpinAngle.Specht

namespace SpinAngle.Young

abbrev Cells (D : YoungDiagram) := {p : ℕ × ℕ // p ∈ D.cells}

end SpinAngle.Young

namespace SpinAngle.PolynomialCarrier
open scoped Classical Matrix
open SpinAngle.Specht SpinAngle.Young
variable {ι n : Type*} [Fintype ι] [DecidableEq ι] [Fintype n] [DecidableEq n]

instance coloringAction : MulAction (Equiv.Perm ι) (ι → n) where
    smul g x := x ∘ g.symm  -- control comment
    one_smul _ := rfl  -- control comment
    mul_smul _ _ _ := rfl  -- control comment

def reindex (g : Equiv.Perm ι) : (ι → n) ≃ (ι → n) where
    toFun x := x ∘ g  -- control comment
    invFun x := x ∘ g.symm  -- control comment
    left_inv x := by funext i; simp  -- control comment
    right_inv x := by funext i; simp  -- control comment

lemma action_site_commute (a : Matrix n n ℂ) (g : Equiv.Perm ι)
    (v : EuclideanSpace ℂ (ι → n)) :  -- control comment
    TensorRep.action a (PermutationSpace.rep g v) =  -- control comment
    PermutationSpace.rep g (TensorRep.action a v) := by  -- control comment
    ext x  -- control comment
    change (∑ y, TensorRep.tensor (fun _ : ι => a) x y * v (y ∘ g)) =  -- control comment
    ∑ y, TensorRep.tensor (fun _ : ι => a) (x ∘ g) y * v y  -- control comment
    rw [← Equiv.sum_comp (reindex (n := n) g)  -- control comment
    (fun y => TensorRep.tensor (fun _ : ι => a) (x ∘ g) y * v y)]  -- control comment
    apply Finset.sum_congr rfl  -- control comment
    intro y _  -- control comment
    change _ = TensorRep.tensor (fun _ : ι => a) (x ∘ g) (y ∘ g) * v (y ∘ g)  -- control comment
    rw [TensorRep.tensor_reindex]  -- control comment

def columnGroup (D : YoungDiagram) : Subgroup (Equiv.Perm (Cells D)) where
    carrier := {g | ∀ x, (g x).val.2 = x.val.2}  -- control comment
    one_mem' := fun _ => rfl  -- control comment
    mul_mem' := by intro g h hg hh x; exact (hg (h x)).trans (hh x)  -- control comment
    inv_mem' := by  -- control comment
    intro g hg x  -- control comment
    simpa using (hg (g⁻¹ x)).symm  -- control comment

variable (D : YoungDiagram) (q : ℕ)
abbrev TensorSpace := EuclideanSpace ℂ (Cells D → Fin q)

def alternating : Subrepresentation (TensorRep.rep (ι := Cells D) (n := Fin q)) where
    toSubmodule := {  -- control comment
    carrier := {v | ∀ g : columnGroup D,  -- control comment
    PermutationSpace.rep (g : Equiv.Perm (Cells D)) v = complexSign g.val • v}  -- control comment
    zero_mem' := by intro g; simp  -- control comment
    add_mem' := by intro x y hx hy g; simp [map_add, hx g, hy g, smul_add]  -- control comment
    smul_mem' := by intro c x hx g; simp [map_smul, hx g, smul_comm c] }  -- control comment
    apply_mem_toSubmodule a := by  -- control comment
    intro v hv g  -- control comment
    change PermutationSpace.rep g.val (TensorRep.action (a : Matrix (Fin q) (Fin q) ℂ) v) = _  -- control comment
    rw [← action_site_commute, hv g, map_smul]  -- control comment
    rfl  -- control comment

variable (hq : D.colLen 0 ≤ q)

def rowColor : Cells D → Fin q := fun x => ⟨x.val.1, by
    have hm := D.up_left_mem le_rfl (Nat.zero_le x.val.2) x.property  -- control comment
    have hl := YoungDiagram.mem_iff_lt_colLen.mp hm  -- control comment
    exact lt_of_lt_of_le hl hq⟩  -- control comment

def highest : TensorSpace D q := by
    classical  -- control comment
    exact PermutationSpace.alternator (columnGroup D).subtype  -- control comment
    (complexSign.comp (columnGroup D).subtype)  -- control comment
    (EuclideanSpace.single (rowColor D q hq) (1 : ℂ))  -- control comment

lemma highest_mem : highest D q hq ∈ alternating D q := by
    classical  -- control comment
    intro g  -- control comment
    change PermutationSpace.rep g.val (PermutationSpace.alternator _ _ _) = _  -- control comment
    have hh := PermutationSpace.rep_alternator (columnGroup D).subtype  -- control comment
    (complexSign.comp (columnGroup D).subtype) g (EuclideanSpace.single (rowColor D q hq) (1 : ℂ))  -- control comment
    change PermutationSpace.rep g.val (highest D q hq) = complexSign (g.val⁻¹) • highest D q hq at hh  -- control comment
    rw [complexSign_inv] at hh  -- control comment
    exact hh  -- control comment

def ordinary : Subrepresentation (alternating D q).toRepresentation :=
    cyclic (alternating D q).toRepresentation  -- control comment
    (⟨highest D q hq, highest_mem D q hq⟩ : (alternating D q).toSubmodule)  -- control comment

abbrev Carrier : Type := (ordinary D q hq).toSubmodule

instance carrierInner : InnerProductSpace ℂ (Carrier D q hq) :=
    @Submodule.innerProductSpace ℂ (alternating D q).toSubmodule _ _ inferInstance  -- control comment
    (ordinary D q hq).toSubmodule  -- control comment

end SpinAngle.PolynomialCarrier

namespace SpinAngle.ExternalTensor
open Module
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    [NormedAddCommGroup F] [InnerProductSpace ℂ F]  -- control comment
    [FiniteDimensional ℂ E] [FiniteDimensional ℂ F]  -- control comment
variable {G H : Type*} [Group G] [Group H]

def rep (ρ : Representation ℂ G E) (σ : Representation ℂ H F) :
    Representation ℂ (G × H) (E ⊗[ℂ] F) :=  -- control comment
    Representation.tprod (ρ.comp (MonoidHom.fst G H)) (σ.comp (MonoidHom.snd G H))  -- control comment

end SpinAngle.ExternalTensor

namespace SpinAngle.SignedTensor
open scoped Classical Matrix TensorProduct InnerProductSpace
open Module
variable {q : ℕ}
abbrev Spin (q : ℕ) := Fin q × Bool
abbrev Mat (q : ℕ) := Matrix (Fin q) (Fin q) ℂ
abbrev Group (q : ℕ) := Matrix.unitaryGroup (Fin q) ℂ × Matrix.unitaryGroup (Fin q) ℂ

def block : (Mat q × Mat q) →* Matrix (Spin q) (Spin q) ℂ where
    toFun a := Matrix.blockDiagonal (fun b : Bool => cond b a.2 a.1)  -- control comment
    map_one' := by  -- control comment
    convert (Matrix.blockDiagonal_one (m := Fin q) (o := Bool) (α := ℂ)) using 1  -- control comment
    congr 1  -- control comment
    funext b  -- control comment
    cases b <;> rfl  -- control comment
    map_mul' a b := by  -- control comment
    rw [← Matrix.blockDiagonal_mul]  -- control comment
    congr 1  -- control comment
    funext c  -- control comment
    cases c <;> rfl  -- control comment

lemma block_star (a : Mat q × Mat q) : block (star a) = star (block a) := by
    change Matrix.blockDiagonal (fun b : Bool => cond b (star a.2) (star a.1)) = (Matrix.blockDiagonal (fun b : Bool => cond b a.2 a.1))ᴴ  -- control comment
    rw [Matrix.blockDiagonal_conjTranspose]  -- control comment
    congr 1  -- control comment
    funext b  -- control comment
    cases b <;> rfl  -- control comment

def blockGroup : Group q →* Matrix.unitaryGroup (Spin q) ℂ where
    toFun g := ⟨block (g.1.val,g.2.val), by  -- control comment
    rw [Matrix.mem_unitaryGroup_iff', ← block_star, ← map_mul]  -- control comment
    have he : star (g.1.val,g.2.val) * (g.1.val,g.2.val) = 1 :=  -- control comment
    Prod.ext g.1.property.1 g.2.property.1  -- control comment
    rw [he, map_one]⟩  -- control comment
    map_one' := by  -- control comment
    apply Subtype.ext  -- control comment
    change block (1 : Mat q × Mat q) = 1  -- control comment
    exact block.map_one  -- control comment
    map_mul' g h := by  -- control comment
    apply Subtype.ext  -- control comment
    change block ((g.1.val,g.2.val) * (h.1.val,h.2.val)) =  -- control comment
    block (g.1.val,g.2.val) * block (h.1.val,h.2.val)  -- control comment
    exact block.map_mul _ _  -- control comment

variable {ι κ τ : Type*} [Fintype ι] [DecidableEq ι] [Fintype κ] [DecidableEq κ]
    [Fintype τ] [DecidableEq τ]  -- control comment

abbrev Raw := EuclideanSpace ℂ (τ → Spin q)

def rep : Representation ℂ (Group q) (Raw (q := q) (τ := τ)) :=
    (TensorRep.rep (ι := τ)).comp blockGroup  -- control comment

end SpinAngle.SignedTensor

namespace SpinAngle.EntropyMonomial
variable {ι : Type*} [Fintype ι]

def entropy (n : ι → ℕ) : ℝ :=
    (∑ i, n i : ℕ) * Real.log (∑ i, n i : ℕ) - ∑ i, (n i : ℝ) * Real.log (n i)  -- control comment

end SpinAngle.EntropyMonomial

namespace SpinAngle.Isotypic
variable {G : Type*} [Group G]
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    [NormedAddCommGroup F] [InnerProductSpace ℂ F]  -- control comment
    [FiniteDimensional ℂ E] [FiniteDimensional ℂ F]  -- control comment
variable (ρ : Representation ℂ G E) (σ : Representation ℂ G F)

def space : Subrepresentation σ where
    toSubmodule := Submodule.span ℂ (Set.range fun z : ρ.IntertwiningMap σ × E => z.1 z.2)  -- control comment
    apply_mem_toSubmodule := by  -- control comment
    intro g v hv  -- control comment
    induction hv using Submodule.span_induction with  -- control comment
    | mem v hv =>  -- control comment
    obtain ⟨⟨f,x⟩,rfl⟩ := hv  -- control comment
    apply Submodule.subset_span  -- control comment
    refine ⟨⟨f,ρ g x⟩, ?_⟩  -- control comment
    exact Representation.IntertwiningMap.isIntertwining ρ σ f g x  -- control comment
    | zero => simp  -- control comment
    | add x y hx hy ihx ihy => simpa only [map_add] using Submodule.add_mem _ ihx ihy  -- control comment
    | smul a x hx ih => simpa only [map_smul] using Submodule.smul_mem _ a ih  -- control comment

def projection : F →L[ℂ] F := (space ρ σ).toSubmodule.starProjection

end SpinAngle.Isotypic

namespace SpinAngle.SignedCarrier
open scoped Classical TensorProduct InnerProductSpace
open SpinAngle.Young SpinAngle.Specht PolynomialCarrier Module SignedTensor
variable (a b : YoungDiagram) (q : ℕ) (ha : a.colLen 0 ≤ q) (hb : b.colLen 0 ≤ q)

abbrev Carrier := PolynomialCarrier.Carrier a q ha ⊗[ℂ] PolynomialCarrier.Carrier b q hb

instance carrierNormed : NormedAddCommGroup (Carrier a b q ha hb) :=
    TensorProduct.instNormedAddCommGroup (𝕜 := ℂ)  -- control comment
    (E := PolynomialCarrier.Carrier a q ha) (F := PolynomialCarrier.Carrier b q hb)  -- control comment

instance carrierInner : InnerProductSpace ℂ (Carrier a b q ha hb) :=
    TensorProduct.instInnerProductSpace (𝕜 := ℂ)  -- control comment
    (E := PolynomialCarrier.Carrier a q ha) (F := PolynomialCarrier.Carrier b q hb)  -- control comment

instance carrierFinite : FiniteDimensional ℂ (Carrier a b q ha hb) :=
    inferInstanceAs (FiniteDimensional ℂ (PolynomialCarrier.Carrier a q ha ⊗[ℂ] PolynomialCarrier.Carrier b q hb))  -- control comment

abbrev rep : Representation ℂ (Group q) (Carrier a b q ha hb) :=
    ExternalTensor.rep (E := PolynomialCarrier.Carrier a q ha)  -- control comment
    (F := PolynomialCarrier.Carrier b q hb)  -- control comment
    (ordinary a q ha).toRepresentation (ordinary b q hb).toRepresentation  -- control comment

def parts : Fin q ⊕ Fin q → ℕ := Sum.elim (fun i => a.rowLen i) (fun i => b.rowLen i)
def entropy : ℝ := EntropyMonomial.entropy (parts a b q)
def dimension : ℕ := Module.finrank ℂ (Carrier a b q ha hb)

variable {τ : Type*} [Fintype τ] [DecidableEq τ]

abbrev typeProjection : Raw (q := q) (τ := τ) →L[ℂ] Raw (q := q) (τ := τ) :=
    Isotypic.projection (rep a b q ha hb) SignedTensor.rep  -- control comment

def matrixProjection : Matrix (τ → Spin q) (τ → Spin q) ℂ :=
    (Matrix.toEuclideanCLM (n := τ → Spin q) (𝕜 := ℂ)).symm (typeProjection a b q ha hb)  -- control comment

end SpinAngle.SignedCarrier

namespace SpinAngle

def missingCellFactor (m b : ℕ) : ℝ :=
    if b < m then ((m : ℝ) / (m - b : ℕ)) ^ (m - b) else 1  -- control comment

def missingCellProductFactor {ι : Type*} [Fintype ι] (m : ℕ) (b : ι → ℕ) : ℝ :=
    ∏ i, missingCellFactor m (b i)  -- control comment

variable {R C : Type*} [Fintype R] [DecidableEq R] [Fintype C] [DecidableEq C]

def occupiedRow (W : Finset (R × C)) (i : R) : Finset C :=
    Finset.univ.filter (fun j => (i, j) ∈ W)  -- control comment

def missingInRow (W : Finset (R × C)) (i : R) : ℕ :=
    Fintype.card C - (occupiedRow W i).card  -- control comment

end SpinAngle

namespace SpinAngle.DependentTensor
variable {ι : Type*} [Fintype ι] [DecidableEq ι]
variable {ν : ι → Type*} [∀ i, Fintype (ν i)] [∀ i, DecidableEq (ν i)]

abbrev Mat (n : Type*) := Matrix n n ℂ

def tensor (A : ∀ i, Mat (ν i)) : Mat (∀ i, ν i) := fun x y => ∏ i, A i (x i) (y i)

end SpinAngle.DependentTensor

namespace SpinAngle.BlockTensor
open DependentTensor
variable {τ J n : Type*} [Fintype τ] [DecidableEq τ] [Fintype J] [DecidableEq J]
    [Fintype n] [DecidableEq n]  -- control comment
variable (f : τ → J)

abbrev Fiber (j : J) := {i : τ // f i = j}

def splitEquiv : (τ → n) ≃ (∀ j : J, Fiber f j → n) where
    toFun x j i := x i.val  -- control comment
    invFun y i := y (f i) ⟨i,rfl⟩  -- control comment
    left_inv x := rfl  -- control comment
    right_inv y := by  -- control comment
    funext j i  -- control comment
    rcases i with ⟨i,hi⟩  -- control comment
    subst j  -- control comment
    rfl  -- control comment

def tensor (A : ∀ j, Mat (Fiber f j → n)) : Mat (τ → n) :=
    fun x y => DependentTensor.tensor A (splitEquiv f x) (splitEquiv f y)  -- control comment

end SpinAngle.BlockTensor

namespace SpinAngle.MatrixAnalysis
variable {n : Type*} [Fintype n] [DecidableEq n]

abbrev Mat (n : Type*) := Matrix n n ℂ

end SpinAngle.MatrixAnalysis

namespace SpinAngle

open SpinAngle.Young

structure TypeLabel (q : ℕ) where
    even : YoungDiagram  -- control comment
    odd : YoungDiagram  -- control comment
    even_height : even.colLen 0 ≤ q  -- control comment
    odd_height : odd.colLen 0 ≤ q  -- control comment

namespace TypeLabel
variable {q : ℕ}
def size (D : TypeLabel q) : ℕ := Fintype.card (Cells D.even) + Fintype.card (Cells D.odd)
def entropy (D : TypeLabel q) : ℝ := SignedCarrier.entropy D.even D.odd q
def dimension (D : TypeLabel q) : ℕ := SignedCarrier.dimension D.even D.odd q D.even_height D.odd_height

def projection (D : TypeLabel q) (τ : Type*) [Fintype τ] [DecidableEq τ] :
    Matrix (τ → SignedTensor.Spin q) (τ → SignedTensor.Spin q) ℂ :=  -- control comment
    SignedCarrier.matrixProjection D.even D.odd q D.even_height D.odd_height  -- control comment

end TypeLabel

namespace TypeBlocks
universe u
open MatrixAnalysis
variable {q : ℕ}
variable {τ : Type*} {J : Type u} [Fintype τ] [DecidableEq τ] [Fintype J] [DecidableEq J]

abbrev Fiber (f : τ → J) (j : J) := BlockTensor.Fiber f j

def projection (f : τ → J) (D : J → TypeLabel q) : Mat (τ → SignedTensor.Spin q) :=
    BlockTensor.tensor f (fun j => (D j).projection (Fiber f j))  -- control comment

def entropy (D : J → TypeLabel q) : ℝ := ∑ j, (D j).entropy
def dimension (D : J → TypeLabel q) : ℕ := ∏ j, (D j).dimension

end TypeBlocks

end SpinAngle


namespace SpinAngle.TypeAngle

open scoped BigOperators Matrix.Norms.L2Operator MatrixOrder ComplexOrder

variable {q : ℕ} [Nonempty (Fin q)]
variable {R C : Type*}
variable [Fintype R] [DecidableEq R] [Fintype C] [DecidableEq C]

def row (W : Finset (R × C)) (w : W) : R := w.val.1

def column (W : Finset (R × C)) (w : W) : C := w.val.2

def phi (W : Finset (R × C)) : ℝ :=
    missingCellProductFactor (Fintype.card C) (missingInRow W)  -- control comment

theorem one_sided_type_angle (W : Finset (R × C))
    (D : TypeLabel q) (H : C → TypeLabel q) (K : R → TypeLabel q)  -- control comment
    (hD : D.size = W.card)  -- control comment
    (hH : ∀ j, (H j).size = Fintype.card (TypeBlocks.Fiber (column W) j))  -- control comment
    (hK : ∀ i, (K i).size = Fintype.card (TypeBlocks.Fiber (row W) i)) :  -- control comment
    (‖TypeBlocks.projection (column W) H * TypeBlocks.projection (row W) K * D.projection W‖ ^ 2 ≤  -- control comment
    min 1 (Real.exp (TypeBlocks.entropy H + TypeBlocks.entropy K - D.entropy) *  -- control comment
    (TypeBlocks.dimension H : ℝ) * (TypeBlocks.dimension K : ℝ) * phi W)) ∧  -- control comment
    (min 1 (Real.exp (TypeBlocks.entropy H + TypeBlocks.entropy K - D.entropy) *  -- control comment
    (TypeBlocks.dimension H : ℝ) * (TypeBlocks.dimension K : ℝ) * phi W) ≤  -- control comment
    min 1 (Real.exp (TypeBlocks.entropy H + TypeBlocks.entropy K - D.entropy +  -- control comment
    (Fintype.card R * Fintype.card C - W.card : ℕ)) *  -- control comment
    (TypeBlocks.dimension H : ℝ) * (TypeBlocks.dimension K : ℝ))) ∧  -- control comment
    TypeBlocks.dimension H * TypeBlocks.dimension K ≤  -- control comment
    (W.card + 1) ^ ((Fintype.card R + Fintype.card C) * q * (q - 1)) := by  -- control comment
    sorry  -- control comment

end SpinAngle.TypeAngle

end

end OAI
