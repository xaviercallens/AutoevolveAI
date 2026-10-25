"""Deposit Paper J (Kernel-Gated Evolution, foundation paper) as a new Zenodo record.

Paper J proposes Kernel-Gated Evolution: Darwinian mutation-selection over
exact-rational expression genomes, apoptotic one-sided checkpoints, exact
per-locus dosage analysis, and a Lean 4 kernel as the final arbiter of
acceptance -- with a Rust reference implementation.

First deposit, so a new record. Later editions must go through
`/actions/newversion` on the concept DOI this run returns, never a fresh record.

Three rules enforced rather than trusted:

* **No peer-review artefact enters the bundle.** Any file whose name mentions
  peer review aborts the run; the description states the paper is not peer
  reviewed.
* **Publication is verified, never assumed.** Every upload's MD5 is compared with
  the local file before publishing, and a failed publish reads the deposition
  state back instead of retrying, because the API has returned 5xx for writes
  that succeeded and a blind retry risks a duplicate record.
* **The bundle contains the artifacts behind every number**, including the Rust
  crate and its tests, the ladder run, the landscape and hill-climb measurements,
  and the verifier whose per-declaration report makes the one-invocation gate.

Usage:
    .venv/bin/python scripts/publish_paper_j_zenodo.py --dry-run
    .venv/bin/python scripts/publish_paper_j_zenodo.py
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
CRATE = REPO / "crates" / "kernel_gated_evolution"
ZENODO = "https://zenodo.org/api"
RECEIPT = REPO / "results" / "zenodo_paper_j_edition3_receipt.json"
EDITION = "edition-3"
STEM = "PaperJ_Kernel_Gated_Evolution_Foundation"

TITLE = (
    "Kernel-Gated Evolution: a Biomimetic Search with Apoptotic Checkpoints and "
    "Exact Dosage, Arbitrated by a Proof Kernel (Foundation Paper and Rust "
    "Reference Implementation)"
)

DESCRIPTION = """
<p><strong>Kernel-Gated Evolution (KGE)</strong> is a biomimetic search for
programs whose acceptance is decided by a proof kernel rather than by the search
itself. Three mechanisms borrowed from living systems are combined, each chosen
because it earned its place under measurement: <em>Darwinian variation and
selection</em> drives exploration; <em>apoptotic checkpoints</em> &mdash;
one-sided exact screens that can remove a candidate but never confer survival
&mdash; cull what cannot be right before any proof is attempted; and <em>exact
dosage analysis</em> reports, for every locus of a genome, precisely how much its
value reaches the phenotype, in one forward and one backward pass. The final
judgement is a Lean&nbsp;4 kernel: a survivor is rendered to Lean and must prove
its obligation with an axiom dependency free of <code>sorryAx</code>.
<strong>Fitness guides; the kernel decides.</strong> A wrong fitness can waste
search effort but cannot manufacture an acceptance.</p>

<p><strong>Everything is exact.</strong> Every quantity is an exact rational, so
no step of the search is an approximation and every invariant is checkable. The
dosage coefficients are verified against their two-evaluation definition on 500+
locus-point pairs (2,496 in the Python prototype); the required-value identity
v* = v + (want &minus; out)/B on 2,000+ pairs (24,303 in Python); and the
checkpoint's one-sidedness by constructing a candidate that agrees at every
sample point yet differs as a function &mdash; it survives the checkpoint and is
rejected by the kernel.</p>

<p><strong>The gate costs one invocation per batch at any failure rate.</strong>
A Lean compile reports a per-declaration verdict even when it exits nonzero, so a
batch of eight candidates is verified in one invocation whether 0, 1, 2, 4 or 8
of them are false, with every culprit named and no false candidate accepted,
against eight individual proofs (50.88&nbsp;s). Acceptance never rests on the
exit code; it rests on a forgery scan, a per-declaration axioms line and a
whitelist free of <code>sorryAx</code>.</p>

