# SLR-18 independent audit (producer != verifier)

Date: 2026-10-31. Auditor: separate Opus agent, which did not write any producer code and did not read
`code/slr_exact.py`, `code/check_cover.c` or `code/verify_all.py`. Subject: `RESULT.md`, `result.json`, `certificates/`,
`controls/` and `logs/` at commit bbfc565. Every heavy job ran under `taskset -c 1`. The auditor's tools are reproduced
verbatim in the Appendix, so the work can be rebuilt after `/tmp/slraudit/` is gone.

**Verdict: ACCEPT_WITH_CORRECTIONS.**
- All 34 certificates (n = 5..38) are valid counterexamples to the shifted lonely runner conjecture in the sense of
  Blanco-Criado-Santos (BCS) Conj. 1.1(ii). An independent third checker confirms this with two different exact
  methods.
- The auditor's Lean replay kernel-checks the exact covering statement: for **every n = 5..38** (34/34 rc 0, only whitelisted axioms; n = 18..38 are the new cases).
- No published result conflicts with the certificates.
- The corrections concern wording, tiers, provenance and bookkeeping. None changes the mathematical claim.

## 1. Definition pinned from the sources (read by the auditor on alphaXiv, not taken from the producer)

- **BCS**, arXiv 2603.24784 v4 (24 Oct 2026):
  - p. 2, Conj. 1.1(ii): "Let v_1..v_n be non-zero real numbers. ... If the |v_i| are all different, for every
    s_1..s_n in R there is a t in R such that dist(s_i + v_i t, Z) >= 1/(n+1) for all i."
  - Def. 1.3: gamma(v; s) = sup_t min_i dist(s_i + v_i t, Z) with s in [0,1]^n, and gamma_sh(v) = min_s gamma(v; s).
  - p. 3: integer v is no loss of generality.
  - p. 2: with repeated v_i the conjecture fails trivially (all v_i equal, s_i = i/n), so distinctness is essential.
- **Zhang**, arXiv 2608.13599 v3:
  - App. A: distinct positive integers, s in [0,1)^n, gamma = max_t min_i ||s_i + v_i t||, and
    Gamma(n) = min_{|v|=n} gamma_min(v).
  - Question 8.5: "is Gamma(n) < 1/(n+1) for every n >= 5?"
  - p. 19: "open only for 18 <= n <= 94".
- **Poliakova**, arXiv 2609.23952 v1:
  - Sec. 1: distinct positive integer velocities, shifts in R/Z, t in R/Z, and
    1/(n+1+E_n) = inf_{v,s} max_t min_i ||s_i + v_i t||.
  - Theorem 2 (E_n >= 1) covers only n >= 95.
  - p. 3: "finding counterexamples for the remaining 18 <= n <= 94 would establish that SLR is false for all n >= 5".

Consequences for the certificates:
- (a) A counterexample of size n means exactly n runners, with pairwise distinct positive integer velocities, real
  shifts, and gamma(v; s) < 1/(n+1) strictly.
- (b) With integer v the function is 1-periodic, so t in R reduces to t in R/Z. The maximum is attained, so
  gamma < delta <=> for every t some i has ||s_i + v_i t|| < delta <=> the **open** arcs cover the circle. That is
  the producer's criterion.
- (c) Shifts matter only mod 1, so the shift convention does not matter. Rational shifts are a special case of real
  ones. Normalising one shift to 0 is not needed.
- (d) Positive velocities suffice, since the conjecture is stated for nonzero reals with distinct |v_i|.
- (e) The certificates give upper bounds only: gamma_sh(v) <= gamma(v; s) < 1/(n+1), hence Gamma(n) < 1/(n+1) and
  E_n > 0. The auditor's exact gamma(v; s) gives the explicit bound E_n >= 1/gamma(v; s) - (n+1), which lies in
  [0.0961, 0.1098] for n = 18..38.

All 34 certificate files have the right form:
- v consists of distinct positive integers and len(v) = n;
- delta = 1/(n+1);
- s_i = a_i/D, and the `s` strings equal a_i/D exactly;
- the arcs are open.

**They meet the literature definition.**

## 2. Third checker (written from scratch, different style)

`audit_check.py` (Appendix A, standard library only) has two methods and a validation step:
- **Method A**: exact interval subtraction with `fractions.Fraction`. It starts from the closed set [0,1] and
  removes every integer translate of every open arc. The arcs cover if nothing is left. Single points count as
  uncovered, so tangencies are rejected.
