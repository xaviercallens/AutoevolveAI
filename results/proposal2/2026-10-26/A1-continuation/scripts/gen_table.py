"""Generator for the L1 port of stage `table(24000)` (core.hpp:246-267).

Usage: gen_table.py [--nodes=a:b] [--workers=W]

Writes under formal_cert/Programmes/SandierSerfatyL1/Table/:
  Core.lean          template lean_table_core.lean.txt (+ `nodeT`, `origL` access to the shared table)
  StateB{k}.lean     the state witnesses pointS[i], cellS[i] (C++ values, dump2), blocks of 256 nodes
  Init.lean          ss0(small) = pointS[1562]; the mesh: ts recomputed = the shared table's node intervals; origL
  N{i}.lean          node i >= 1562: the propagation step i (from pointS[i-1] to pointS[i], cellS[i-1]),
                     fh at node i (= pts[i]) and on cell i-1 (= cels[i-1]), with basis / solve / row-block witnesses
  Z{i0}.lean         nodes i0..i0+15 of segment 0: fh0 at the nodes and on the cells (no state)
  PlantN{i}.lean     planted false propagation step (state + 1 ulp), must be rejected
  Assemble.lean      imports every chunk; one conjunction per node
Every witness comes from the Python mirror (jetmirror.py), which must reproduce dump2's pts, cels, pointS, cellS
for every node generated (else abort); targets are the shared table literal (Grid/TableB*) and the state literals.
"""
from __future__ import annotations

import json
import re
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump2io import Dump2  # noqa: E402
from jetmirror import (KEYS, Ctx, fh0, fh_final, fh_solve, jaddi, jmul, neg, prop_step, qe_rows, ss0_A0,  # noqa: E402
                       horJ)
from l1common import CONT, DUMP2, L1DIR, ONE, ZERO, add, inv, lit, mul, ofint, sha256  # noqa: E402

HERE = Path(__file__).resolve().parent
TD = L1DIR / "Table"
BLOCK = 256
FIRST = 1562  # first node with orig >= 1 (t = small)
QEB = [(0, 2), (2, 2), (4, 2), (6, 2), (8, 2), (10, 3), (13, 3), (16, 3), (19, 4), (23, 5), (28, 11)]
_D = None
_C = None


def nc(txt: str) -> str:
    return re.sub(r"^def ", "noncomputable def ", txt, flags=re.M)


def jl(j) -> str:
    return "⟨" + ", ".join(lit(x) for x in j) + "⟩"


def ssl(s) -> str:
    return f"⟨{lit(s[0])}, {lit(s[1])}, [" + ", ".join(lit(x) for x in s[2]) + "]⟩"


def ssjl(s) -> str:
    return f"⟨{jl(s[0])}, {jl(s[1])}, [" + ", ".join(jl(x) for x in s[2]) + "]⟩"


def st(s: tuple) -> tuple:
    s1, s2, ps = s
    return (s1, s2, [ps[k] for k in KEYS])


def init_worker() -> None:
    global _D, _C
    _D = Dump2(want={"node", "cell", "pS", "cS"})
    _C = Ctx(_D.sc)


