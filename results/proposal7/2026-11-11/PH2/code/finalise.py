"""Finalise PH-2: reads logs/enclosure_ckpt.json, logs/cvode_raw.jsonl, logs/controls.json and writes
enclosures.json, cvode_runs.json, comparison.json, RESULT.md, result.json.
usage (from the PH2 directory):  sage --python3 code/finalise.py
Safe to run while the driver is still running (uses the last checkpoint)."""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ph2_enclose import *

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)
ck = json.load(open("logs/enclosure_ckpt.json"))
res = ck["res"]
raw = [json.loads(l) for l in open("logs/cvode_raw.jsonl") if l.startswith("{")]
solver_errors = [l.strip() for l in open("logs/cvode_raw.jsonl") if not l.startswith("{") and l.strip()]
ctr = json.load(open("logs/controls.json")) if os.path.exists("logs/controls.json") else None
RUSTY_SHA = "af4886f23188baef113e47f3309d64b2bf440e47"


def Bf(x):
    n, d = float(x).as_integer_ratio()
    return R(QQ(n) / QQ(d))


encl = []
for o in res["outputs"]:
    E2, E3 = box_ball(o["box"][0]), box_ball(o["box"][1])
    E1 = 1 - E2 - E3
    comp = []
    for nm, E in (("y1", E1), ("y2", E2), ("y3", E3)):
        comp.append(dict(name=nm, mid=str(E.mid().exact_rational()), rad=str(QQ(E.rad().exact_rational())),
                         mid_dec=float(E.mid().n(53)), abs_width=float((2 * R(E.rad())).upper()),
                         rel_width=float(((2 * R(E.rad())) / abs(R(E.mid()))).upper())))
    encl.append(dict(t=o["tf"], t_exact=o["t"], steps=o["step"], comps=comp, _E=[E1, E2, E3]))
maxrel = {e["t"]: max(c["rel_width"] for c in e["comps"]) for e in encl}
json.dump([{k: v for k, v in e.items() if k != "_E"} for e in encl], open("enclosures.json", "w"), indent=1)

runs = []
cmp_rows = []
for r in raw:
    runs.append(dict(solver="rusty-SUNDIALS cvode crate (Rust port, NOT LLNL C CVODE)", commit=RUSTY_SHA, method="BDF, Newton, dense LU, analytic Jacobian",
                     **r))
fails = sorted(set(float(r["rtol"]) for r in raw))
for e in encl:
    for r in raw:
        if r["tout"] != e["t"]:
            continue
        rtol, atol = float(r["rtol"]), float(r["atol"])
        for i in range(3):
            Y = e["_E"][i]
            d = Bf(r["y"][i]) - Y
            lo = R(0) if d.contains_zero() else R(min(abs(d.lower()), abs(d.upper())))
            lo = R(0) if d.contains_zero() else R(d.abs().lower())
            hi = R(max(abs(d.lower()), abs(d.upper())))
            tol_hi = Bf(rtol) * R(Y.abs().upper()) + Bf(atol)
            tol_lo = Bf(rtol) * R(max(Y.abs().lower(), 0)) + Bf(atol)
            cmp_rows.append(dict(t=e["t"], rtol=rtol, atol=atol, comp=f"y{i+1}", cvode=r["y"][i], err_lo=float(lo.lower()), err_hi=float(hi.upper()),
                                 ratio_lo=float((lo / tol_hi).lower()), ratio_hi=float((hi / tol_lo).upper()),
                                 exceeds=bool(lo.lower() > tol_hi.upper()), within=bool(hi.upper() <= tol_lo.lower())))
json.dump(runs, open("cvode_runs.json", "w"), indent=1)
json.dump(cmp_rows, open("comparison.json", "w"), indent=1)

# secondary literature values (recalled from the SUNDIALS cvRoberts_dns printout, NOT fetched here)
lit = {0.4: [9.8517e-01, 3.3864e-05, 1.4794e-02], 4.0: [9.0551e-01, 2.2406e-05, 9.4459e-02], 40.0: [7.1583e-01, 9.1856e-06, 2.8416e-01]}
litrows = []
for e in encl:
    if e["t"] in lit:
        for i in range(3):
            v = lit[e["t"]][i]
            m = e["comps"][i]["mid_dec"]
            litrows.append((e["t"], f"y{i+1}", v, m, abs(v - m) / abs(m)))

# ---- RESULT.md
Tmax = max(e["t"] for e in encl) if encl else 0
okwidth = [e["t"] for e in encl if maxrel[e["t"]] <= 1e-6]
Twidth = max(okwidth) if okwidth else 0
if Twidth >= 40000:
    outcome = "FOUND"
elif Twidth >= 40:
    outcome = "PARTIAL"