- **Method B**: the exact value gamma(v; s) in integer arithmetic. f(t) = min_i ||s_i + v_i t|| is evaluated at every
  candidate maximiser: all pairwise crossings s_i + v_i t = ±(s_j + v_j t) mod 1, and all single-runner peaks.
  The arcs cover if gamma < delta.
- **Validation**: len(v) = n, positive integer velocities, no repeats, delta = 1/(n+1), and each s string equals a/D.

### 2a. Results on every certificate

All 34 files cert_n005..cert_n038 are valid. Method A says COVERED for all of them, and Method B gives
gamma < 1/(n+1) for all of them. Exact gamma(v; s):

| n | gamma(v;s) | 1/gamma - (n+1) | n | gamma(v;s) | 1/gamma - (n+1) |
|---|---|---|---|---|---|
| 18 | 2117/40439 | 0.1020 | 29 | 3349/100800 | 0.0985 |
| 19 | 7323/147200 | 0.1011 | 30 | 989/30754 | 0.0961 |
| 20 | 1003/21171 | 0.1077 | 31 | 5869/188416 | 0.1036 |
| 21 | 841/18588 | 0.1023 | 32 | 11579/383328 | 0.1054 |
| 22 | 8427/194672 | 0.1010 | 33 | 16814/573407 | 0.1029 |
| 23 | 7264/175123 | 0.1083 | 34 | 4467/156808 | 0.1036 |
| 24 | 11554/290029 | 0.1020 | 35 | 342/12349 | 0.1082 |
| 25 | 1657/43264 | 0.1098 | 36 | 367/13616 | 0.1008 |
| 26 | 3443/93312 | 0.1019 | 37 | 32142/1224565 | 0.0986 |
| 27 | 10268/288535 | 0.1004 | 38 | 74066/2896103 | 0.1017 |
| 28 | 2312/67285 | 0.1025 | | | |

**Literature consistency of Method B.** For n = 5..15 the certificates use v = [n], and BCS Table 2 gives the exact
gamma_sh(1..n). Each certificate's gamma(v; s) must therefore be at least the published value, and all 11 are:

| n | cert gamma | BCS gamma_sh | n | cert gamma | BCS gamma_sh |
|---|---|---|---|---|---|
| 5 | 189/1154 | 15/94 | 11 | 1332/16135 | 1/14 |
| 6 | 9/64 | 9/67 | 12 | 619/8112 | 6/91 |
| 7 | 505/4096 | 25/214 | 13 | 4003/56466 | 1/16 |
| 8 | 379/3456 | 1/10 | 14 | 1669/25200 | 71/1228 |
| 9 | 791/8000 | 5/58 | 15 | 763/12288 | 1/18 |
| 10 | 872/9685 | 27/349 | | | |

### 2b. Adversarial tests (`adversarial.py`, Appendix B)

| test | outcome |
|---|---|
| [n], s = 0, delta = 1/(n+1), n = 2..40 | 0/39 covered; gamma = 1/(n+1) exactly in all 39 cases (Dirichlet) |
| published gammas (BCS Prop. 5.11, 5.12) | (1..5) gives 15/94; (2,3,4,5,6,8) gives 2/15; (1..6) with s = (0,39,37,51,62,54)/67 gives 9/67. All exactly as published |
| tangency on n = 5, 18, 29, 38 | not covered at delta = gamma, covered at gamma + 1e-12, not covered at gamma - 1e-12 (all 4) |
| producer control N_P1 (delta = 15/94) | not covered; uncovered points include 63/188, 39/94 and 45/94 (the published tangent instants) |
| duplicated velocity, zero velocity, delta = 1/n | each flagged invalid |
| trivial repeated-velocity cover (v = 1^6, s = i/6) | covers, but flagged invalid (repeated velocity) |
| shift one runner by delta/2, both signs | n = 18: 36/36 broke; n = 38: 72/76 broke (4 runners redundant); 0 disagreements between Method A and Method B |
| fuzz: 400 random small instances × 4 deltas | 0 mismatches between Method A and Method B; a 4000-point float grid never exceeds the exact gamma |
| producer positive controls P1, P2 | covered at 1/6 and 1/7; gamma = 15/94 and 2/15 |

These results agree with the producer's controls (`logs/controls_run1.json`). The auditor's perturbation is larger
(delta/2 instead of 1/(10·Σv)), so more perturbations break, as expected.

