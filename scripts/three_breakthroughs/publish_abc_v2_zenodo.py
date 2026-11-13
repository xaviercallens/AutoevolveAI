"""Deposit edition 2 of Papers A, B and C as new versions of their Zenodo records.

Edition 2 of each paper withdraws edition 1's claims that an audit on 21 October 2026 found
unsupported, and replaces them with a pre-registered, control-backed computational test plus a
Lean 4 file that passes `anse.formal.lean_runner` (compile + `#print axioms`). The scripted
"5-round Opus peer review" JSONs are not, and will not be, part of any bundle: that procedure
calls no model.

Run from the repository root:
    .venv/bin/python scripts/three_breakthroughs/publish_abc_v2_zenodo.py [--paper A|B|C]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
ZENODO = "https://zenodo.org/api"
RECEIPT = REPO / "results" / "three_breakthroughs" / "zenodo_abc_v2_receipts.json"
# Drafts left open by an interrupted run, to be reused rather than re-minted.
# Paper A was deposited in an earlier run (10.5281/zenodo.23532458).
RESUME: dict[str, int] = {}

CREATORS = [{"name": "Callens, Xavier", "affiliation": "SocrateAI Lab"}]
REPO_URL = "https://github.com/xaviercallens/AutoevolveAI"

NOT_REVIEWED = (
    "<p><b>This paper has not been reviewed by anyone other than the author.</b> Edition 1 was "
    "deposited alongside files from a pipeline that described a multi-round review with referee "
    "findings and numeric scores. That procedure called no model and involved no reviewer: its "
    "findings were fixed strings and its scores were pass fractions of local string checks. Any "
    "review, score or approval attached to edition 1 is void, and those files are not "
    "distributed.</p>"
)
VERIFY = (
    "<p><b>Verification.</b> Every Lean 4 file listed below passes the repository's axiom gate "
    "(<code>anse/formal/lean_runner.py</code>: compile, then <code>#print axioms</code> per "
    "declaration, rejecting <code>sorryAx</code> and any axiom outside {propext, "
    "Classical.choice, Quot.sound}). Every number quoted in the manuscript is reproducible from "
    "the included script and results JSON; the script's SHA-256 is recorded in the JSON.</p>"
)


def _p(*parts: str) -> Path:
    return REPO.joinpath(*parts)


PAPERS: dict[str, dict[str, Any]] = {
    "A": {
        "previous": 23511649,
        "title": (
            "RK4 Cools at Resolved Step Sizes, It Does Not Heat: Energy-Error Sign of Explicit "
            "Runge-Kutta Integrators and Relaxation RK in a Nonlinear Magnetic-Well Model, with "
            "Lean 4 Certificates for the Linear Well"
        ),
        "keywords": [
            "relaxation Runge-Kutta", "geometric numerical integration", "energy error",
            "magnetic well", "Lean 4", "formal verification", "falsification",
            "stellarator confinement",
        ],
        "description": (
            "<p>Edition 2, and a refutation of edition 1's own motivating hypothesis.</p>"
            "<p>Edition 1 justified relaxation Runge-Kutta integration by asserting that classical "
            "RK4's secular numerical heating pushes trapped particles over magnetic-mirror "
            "barriers. Edition 2 tests that assertion in the 2-DOF cubic magnetic well that "
            "edition 1 actually integrated, whose escape energy is exactly H* = 29/40. With 2000 "
            "microcanonically sampled orbits per energy band, five step sizes from 0.05 to 0.8, a "
            "horizon T = 2000, a falsification criterion fixed in advance and six controls that "
            "all pass: <b>the heating hypothesis is refuted</b>. Below H*, at every step size, "
            "100% of RK4 orbits end with less energy than they started, with zero spurious escapes "
            "and zero crossings of the saddle line. RK4's real failure mode is the opposite one, "
            "spurious <i>trapping</i>: against a DOP853 reference escape fraction of 0.618, RK4 "
            "lets only 0.464 escape at step 0.4 and 0.0905 at step 0.8 (deficits of 10.0 and 34.3 "
            "binomial standard errors). Explicit midpoint RK2 and forward Euler, which heat "
            "provably, do produce spurious escapes, so the controls can fail.</p>"
            "<p>In Lean 4 (18 of 18 declarations clean) the linear well is settled exactly: the "
            "RK4 energy factor rho_4(y) = 1 - y^6/72 + y^8/576; 1/4 <= rho_4 < 1 on 0 < y^2 < 8, "
            "and rho_4 > 1 beyond it, where RK4 does heat and is unstable; the n-step closed form "
            "rho_4^n; a one-step two-mode monotonicity; the heating factors of Euler and midpoint; "
            "a general trapping lemma for energy-nonincreasing maps; and the relaxation root in "
            "R^d.</p>"
            "<p>Withdrawn from edition 1: the calibrated-confidence 0.9150 and gate-pass 1.0000 "
            "figures, the formula-drawn figures, the Villani/Landau theorem, the zero-sound and "
            "Volterra constants, and the benchmark description (the quoted drifts are real harness "
            "output but come from 1000 steps, not 4000, of a different system).</p>"
            + VERIFY + NOT_REVIEWED
        ),
        "files": [
            _p("papers/three_breakthroughs/paper_a/PaperA_Stellarator_Fusion_DualRRK_Villani_LeanFlow.pdf"),
            _p("papers/three_breakthroughs/paper_a/PaperA_Stellarator_Fusion_DualRRK_Villani_LeanFlow.tex"),
            _p("papers/three_breakthroughs/paper_a/fig_a1_well_trajectories_3d.pdf"),
            _p("papers/three_breakthroughs/paper_a/fig_a2_energy_sign_escape.pdf"),
            _p("papers/three_breakthroughs/paper_a/fig_a3_linear_well_controls.pdf"),
            _p("papers/three_breakthroughs/paper_a/fig_a4_poincare_energy_shells_3d.pdf"),
            _p("papers/three_breakthroughs/paper_a/paper_a_v2_results.json"),
            _p("papers/three_breakthroughs/paper_a/paper_a_v2_lean_gate.json"),
            _p("scripts/three_breakthroughs/paper_a_v2_experiment.py"),
            _p("scripts/three_breakthroughs/paper_a_v2_figures.py"),
            _p("formal/ANSE/PaperA_RK4EnergySign.lean"),
            _p("formal/ANSE/Breakthroughs3Domains.lean"),
            _p("formal/ANSE/ElenchusTrilogy.lean"),
            _p("sub_projects/socrateai_scientific_fusion_energy/fusion_guiding_center_harness.py"),
        ],
    },
    "B": {
        "previous": 23511655,
        "title": (
            "The Scale-Dual Subgrid Model of 3D Navier-Stokes: Its True Quadratic Invariant, Its "
            "Identity with the Modified Leray-alpha Model, and What Lean 4 Checks"
        ),
        "keywords": [
            "Navier-Stokes", "modified Leray-alpha", "Lyapunov functional", "enstrophy",
            "pseudospectral DNS", "Lean 4", "formal verification", "falsification",
        ],
        "description": (
            "<p>Edition 2, which refutes edition 1's Theorem 2.5 at edition 1's own "
            "parameters.</p>"
            "<p>The scale-dual model's conserved quantity is Q, not the L2 energy E. Exact "
            "rational triad counterexamples give dE/dt = +6/5 and +32/15 while dQ/dt = 0 "
            "identically, and the exact growth rate is positive precisely for lambda > 169/5. "
            "Across 59,780 exact evaluations, not one divergence-free field has dQ/dt != 0, while "
            "12,200 piecewise amplitude draws at alpha' = 1/25 move L2 energy. A 299-run "
            "pseudospectral Galerkin ensemble with positive and negative controls reproduces the "
            "exact rationals to 1e-15 and conserves Q to 9.5e-11 inviscidly. <b>Edition 1's "
            "inequality E(t) <= E_0 is refuted</b> at (alpha', nu) = (1/25, 1/100) and E_0 = 32 by "
            "the criterion fixed in advance: the piecewise model exceeds E_0 in 5 of 5 seeds while "
            "the Navier-Stokes control never does, and the excess survives halving the time step "
            "and doubling the resolution. Its <i>size</i> is not converged in N (about 1.77 at "
            "N = 32 against about 3.0 at N = 64), and the paper claims only that E > E_0 occurs "
            "and persists, never a converged supremum. At the originally planned amplitude "
            "E_0 = 1/2 the inequality held in all 10 seeds, so only instantaneous growth is shown "
            "there.</p>"
            "<p>Lean 4 (25 declarations across two files, all clean) carries the invariant "
            "structure: L2 conservation holds iff the weights are constant (a no-go theorem with "
            "an explicit skew tensor built for the forward direction), the weighted energy is "
            "antitone along trajectories, and the chain Omega_eff <= Q/alpha' <= Q_0/alpha' <= "
            "E_0/alpha' holds for both symbols, the smooth case via m_ML <= m_pw.</p>"
            "<p>Also corrected: the smooth model is exactly the modified Leray-alpha model of "
            "Ilyin, Lunasin and Titi (2006), not the Leray-alpha model edition 1 named, and Q is "
            "its known energy; edition 1's blow-up claim is withdrawn, since the true enstrophy is "
            "not capped, for the models or for Navier-Stokes; the tail-bound scaling, a CRT "
            "product and a misattributed Chen-Hou citation are fixed. No computer-assisted proof "
            "was performed; Theorem 2.1 is relabelled accordingly.</p>"
            + VERIFY + NOT_REVIEWED
        ),
        "files": [
            _p("papers/three_breakthroughs/paper_b/PaperB_NavierStokes_Hurricane_Mensura_DualScale_CAP.pdf"),
            _p("papers/three_breakthroughs/paper_b/PaperB_NavierStokes_Hurricane_Mensura_DualScale_CAP.tex"),
            _p("papers/three_breakthroughs/paper_b/fig1_v2_invariant_trajectories_3d.pdf"),
            _p("papers/three_breakthroughs/paper_b/fig2_v2_energy_production_density_3d.pdf"),
            _p("papers/three_breakthroughs/paper_b/fig3_v2_energy_vs_Q_and_threshold.pdf"),
            _p("papers/three_breakthroughs/paper_b/fig4_v2_amplitude_scan.pdf"),
            _p("papers/three_breakthroughs/paper_b/fig5_v2_symbols.pdf"),
            _p("papers/three_breakthroughs/paper_b/paper_b_v2_results.json"),
            _p("papers/three_breakthroughs/paper_b/paper_b_v2_fig2_values.json"),
            _p("scripts/three_breakthroughs/paper_b_v2_experiment.py"),
            _p("scripts/three_breakthroughs/paper_b_v2_figures.py"),
            _p("tests/test_paper_b_v2_experiment.py"),
            _p("formal/ANSE/PaperB_ScaleDualEd2.lean"),
            _p("formal/ANSE/PaperB_EnergyBudget.lean"),
            _p("formal/ANSE/Breakthroughs3Domains.lean"),
            _p("formal/ANSE/Breakthroughs3DomainsSpec.lean"),
            _p("formal/ANSE/MensuraElenchusThreeMissions.lean"),
        ],
    },
    "C": {
        "previous": 23511660,
        "title": (
            "The Maximal Order of SQIsign's Starting Curve: Machine-Checked Arithmetic in Lean 4, "
            "Corrections, and Which Hecke Eigenforms Govern 2-Isogeny Returns to E_0"
        ),
        "keywords": [
            "supersingular isogeny graph", "SQIsign", "Deuring correspondence", "Brandt matrices",
            "Ramanujan graph", "Gross formula", "Lean 4", "formal verification",
        ],
        "description": (
            "<p>Edition 2, which withdraws three of edition 1's headline claims and replaces them "
            "with a measurement.</p>"
            "<p><b>Withdrawn.</b> The Rust \"verified SQIsign verifier\" takes no public key, "
            "message, curve or challenge isogeny and does no F_p^2 arithmetic: it is a reduced-norm "
            "check, and a probe crate shows it accepts the scalar 256. Edition 1's "
            "\"non-backtracking response\" sigma = 128+128j has O_0 coordinates "
            "(128,-128,256,0) = 2*(64,-64,128,0), so it lies in 2*O_0 and its walk backtracks. For "
            "the family (3^p, 4^p, 3^p+4^p), Ribet level lowering does not reach level 2: the prime "
            "7 survives for every p != 7, and for p = 7 the representation is not finite at 7.</p>"
            "<p><b>Measured instead.</b> Which weight-2 newforms of level p control N_e(p), the "
            "number of primitive elements of reduced norm 2^e in O_0 = End(E_0), equivalently the "
            "closed non-backtracking 2-isogeny walks at SQIsign's starting curve? Five independent "
            "instruments: exact lattice counts, the supersingular 2-isogeny graph over F_p^2, "
            "modular-symbol projections of the theta series, PARI/GP L-values at 38 digits, and "
            "Lean 4. The class-number-one laws hold exactly to e = 22; the minimal recurrence of "
            "N_e matches the prediction for all 13 primes p <= 83, with every non-trivial root on "
            "|z|^2 = 2 to 4.4e-16; and at 36 of 155 primes the largest eigenvalue seen from E_0 is "
            "strictly smaller than the global one, so walks from this base point mix faster than "
            "the graph's own spectral gap predicts.</p>"
            "<p><b>A negative result about this edition's own test.</b> The invisibility of all 211 "
            "root-number-(-1) orbits is <i>not</i> evidence for Gross's formula, and it is forced "
            "twice over. Because j(E_0) = 1728 is F_p-rational, Frobenius fixes the base vector and "
            "commutes with the Brandt matrices, so the projection onto any such orbit vanishes "
            "identically, for every p, whatever the central values do; and independently of any "
            "base point, w = -1 makes the functional equation odd, so L(f,1) = 0 and Gross's "
            "criterion predicts invisibility anyway. That count is an identity, not a measurement. "
            "The permutation test and its p < 1e-4 are withdrawn, as is the corresponding "
            "falsification criterion. The surviving, genuinely falsifiable half is the "
            "root-number-(+1) one: 21 of 209 orbits are invisible, and each has exactly one central "
            "value vanishing below 2e-38 with the other above 0.576. Of the 83 classes examined at "
            "53 primes, the 47 with w = +1 carry that content and the 36 with w = -1 do not. "
            "Testing the other half needs a base point with j outside F_p, where the prediction can "
            "at least come out false; the paper sets this out as a research direction.</p>"
            "<p>Lean 4: 20 of 20 declarations clean, including the Ihara-circle lemma "
            "(|z|^2 = l iff a^2 <= 4l), the O_0 norm form and its halving lemma, semistability for "
            "every inhabited Hellegouarch triple, and v_7(3^p+4^p) = 1 + v_7(p) with p not dividing "
            "2*v_7 for every prime p >= 5. Results that are constant evaluations rather than "
            "general theorems are labelled as such.</p>"
            + VERIFY + NOT_REVIEWED
        ),
        "files": [
            _p("papers/three_breakthroughs/paper_c/PaperC_FLT_Modular_PQC_SQIsign_Quantum_Rust_Lean4.pdf"),
            _p("papers/three_breakthroughs/paper_c/PaperC_FLT_Modular_PQC_SQIsign_Quantum_Rust_Lean4.tex"),
            _p("papers/three_breakthroughs/paper_c/fig3_ramanujan_cylinder.pdf"),
            _p("papers/three_breakthroughs/paper_c/fig4_deviation_bars.pdf"),
            _p("papers/three_breakthroughs/paper_c/fig5_visibility_and_frey.pdf"),
            _p("papers/three_breakthroughs/paper_c/fig6_spectral_gap_E0.pdf"),
            _p("papers/three_breakthroughs/paper_c/paper_c_v2_results.json"),
            _p("papers/three_breakthroughs/paper_c/paper_c_v2_lean_gate.json"),
            _p("scripts/three_breakthroughs/paper_c_v2_experiment.py"),
            _p("scripts/three_breakthroughs/paper_c_v2_pari_worker.py"),
            _p("scripts/three_breakthroughs/paper_c_v2_figures.py"),
            _p("scripts/three_breakthroughs/paper_c_v2_rust_probe/Cargo.toml"),
            _p("scripts/three_breakthroughs/paper_c_v2_rust_probe/src/main.rs"),
            _p("formal/ANSE/PaperC_DeuringSpectrum.lean"),
            _p("formal/ANSE/Breakthroughs3Domains.lean"),
            _p("formal/ANSE/Breakthroughs3DomainsSpec.lean"),
            _p("formal/ANSE/ElenchusTrilogySpec.lean"),
        ],
    },
}


def token() -> str:
    spec = importlib.util.spec_from_file_location(
        "p", REPO / "scripts/three_breakthroughs/publish_3breakthroughs_to_zenodo.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return str(mod.load_zenodo_token())


def req(method: str, url: str, tok: str, data: bytes | None = None,
        ctype: str = "application/json", attempts: int = 5) -> dict[str, Any]:
    """One Zenodo call, retrying only on transient server-side failures.

    Zenodo returns a bare 500 under load. Retrying a 4xx would just repeat a rejected request,
    so only 5xx and socket errors are retried, with a linear back-off.
    """
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        r = urllib.request.Request(
            url, data=data, method=method,
            headers={"Authorization": f"Bearer {tok}", "Content-Type": ctype})
        try:
            with urllib.request.urlopen(r, timeout=900) as resp:
                body = resp.read()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:2000]
            if exc.code < 500:  # a validation error will not fix itself
                raise RuntimeError(f"{method} {url} -> {exc.code}: {detail}") from exc
            last = RuntimeError(f"{method} {url} -> {exc.code}: {detail}")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = RuntimeError(f"{method} {url} -> {exc!r}")
        if attempt < attempts:
            print(f"  transient failure ({attempt}/{attempts}), retrying: {last}")
            time.sleep(10 * attempt)
    assert last is not None
    raise last


def remote_md5(dep_id: int, name: str, tok: str) -> str | None:
    """The MD5 Zenodo holds for `name`, or None if it holds no such file."""
    for got in req("GET", f"{ZENODO}/deposit/depositions/{dep_id}", tok).get("files", []):
        if (got.get("filename") or got.get("key")) == name:
            return str(got.get("checksum", "")).removeprefix("md5:")
    return None


def upload(dep: dict[str, Any], f: Path, payload: bytes, tok: str) -> None:
    """PUT one file, treating a 5xx as unknown rather than failed.

    Zenodo's bucket API can return a bare 500 *after* writing the object. Retrying then either
    re-uploads needlessly or fails a deposit whose file is already in place, so on a 5xx we ask
    the server what it actually holds and accept the write when the MD5 matches.
    """
    want = hashlib.md5(payload).hexdigest()
    try:
        req("PUT", f"{dep['links']['bucket']}/{f.name}", tok, payload,
            "application/octet-stream", attempts=1)
        return
    except RuntimeError as exc:
        if "-> 5" not in str(exc):
            raise
        got = remote_md5(int(dep["id"]), f.name, tok)
        if got == want:
            print(f"  {f.name}: server reported 500 but holds the correct bytes, continuing")
            return
        raise RuntimeError(
            f"{f.name}: upload failed and the server holds {got!r}, expected {want!r}") from exc


def check(spec: dict[str, Any]) -> list[Path]:
    files = list(spec["files"])
    missing = [str(f) for f in files if not f.exists()]
    assert not missing, f"missing: {missing}"
    forbidden = [str(f) for f in files if "peer_review" in f.name]
    assert not forbidden, f"peer-review files must never be bundled: {forbidden}"
    names = [f.name for f in files]
    dupes = {n for n in names if names.count(n) > 1}
    assert not dupes, f"duplicate basenames would overwrite on Zenodo: {dupes}"
    return files


def publish(key: str, tok: str) -> dict[str, Any]:
    spec = PAPERS[key]
    files = check(spec)
    previous = int(spec["previous"])

    prev = req("GET", f"{ZENODO}/deposit/depositions/{previous}", tok)
    assert prev["state"] == "done", f"record {previous} is in state {prev['state']}"

    draft_id = RESUME.get(key)
    if draft_id is not None:
        # A previous run already minted the new version and then failed mid-upload. Reuse that
        # draft; minting a second one would leave an orphan version in the concept.
        dep = req("GET", f"{ZENODO}/deposit/depositions/{draft_id}", tok)
        assert dep["state"] != "done", f"draft {draft_id} is already published"
        print(f"  resuming existing draft {draft_id}")
    else:
        nv = req("POST", f"{ZENODO}/deposit/depositions/{previous}/actions/newversion", tok)
        dep = req("GET", nv["links"]["latest_draft"], tok)
    for old in dep.get("files", []):
        req("DELETE", f"{ZENODO}/deposit/depositions/{dep['id']}/files/{old['id']}", tok)

    sums: dict[str, str] = {}
    for f in files:
        payload = f.read_bytes()
        upload(dep, f, payload, tok)
        sums[f.name] = hashlib.sha256(payload).hexdigest()

    # Nothing may ship that we did not intend to ship, including probe files from a failed run.
    final = req("GET", f"{ZENODO}/deposit/depositions/{dep['id']}", tok)
    expected = {f.name for f in files}
    for got in final.get("files", []):
        name = got.get("filename") or got.get("key")
        if name not in expected:
            print(f"  removing stray file {name}")
            req("DELETE", f"{ZENODO}/deposit/depositions/{dep['id']}/files/{got['id']}", tok)
    landed = {(g.get("filename") or g.get("key")) for g in final.get("files", [])}
    assert expected <= landed, f"missing after upload: {sorted(expected - landed)}"

    meta = {"metadata": {
        "title": spec["title"],
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": spec["description"],
        "creators": CREATORS,
        "keywords": spec["keywords"],
        "license": "cc-by-4.0",
        "version": "2",
        "related_identifiers": [
            {"identifier": REPO_URL, "relation": "isSupplementTo", "scheme": "url"},
            {"identifier": f"10.5281/zenodo.{previous}", "relation": "isNewVersionOf",
             "scheme": "doi"},
        ],
    }}
    req("PUT", f"{ZENODO}/deposit/depositions/{dep['id']}", tok, json.dumps(meta).encode())
    try:
        done = req("POST", f"{ZENODO}/deposit/depositions/{dep['id']}/actions/publish", tok,
                   attempts=1)
    except RuntimeError as exc:
        # Same failure mode as the bucket PUTs: the action can take effect and still report an
        # error. Publishing twice is not possible, so ask what the record actually is.
        done = req("GET", f"{ZENODO}/deposit/depositions/{dep['id']}", tok)
        if done.get("state") != "done":
            raise
        print(f"  publish reported an error but the record is live: {str(exc)[:120]}")

    return {
        "paper": key,
        "previous": previous,
        "id": done.get("id"),
        "doi": done.get("doi"),
        "conceptrecid": done.get("conceptrecid"),
        "state": done.get("state"),
        "n_files": len(sums),
        "sha256": sums,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", choices=sorted(PAPERS), action="append",
                    help="deposit only this paper (repeatable); default is all three")
    args = ap.parse_args()
    keys = args.paper or sorted(PAPERS)

    for key in keys:
        check(PAPERS[key])
    print(f"pre-flight ok for {', '.join(keys)}")

    tok = token()
    receipts = []
    for key in keys:
        r = publish(key, tok)
        receipts.append(r)
        print(f"{key}: {r['id']} {r['doi']} {r['state']} ({r['n_files']} files, "
              f"concept {r['conceptrecid']})")

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipts, indent=2) + "\n", encoding="utf-8")
    print(f"receipt -> {RECEIPT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