else:
    outcome = "NEGATIVE"
cpu_h = res.get("cpu_s", 0) / 3600.0
L = []
w = L.append
w(f"# PH-2 RESULT: {outcome}\n")
w(f"Rigorous enclosure of Robertson's problem reached T = {Tmax:g} (largest output time with relative width <= 1e-6 in every component: {Twidth:g}). "
  f"Steps {res.get('steps')}, attempts {res.get('attempts')}, driver CPU {cpu_h:.3f} core-hours (getrusage; controls extra, small, not metered). "
  f"Finished flag: {res.get('finished', False)}; stopped: {res.get('stopped')}; failed: {res.get('failed')}.\n")
w("## Enclosure (y(t) in box; y1 = 1 - y2 - y3)\n")
w("| t | y1 mid | y2 mid | y3 mid | rel.width y1 | rel.width y2 | rel.width y3 | abs.width y2 |\n|---|---|---|---|---|---|---|---|")
for e in encl:
    c = e["comps"]
    w(f"| {e['t']:g} | {c[0]['mid_dec']:.15e} | {c[1]['mid_dec']:.15e} | {c[2]['mid_dec']:.15e} | {c[0]['rel_width']:.2e} | {c[1]['rel_width']:.2e} | {c[2]['rel_width']:.2e} | {c[1]['abs_width']:.2e} |")
w("\nExact midpoints/radii as rationals: enclosures.json.\n")
w("## Solver comparison: rusty-SUNDIALS cvode crate (Rust port of CVODE; BDF/Newton/dense; analytic Jacobian), atol = 1e-3*rtol scalar\n")
w("No LLNL C CVODE exists on this host; nothing here is a statement about the C library. Error interval = |y_solver - y| using the enclosure; ratio = error / (rtol|y|+atol), shown as [lo,hi].\n")
w("| rtol | atol | t | comp | err in | ratio in | provably > tol | provably <= tol |\n|---|---|---|---|---|---|---|---|")
for rr in cmp_rows:
    w(f"| {rr['rtol']:g} | {rr['atol']:.1e} | {rr['t']:g} | {rr['comp']} | [{rr['err_lo']:.2e}, {rr['err_hi']:.2e}] | [{rr['ratio_lo']:.2e}, {rr['ratio_hi']:.2e}] | {rr['exceeds']} | {rr['within']} |")
w(f"\nSolver error lines in the raw log (rtol=1e-10, atol=1e-13, the preregistered setting, failed at the first output time with no output; an extra NON-preregistered run with atol=1e-10 was added): {solver_errors}")
w("\nFirst output time per rtol/component with a provable tolerance violation:")
for rt, at in sorted(set((r["rtol"], r["atol"]) for r in cmp_rows)):
    for comp in ("y1", "y2", "y3"):
        ex = [r["t"] for r in cmp_rows if r["rtol"] == rt and r["atol"] == at and r["comp"] == comp and r["exceeds"]]
        w(f"- rtol {rt:g} atol {at:.1e} {comp}: {min(ex) if ex else 'none among the reached output times'}")
got = {}
for r in raw:
    got.setdefault(r["rtol"], 0)
    got[r["rtol"]] += 1
w(f"\nSolver outputs available per rtol (12 requested each): {got}. Missing rtol/time = the solver returned an error (see logs/cvode_err.txt: e.g. ErrTestFailure); it is reported as such, not retried.\n")
w("## Secondary literature values (recalled from the SUNDIALS cvRoberts_dns example printout, 5 digits, NOT fetched or verified here)\n")
for t, c, v, m, rel in litrows:
    w(f"- t={t:g} {c}: literature {v:.5e} vs enclosure mid {m:.5e}, relative difference {rel:.1e} (rounding of the 5-digit print is about 5e-6 relative)")
w("\n## Controls (code/controls.py, logs/controls.json)\n")
if ctr:
    for k, v in ctr.items():
        w(f"- {k}: steps {v['steps']}; " + "; ".join(f"t={r['t']:g}: contained {r['contained']}" + (f", rel.width {r['rel_width']}" if 'rel_width' in r else "") + (f", x(1+1e-6) disjoint {r['exact_x1_plus_1e6_disjoint']}" if 'exact_x1_plus_1e6_disjoint' in r else "") for r in v["rows"]))
else:
    w("- controls.json missing")