### 2c. Lean kernel replay (auditor)

The generator `gen_lean.py` (Appendix C) is untrusted. Its output was compiled with
`scripts/certified_numerics/lean_pinned.py` (Lean 4.34.1 + Mathlib d13f23b7) and `#print axioms`. The files import
`Mathlib.Tactic` only and contain no `sorry`, `admit`, `native_decide` or `axiom`. The kernel-checked statement is
exactly the covering statement. For n = 18:

```lean
def v : Fin 18 → ℕ := ![1, 2, ..., 18]
def s : Fin 18 → ℚ := ![3521/5777, ..., 4869/5777]       -- a_i/D of cert_n018.json
theorem v_injective : Function.Injective v
theorem v_pos : ∀ i, 0 < v i
theorem cover : ∀ t : ℝ, ∃ i : Fin 18, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / 19
```

The proof reduces t to t - ⌊t⌋ in [0,1), splits on a chain of arc right endpoints (82 cases at n = 18, 449 at
n = 38), and closes each case with `linarith`. `cover` + `v_injective` + `v_pos` together say that the certificate
is a counterexample of size n to Conj. 1.1(ii).

Controls:
- P1 (n = 5, delta = 1/6): rc 0, axioms propext, Classical.choice, Quot.sound.
- The same file tampered to delta = 15/94 (the exact gamma): rc 1, `linarith` fails, as it should.
- A failed first n = 38 attempt (parse error) still printed axioms for `cover`, so rc is the gate and the axiom
  line alone proves nothing.

**All-n replay** (`run_all_lean.py`, Appendix D; sequential on core 1, 3456 s in total). Every certificate cert_n005..cert_n038 compiled with **rc 0**. There were no banned tokens. `cover` and `v_injective` depend on [propext, Classical.choice, Quot.sound], and `v_pos` depends on [propext]. Compile time per n: 5 (17 s); 6 (16 s); 7 (18 s); 8 (19 s); 9 (23 s); 10 (32 s); 11 (29 s); 12 (27 s); 13 (38 s); 14 (49 s); 15 (43 s); 16 (58 s); 17 (55 s); 18 (80 s); 19 (63 s); 20 (57 s); 21 (68 s); 22 (94 s); 23 (98 s); 24 (102 s); 25 (107 s); 26 (108 s); 27 (109 s); 28 (110 s); 29 (158 s); 30 (161 s); 31 (170 s); 32 (193 s); 33 (172 s); 34 (154 s); 35 (198 s); 36 (203 s); 37 (300 s); 38 (327 s).

Gate scope: the gate was `lean_pinned.py` plus a manual `#print axioms`, as the audit brief asked. It was **not**
`anse/formal/lean_runner.py` (the binding rule in CLAUDE.md), and no statement lock was run. Read the Lean result as
"Tier A by the brief's criterion; repo gates pending" until the files are committed and re-run through
`lean_runner.py`.

## 3. Literature / scoop check (2026-10-31, by the auditor)

- **alphaXiv** (discover with recency, and with published_after 2026-10-01) for "shifted lonely runner",
  "lonely runner" and "counterexamples": the only shifted-LRC counterexample papers are 2603.24784 and 2609.23952.
  Newer hits are about other problems: 2610.23790 (unshifted ML(V)), 2610.37711 (view-obstruction for spheres),
  2610.35206 (runner-flow PDE).
- **Web search** (extended): no source settles any n in 18..94.
  - Zhang v3 (18 Oct 2026) and Poliakova v1 both say this range is open.
  - BCS v4 (24 Oct 2026) states failure only for n in 5..17, and E_n >= 1 only for n >= 95.
- **No conflict found.**
  - The shifted LRC is proved only for n <= 4 (Alcántara-Criado-Santos; BCS Remark 1.2).
  - Nothing published gives a lower bound on gamma_sh or Gamma(n) for n in 18..38.
  - Beck-Everett (2609.06259 v2, Thm 3.2) require a shifted counterexample to satisfy a small relation m·v = 0. The
    certificates satisfy it: [n] has 2·1 - 2 = 0, and the swapped sets for n >= 29 contain many relations a + b = c.
  - Zhang Lemma A.1 is consistent with the certificates.
  - BCS Table 2 gives 1/gamma_sh(1..15) = 18 (E = 2), so it is plausible that [n] still fails at n = 18..28.
