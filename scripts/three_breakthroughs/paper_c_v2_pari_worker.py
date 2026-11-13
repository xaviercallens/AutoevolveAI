"""Paper C, edition 2: PARI/GP worker (run with a Python that has cypari2).

Called by paper_c_v2_experiment.py as a subprocess. Every arithmetic fact that needs ground truth
(minimal models, conductors, ramification, Hecke data, L-values, supersingular isogeny graphs) is
computed here by PARI/GP, never by hand-rolled arithmetic.

Usage: <python-with-cypari2> paper_c_v2_pari_worker.py TASK JSON_ARGS  -> JSON on stdout
Tasks: version, frey, family, quat, gram, qfrep, graph_counts, visB, visA, lvals
"""

from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool
from typing import Any

GP_CODE = r"""
sigstar(n,p) = sumdiv(n, d, if(d%p, d, 0));
colof(c) = Col(c);
horner(P, A, v) = { my(d=poldegree(P), w=polcoef(P,d)*v); forstep(i=d-1,0,-1, w = A*w + polcoef(P,i)*v); w };

\\ ---------- supersingular l-isogeny graphs over F_{p^2} (vertices: 2-isogeny BFS from j = 1728)
ssroots(Phi, j, one) = {
  my(fa=factor(substvec(Phi, ['x,'y], [j, 'Y])*one), out=List());
  for(r=1,#fa~, my(g=fa[r,1]);
    if(poldegree(g)!=1, error("root outside F_p2 at j=", j));
    listput(out, [(-polcoef(g,0)/polcoef(g,1))*one, fa[r,2]]));
  Vec(out);
}
ssvertices(p) = {
  my(t=ffgen(p^2,'t), one=t^0, Phi=polmodular(2), V=List([1728*one]), idx=Map(), k=1);
  mapput(idx, Str(1728*one), 1);
  while(k <= #V,
    my(R=ssroots(Phi, V[k], one));
    for(r=1,#R, my(s=Str(R[r][1])); if(!mapisdefined(idx, s), listput(V, R[r][1]); mapput(idx, s, #V)));
    k++);
  [Vec(V), idx, one];
}
ssadj(VV, l) = {
  my(V=VV[1], idx=VV[2], one=VV[3], n=#V, A=matrix(n,n), Phi=polmodular(l), id);
  for(i=1,n, my(R=ssroots(Phi, V[i], one));
    for(r=1,#R, if(!mapisdefined(idx, Str(R[r][1]), &id), error("neighbour not in vertex set"));
      A[i,id] += R[r][2]));
  A;
}
ssfrob(VV, p) = {
  my(V=VV[1], idx=VV[2], n=#V, F=matrix(n,n), id);
  for(i=1,n, if(!mapisdefined(idx, Str(V[i]^p), &id), error("Frobenius image missing")); F[id,i]=1);
  F;
}
\\ charpoly of A2 on ker Pi(T), computed modulo a 400-bit prime and lifted; checked to divide charpoly(A2)
orbitcp(Pi, T, A2) = {
  my(ell=nextprime(2^400), Tm=T*Mod(1,ell), K=matker(subst(Pi, 'x, Tm)), R=matsolve(K~*K, K~*(A2*Mod(1,ell))*K));
  my(c=Pol(apply(z->centerlift(z), Vec(charpoly(R))), 'x));
  if(charpoly(A2) % c != 0, error("lifted orbit charpoly does not divide charpoly(A2)"));
  c;
}
\\ visibility of each Hecke orbit in e_{1728} and its Frobenius (= T_p = a_p = root number) sign
brandtvis(p) = {
  my(VV=ssvertices(p), n=#VV[1], A2=ssadj(VV,2), Fr=ssfrob(VV,p), T=A2, ops=List(), L=[3,5,7,11,13], tries=0, ok=0, fa, P);
  if(Fr*A2 != A2*Fr, error("Frobenius does not commute with A2"));
  for(i=1,n, if(vecsum(A2[i,]) != 3, error("row sum of A2 is not 3")));
  while(!ok,
    P=charpoly(T); fa=factor(P); ok=1; for(i=1,#fa~, if(fa[i,2]>1, ok=0));
    if(!ok, tries++; if(tries > #L, error("Hecke operators up to 13 do not separate orbits"));
       listput(ops, ssadj(VV, L[tries])); T = T + (tries+1)*ops[tries]));
  my(e0=vectorv(n,i,i==1), out=List());
  for(i=1,#fa~,
    my(Pi=fa[i,1], d=poldegree(Pi), oth=P/Pi, u=horner(oth, T, e0), vis=(u!=0), v=1, w, eps, cp2);
    while(u==0, v++; u=horner(oth, T, vectorv(n,ii,ii==v)));
    w=Fr*u; eps = if(w==u, 1, if(w==-u, -1, 0));
    cp2 = if(tries==0, Pi, orbitcp(Pi, T, A2));
    my(rts=polroots(cp2));
    listput(out, [cp2, d, eps, vis, vecmax(abs(rts)), vecmax(abs(imag(rts)))]));
  [n, Vec(out), tries, mfdim([p,2],1)];
}
\\ diagonal entries (B(2^e))_{1728,1728} from the Hecke recursion B(2^{k+1}) = B(2) B(2^k) - 2 B(2^{k-1})
graphcounts(p, emax) = {
  my(VV=ssvertices(p), n=#VV[1], A2=ssadj(VV,2), e0=vectorv(n,i,i==1), prev=e0, cur=A2*e0, out=List([1, cur[1]]));
  for(k=1, emax-1, my(nx=A2*cur - 2*prev); prev=cur; cur=nx; listput(out, cur[1]));
  [n, mfdim([p,2],1), Vec(out)];
}
\\ ---------- theta_{O_0} projected on newform orbits via modular symbols (independent of the graph)
visA(p) = {
  my(m=(p+1)/4, G=[2,0,0,1;0,2,1,0;0,1,2*m,0;1,0,0,2*m]);
  my(B=(p+1)\6 + 2);
  my(r=2*Vec(qfrep(G, B, 1)));
  my(cusp=vector(B, n, r[n] - 24/(p-1)*sigstar(n,p)));
  if(mfdim([p,2],1)==0, return([[], cusp==vector(B,n,0)]));
  my(M=msinit(p,2,1), S=mscuspidal(M), H=mssplit(M, S), cols=List(), blk=List(), info=List());
  for(i=1,#H,
    my(q=msqexpansion(M, H[i], B), a2=q[2], P='x, d=1, W, eps, cp);
    if(type(a2)=="t_POLMOD", P=a2.mod; d=poldegree(P));
    W=msatkinlehner(M, p, H[i]); eps=W[1,1];
    if(W != eps*matid(#W), error("W_p not scalar on orbit"));
    cp = if(d==1, 'x - a2, charpoly(a2));
    for(j=0,d-1,
      listput(cols, vector(B, n, if(d==1, q[n], trace(Mod(lift(q[n])*variable(P)^j, P)))));
      listput(blk, i));
    listput(info, [cp, d, -eps]));
  my(A=matconcat(apply(colof, Vec(cols))));
  if(matrank(A) != #cols, error("orbit q-expansions not independent up to the Sturm bound"));
  my(sol=matinverseimage(A, Col(cusp)));
  if(#sol==0, error("theta - E not in the cusp space"));
  my(out=vector(#H, i, my(nz=0); for(k=1,#blk, if(blk[k]==i && sol[k]!=0, nz=1)); concat(info[i], [nz])));
  [out, 1];
}
\\ ---------- L(f,1), L(f x chi_{-4},1) for every embedding of every newform orbit of dim <= dl
lvals(p, dl) = {
  my(mf=mfinit([p,2],0), sp=mfsplit(mf, dl), vF=sp[1], vK=sp[2], out=List());
  my(need=ceil(1.15*lfuncost(lfuncreate([vector(1,n,0),0,[0,1],2,16*p,1]),[1])[1]) + 50);
  need = max(need, p + 1);
  my(C=mfcoefs(mf, need));
  for(i=1,#vK,
    my(K=vK[i], d=poldegree(K), c=C*vF[,i]);
    c = vector(#c, n, if(d==1, if(type(c[n])=="t_POLMOD", lift(c[n]), c[n]), Mod(lift(c[n]), K)));
    if(d==1, c = vector(#c, n, if(type(c[n])=="t_POL", polcoef(c[n],0), c[n])));
    my(a1=c[2]); c = vector(#c, n, c[n]/a1);
    my(a2=c[3], ap=c[p+1], cp=if(d==1, 'x - a2, charpoly(a2)), w);
    w = if(d==1, ap, my(l=lift(ap)); if(type(l)=="t_POL", if(poldegree(l)>0, error("a_p irrational"), polcoef(l,0)), l));
    if(type(w)!="t_INT" || abs(w)!=1, error("a_p not +-1"));
    my(rts=if(d==1, [0], polroots(K)), res=List());
    for(r=1,#rts,
      my(an=vector(#c-1, n, if(d==1, c[n+1], real(subst(lift(c[n+1]), variable(K), rts[r])))));
      my(ant=vector(#an, n, an[n]*kronecker(-4,n)));
      my(L=lfuncreate([an,0,[0,1],2,p,w]), Lt=lfuncreate([ant,0,[0,1],2,16*p,w]));
      listput(res, [lfuncheckfeq(L), lfun(L,1), lfuncheckfeq(Lt), lfun(Lt,1)]));
    listput(out, [cp, d, w, Vec(res)]));
  [Vec(out), need];
}
"""