w("""
## Method and proof obligations (mapping to code/ph2_enclose.py)
Reduction: (a,b)=(y2,y3), y1 = 1 - a - b (conservation, exact in balls). Region of the vector field: all of R^2 (no positivity used; quasi-positivity / simplex invariance is NOT needed because the tube argument O4 is self-contained. The prereg listed O1 as a region restriction; it was not used.)
- O2 defect: `attempt`: coefficients D_k of f(q(t)) - q'(t) (k=0..2p-2) by exact ball Cauchy products from the dyadic coefficients of q (`Fk`, `taylor_q`); dbar = sum_k ||P^-1 D_k||_2 h^k >= sup_{[0,h]} ||P^-1 D(t)||_2 (triangle inequality).
- O3 one-sided Lipschitz: `attempt`: U = hull_t q([0,h]) + row-norm(P)*rho box (superset of every point on a segment between z(t) and q(t)); `Quad.jac_ball` interval Jacobian (affine in y, exact enclosure of J over U); S = sym(P^-1 J P); nu = upper bound of lambda_max(S) by the closed 2x2 formula in balls (monotone, so the ball evaluation bounds all matrices in the set). Lemma: <e, P^-T P^-1 (f(z)-f(q))> <= nu |e|_P^2 for z,q with segment in U.
- O4 bootstrap: `attempt`: rho = 8(eps0 + dbar h); require (eps0+dbar h) exp(max(nu,0) h) < rho strictly (checked with .upper()/.lower()), so the exact solution cannot leave the rho-tube on [0,h]; global existence on the step follows (it stays in a compact set). Then eps_end = eps0 e^{nu h} + dbar int_0^h e^{nu s} ds (ball).
- O5 jump: m' = mid(q(h)); jump = q(h) - m' as a ball, added in the next norm (`attempt`, eps0).
- O6 basis change: factor sigma_max(P_{k+1}^-1 P_k) by the exact 2x2 singular-value formula in balls (`attempt`).
- P exact balls from floats (`choose_basis`), P^-1 by ball adjugate (`inv2`; rejects det containing 0).
- O7 output: |e_i| <= ||row_i P||_2 eps (Cauchy-Schwarz); box = q(h) +/- that, `attempt`. Output times are hit exactly by truncating the last step (`run`); h as exact rational in a ball H.
- Initial value exact: eps_0 = 0.
Floats: only h choice, eigenvector choice for P, display.

## Unproved assumptions / what an auditor must check
1. Arb ball arithmetic (Sage 9.5 RealBall) is rigorous; no independent second implementation or second precision was run (producer != verifier NOT satisfied; prereg mentioned it).
2. The lemma in O3/O4 (log-norm comparison, first-exit argument) is argued here, not formalized in Lean.
3. Boundary subtleties of ball comparisons: rsqrt/sq helpers clip lower ends at 0 (valid because the quantities are mathematically >= 0); auditors should read them.
4. The solver comparison uses exact doubles of the Rust solver's printed shortest round-trip floats and exactly representable output times (0.1 and 0.4 are the doubles passed to the solver). The Rust right-hand side uses fl(0.04) != 1/25 and fl(1e4*y...) roundings: that is the solver's own arithmetic, counted as solver error.
5. CVODE (Rust port) is not LLNL CVODE; the port's behavior says nothing about the C library.
6. Literature numbers are recalled, not retrieved.
7. Step history: code/ph2_enclose.py stores [t,h,nu,eps_end] every 20 steps in logs/enclosure_ckpt.json (res.history).
""")
hist = res.get("history", [])
if hist:
    w("## Step history (every 20th step: t, h, nu, eps_end)\n")
    sel = hist[:: max(1, len(hist) // 25)]
    for h in sel:
        w(f"- t={h[0]:.6g} h={h[1]:.3e} nu={h[2]:.3e} eps={h[3]:.3e}")
w(f"\n## CPU ledger\nDriver CPU {res.get('cpu_s', 0):.1f} s (checkpoint field cpu_s; cumulative across restarts). Rusty-SUNDIALS runs: a few seconds. Controls: not metered (minutes).\n")
open("RESULT.md", "w").write("\n".join(L))

files = ["PREREG_ITEM.md", "PREREG_ITEM.md.sha256", "RESULT.md", "enclosures.json", "cvode_runs.json", "comparison.json", "logs/cvode_raw.jsonl",
         "logs/controls.json", "logs/enclosure_ckpt.json", "code/ph2_enclose.py", "code/run_robertson.py", "code/controls.py", "code/finalise.py",
         "code/rob_runner/src/main.rs", "code/rob_runner/Cargo.toml"]
sh = {f: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in files if os.path.exists(f)}
json.dump(dict(outcome=outcome, T_reached=Tmax, T_width_ok=Twidth, cpu_core_hours=cpu_h, steps=res.get("steps"), finished=res.get("finished", False),
               rusty_commit=RUSTY_SHA, sha256=sh), open("result.json", "w"), indent=1)
print(outcome, Tmax, Twidth, cpu_h)