- **Remaining scoop risk:** arXiv listings after the alphaXiv index, unpublished BCS/Criado computations (the
  producer saw repository outputs only up to n = 13), and private communications.

## 4. Bookkeeping

- `result.json` sha256: all 113 hashed files match.
- 333 tracked files under `logs/fast_tmp/` are not in the hash list (correction 5). No `__pycache__` is tracked.
- **CPU ledger:**
  - `cpu_seconds_by_log` sums to 101746.4 s and `cpu_seconds_manual_runs` is 5344.8 s, for a total of 107091.2 s =
    29.75 core-h, within the 30 core-h cap.
  - Three logs are counted at 0.0 s (`certify_file.log`, `deletion_probe_N11.log`, `smooth_test.log`), but their
    runs do appear in `logs/manual_runs_ledger.json` (certify_file --polish 4.4 s, deletion probe 135.6 s,
    smooth.py 5.8 s). `swap2_36_94.log` exists.
  - The controls/checks entry (300 s) is an estimate, as the producer says, and the margin to the cap is about
    900 s. The auditor did not re-derive the per-log figures.
- **Third-party text:** grep for criado/copyright/arxiv-pdf finds only citations in RESULT.md and its template.
  No copy of Criado's `consecutive.out` and no paper text is tracked. This is grep-level only; not every log was
  read in full.
- **Auditor CPU:** about 1.5 core-h on core 1, most of it the all-n Lean replay (3456 s). For a few minutes an early Lean
  n = 18 compile overlapped with the adversarial script on core 1 (two processes on one core). This is recorded,
  not hidden. The A1 scheduler's `lean` process was pinned to core 0, so it did not share core 1.

## 5. Corrections (old -> new)

1. `result.json` "claim": "... checked in exact integer arithmetic by two independent checkers." -> "... checked in
   exact integer arithmetic by two producer checkers (different criteria and languages, same author) and by an
   independent auditor checker; covering statement kernel-checked in Lean by the auditor (AUDIT.md §2c)."
2. `result.json` "tier": "C (exact integer checks, two independent checkers; no Lean replay)" -> "A by the audit brief's criterion for n = 5..38 (auditor Lean kernel replay of the exact covering statement, AUDIT.md §2c; repo gates lean_runner.py + statement lock pending), on top of three exact checkers (one independent)"
3. RESULT.md, Status line: "Contiguous closed range: n in [18, 38]." -> "Counterexamples certified for every n in
   [18, 38]. Together with n = 5..17 (BCS) and n >= 95 (Poliakova), the shifted LRC is known to fail for n in 5..38
   and n >= 95; n in 39..94 stays open."
4. RESULT.md, "What is NOT claimed" and "Tiers": "Not Lean-checked (Tier C, not A). No Lean replay was attempted." ->
   "Producer: no Lean replay. Auditor: Lean kernel replay of the exact covering statement (AUDIT.md §2c, standard
   axioms); Tier A by the audit brief's criterion, repo gates (lean_runner.py, statement lock) pending."
5. Hash coverage: add the 333 `logs/fast_tmp/*.txt` files to `result.json` "sha256", or untrack them. Either way,
   state in RESULT.md that they are raw search scratch.
6. RESULT.md, Deviations: "the margins are E of about 0.125, which is too small to chain" -> "the exact margins
   1/gamma(v;s) - (n+1) lie in [0.0961, 0.1098] for n = 18..38 (AUDIT.md §2a), too small to chain". 0.125 is the
   search target radius, not the achieved margin.
7. RESULT.md, "What is NOT claimed", third bullet: "No exact gamma_sh values and no value of E_n beyond E_n > 0" ->
   "No exact gamma_sh values. The auditor's exact gamma(v;s) gives explicit lower bounds
   E_n >= 1/gamma(v;s) - (n+1) >= 0.096 for n = 18..38."
8. Commit `gen_lean.py` (Appendix C) and the generated `.lean` files, for example under
   `formal_cert/Programmes/SLR18/`. Re-run them through `anse/formal/lean_runner.py` with a statement lock before a
   Tier A label is published.

Wording check: RESULT.md already says "No breakthrough", "Nothing about the unshifted Lonely Runner Conjecture",
"upper bounds only", and that n in 39..94 stays open with no evidence either way. That is appropriate. Do not write
"the shifted LRC fails for all n >= 5": the preregistered title says so, but this result does not support it.

## 6. What remains unverified

