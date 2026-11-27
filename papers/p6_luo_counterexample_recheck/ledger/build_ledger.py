"""Build the Elenchus claim ledger for the AIC-LUO paper (papers/p6_luo_counterexample_recheck).

Modelled on papers/p6_bistable_networks_recheck/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on; the kind caps the tier (citation L, argument C, numeric X). No Lean, so no Tier A row. An AI audit exists
(AUDIT.md, ACCEPT_WITH_CORRECTIONS), not a person. This is a recheck of a claim by others (Guo, arXiv:2610.13979); no novelty claim.
Run:  python3 -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
D = PAPER / "data"
SRC_COMMIT = "a256903"  # HEAD when the lane records were written; the lane records and this paper are uncommitted working-tree files


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def fref(p: Path) -> dict:
    return {"path": str(p.relative_to(PAPER)), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def cite(source: str, where: str, text: str, note: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text, "note": note}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    S = D / "summaries"
    C = D / "code"
    A = D / "audit"
    c = [
        rec("LUO-L-0001", "L", "citation",
            "Guo, 'A Counterexample to Three Conjectures of Luo', arXiv:2610.13979 v1 (11 Oct 2026, unrefereed; title and author checked on arxiv.org 2026-11-02): a 2-tetrahedron one-vertex triangulation T of L(3,1) (face pairings 1230, 1230, 3201, 3201) with clauses (i) pi1 = C3 and a null-homotopic loop edge, (ii) Q-matching rank 2 with no 3-cluster of 2-quad-type solutions, (iii) Thurston's equation unsolvable, (iv) all maxima of vol on SAS(T) smooth; hence Luo's Conjectures 1-3 fail. Taken as stated. The paper credits ChatGPT with the idea. The paper full text is third-party and not shipped.",
            [], cite("arXiv:2610.13979v1", "Sections 1-4, Remarks 1.2, 4.2, 4.3", "Read by the producer and the independent AI auditor", "taken as stated; full text not shipped")),
        rec("LUO-L-0002", "L", "citation",
            "F. Luo, 'Triangulated 3-Manifolds: from Haken's normal surfaces to Thurston's algebraic equation', arXiv:1003.4413 (v1 23 Mar 2010, v2 23 Jul 2010; title and author checked on arxiv.org 2026-11-02). The auditor checked Guo's quoted Conjectures 1-3 and definitions (2-quad-type, cluster, signed real Haken solutions, Thurston's equation (3.7), SAS, smooth point) against v2 pp. 2-3, 6-9, 12-14, 17-20: faithful. The Contemp. Math. 541 published version was not compared.",
            [], cite("arXiv:1003.4413v2", "pp. 2-3, 6-9, 12-14, 17-20", "Read by the independent AI auditor", "published version not compared")),
        rec("LUO-L-0003", "L", "citation",
            "Literature search (alphaXiv and web, 2026-11-01, limited): only 2610.13979, 1003.4413, 0903.1138 and 2303.04380 surfaced; no independent verification or critique of Guo's paper and no earlier refutation of Luo's Conjectures 1-3 found. Not an exhaustive prior-art search. Milnor's single-tetrahedron volume bound and the implication pi1 = Z/3 => L(3,1) (geometrization) are classical facts used only for side remarks.",
            [], cite("AUDIT.md sections 8, 10; PREREG_ITEM.md", "literature note", "auditor's and producer's searches", "not exhaustive")),
        rec("LUO-C-0001", "C", "argument",
            "Triangulation and topology (producer and auditor, own code each, Regina 7.4 as cross-check): gluing perms 1230, 1230, 3201, 3201 (all odd), 8 faces each glued once, 1 vertex, vertex link (V,E,F) = (6,12,8) with chi = 2, 3 edge classes of degrees 2,5,5, chi(M) = 0; the local-edge table equals the paper's (2). isoSig cMcabbjak = Regina lens(3,1), census 'L(3,1) : #3'. Smith normal forms of the auditor's boundary matrices give H1 = Z/3, H2 = 0, H3 = Z. pi1 = C3 by two routes (producer's GAP; auditor's sympy, order 3 and subgroup <a> of index 3), so the loop edge a is null-homotopic. Correction: in the producer's presentation b, c are oriented opposite to the paper; with the paper's orientation the relators are exactly the paper's (3).",
            ["LUO-L-0001"],
            arg("C-exact-integer", "data/code/m12_structure.py, luo_lib.py, data/summaries/m12_paper.json, data/audit/code/a1_struct.py, a1.json",
                [C / "m12_structure.py", C / "luo_lib.py", S / "m12_paper.json", A / "code" / "a1_struct.py", A / "outputs" / "a1.json"], "m12_structure.py (producer); a1_struct.py (auditor)")),
        rec("LUO-C-0002", "C", "argument",
            "Q-matching: I and W = I*Omega equal the paper's matrices entry by entry; Regina's quad matching matrix is identical to W; rank W = 2 (kernel dimension 4); the Haken system has rank 9 with a 5-dimensional solution space whose projection to the quads equals ker W; the only proportional column pair is (x1,y1), so Lemma 3.1 holds. A Regina vertex normal surface is a torus with quads (1,0,0,1,0,0): a genuine 2-quad-type solution exists but only with quads x1, y1, so no cluster. Clause (ii) holds for nonnegative, integer or signed Haken solutions.",
            ["LUO-L-0001", "LUO-L-0002", "LUO-C-0001"],
            arg("C-exact-rational", "data/summaries/m12_paper.json, nonneg_lp.json, data/audit/code/a2_qmatch_thurston.py, a2.json, a5_ns.py, a5.json",
                [S / "m12_paper.json", S / "nonneg_lp.json", C / "nonneg_lp.py", A / "code" / "a2_qmatch_thurston.py", A / "outputs" / "a2.json", A / "code" / "a5_ns.py", A / "outputs" / "a5.json"], "m12_structure.py, nonneg_lp.py (producer); a2, a5 (auditor, Regina)")),
        rec("LUO-C-0003", "C", "argument",
            "Thurston's gluing equations (Groebner bases over Q, Singular, nondegeneracy t*z(1-z)w(1-w) = 1): in both orientation conventions, of the 8 sign patterns of the edge products exactly (+,-,-), (-,+,-), (-,-,+) are solvable and the other five, including (+,+,+), have Groebner basis {1}; (+,-,-) gives z = w = -1 (Remark 4.2). Hence Thurston's equation has no solution (iii).",
            ["LUO-L-0001", "LUO-L-0002", "LUO-C-0001"],
            arg("C-symbolic", "data/code/m34_equations.py, data/summaries/m34_paper.json, data/audit/code/thurston.sing.txt, a2_qmatch_thurston.py",
                [C / "m34_equations.py", S / "m34_paper.json", A / "code" / "thurston.sing.txt", A / "code" / "a2_qmatch_thurston.py", A / "outputs" / "a2.json"], "m34_equations.py (producer, sympy); Singular + a2 (auditor)")),
        rec("LUO-C-0004", "C", "argument",
            "Clause (iv), analytic bound (auditor): a partially flat tetrahedron contributes 0 volume and |Lambda| <= Lambda(pi/6), so every non-smooth point of SAS(T) has vol <= 3 Lambda(pi/6) <= 1.52316; the exact rational point theta/pi = (3/5,1/8,11/40,7/5,17/40,47/40) lies in SAS and is smooth with vol >= 1.58529 (30-digit floats plus a rigorous series-tail bound, not interval arithmetic). So every maximum is smooth. The non-smooth supremum is v3 = 1.0149416 at (2/3,0,1/3,-2/3,1/3,4/3) (Milnor's bound, Tier L, side remark only). Producer's numerical maximum 1.58864663930016 at 8 symmetric smooth points, strict local maximum, min|sin| = 0.3928.",
            ["LUO-L-0001", "LUO-C-0001"],
            arg("C-exact-rational", "data/audit/code/a3b_sas_exact.py, a3c_shape.py, a3d_elementary.py, a3b.json, data/summaries/m5b_sas.json",
                [A / "code" / "a3b_sas_exact.py", A / "code" / "a3c_shape.py", A / "code" / "a3d_elementary.py", A / "outputs" / "a3b.json", S / "m5b_sas.json", S / "m5_sas.json", C / "m5b_sas_param.py"], "a3b, a3c, a3d (auditor, mpmath tail bound); m5b_sas_param.py (producer, floating-point search)")),
        rec("LUO-C-0005", "C", "argument",
            "Minimality (auditor, Regina enumeration): none of the 108 one-tetrahedron gluings has H1 = Z/3, so 2 tetrahedra is minimal. Among 2-tetrahedron gluings (136080, 5088 closed orientable valid, 16 classes) three have H1 = Z/3: cMcabbgaj (1 vertex, degrees 1,2,9), cMcabbjak (Guo's) and cPcbbbaai (2 vertices). So Guo's is not the only one-vertex minimal triangulation of L(3,1); the other was not tested against C1-C3. Naming the other classes L(3,1) uses geometrization (Tier L).",
            ["LUO-L-0003"],
            arg("C-exact-integer", "data/audit/code/a4_census.py, a4.json",
                [A / "code" / "a4_census.py", A / "outputs" / "a4.json"], "a4_census.py (auditor, Regina)")),
        rec("LUO-C-0006", "C", "argument",
            "Controls: positive, Regina figure-eight (z = w = exp(+-i pi/3); SnapPy 4_1 shapes satisfy the edge equations to 1.4e-15; does not distinguish the two orientation conventions); pi1 of L(3,1), L(5,2), L(7,2), L(2,1), S^3 matches Regina; the sign patterns of LUO-C-0003. Negative, 20 single-pairing perturbations: 0 of 20 keep the claim profile; 18 single-entry increments of I are all unsolvable (weak control: the solver never said yes there).",
            ["LUO-C-0001", "LUO-C-0003"],
            arg("C-symbolic", "data/summaries/controls.json, data/code/controls.py",
                [S / "controls.json", C / "controls.py"], "controls.py (producer)")),
        rec("LUO-X-0001", "X", "numeric",
            "NOT done / not verified: Milnor's v3 bound (side remark only); geometrization step for naming other census classes; the Contemp. Math. 541 text of Luo; Segerman-Tillmann (Remark 4.3); interval arithmetic for the volume bounds; Lean or any proof assistant (Tier A not reached); an exhaustive prior-art search; a human audit. The other one-vertex minimal triangulation was not tested. Provenance: PREREG_ITEM.md is self-attested (sha256 recorded, no independent timestamp).",
            [], num([D / "RESULT.md", D / "PREREG_ITEM.md", D / "AUDIT.md"], "producer text, preregistration, audit; recorded absences and caveats")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