<p><strong>Rust reference implementation</strong> with replayable seeds and six
exact-arithmetic tests; a <code>kge ladder</code> binary that runs a calibration
ladder of exact targets up to the Verlet position update, reports solve rates,
distinct solutions and the inert (dead-code) fraction of each best individual,
exercises the checkpoint as a control with a known answer, and writes Lean
candidates for the gate. Results, a population-versus-hill-climbing comparison,
and a landscape characterisation are reported in the paper.</p>

<p><strong>Where it applies:</strong> verified numerical kernels (integrator
steps, stencils, update rules that must be proved equal to a specification); any
synthesis with a formal acceptance criterion; exact dead-code analysis of
evolved programs; and batching expensive verification in general.</p>

<p><strong>Limitations</strong> are stated plainly: one closed grammar in the
reference implementation; solve rates fall steeply above targets of about nine
nodes and the full Verlet target is unsolved at the tested budget &mdash; a cliff
not explained by basin geometry and not relieved by recombination (eight
operators tested under pre-registered bars; companion measurements in Paper I,
DOI 10.5281/zenodo.23622868), which is why KGE is mutation-driven; the
checkpoint is one-sided by design; dosage is instrumentation rather than
steering; and about 97% of a Lean invocation is fixed overhead that batching
amortises but a persistent kernel would remove.</p>

<p><strong>Future research:</strong> exploiting the affine structure to solve
constant loci by exact linear algebra; representations with higher solution
density at scale; a properly powered study of contribution-preserving transfer
(positive signal p = 0.031 against its matched control, not surviving
correction); a persistent kernel; adaptive checkpoints; and application to the
project's Python-genome kernel path.</p>

<p><strong>Edition 3</strong> adds exact <strong>lifetime learning of constants</strong>
&mdash; the Baldwin effect (and its Lamarckian variant) made exact: each constant locus
is set to its required value v* = v + (want &minus; out)/B when that value agrees at
every sample point. Over 1,200 paired seeds it never lost a solve the plain population
found, raised the ladder from L1 0.550&rarr;0.835, L3 0.255&rarr;0.450 and L5
0.015&rarr;0.060, every solution kernel-proved, and is compared with the plain
population at matched total work. Baldwin and Lamarck coincide on every seed, because
exact tuning is all-or-nothing.</p>

<p><strong>Edition 2</strong> adds: the identities proved in Lean
(<code>formal/ANSE/AlixKalSpec.lean</code>, six theorems, zero sorry, one of them
axiom-free); a benchmark on the SRSD-Feynman datasets from the Hugging Face Hub
(yoshitomo-matsubara/srsd-feynman_{easy,medium,hard}, CC-BY-4.0) &mdash; 8 of
120 laws lie inside the reference grammar, five were run against random search,
a restart hill-climber and exact polynomial regression on the same seeds, points
and budget, and <strong>every one of the 39 distinct recovered laws was proved by
the kernel</strong> with a planted wrong candidate rejected in each batch; the
honest finding that on tiny targets (four leaves or fewer) the population is
beaten by the naive baselines on three of the five laws, which becomes the
guideline "choose the search layer by target size"; a "where and how to use it"
guide; a statement of significance; and seven figures rendered from the
artifacts. The engine's codename is ALIX (Apoptotic checkpoint, Lean-gated,
Inheritance by mutation, eXact).</p>