- Repo-gate Lean verification (lean_runner.py + statement lock) of the auditor's Lean files.
- Scoop completeness beyond the alphaXiv index and web search, including unpublished BCS computations.
- The per-log CPU figures and the estimated controls/checks ledger entry.
- The producer's search code. It is untrusted and not needed for validity.
- A full reading of every log for third-party text (grep-level only).

## Reproduction

```
python3 -I audit_check.py results/proposal5/2026-10-27/SLR18/certificates      # §2a
python3 -I adversarial.py results/proposal5/2026-10-27/SLR18/certificates      # §2b
python3 -I gen_lean.py results/proposal5/2026-10-27/SLR18/certificates/cert_n018.json N18 > SLRN18.lean
python3 scripts/certified_numerics/lean_pinned.py compile SLRN18.lean --timeout 3600
```

Expected sha256 of the generated files: SLRN18.lean 19a312563d9277568341a0a01bb21c6f83c4c8fced45d85869fa7fd379faaa65; SLRN38.lean 9dcac924e547ad82f39f7bd77ed4f8bfc70cccf44cee39f4d4136a3f01154dd4 (the generator is deterministic). `adversarial.py` imports `audit_check` from /tmp/slraudit; edit that path if you copy it elsewhere.

## Appendix (auditor tools, verbatim)

### A. `audit_check.py`

```python
#!/usr/bin/env python3
"""Independent auditor checker for shifted-lonely-runner covering certificates.

Method A: exact interval subtraction with fractions.Fraction on [0,1] (circle, t in R/Z since v integer).
  Uncovered set starts as the closed interval [0,1]; each open arc (c-r, c+r) (all integer translates
  meeting [0,1]) is removed; covered iff nothing remains (closed pieces, including single points, count).
Method B: exact gamma(v;s) = max_t min_i ||s_i + v_i t|| by enumerating every candidate maximiser
  (pairwise crossings s_i+v_i t = +-(s_j+v_j t) mod 1 and single-runner peaks at 1/2), integer arithmetic.
Open arcs of radius delta cover iff gamma < delta.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from math import ceil, floor


def validate(cert: dict) -> list[str]:
    errs: list[str] = []
    n, v, a, D = cert["n"], cert["v"], cert["a"], cert["D"]
    if len(v) != n or len(a) != n:
        errs.append("length mismatch")
    if any((not isinstance(x, int)) or x <= 0 for x in v):
        errs.append("non-positive or non-int velocity")
    if len(set(v)) != len(v):
        errs.append("repeated velocity")
    if not isinstance(D, int) or D <= 0:
        errs.append("bad D")
    if "s" in cert:
        for ai, si in zip(a, cert["s"]):
            if F(si) != F(ai, D):
                errs.append(f"s string {si} != {ai}/{D}")
    if "delta_num" in cert and F(cert["delta_num"], cert["delta_den"]) != F(1, n + 1):
        errs.append("delta != 1/(n+1)")
    return errs


def cover_A(v: list[int], s: list[F], delta: F) -> tuple[bool, list[tuple[F, F]]]:
    unc: list[tuple[F, F]] = [(F(0), F(1))]
    for vi, si in zip(v, s):
        r = delta / vi
        kmin = floor(si - delta) - 1
        kmax = ceil(si + vi + delta) + 1
        for k in range(kmin, kmax + 1):
            c = (k - si) / vi
            lo, hi = c - r, c + r
            if hi <= 0 or lo >= 1:
                continue
            new: list[tuple[F, F]] = []
            for (x, y) in unc:
                if hi <= x or lo >= y:
                    new.append((x, y))
                    continue
                if x <= lo:
                    new.append((x, lo))
                if hi <= y:
                    new.append((hi, y))
            unc = new
            if not unc:
                return True, []
    return (len(unc) == 0), unc


def evalt(v: list[int], a: list[int], D: int, t: F) -> F:
    p, Q = t.numerator, t.denominator
    den = D * Q
    m = den
    for vm, am in zip(v, a):
        num = (am * Q + vm * p * D) % den
        d = min(num, den - num)
        if d < m:
            m = d
    return F(m, den)


def gamma_B(v: list[int], a: list[int], D: int) -> tuple[F, F]:
    n = len(v)
    best, arg = F(-1), F(0)
    seen: set[F] = set()

    def consider(p: int, Q: int) -> None:
        nonlocal best, arg
        t = F(p, Q) % 1
        if t in seen:
            return
        seen.add(t)
        val = evalt(v, a, D, t)
        if val > best:
            best, arg = val, t

    for i in range(n):
        for k in range(-1, v[i] + 1):
            consider(2 * k * D + D - 2 * a[i], 2 * D * v[i])
        for j in range(i + 1, n):
            for sgn in (1, -1):
                w = v[i] + sgn * v[j]
                if w == 0:
                    continue
                for k in range(-abs(w) - 3, abs(w) + 4):
                    p = k * D - (a[i] + sgn * a[j])
                    consider(p, D * w)
    return best, arg


def check(cert: dict, do_gamma: bool = True) -> dict:
    errs = validate(cert)
    n, v, a, D = cert["n"], cert["v"], cert["a"], cert["D"]
    delta = F(cert.get("delta_num", 1), cert.get("delta_den", n + 1))
    s = [F(x, D) for x in a]
    if any((not isinstance(x, int)) or x <= 0 for x in v):
        return {"n": n, "valid": False, "errs": errs, "coverA": None, "coverB": None}
    covA, unc = cover_A(v, s, delta)
    out: dict = {"n": n, "valid": not errs, "errs": errs, "delta": str(delta), "coverA": covA,
                 "uncovered_sample": [(str(x), str(y)) for x, y in unc[:3]]}
    if do_gamma:
        g, t = gamma_B(v, a, D)
        out.update({"gamma": str(g), "argmax": str(t), "coverB": g < delta,
                    "E_lower": float(1 / g - (n + 1)) if g > 0 else None})
    return out


if __name__ == "__main__":
    import os
    paths: list[str] = []
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            paths += sorted(os.path.join(arg, f) for f in os.listdir(arg) if f.endswith(".json"))
        else:
            paths.append(arg)
    for path in paths:
        with open(path) as fh:
            cert = json.load(fh)
        print(json.dumps({"file": path.split("/")[-1], **check(cert)}), flush=True)
```

