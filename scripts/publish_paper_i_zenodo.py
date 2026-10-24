"""Deposit Paper I as a new Zenodo record.

Paper I reports three things: that the verification cost which made this
measurement look unaffordable was an artifact of our own wrapper rather than of
Lean; that random subtree crossover significantly lowers the solve rate of a
kernel-gated program search; and that the repair its exact mechanism recommends
-- restricting recombination to homologous sites -- fails, refuted by its own
negative control.

First deposit, so a new record. Later editions must go through
`/actions/newversion` on the concept DOI this run returns, never a fresh record:
a corrected edition published as a new record leaves the old one as a separate
citable artefact with no link to its correction.

Three rules this script enforces rather than trusts:

* **No peer-review artefact enters the bundle.** This repository once described
  work as "5-round Opus peer reviewed" on the strength of a function that made no
  model call. Any file whose name mentions peer review aborts the run, and the
  description states plainly that the paper has not been peer reviewed.
* **Publication is verified, never assumed.** The Zenodo API has been observed
  returning 5xx for writes that in fact succeeded, so a failed publish is
  followed by a state read, and every uploaded file's MD5 is compared against the
  locally computed one before publishing. A blind retry would risk a duplicate
  record.
* **The bundle must contain the artifacts behind the numbers.** Every headline
  figure in the paper is reproduced by a file deposited alongside it, including
  the two artifacts that record superseded conclusions of our own.

Usage:

    .venv/bin/python scripts/publish_paper_i_zenodo.py --dry-run
    .venv/bin/python scripts/publish_paper_i_zenodo.py
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
SUBPROJECT = REPO / "sub_projects" / "socrateai_scientific_genetic" / "SocrateAI-Scientific-Genetic"
ZENODO = "https://zenodo.org/api"
RECEIPT = REPO / "results" / "zenodo_paper_i_edition1_receipt.json"
STEM = "PaperI_Recombination_Does_Not_Help_Lean4"

TITLE = (
    "Recombination Does Not Help: a Kernel-Gated Measurement of Crossover in "
    "Program Synthesis, and the Verifier Artifact That Made It Affordable"
)

DESCRIPTION = """
<p>Crossover is the operator that distinguishes a genetic algorithm from a
hill-climber, and in evolutionary program synthesis its contribution is usually
<em>asserted rather than measured</em>. Three preceding papers in this programme
asked whether recombination is <em>detectable</em> in evolved programs and
refuted the question's instrument each time. None asked the prior question: does
recombination <em>help</em>?</p>

<p><strong>The measurement was unaffordable for a reason that turned out to be
ours.</strong> A verified answer needs a formal gate over hundreds of
candidates, and our gate cost one Lean&nbsp;4 invocation per candidate. A Lean
compile containing a false obligation exits nonzero and <em>still prints a
per-declaration axiom line for every candidate</em>, the failing ones carrying
<code>sorryAx</code>. Our wrapper discarded those lines the instant the exit code
was nonzero, which made a batch appear atomic and motivated three successive
rounds of isolation machinery &mdash; a bisection, a flat fall-back measured as
better than the bisection, and a break-even law (1-p)^b &gt; 1/b derived from the
cost of isolating a failure. All three were solving a problem the wrapper had
invented. Reading the kernel's own report gives every verdict in <strong>one
invocation at any failure rate</strong>: measured at 1 invocation for 0, 1, 2, 4
and 8 failures of 8, every culprit named, no false candidate accepted. Dropping
the exit code is sound because acceptance never rested on it &mdash; the
forgery scan, a per-declaration axioms line, and a whitelist free of
<code>sorryAx</code> are unchanged.</p>

<p><strong>Crossover significantly reduces the solve rate.</strong> Fitness is
exact rational agreement with a specification at sample points, computed outside
the proof assistant; acceptance is the Lean kernel, so a wrong fitness can
misguide the search but cannot manufacture an acceptance. Over 200 paired seeds
on a calibrated target, mutation-only solved <strong>94/200 (47.0%)</strong>
against crossover's <strong>58/200 (29.0%)</strong>, Fisher exact
<strong>p = 2.98&times;10<sup>-4</sup></strong>. Conditional on solving, the
evaluation count is unchanged (median ratio 0.959 over 35 pairs, sign test
p = 1.000). Crossover does not make successful searches faster; it makes success
<em>less likely</em>.</p>

<p><strong>The mechanism is exact.</strong> An expression is affine in any one
subtree's value, out = A + B&middot;v, and B is computable in exact rationals by
one forward and one backward pass (verified against the defining two evaluations
over 500+ address-point pairs). A donor contributing B_donor&middot;v in its own
parent contributes B_site&middot;v after transplant, so its contribution is
rescaled or sign-inverted whenever the coefficients differ &mdash; subtree
crossover transmits structure and not function.</p>