def basis_block(ctx: Ctx, name: str, t, seg: int, texpr: str) -> tuple[list[str], tuple]:
    """Lean lines proving `basis texpr seg = (B_name, D_name)`; for seg 2 through the 38 Horner witnesses."""
    B, D = ctx.basis(t, seg)
    L = [f"def B_{name} : J := {jl(B)}", f"def D_{name} : List J := [" + ", ".join(jl(x) for x in D) + "]", ""]
    if seg != 2:
        L += ["set_option maxRecDepth 100000 in",
              f"theorem bas_{name} : basis ({texpr}) {seg} = (B_{name}, D_{name}) := by decide +kernel", ""]
        return L, (B, D)
    z = jaddi(jmul(t, t), neg(mul(ctx.p, ctx.p)))
    hs = [horJ(z, ctx.edge[m]) for m in range(38)]
    for m, h in enumerate(hs):
        L += [f"def h_{name}_{m} : J := {jl(h)}", "set_option maxRecDepth 100000 in",
              f"theorem hor_{name}_{m} : horJ (z2Of ({texpr})) (dEdge.getD {m} []) = h_{name}_{m} := by decide +kernel"]
    hl = ", ".join(f"h_{name}_{m}" for m in range(38))
    expl = ", ".join(f"horJ (z2Of ({texpr})) (dEdge.getD {m} [])" for m in range(38))
    rws = ", ".join(f"hor_{name}_{m}" for m in range(38))
    L += ["set_option maxRecDepth 100000 in",
          f"theorem basw_{name} : basisW ({texpr}) 2 [{hl}] = (B_{name}, D_{name}) := by decide +kernel", "",
          "set_option maxRecDepth 100000 in",
          f"theorem bas_{name} : basis ({texpr}) 2 = (B_{name}, D_{name}) := by",
          f"  rw [basis_seg2, show (List.range 38).map (fun m => horJ (z2Of ({texpr})) (dEdge.getD m [])) = [{expl}] from rfl, {rws}]",
          f"  exact basw_{name}", ""]
    return L, (B, D)


def fh_block(ctx: Ctx, name: str, t, bd: tuple, S: tuple, texpr: str, sexpr: str, target: str, expect: list) -> list[str]:
    B, D = bd
    ss = fh_solve(ctx, t, B, S)
    qs = [qe_rows(t, D, a, a + c) for a, c in QEB]
    quad, e = ZERO, ZERO
    quad = (ZERO, ZERO, ZERO, ZERO)
    e = (ZERO, ZERO, ZERO, ZERO)
    for q in qs:
        quad = tuple(add(a, b) for a, b in zip(quad, q[0]))
        e = tuple(add(a, b) for a, b in zip(e, q[1]))
    got = fh_final(ctx, t, D, ss, quad, e)
    if got != expect:
        raise SystemExit(f"MIRROR fh MISMATCH {name}")
    L = [f"def ss_{name} : SSJ := {ssjl(ss)}", "set_option maxRecDepth 100000 in",
         f"theorem sol_{name} : fhSolve ({texpr}) B_{name.split('_')[0]}_{name.split('_')[1]} {sexpr} = ss_{name} := by decide +kernel", ""]
    for k, ((a, c), q) in enumerate(zip(QEB, qs)):
        L += [f"def q_{name}_{k} : J × J := ({jl(q[0])}, {jl(q[1])})", "set_option maxRecDepth 100000 in",
              f"theorem qe_{name}_{k} : qeRange ({texpr}) D_{name.split('_')[0]}_{name.split('_')[1]} {a} {c} = q_{name}_{k} := by decide +kernel"]
    nest = "(jz, jz)"
    for k in reversed(range(len(QEB))):
        nest = f"(jadd2 q_{name}_{k} {nest})"
    bn = f"{name.split('_')[0]}_{name.split('_')[1]}"
    rws = ", ".join(f"qe_{name}_{k}" for k in range(len(QEB)))
    L += ["", "set_option maxRecDepth 100000 in",
          f"theorem fin_{name} : fhFinal ({texpr}) D_{bn} ss_{name} {nest} = {target} := by decide +kernel", ""]
    return L, rws, bn