### B. `adversarial.py`

```python
#!/usr/bin/env python3
"""Adversarial tests of the auditor checker (audit_check.py)."""
from __future__ import annotations

import json
import os
import random
import sys
from fractions import Fraction as F

sys.path.insert(0, "/tmp/slraudit")
from audit_check import check, cover_A, evalt, gamma_B  # noqa: E402

CERTS = sys.argv[1]
res: dict = {}

# 1. [n], s=0 at delta=1/(n+1): must NOT cover; gamma must equal 1/(n+1) (Dirichlet + t=1/(n+1)).
bad = []
for n in range(2, 41):
    v = list(range(1, n + 1)); a = [0] * n
    c = check({"n": n, "v": v, "a": a, "D": 1})
    if c["coverA"] or c["coverB"] or F(c["gamma"]) != F(1, n + 1):
        bad.append(n)
res["T1_unshifted_[n]_n2..40_failures"] = bad

# 2. Published gammas (Blanco-Criado-Santos Prop 5.11, 5.12).
pub = [((1, 2, 3, 4, 5), (0, 46, 38, 47, 72), 94, F(15, 94)),
       ((2, 3, 4, 5, 6, 8), (0, 29, 17, 0, 16, 22), 30, F(2, 15)),
       ((1, 2, 3, 4, 5, 6), (0, 39, 37, 51, 62, 54), 67, F(9, 67))]
res["T2_published_gamma"] = [(str(gamma_B(list(v), list(a), D)[0]), str(g)) for v, a, D, g in pub]

# 3. Tangency: every certificate at delta = its own exact gamma must fail; at gamma + 1/10^12 must cover.
tang = []
files = sorted(f for f in os.listdir(CERTS) if f.endswith(".json"))
certs = {f: json.load(open(os.path.join(CERTS, f))) for f in files}
for f in ["cert_n005.json", "cert_n018.json", "cert_n029.json", "cert_n038.json"]:
    c = certs[f]
    g, _ = gamma_B(c["v"], c["a"], c["D"])
    s = [F(x, c["D"]) for x in c["a"]]
    at, _ = cover_A(c["v"], s, g)
    above, _ = cover_A(c["v"], s, g + F(1, 10**12))
    below, _ = cover_A(c["v"], s, g - F(1, 10**12))
    tang.append((f, str(g), at, above, below))
res["T3_tangency(file,gamma,cover@gamma,cover@gamma+eps,cover@gamma-eps)"] = tang

# 4. Duplicated velocity / wrong n / wrong delta must be flagged by validate.
c = dict(certs["cert_n018.json"]); v = list(c["v"]); v[-1] = v[0]; c["v"] = v
r4a = check(c, do_gamma=False)
c2 = dict(certs["cert_n018.json"]); c2["delta_den"] = 18
r4b = check(c2, do_gamma=False)
c3 = dict(certs["cert_n018.json"]); c3["v"] = [0] + c3["v"][1:]
r4c = check(c3, do_gamma=False)
res["T4_dup_velocity_errs"] = r4a["errs"]; res["T4_wrong_delta_errs"] = r4b["errs"]; res["T4_zero_velocity_errs"] = r4c["errs"]
# trivial repeated-velocity counterexample v_i=1, s_i=i/n covers but is invalid
n = 6
r4d = check({"n": n, "v": [1] * n, "a": list(range(n)), "D": n})
res["T4_trivial_repeated(valid,coverA)"] = (r4d["valid"], r4d["coverA"])

# 5. Perturbations: shift one runner of n18/n38 by +-1/2 of an arc (delta/(2 v_i)) in t-space, i.e. a_i += +-D*delta/2.
pert = {}
for f in ["cert_n018.json", "cert_n038.json"]:
    c = certs[f]; n = c["n"]; D = c["D"]
    broke = 0; tot = 0; disagree = 0
    for i in range(n):
        for sgn in (1, -1):
            a2 = list(c["a"]); D2 = D * 2 * (n + 1)
            a2 = [x * 2 * (n + 1) for x in a2]; a2[i] += sgn * D  # shift s_i by delta/2
            cc = {"n": n, "v": c["v"], "a": a2, "D": D2}
            r = check(cc)
            tot += 1; broke += (not r["coverA"]); disagree += (r["coverA"] != r["coverB"])
    pert[f] = {"perturbations": tot, "broken": broke, "A_vs_B_disagree": disagree}
res["T5_shift_by_delta/2"] = pert

# 6. Random fuzz: method A vs method B vs dense float grid on small instances.
rng = random.Random(20261031)
mism = 0; tests = 0; grid_viol = 0
for _ in range(400):
    n = rng.randint(2, 7)
    v = rng.sample(range(1, 13), n); D = rng.randint(2, 60); a = [rng.randrange(D) for _ in range(n)]
    g, _ = gamma_B(v, a, D)
    # grid check: no grid point exceeds gamma
    N = 4000
    gm = max(min(abs(((am / D + vm * k / N) + 0.5) % 1 - 0.5) for vm, am in zip(v, a)) for k in range(N))
    if gm > float(g) + 1e-12: grid_viol += 1
    for delta in (g, g + F(1, 10**9), g - F(1, 10**9), F(1, n + 1)):
        if delta <= 0: continue
        ca, _ = cover_A(v, [F(x, D) for x in a], delta)
        tests += 1; mism += (ca != (g < delta))
res["T6_fuzz"] = {"instances": 400, "tests": tests, "A_vs_B_mismatch": mism, "grid_exceeds_gamma": grid_viol}
print(json.dumps(res, indent=1))
```