_PARI: Any = None


def pari() -> Any:
    """Lazily create one PARI instance per process (safe with fork-based pools)."""
    global _PARI
    if _PARI is None:
        import cypari2

        _PARI = cypari2.Pari()
        _PARI.allocatemem(3 * 10**9, silent=True)
        _PARI("default(realprecision, 38)")
        _PARI(f'read("{_gp_file()}")')
    return _PARI


_GP_PATH: str | None = None


def _gp_file() -> str:
    """Write GP_CODE to a temporary .gp file once per process and return its path."""
    global _GP_PATH
    if _GP_PATH is None:
        import tempfile

        fd, path = tempfile.mkstemp(suffix=".gp", prefix="paper_c_v2_")
        with open(fd, "w") as fh:
            fh.write(GP_CODE)
        _GP_PATH = path
    return _GP_PATH


def pstr(x: Any) -> str:
    return str(x)


def task_version(_: dict[str, Any]) -> dict[str, Any]:
    g = pari()
    return {"pari_version": str(g("Strprintf(\"%d.%d.%d\", version()[1], version()[2], version()[3])"))}


def task_frey(args: dict[str, Any]) -> list[dict[str, Any]]:
    """Minimal model, invariants, conductor and Kodaira types of y^2 = x(x - A)(x + B)."""
    g = pari()
    out: list[dict[str, Any]] = []
    for a_, b_ in args["pairs"]:
        g(f"E=ellinit([0,{b_ - a_},0,{-a_ * b_},0]); M=ellminimalmodel(E); G=ellglobalred(E)")
        fac = g("factor(G[1])")
        primes = [int(q) for q in fac[0]] if int(g("#factor(G[1])~")) > 0 else []
        local = {}
        for q in primes:
            loc = g(f"elllocalred(E,{q})")
            local[str(q)] = {"f": int(loc[0]), "kodaira": int(loc[1])}
        row = {
            "A": a_, "B": b_, "C": a_ + b_,
            "minimal_model": [int(v) for v in g("M[1..5]")],
            "c4_min": int(g("M.c4")), "disc_min": int(g("M.disc")),
            "conductor": int(g("G[1]")), "conductor_factored": pstr(fac),
            "local_reduction": local,
        }
        if (a_, b_) == (15, 16):
            row["paper_model_1_0_0_m15_0_isomorphic"] = bool(int(g("ellisisom(ellinit([1,0,0,-15,0]), M) != 0")))
        out.append(row)
    return out