<p>Every number is produced by a committed script or test and checked against
its artefact before deposit. <strong>Not peer reviewed.</strong></p>
""".strip()

KEYWORDS = [
    "biomimetic computing", "evolutionary computation", "genetic programming",
    "program synthesis", "formal verification", "Lean 4", "proof-carrying",
    "kernel-gated search", "apoptosis", "developmental checkpoint", "gene dosage",
    "reverse-mode differentiation", "exact rational arithmetic", "dead code analysis",
    "Rust", "reproducibility",
]

CREATORS = [
    {"name": "Callens, Xavier",
     "affiliation": "SocrateAI Scientific Research & Formal Verification Laboratory"}
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


def req(method: str, url: str, tok: str, data: bytes | None = None,
        ctype: str = "application/json") -> Dict[str, Any]:
    """One Zenodo API call. Raises on HTTP error; the caller decides what to do."""
    request = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": f"Bearer {tok}", "Content-Type": ctype},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        body = response.read()
        return json.loads(body) if body else {}


def md5_of(path: Path) -> str:
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
        # The Rust reference implementation and its tests.
        CRATE / "Cargo.toml",
        CRATE / "src" / "lib.rs",
        CRATE / "src" / "main.rs",
        CRATE / "tests" / "exactness.rs",
        # The measurements the paper's numbers come from.
        REPO / "results" / "kge_rust_ladder.json",
        REPO / "results" / "kge_rust_gate.json",
        REPO / "results" / "kge_rust_hillclimb.json",
        REPO / "results" / "kge_rust_ladder_python_points.json",
        REPO / "results" / "python_sample_points.json",
        REPO / "results" / "gp_landscape_cliff.json",
        REPO / "results" / "lean_atomicity_is_the_wrapper.json",
        # The gate, its specification, and the Python prototype of the identities.
        REPO / "anse" / "formal" / "lean_runner.py",
        REPO / "formal" / "ANSE" / "VerletSymplectic.lean",
        REPO / "scripts" / "lean_gated_recombination.py",
        REPO / "scripts" / "gp_landscape_cliff.py",
        # The scripts that gated the solutions, filled the paper from artifacts,
        # and checked every claim before this deposit.
        REPO / "scripts" / "kge_gate_rust_solutions.py",
        REPO / "scripts" / "fill_paper_j_results.py",
        REPO / "scripts" / "verify_paper_j_claims.py",
        # Edition 2: the Lean-proved identities, the Hub benchmark and its
        # baselines, the guidelines, and the figure script.
        REPO / "formal" / "ANSE" / "AlixKalSpec.lean",
        REPO / "results" / "kge_hf_selection.json",
        REPO / "results" / "kge_hf_traditional_baseline.json",
        REPO / "results" / "kge_hf_gate.json",
        REPO / "results" / "kge_hf_feynman_i_12_1.json",
        REPO / "results" / "kge_hf_feynman_i_39_10.json",
        REPO / "results" / "kge_hf_feynman_i_14_4.json",
        REPO / "results" / "kge_hf_feynman_ii_34_2.json",
        REPO / "results" / "kge_hf_feynman_ii_37_1.json",
        REPO / "scripts" / "kge_select_hf_problems.py",
        REPO / "scripts" / "kge_traditional_baseline.py",
        REPO / "scripts" / "kge_figures.py",
        REPO / "docs" / "KGE_GUIDELINES.md",
        # Edition 3: lifetime learning of constants (Baldwin / Lamarck).
        REPO / "results" / "kge_rust_ladder_baldwin.json",
        REPO / "results" / "kge_rust_ladder_lamarck.json",
        REPO / "results" / "kge_rust_ladder_costmatched.json",
        REPO / "results" / "kge_lifetime_learning.json",
        REPO / "results" / "kge_baldwin_gate.json",
        REPO / "scripts" / "kge_lifetime_learning_analysis.py",
        CRATE / "README.md",
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


def new_version(previous: int, tok: str, metadata):
    """Deposit as a NEW VERSION of an existing record, never as a fresh record.

    A corrected edition published as a new record leaves the old one as a
    separate citable artefact with no link to its correction; /actions/newversion
    keeps one concept DOI resolving to the latest edition.
    """
    draft = req("POST", f"{ZENODO}/deposit/depositions/{previous}/actions/newversion", tok)
    deposition = req("GET", draft["links"]["latest_draft"], tok)
    deposition_id = deposition["id"]
    print(f"new version draft {deposition_id} of record {previous}")
    inherited = deposition.get("files", [])
    for old in inherited:
        req("DELETE", f"{ZENODO}/deposit/depositions/{deposition_id}/files/{old['id']}", tok)
    print(f"  cleared {len(inherited)} inherited files")
    req("PUT", f"{ZENODO}/deposit/depositions/{deposition_id}", tok, json.dumps(metadata).encode())
    return deposition_id, deposition["links"]["bucket"]


def adopt_draft(deposition_id: int, tok: str, metadata):
    """Finish an EXISTING unsubmitted draft instead of creating another one."""
    deposition = req("GET", f"{ZENODO}/deposit/depositions/{deposition_id}", tok)
    if deposition.get("submitted"):
        raise RuntimeError(f"deposition {deposition_id} is already submitted")
    inherited = deposition.get("files", [])
    for old in inherited:
        req("DELETE", f"{ZENODO}/deposit/depositions/{deposition_id}/files/{old['id']}", tok)
    print(f"adopted draft {deposition_id}; cleared {len(inherited)} inherited files")
    req("PUT", f"{ZENODO}/deposit/depositions/{deposition_id}", tok,
        json.dumps(metadata).encode())
    return deposition_id, deposition["links"]["bucket"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="assemble and check the bundle, contact nothing")
    parser.add_argument("--use-draft", type=int, default=0,
                        help="finish this existing unsubmitted draft after a 5xx")
    parser.add_argument("--new-version-of", type=int, default=0,
                        help="deposit as a new version of this published record id; the only "
                             "correct way to publish a corrected edition")
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
            "version": EDITION,
            "language": "eng",
            "related_identifiers": [
                {"identifier": "10.5281/zenodo.23622868", "relation": "isSupplementedBy",
                 "scheme": "doi"},
            ],
        }
    }

    if args.use_draft:
        deposition_id, bucket = adopt_draft(args.use_draft, tok, metadata)
    elif args.new_version_of:
        deposition_id, bucket = new_version(args.new_version_of, tok, metadata)
    else:
        deposition = req("POST", f"{ZENODO}/deposit/depositions", tok,
                         json.dumps(metadata).encode())
        deposition_id = deposition["id"]
        bucket = deposition["links"]["bucket"]
        print(f"created deposition {deposition_id}")

    uploaded: Dict[str, str] = {}
    for path in files:
        local = md5_of(path)
        result = req("PUT", f"{bucket}/{path.name}", tok, path.read_bytes(),
                     "application/octet-stream")
        remote = str(result.get("checksum", "")).removeprefix("md5:")
        if remote != local:
            raise RuntimeError(
                f"{path.name}: Zenodo stored md5 {remote!r}, local file is {local!r}. "
                "Not publishing a bundle whose contents do not match.")
        uploaded[path.name] = local
        print(f"  uploaded {path.name} (md5 verified)")

    try:
        published = req("POST", f"{ZENODO}/deposit/depositions/{deposition_id}/actions/publish", tok)
    except urllib.error.HTTPError as error:
        print(f"publish returned HTTP {error.code}; reading the state back")
        published = req("GET", f"{ZENODO}/deposit/depositions/{deposition_id}", tok)
        if published.get("state") != "done" or not published.get("submitted"):
            raise RuntimeError(
                f"publish failed and the deposition is still {published.get('state')!r}; "
                f"inspect deposition {deposition_id} by hand before retrying") from error
        print("the deposition is published despite the error response")

    receipt = {
        "record_id": published.get("id"),
        "doi": published.get("doi"),
        "concept_doi": published.get("conceptdoi"),
        "concept_record_id": published.get("conceptrecid"),
        "state": published.get("state"),
        "submitted": published.get("submitted"),
        "title": TITLE,
        "version": EDITION,
        "files_uploaded": uploaded,
        "peer_reviewed": False,
        "note": (f"Paper J {EDITION}. Editions after the first are deposited with "
                 "/actions/newversion on the concept record above, never as a fresh record. "
                 "This paper has not been peer reviewed."),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"\nDOI        : {receipt['doi']}")
    print(f"concept DOI: {receipt['concept_doi']}")
    print(f"receipt    : {RECEIPT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