<p><strong>The repair the mechanism recommends fails, refuted by its own
control.</strong> Biology recombines at homologous sites, so we restricted
recombination to sites whose coefficient sign pattern matches the donor's, with
an anti-homologous arm as the negative control and the falsifier fixed in
advance. Homologous crossover reached 70/200 (35.0%): not significantly above
random crossover (p = 0.238), and significantly <em>below</em> mutation-only
(p = 0.019). The anti-homologous control, predicted to be worse, scored
<strong>higher</strong> at 79/200 (39.5%) and is statistically indistinguishable
from the treatment (<strong>p = 0.408</strong>) &mdash; exactly the outcome
registered in advance as meaning the signature carries nothing. A
fallback-to-mutation confound is excluded by counts: effective mutation fractions
of 0.5117 and 0.5196 against 0.5000 cannot produce a 10.5 point spread. The
ordering of the three crossover arms is left <em>unexplained</em> rather than
given a story, since no adjacent pair is significant.</p>

<p><strong>What survives</strong> is the negative result from five independent
directions, the last of them against an idea of our own. In this representation
the only operator that reliably works is mutation. What it does <em>not</em>
license is also recorded: matching sign(B) failing does not show that no
contribution-preserving recombination can work, and a scheme that
<em>rescales</em> the donor to preserve B&middot;v is untested and is the obvious
next candidate. The failure is reported now rather than after hunting for a
variant that wins, because the prediction and its falsifier were fixed before the
run.</p>

<p><strong>Transferable method:</strong> a measured <em>limit</em> reported by
code you own is a property of that code until you check it one layer below. Three
rounds of optimisation here were spent against a barrier of our own making, and
the defect survived an existing guard because the wrapper's output looked like
physics rather than like a choice.</p>

<p><strong>Scope.</strong> One grammar, one calibrated target rung, one budget,
one population scheme, one crossover rate. Evidence about crossover in this
setting, not a general theorem about recombination. The full specification target
was solved by neither arm at this budget, so nothing is established at the size
the gate itself cares about. <strong>Not peer reviewed.</strong></p>
""".strip()

KEYWORDS = [
    "genetic programming",
    "crossover",
    "recombination",
    "evolutionary computation",
    "program synthesis",
    "Lean 4",
    "formal verification",
    "proof-carrying certificate",
    "kernel-gated search",
    "homologous recombination",
    "context coefficient",
    "reverse-mode differentiation",
    "exact rational arithmetic",
    "negative result",
    "pre-registration",
    "reproducibility",
    "measurement artifact",
]

CREATORS = [
    {
        "name": "Callens, Xavier",
        "affiliation": "SocrateAI Scientific Research & Formal Verification Laboratory",
    }
]


def token() -> str:
    """Load the Zenodo token through the repository's existing loader."""
    path = REPO / "scripts/three_breakthroughs/publish_3breakthroughs_to_zenodo.py"
    spec = importlib.util.spec_from_file_location("zenodo_token_loader", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load the token helper at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module.load_zenodo_token())


def req(
    method: str,
    url: str,
    tok: str,
    data: bytes | None = None,
    ctype: str = "application/json",
) -> Dict[str, Any]:
    """One Zenodo API call. Raises on HTTP error; the caller decides what to do."""
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {tok}", "Content-Type": ctype},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        body = response.read()
        return json.loads(body) if body else {}


def md5_of(path: Path) -> str:
    """MD5 of a file, for comparison against what Zenodo reports it stored."""
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bundle() -> List[Path]:
    """The files to deposit, with the checks that must pass before any upload."""
    files: List[Path] = [
        SUBPROJECT / "papers" / f"{STEM}.pdf",
        SUBPROJECT / "papers" / f"{STEM}.tex",
        # The experiment: search, calibration, controls and gate in one file.
        REPO / "scripts" / "lean_gated_recombination.py",
        # The three results the paper's headline numbers come from.
        REPO / "results" / "lean_gated_recombination.json",
        REPO / "results" / "lean_gated_recombination_homology.json",
        REPO / "results" / "lean_gated_recombination_calibration.json",
        # The verifier artifact, and the two artifacts it superseded. These are
        # deposited BECAUSE they record conclusions of ours that were wrong: the
        # bisection-versus-fall-back comparison was real and was the evidence for
        # shipping the fall-back, and it is the shared premise that failed.
        REPO / "results" / "lean_atomicity_is_the_wrapper.json",
        REPO / "results" / "lean_batching.json",
        REPO / "results" / "lean_batching_bisection.json",
        REPO / "results" / "lean_numeric_screen.json",
        # The gate itself and its specification.
        REPO / "anse" / "formal" / "lean_runner.py",
        REPO / "formal" / "ANSE" / "VerletSymplectic.lean",
        # The tests that make the gate's claims checkable.
        REPO / "tests" / "integration" / "test_batched_gate.py",
        REPO / "tests" / "integration" / "test_numeric_screen.py",
        REPO / "tests" / "unit" / "test_context_coefficients.py",
        REPO / "tests" / "unit" / "test_lean_spec_obligations.py",
    ]

    missing = [str(f) for f in files if not f.exists()]
    if missing:
        raise RuntimeError(f"bundle is missing files: {missing}")
    forbidden = [str(f) for f in files if "peer_review" in f.name.lower()]
    if forbidden:
        raise RuntimeError(f"refusing to deposit a peer-review artefact: {forbidden}")
    names = [f.name for f in files]
    collisions = {n for n in names if names.count(n) > 1}
    if collisions:
        raise RuntimeError(f"duplicate upload names in the bundle: {collisions}")
    return files