def task_family(args: dict[str, Any]) -> list[dict[str, Any]]:
    """Frey curve of (3^p, 4^p, 3^p + 4^p): conductor, v_l(Delta_min), Serre level (prime to p)."""
    g = pari()
    rows = []
    for p in args["primes"]:
        a_, b_ = 3**p, 4**p
        g(f"E=ellinit([0,{b_ - a_},0,{-a_ * b_},0]); M=ellminimalmodel(E); G=ellglobalred(E); f=factor(G[1])")
        nf = int(g("#f~"))
        ls = [int(g(f"f[{i},1]")) for i in range(1, nf + 1)]
        exps = [int(g(f"f[{i},2]")) for i in range(1, nf + 1)]
        vals = {str(q): int(g(f"valuation(M.disc,{q})")) for q in ls}
        serre = [q for q in ls if q != p and vals[str(q)] % p != 0]
        stripped = [q for q in ls if q != p and vals[str(q)] % p == 0]
        prod = 1
        for q in serre:
            prod *= q
        rows.append({
            "p": p, "C_factored": pstr(g(f"factor({a_ + b_})")),
            "conductor_primes": ls, "conductor_exponents": exps,
            "conductor": int(g("G[1]")), "v_l_disc_min": vals,
            "serre_level_primes_prime_to_p": serre, "serre_level_prime_to_p": prod,
            "stripped_primes": stripped,
            "seven_in_serre_level": 7 in serre,
            "seven_divides_C": (a_ + b_) % 7 == 0,
            "v7_disc_min": vals.get("7"),
            "p_divides_v7": (vals.get("7", 0) % p == 0),
            "semistable": all(e == 1 for e in exps),
        })
    return rows


def task_quat(args: dict[str, Any]) -> list[dict[str, Any]]:
    g = pari()
    rows = []
    for p in args["primes"]:
        ram = g(f"A=alginit(nfinit(y), [-1,-{p}]); algramifiedplaces(A)")
        rows.append({
            "p": p, "algebra": f"(-1,-{p})_Q", "ramified_places": pstr(ram),
            "hilbert_2": int(g(f"hilbert(-1,-{p},2)")), "hilbert_p": int(g(f"hilbert(-1,-{p},{p})")),
        })
    return rows