def node_file(i: int) -> tuple[int, str, dict]:
    d, ctx = _D, _C
    assert d is not None and ctx is not None
    orig, x, pts = d.node[i]
    so = orig
    hdr = ("import Programmes.SandierSerfatyL1.Table.Core\n" +
           "".join(f"import Programmes.SandierSerfatyL1.Table.StateB{b:02d}\n" for b in sorted({(i - 1) // BLOCK, i // BLOCK}))
           + f"\n/-! table node {i} (L1). Generated by gen_table.py (do not edit). -/\n\nnamespace ProgSandierSerfaty.L1.Table\n\n"
           "open ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV ProgSandierSerfaty.L1.Jet\n\n")
    L: list[str] = []
    conj: list[str] = []
    prfs: list[str] = []
    told, tnew = f"nodeT {i-1}", f"nodeT {i}"
    old = d.node[i - 1][1]
    sp = d.node[i - 1][0]
    L += ["set_option maxRecDepth 100000 in", f"theorem seg_{i} : origL.getD {i-1} 0 = {sp} ∧ origL.getD {i} 0 = {so} := by decide +kernel", ""]
    conj.append(f"origL.getD {i-1} 0 = {sp} ∧ origL.getD {i} 0 = {so}")
    prfs.append(f"seg_{i}")
    tt = (x, ONE, ZERO, ZERO)
    tc = ((old[0], x[1]), ONE, ZERO, ZERO)
    tm = (mul(add(old, x), inv(ofint(2))), ONE, ZERO, ZERO)
    ops = 0
    if sp >= 1:
        lb, bdm = basis_block(ctx, f"m_{i}", tm, sp, f"tmOf ({told}) ({tnew})")
        L += lb
        lb, bdc = basis_block(ctx, f"c_{i}", tc, sp, f"tcOf ({told}) ({tnew})")
        L += lb
        ns, bs = prop_step(ctx, old, x, st(d.pS[i - 1]), sp, bdm[0], bdc[0])
        if ns != st(d.pS[i]) or bs != st(d.cS[i - 1]):
            raise SystemExit(f"MIRROR prop MISMATCH {i}")
        L += ["set_option maxRecDepth 100000 in",
              f"theorem propw_{i} : propW ({told}) ({tnew}) pS_{i-1} B_m_{i} B_c_{i} = (pS_{i}, cS_{i-1}) := by decide +kernel", "",
              f"theorem prop_{i} : prop ({told}) ({tnew}) pS_{i-1} {sp} = (pS_{i}, cS_{i-1}) := by",
              f"  unfold prop", f"  rw [bas_m_{i}, bas_c_{i}]", f"  exact propw_{i}", ""]
        conj.append(f"prop ({told}) ({tnew}) pS_{i-1} {sp} = (pS_{i}, cS_{i-1})")
        prfs.append(f"prop_{i}")
        # cell i-1: fh with cellS[i-1] on tc (basis shared with the step)
        lf, rws, bn = fh_block(ctx, f"c_{i}_cell", tc, bdc, st(d.cS[i - 1]), f"tcOf ({told}) ({tnew})", f"cS_{i-1}",
                               f"cellL (cellAt {i-1})", list(d.cell[i - 1]))
        L += lf
        L += [f"theorem fhc_{i} : fhT (tcOf ({told}) ({tnew})) {sp} (some cS_{i-1}) = cellL (cellAt {i-1}) := by",
              f"  show fhW _ _ (basis _ {sp}) = _", f"  rw [bas_c_{i}]",
              "  simp only [fhW, qeBlocks, qeBlocksL, List.foldr]",
              f"  rw [sol_c_{i}_cell, {rws}]", f"  exact fin_c_{i}_cell", ""]
        conj.append(f"fhT (tcOf ({told}) ({tnew})) {sp} (some cS_{i-1}) = cellL (cellAt {i-1})")
        prfs.append(f"fhc_{i}")
        ops += 60000 if sp == 2 else 30000
    else:
        got = fh0(ctx, tc)
        assert got == list(d.cell[i - 1])
        L += ["set_option maxRecDepth 100000 in",
              f"theorem fhc_{i} : fhT (tcOf ({told}) ({tnew})) 0 none = cellL (cellAt {i-1}) := by decide +kernel", ""]
        conj.append(f"fhT (tcOf ({told}) ({tnew})) 0 none = cellL (cellAt {i-1})")
        prfs.append(f"fhc_{i}")
    # point i: fh with pointS[i] on tt
    lb, bdp = basis_block(ctx, f"p_{i}", tt, so, f"ttAt {i}")
    L += lb
    L += [f"def pts_{i} : List IV := [" + ", ".join(lit(z) for z in pts) + "]",
          "set_option maxRecDepth 100000 in",
          f"theorem ptsT_{i} : (pts_{i}.getD 0 z0 = (nodeAt {i}).f ∧ pts_{i}.getD 3 z0 = (nodeAt {i}).e) := by decide +kernel", ""]
    lf, rws, bn = fh_block(ctx, f"p_{i}_pt", tt, bdp, st(d.pS[i]), f"ttAt {i}", f"pS_{i}", f"pts_{i}", list(pts))
    L += lf
    L += [f"theorem fhp_{i} : fhT (ttAt {i}) {so} (some pS_{i}) = pts_{i} := by",
          f"  show fhW _ _ (basis _ {so}) = _", f"  rw [bas_p_{i}]",
          "  simp only [fhW, qeBlocks, qeBlocksL, List.foldr]",
          f"  rw [sol_p_{i}_pt, {rws}]", f"  exact fin_p_{i}_pt", ""]
    conj += [f"fhT (ttAt {i}) {so} (some pS_{i}) = pts_{i}", f"(pts_{i}.getD 0 z0 = (nodeAt {i}).f ∧ pts_{i}.getD 3 z0 = (nodeAt {i}).e)"]
    prfs += [f"fhp_{i}", f"ptsT_{i}"]
    ops += 45000 if so == 2 else 35000
    L += ["set_option maxRecDepth 100000 in", f"theorem node_{i} : " + " ∧\n    ".join(f"({c})" for c in conj) + " :=", f"  ⟨{', '.join(prfs)}⟩", "", f"#print axioms node_{i}", "",
          "end ProgSandierSerfaty.L1.Table", ""]
    return i, nc(hdr + "\n".join(L)), {"ops": ops, "sp": sp}


def zero_file(i0: int, i1: int, d: Dump2, ctx: Ctx) -> str:
    hdr = ("import Programmes.SandierSerfatyL1.Table.Core\n\n"
           f"/-! table nodes {i0}..{i1-1} of segment 0 (fh0 at the nodes and on the cells; no state). Generated by gen_table.py. -/\n\n"
           "namespace ProgSandierSerfaty.L1.Table\n\nopen ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV ProgSandierSerfaty.L1.Jet\n\n")
    L, conj = [], []
    for i in range(i0, i1):
        orig, x, pts = d.node[i]
        assert orig == 0
        assert fh0(ctx, (x, ONE, ZERO, ZERO)) == list(pts)
        L += [f"def pts_{i} : List IV := [" + ", ".join(lit(z) for z in pts) + "]"]
        c = [f"origL.getD {i} 0 = 0", f"fhT (ttAt {i}) 0 none = pts_{i}",
             f"(pts_{i}.getD 0 z0 = (nodeAt {i}).f ∧ pts_{i}.getD 3 z0 = (nodeAt {i}).e)"]
        if i >= 1:
            old = d.node[i - 1][1]
            assert fh0(ctx, ((old[0], x[1]), ONE, ZERO, ZERO)) == list(d.cell[i - 1])
            c.append(f"fhT (tcOf (nodeT {i-1}) (nodeT {i})) 0 none = cellL (cellAt {i-1})")
        L += ["set_option maxRecDepth 100000 in", f"theorem z_{i} : " + " ∧ ".join(f"({x})" for x in c) + " := by decide +kernel", "", f"#print axioms z_{i}", ""]
        conj.append(f"z_{i}")
    L += ["end ProgSandierSerfaty.L1.Table", ""]
    return nc(hdr + "\n".join(L))


def main() -> int:
    nodes = None
    workers = 2
    for a in sys.argv[1:]:
        if a.startswith("--nodes="):
            nodes = []
            for part in a.split("=")[1].split(","):
                lo, hi = part.split(":")
                nodes += list(range(int(lo), int(hi)))
        if a.startswith("--workers="):
            workers = int(a.split("=")[1])
    d = Dump2(want={"node", "cell", "pS", "cS", "init_ps"})
    ctx = Ctx(d.sc)
    n = len(d.node)
    TD.mkdir(parents=True, exist_ok=True)
    # Core: template + access to the shared table and the segment list
    core = (HERE / "lean_table_core.lean.txt").read_text()
    core = core.replace("import Programmes.SandierSerfatyL1.Jet.Core\n", "import Programmes.SandierSerfatyL1.Jet.Core\nimport Programmes.SandierSerfatyL1.Grid.Table\n", 1)
    origs = [d.node[i][0] for i in range(n)]
    extra = ("\ndef dfltN : ProgSandierSerfaty.Cert.CalcK.NodeD := ⟨z0, z0, z0⟩\n"
             "def dfltC : ProgSandierSerfaty.Cert.CalcK.CellD := ⟨z0, z0, z0, z0, z0, z0⟩\n"
             "/-- table entry `i` of the shared table (Grid/Table.lean) -/\n"
             "noncomputable def nodeAt (i : Nat) : ProgSandierSerfaty.Cert.CalcK.NodeD := ProgSandierSerfaty.L1.Grid.tblN.getD i dfltN\n"
             "noncomputable def cellAt (i : Nat) : ProgSandierSerfaty.Cert.CalcK.CellD := ProgSandierSerfaty.L1.Grid.tblC.getD i dfltC\n"
             "/-- node `i`'s interval `ts[i]` -/\n"
             "noncomputable def nodeT (i : Nat) : IV := (nodeAt i).t\n"
             "noncomputable def ttAt (i : Nat) : J := ⟨nodeT i, o1, z0, z0⟩\n"
             "def cellL (c : ProgSandierSerfaty.Cert.CalcK.CellD) : List IV := [c.c0, c.c1, c.c2, c.c3, c.c4, c.c5]\n"
             "/-- `orig[i]`: the segment of node `i` (checked against the mesh in Init.lean) -/\n"
             "def origL : List Nat := [" + ", ".join(map(str, origs)) + "]\n\n")
    core = core.replace("end ProgSandierSerfaty.L1.Table\n", extra + "end ProgSandierSerfaty.L1.Table\n")
    (TD / "Core.lean").write_text(core)
    # state blocks
    nb = (n + BLOCK - 1) // BLOCK
    for b in range(nb):
        L = []
        for i in range(b * BLOCK, min(n, (b + 1) * BLOCK)):
            if i >= FIRST:
                L.append(f"def pS_{i} : SS := {ssl(st(d.pS[i]))}")
            if FIRST <= i < n - 1:
                L.append(f"def cS_{i} : SS := {ssl(st(d.cS[i]))}")
        txt = ("import Programmes.SandierSerfatyL1.Table.Core\n\n"
               f"/-! State witnesses pointS[i], cellS[i] for nodes [{b*BLOCK}, {min(n,(b+1)*BLOCK)}) (C++ values, dump2). Generated by gen_table.py. -/\n\n"
               "namespace ProgSandierSerfaty.L1.Table\n\nopen ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV\n\nset_option maxRecDepth 100000\n\n"
               + "\n".join(L) + "\n\nend ProgSandierSerfaty.L1.Table\n")
        (TD / f"StateB{b:02d}.lean").write_text(nc(txt))
    # Init: ss0 and the mesh
    s0 = ss0_A0(ctx, ctx.small)
    assert s0 == st(d.pS[FIRST]) or (s0[0], s0[1], s0[2]) == st(d.pS[FIRST])
    init = (f"import Programmes.SandierSerfatyL1.Table.StateB{FIRST // BLOCK:02d}\n\n"
            "/-! Initial state and mesh of `table(24000)` (L1). Generated by gen_table.py. -/\n\n"
            "namespace ProgSandierSerfaty.L1.Table\n\nopen ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV ProgSandierSerfaty.L1.Jet\n\n"
            "/-- `table` mesh (core.hpp:248): `n_i = max(1, ⌊((up-lo)·N_i).v / Q⌋ + 1)` (N = 8000 on segment 0, 24000\n"
            "elsewhere), nodes `lo + (up-lo)·j/n_i`, then `breaks.back()`; with the segment index of each node. -/\n"
            "def meshSeg (i : Nat) : List (IV × Nat) :=\n"
            "  let lo := dBreaks.getD i z0\n  let up := dBreaks.getD (i + 1) z0\n"
            "  let nn : Nat := (max 1 ((mul (sub up lo) (ofInt (if i = 0 then 8000 else 24000))).v / Q + 1)).toNat\n"
            "  (List.range nn).map fun j => (add lo (mul (mul (sub up lo) (ofInt j)) (IV.inv (ofInt nn))), i)\n"
            "def meshL : List (IV × Nat) := ((List.range 6).map meshSeg).foldr (· ++ ·) [] ++ [(dBreaks.getD 6 z0, 6)]\n\n"
            "set_option maxRecDepth 100000 in\n"
            "theorem mesh_ok : meshL.map Prod.fst = ProgSandierSerfaty.L1.Grid.tblN.map (·.t) ∧ meshL.map Prod.snd = origL := by decide +kernel\n\n"
            "set_option maxRecDepth 100000 in\n"
            f"/-- `ss0(J(small))` (order 0) is the C++ initial state `pointS[{FIRST}]` (node {FIRST} is `small`). -/\n"
            f"theorem init_ok : ss0I dsmall = pS_{FIRST} ∧ nodeT {FIRST} = dsmall := by decide +kernel\n\n"
            "#print axioms mesh_ok\n#print axioms init_ok\n\nend ProgSandierSerfaty.L1.Table\n")
    (TD / "Init.lean").write_text(nc(init))
    chunks = [{"id": "table/Init", "stage": "table", "kind": "chunk", "file": "Programmes/SandierSerfatyL1/Table/Init.lean",
               "module": "Programmes.SandierSerfatyL1.Table.Init", "deps": [f"Programmes.SandierSerfatyL1.Table.StateB{FIRST // BLOCK:02d}"],
               "ops_hint": 60000, "order": 0}]
    # segment-0 files
    for i0 in range(0, FIRST, 16):
        i1 = min(FIRST, i0 + 16)
        (TD / f"Z{i0:04d}.lean").write_text(zero_file(i0, i1, d, ctx))
        chunks.append({"id": f"table/Z{i0:04d}", "stage": "table", "kind": "chunk", "file": f"Programmes/SandierSerfatyL1/Table/Z{i0:04d}.lean",
                       "module": f"Programmes.SandierSerfatyL1.Table.Z{i0:04d}", "deps": ["Programmes.SandierSerfatyL1.Table.Core"],
                       "ops_hint": 400 * (i1 - i0), "order": i0})
    nodes = nodes or range(FIRST, n)
    with Pool(workers, initializer=init_worker) as pool:
        for i, txt, info in pool.imap(node_file, list(nodes), chunksize=4):
            (TD / f"N{i:04d}.lean").write_text(txt)
            deps = ["Programmes.SandierSerfatyL1.Table.Core"] + [f"Programmes.SandierSerfatyL1.Table.StateB{b:02d}" for b in sorted({(i - 1) // BLOCK, i // BLOCK})]
            chunks.append({"id": f"table/N{i:04d}", "stage": "table", "kind": "chunk", "file": f"Programmes/SandierSerfatyL1/Table/N{i:04d}.lean",
                           "module": f"Programmes.SandierSerfatyL1.Table.N{i:04d}", "deps": deps, "ops_hint": info["ops"], "order": i})
            if i % 200 == 0:
                print("node", i, "ok", flush=True)
    # planted: propagation step of the first generated propagating node with pointS + 1 ulp
    ip = next(i for i in nodes if i > FIRST)
    src = (TD / f"N{ip:04d}.lean").read_text()
    m = re.search(rf"theorem propw_{ip} : (.*) = \(pS_{ip}, cS_{ip-1}\) := by decide \+kernel", src)
    assert m
    lhs = m.group(1)
    pre = src.split(f"theorem propw_{ip}")[0]
    s_bad = st(d.pS[ip])
    s_bad = ((s_bad[0][0] + 1, s_bad[0][1]), s_bad[1], s_bad[2])
    plant = (pre + f"def plant_S : SS := {ssl(s_bad)}\n\nset_option maxRecDepth 100000 in\n"
             f"theorem plant_refuted : {lhs} ≠ (plant_S, cS_{ip-1}) := by decide +kernel\n\n#print axioms plant_refuted\n\n"
             f"set_option maxRecDepth 100000 in\ntheorem plant_claim : {lhs} = (plant_S, cS_{ip-1}) := by decide +kernel\n\n"
             "end ProgSandierSerfaty.L1.Table\n")
    plant = plant.replace(f"/-! table node {ip} (L1).", f"/-! PLANTED FALSE propagation step {ip} (pointS[{ip}].s1 lower endpoint + 1 ulp).")
    (TD / f"PlantN{ip:04d}.lean").write_text(nc(plant))
    chunks.append({"id": f"table/PlantN{ip:04d}", "stage": "table", "kind": "planted", "file": f"Programmes/SandierSerfatyL1/Table/PlantN{ip:04d}.lean",
                   "module": f"Programmes.SandierSerfatyL1.Table.PlantN{ip:04d}",
                   "deps": ["Programmes.SandierSerfatyL1.Table.Core"] + [f"Programmes.SandierSerfatyL1.Table.StateB{b:02d}" for b in sorted({(ip - 1) // BLOCK, ip // BLOCK})],
                   "ops_hint": 1, "order": 0})
    if list(nodes) == list(range(FIRST, n)):
        mods = [c["module"] for c in chunks if c["kind"] == "chunk"]
        imps = "\n".join(f"import {mm}" for mm in mods)
        names = ["mesh_ok", "init_ok"] + [f"z_{i}" for i in range(FIRST)] + [f"node_{i}" for i in range(FIRST, n)]
        conj = " ∧\n    ".join(f"(type_of% {x})" for x in names)
        asm = (imps + "\n\n/-! # Assembly of stage `table` (L1). Generated by gen_table.py (do not edit). -/\n\n"
               "namespace ProgSandierSerfaty.L1.Table\n\n"
               "/-- Stage `table`, L1: the mesh, the initial state, every segment-0 node and every propagation step and fh. -/\n"
               f"set_option maxRecDepth 1000000 in\ntheorem table_stage : {conj} :=\n  ⟨{', '.join(names)}⟩\n\n"
               "#print axioms table_stage\n\nend ProgSandierSerfaty.L1.Table\n")
        (TD / "Assemble.lean").write_text(asm)
        chunks.append({"id": "table/Assemble", "stage": "table", "kind": "assemble", "file": "Programmes/SandierSerfatyL1/Table/Assemble.lean",
                       "module": "Programmes.SandierSerfatyL1.Table.Assemble", "deps": mods, "ops_hint": 1, "order": 10**9})
    man = {"stage": "table",
           "core": [{"module": "Programmes.SandierSerfatyL1.Table.Core", "file": "Programmes/SandierSerfatyL1/Table/Core.lean",
                     "deps": ["Programmes.SandierSerfatyL1.Jet.Core", "Programmes.SandierSerfatyL1.Grid.Table"]}] +
                   [{"module": f"Programmes.SandierSerfatyL1.Table.StateB{b:02d}", "file": f"Programmes/SandierSerfatyL1/Table/StateB{b:02d}.lean",
                     "deps": ["Programmes.SandierSerfatyL1.Table.Core"]} for b in range(nb)],
           "chunks": chunks, "inputs": {"dump2_sha256": sha256(DUMP2)}}
    (CONT / "manifests_pending").mkdir(parents=True, exist_ok=True)
    (CONT / "manifests_pending" / "table.json").write_text(json.dumps(man, indent=1))
    print(f"table: {len(chunks)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