def adopt_draft(deposition_id: int, tok: str, metadata):
    """Finish an EXISTING unsubmitted draft instead of creating another one.

    Zenodo has been seen returning 504 on writes that in fact succeeded, which
    can leave a draft behind while the caller sees a failure. Re-running the
    script then creates a SECOND draft and strands the first.
    """
    deposition = req("GET", f"{ZENODO}/deposit/depositions/{deposition_id}", tok)
    if deposition.get("submitted"):
        raise RuntimeError(
            f"deposition {deposition_id} is already submitted; adopting it would "
            "modify a published record"
        )
    inherited = deposition.get("files", [])
    for old in inherited:
        req(
            "DELETE",
            f"{ZENODO}/deposit/depositions/{deposition_id}/files/{old['id']}",
            tok,
        )
    print(f"adopted draft {deposition_id}; cleared {len(inherited)} inherited files")
    req(
        "PUT",
        f"{ZENODO}/deposit/depositions/{deposition_id}",
        tok,
        json.dumps(metadata).encode(),
    )
    return deposition_id, deposition["links"]["bucket"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="assemble and check the bundle, contact nothing",
    )
    parser.add_argument(
        "--use-draft",
        type=int,
        default=0,
        help=(
            "finish this existing unsubmitted draft instead of creating a new "
            "one; use after a 5xx that left a draft behind, so a second draft is "
            "not created and the first stranded"
        ),
    )
    args = parser.parse_args()

    files = bundle()
    print(f"bundle: {len(files)} files")
    for path in files:
        print(f"  {path.relative_to(REPO)}  {path.stat().st_size:>9,} B")
    if args.dry_run:
        print("\ndry run: nothing was uploaded and no record was created")
        return 0

    tok = token()
    metadata = {
        "metadata": {
            "upload_type": "publication",
            "publication_type": "preprint",
            "title": TITLE,
            "description": DESCRIPTION,
            "creators": CREATORS,
            "keywords": KEYWORDS,
            "license": "cc-by-4.0",
            "access_right": "open",
            "version": "edition-1",
            "language": "eng",
        }
    }

    if args.use_draft:
        deposition_id, bucket = adopt_draft(args.use_draft, tok, metadata)
    else:
        deposition = req(
            "POST",
            f"{ZENODO}/deposit/depositions",
            tok,
            json.dumps(metadata).encode(),
        )
        deposition_id = deposition["id"]
        bucket = deposition["links"]["bucket"]
        print(f"created deposition {deposition_id}")

    uploaded: Dict[str, str] = {}
    for path in files:
        local = md5_of(path)
        result = req(
            "PUT",
            f"{bucket}/{path.name}",
            tok,
            path.read_bytes(),
            "application/octet-stream",
        )
        remote = str(result.get("checksum", "")).removeprefix("md5:")
        if remote != local:
            raise RuntimeError(
                f"{path.name}: Zenodo stored md5 {remote!r}, local file is "
                f"{local!r}. Not publishing a bundle whose contents do not match."
            )
        uploaded[path.name] = local
        print(f"  uploaded {path.name} (md5 verified)")

    try:
        published = req(
            "POST",
            f"{ZENODO}/deposit/depositions/{deposition_id}/actions/publish",
            tok,
        )
    except urllib.error.HTTPError as error:
        # The API has been seen reporting 5xx for writes that succeeded. Read the
        # state back rather than retrying, which could create a second record.
        print(f"publish returned HTTP {error.code}; reading the state back")
        published = req("GET", f"{ZENODO}/deposit/depositions/{deposition_id}", tok)
        if published.get("state") != "done" or not published.get("submitted"):
            raise RuntimeError(
                f"publish failed and the deposition is still "
                f"{published.get('state')!r}; inspect deposition {deposition_id} "
                "by hand before retrying"
            ) from error
        print("the deposition is published despite the error response")

    receipt = {
        "record_id": published.get("id"),
        "doi": published.get("doi"),
        "concept_doi": published.get("conceptdoi"),
        "concept_record_id": published.get("conceptrecid"),
        "state": published.get("state"),
        "submitted": published.get("submitted"),
        "title": TITLE,
        "version": "edition-1",
        "files_uploaded": uploaded,
        "peer_reviewed": False,
        "note": (
            "First Zenodo deposit of Paper I, so a new record. Later editions must "
            "use /actions/newversion on the concept record above, never a fresh "
            "record. This paper has not been peer reviewed."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"\nDOI        : {receipt['doi']}")
    print(f"concept DOI: {receipt['concept_doi']}")
    print(f"receipt    : {RECEIPT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