### C. `gen_lean.py`

```python
#!/usr/bin/env python3
"""Generate a Lean 4 file proving the covering statement for one certificate.

Statement: for all real t there are i and an integer k with |s_i + v_i t - k| < 1/(n+1),
plus injectivity and positivity of v. Proof: reduce t to u = t - floor t in [0,1), split [0,1) by a chain of
arc right endpoints b_1 < ... < b_m (computed here in exact rationals, untrusted: the kernel re-checks every case).
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from math import ceil, floor


def chain(v: list[int], s: list[F], delta: F) -> list[tuple[int, int, F, F]]:
    arcs = []
    for i, (vi, si) in enumerate(zip(v, s)):
        for k in range(floor(si - delta) - 1, ceil(si + vi + delta) + 2):
            c = (k - si) / vi
            lo, hi = c - delta / vi, c + delta / vi
            if hi > 0 and lo < 1:
                arcs.append((i, k, lo, hi))
    out = []
    cur = F(0)
    first = True
    while True:
        cand = [a for a in arcs if a[2] < cur and a[3] > cur]
        if not cand:
            raise SystemExit(f"gap at {cur}")
        best = max(cand, key=lambda a: a[3])
        out.append(best)
        if best[3] >= 1:
            return out
        cur = best[3]


def q(x: F) -> str:
    return f"({x.numerator} / {x.denominator} : ℝ)" if x.denominator != 1 else f"({x.numerator} : ℝ)"


def main() -> None:
    cert = json.load(open(sys.argv[1]))
    name = sys.argv[2]
    n, v, a, D = cert["n"], cert["v"], cert["a"], cert["D"]
    delta = F(1, n + 1)
    s = [F(x, D) for x in a]
    ch = chain(v, s, delta)
    L = []
    L.append("import Mathlib.Tactic")
    L.append("")
    L.append("set_option linter.unusedSimpArgs false")
    L.append("set_option maxHeartbeats 0")
    L.append(f"namespace SLRAudit.{name}")
    L.append("")
    L.append(f"/-- velocities of certificate n = {n} -/")
    L.append(f"def v : Fin {n} → ℕ := ![{', '.join(map(str, v))}]")
    L.append(f"/-- shifts s_i = a_i / {D} -/")
    L.append(f"def s : Fin {n} → ℚ := ![{', '.join(f'{x}/{D}' for x in a)}]")
    L.append("")
    L.append("theorem v_injective : Function.Injective v := by decide")
    L.append("theorem v_pos : ∀ i, 0 < v i := by decide")
    L.append("")
    L.append(f"/-- covering: for every real t some runner is within distance < 1/{n+1} of an integer. -/")
    L.append(f"theorem cover : ∀ t : ℝ, ∃ i : Fin {n}, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / {n+1} := by")
    L.append("  intro t")
    L.append("  have h0 : (0 : ℝ) ≤ t - ⌊t⌋ := by have := Int.floor_le t; linarith")
    L.append("  have h1 : t - ⌊t⌋ < (1 : ℝ) := by have := Int.lt_floor_add_one t; linarith")
    prev = "h0"
    for j, (i, k, lo, hi) in enumerate(ch):
        last = j == len(ch) - 1
        vi = v[i]
        wit = f"  refine ⟨{i}, {k} + {vi} * ⌊t⌋, ?_⟩"
        tac = [wit,
               "  simp only [v, s, Matrix.cons_val, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons] at *",
               "  rw [abs_lt]",
               "  push_cast",
               f"  constructor <;> linarith only [{prev}, {'h1' if last else f'c{j}'}]"]
        if last:
            L += tac
        else:
            L.append(f"  rcases lt_or_ge (t - ⌊t⌋) {q(hi)} with c{j} | c{j}")
            L.append("  ·" + tac[0][1:])
            L += ["   " + x[1:] for x in tac[1:]]
            prev = f"c{j}"
    L.append("")
    L.append("#print axioms cover")
    L.append("#print axioms v_injective")
    L.append("#print axioms v_pos")
    L.append(f"end SLRAudit.{name}")
    print("\n".join(L))
    print(f"-- chain length {len(ch)}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

### D. `run_all_lean.py`

```python
#!/usr/bin/env python3
"""Generate and compile the Lean covering proof for every certificate n=5..38 (sequential, one process)."""
from __future__ import annotations

