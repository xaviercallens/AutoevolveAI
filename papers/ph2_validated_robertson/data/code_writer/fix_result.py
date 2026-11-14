from pathlib import Path
p = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal7/2026-11-11/PH2/RESULT.md")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (old[:60], n, count)
    s = s.replace(old, new)
rep("stopped: None;", "stopped: cpu_cap (cumulative 29900 s, main-session cap; the checkpoint omits the flag because of a bookkeeping order bug in run(), ph2_enclose.py:342-343: res[\"stopped\"] is set after save(). The code was left unchanged so that it matches the code that produced the run);")
rep("analytic Jacobian), atol = 1e-3*rtol scalar", "analytic Jacobian), atol = 1e-3*rtol scalar for rtol 1e-4, 1e-6, 1e-8; rtol 1e-10 rows use atol = 1e-10 (NON-preregistered: the preregistered atol 1e-13 run failed with ErrTestFailure and produced no output)")
rep("y2: none among the reached output times", "y2: none, because the tolerance for y2 is atol-dominated (y2 <= 3.6e-5); relative to rtol*|y2| alone the error exceeds rtol by up to 169x (1e-10), 20x (1e-8), 11x (1e-6), 4.1x (1e-4)", 4)
rep("{0.0001: 12, 1e-06: 12, 1e-08: 12, 1e-10: 12}.", "{0.0001: 12, 1e-06: 12, 1e-08: 12, 1e-10: 12} (the 1e-10 count is the non-preregistered atol=1e-10 run; the preregistered 1e-10/1e-13 run gave 0 outputs). Only 10 of the 12 times have an enclosure.")
rep("shown as [lo,hi].\n", "shown as [lo,hi]. NOTE: 'provably > tol' compares the GLOBAL error with the per-component tolerance scale; CVODE controls a local error estimate, so this is not a breach of the solver's contract.\n")
rep("## Secondary literature values (recalled from the SUNDIALS cvRoberts_dns example printout, 5 digits, NOT fetched or verified here)",
    "## Secondary values: SUNDIALS cvRoberts_dns printout (solver output at rtol=1e-4, NOT the true solution; recalled, not fetched)")
rep("(rounding of the 5-digit print is about 5e-6 relative)", "(differences are consistent with rtol=1e-4 solver error)", 9)
j = s.index("## Method and proof obligations")
s = s[:j].rstrip("\n") + "\n\nC-1 has no power for lin y2 (y2 = e^{-1e4 t}, relative width >= 2e4): never rejected; this is adjudicated as a powerless test, not a soundness failure (AUDIT.md section 4). The controls in logs/controls.json were run on a pre-final ph2_enclose.py; the auditor's rerun on the final code gives the same verdicts.\n\n" + s[j:]
rep("no independent second implementation or second precision was run (producer != verifier NOT satisfied; prereg mentioned it).",
    "independent MPFI/Lohner integrator by the auditor (AUDIT.md section 3) confirms t=1, 10 and 40 (the t=40 run finished after the first audit text; AUDIT.md Addendum); t>40 is single-implementation. Independent check exists for t <= 40.")
k = s.index("- O6 basis change:")
e = s.index("\n", k)
s = s[:e] + " Correction (audit): O6 uses the exact 2x2 spectral norm (prereg: Frobenius); tighter and valid." + s[e:]
rep("## Step history (every 20th step: t, h, nu, eps_end)", "## Step history (a subsample of the every-20th-step history)")
rep("## CPU ledger", "## Preregistration anchoring caveat\nPREREG_ITEM.md was first git-committed 2026-11-13 (00328e1), after the launch; the freeze rests on file mtimes and a self-hash.\n\n## Audit status\nIndependently audited once by an AI agent (AUDIT.md, ACCEPT_WITH_CORRECTIONS); the eleven corrections of AUDIT.md section 8 are applied to this file (correction 8 per the Addendum). No human audit.\n\n## CPU ledger")
p.write_text(s)
print("ok")
