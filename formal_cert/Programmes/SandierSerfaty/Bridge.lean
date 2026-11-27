import Programmes.SandierSerfatyStatement
import Programmes.SandierSerfaty.Constants

/-!
# Bridge from the certificate constants to `SandierSerfatyStatement.lean`

The only link, in this run, between the A1 port and the definitions of the Lean statement of the conjecture: the
certificate's lattice constants are enclosures of the statement's `triScale = √(2/√3)` (the scale of the covolume-one
triangular lattice `triLattice`): `a = triScale` and `p = triScale / 2`.
-/

namespace ProgSandierSerfaty.Cert

theorem tri_eq_triScale : tri = ProgSandierSerfaty.triScale := rfl

/-- The C++ interval `a` encloses the nearest-neighbour distance `triScale` of `ProgSandierSerfaty.triLattice`. -/
theorem a_mem_triScale : aC.Contains ProgSandierSerfaty.triScale := tri_eq_triScale ▸ a_mem

/-- The C++ interval `p` encloses `triScale / 2`, the apothem of the hexagonal Voronoi cell of `triLattice`. -/
theorem p_mem_triScale : pC.Contains (ProgSandierSerfaty.triScale / 2) := tri_eq_triScale ▸ p_mem

end ProgSandierSerfaty.Cert

#print axioms ProgSandierSerfaty.Cert.tri_eq_triScale
#print axioms ProgSandierSerfaty.Cert.a_mem_triScale
#print axioms ProgSandierSerfaty.Cert.p_mem_triScale