import json
import subprocess
import sys

REPO = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery"
CERTS = REPO + "/results/proposal5/2026-10-27/SLR18/certificates"
OUT = "/tmp/slraudit/final"


def main() -> None:
    summary = []
    for n in range(5, 39):
        name = f"N{n:02d}"
        lean = f"{OUT}/SLR{name}.lean"
        with open(lean, "w") as fh:
            subprocess.run(["python3", "-I", "/tmp/slraudit/gen_lean.py", f"{CERTS}/cert_n{n:03d}.json", name],
                           stdout=fh, stderr=subprocess.DEVNULL, check=True)
        src = open(lean).read()
        banned = any(w in src for w in ("sorry", "admit", "native_decide", "\naxiom "))
        res = subprocess.run(["python3", REPO + "/scripts/certified_numerics/lean_pinned.py", "compile", lean,
                              "--timeout", "3600", "--json-out", f"{OUT}/lean_{name}.json"],
                             cwd=REPO, capture_output=True, text=True)
        out = res.stdout
        axl = [l for l in out.splitlines() if "depends on axioms" in l or "does not depend" in l]
        head = json.loads(out.splitlines()[0])
        row = {"n": n, "rc": head["rc"], "seconds": head["seconds"], "banned_tokens": banned, "axioms": axl}
        summary.append(row)
        print(json.dumps(row), flush=True)
    json.dump(summary, open(f"{OUT}/lean_all_summary.json", "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
```