def task_gram(args: dict[str, Any]) -> list[dict[str, Any]]:
    """det of the Gram matrix of the trace form 2*Nrd: O_0 basis vs Lipschitz basis -> index."""
    g = pari()
    rows = []
    for p in args["primes"]:
        m = (p + 1) // 4
        d_o = int(g(f"matdet([2,0,0,1;0,2,1,0;0,1,{2 * m},0;1,0,0,{2 * m}])"))
        d_l = int(g(f"matdet(matdiagonal([2,2,{2 * p},{2 * p}]))"))
        rows.append({"p": p, "det_gram_O0": d_o, "det_gram_lipschitz": d_l,
                     "index": int(g(f"sqrtint({d_l}/{d_o})")), "ratio": f"{d_l}/{d_o}"})
    return rows


def task_qfrep(args: dict[str, Any]) -> dict[str, list[int]]:
    g = pari()
    out = {}
    for p in args["primes"]:
        m = (p + 1) // 4
        v = g(f"Vec(qfrep([2,0,0,1;0,2,1,0;0,1,{2 * m},0;1,0,0,{2 * m}], {args['nmax']}, 1))")
        out[str(p)] = [2 * int(z) for z in v]
    return out


def _graph_counts(job: tuple[int, int]) -> dict[str, Any]:
    p, emax = job
    r = pari()(f"graphcounts({p},{emax})")
    return {"p": p, "vertices": int(r[0]), "dim_S2": int(r[1]), "B2e_00": [int(z) for z in r[2]]}


def _visB(p: int) -> dict[str, Any]:
    t = time.time()
    r = pari()(f"brandtvis({p})")
    orbs = [{"a2_charpoly": pstr(o[0]), "dim": int(o[1]), "frobenius_sign": int(o[2]), "visible": bool(int(o[3])),
             "max_abs_eigenvalue": float(o[4]), "max_abs_imag_part": float(o[5])}
            for o in r[1]]
    return {"p": p, "vertices": int(r[0]), "orbits": orbs, "extra_hecke_ops": int(r[2]),
            "dim_S2": int(r[3]), "seconds": round(time.time() - t, 2)}


def _visA(p: int) -> dict[str, Any]:
    t = time.time()
    r = pari()(f"visA({p})")
    orbs = [{"a2_charpoly": pstr(o[0]), "dim": int(o[1]), "root_number": int(o[2]), "visible": bool(int(o[3]))}
            for o in r[0]]
    return {"p": p, "orbits": orbs, "ok": bool(int(r[1])), "seconds": round(time.time() - t, 2)}


def _lvals(job: tuple[int, int]) -> dict[str, Any]:
    p, dl = job
    t = time.time()
    r = pari()(f"lvals({p},{dl})")
    orbs = []
    for o in r[0]:
        emb = [{"feq_L": int(e[0]), "L_f_1": float(e[1]), "feq_Ltwist": int(e[2]), "L_ftwist_1": float(e[3])}
               for e in o[3]]
        orbs.append({"a2_charpoly": pstr(o[0]), "dim": int(o[1]), "root_number": int(o[2]), "embeddings": emb})
    return {"p": p, "dimlim": dl, "orbits": orbs, "n_coefficients": int(r[1]), "seconds": round(time.time() - t, 2)}


def _pool_map(fn: Any, jobs: list[Any], procs: int) -> list[Any]:
    if procs <= 1 or len(jobs) <= 1:
        return [fn(j) for j in jobs]
    with Pool(processes=procs) as pool:
        return pool.map(fn, jobs, chunksize=1)


def main() -> int:
    task, args = sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    procs = int(args.get("procs", 1))
    if task == "version":
        res: Any = task_version(args)
    elif task == "frey":
        res = task_frey(args)
    elif task == "family":
        res = task_family(args)
    elif task == "quat":
        res = task_quat(args)
    elif task == "gram":
        res = task_gram(args)
    elif task == "qfrep":
        res = task_qfrep(args)
    elif task == "graph_counts":
        res = _pool_map(_graph_counts, [(p, args["emax"]) for p in args["primes"]], procs)
    elif task == "visB":
        res = _pool_map(_visB, list(args["primes"]), procs)
    elif task == "visA":
        res = _pool_map(_visA, list(args["primes"]), procs)
    elif task == "lvals":
        res = _pool_map(_lvals, [(p, args["dimlim"]) for p in args["primes"]], procs)
    else:
        raise SystemExit(f"unknown task {task}")
    json.dump(res, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
