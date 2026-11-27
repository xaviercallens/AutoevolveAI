#!/usr/bin/env python3
"""Publish the SLR-GAP2 negative-result note to Zenodo (token never printed).

usage: publish_zenodo.py --token-file ~/.token_workflow_token [--publish]
Without --publish: creates the deposition, uploads, prints the reserved DOI (draft).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ZENODO = "https://zenodo.org/api"
SKIP = {"p2", "__pycache__"}


def tokens(path: Path) -> str:
    for raw in path.read_text().splitlines():
        line = raw.strip().removeprefix("export ")
        if line.startswith("ZENODO_TOKEN="):
            return line.partition("=")[2].strip().strip('"').strip("'")
    return os.environ["ZENODO_TOKEN"]


def req(method: str, url: str, token: str, data: bytes | None = None, ct: str = "application/json") -> dict[str, Any]:
    r = urllib.request.Request(url, data=data, method=method,
                               headers={"Authorization": f"Bearer {token}", "Content-Type": ct})
    with urllib.request.urlopen(r, timeout=600) as resp:
        body = resp.read()
        return json.loads(body) if body else {}


def build_bundle() -> Path:
    out = HERE / "SLR-GAP2_bundle.tar.gz"
    with tarfile.open(out, "w:gz") as tar:
        for p in sorted(HERE.rglob("*")):
            if p.is_file() and not (set(p.relative_to(HERE).parts) & SKIP) and p != out and p.suffix != ".pyc" \
                    and p.name != "publish_zenodo.py":
                tar.add(p, arcname="SLR-GAP2/" + str(p.relative_to(HERE)))
    return out


META = {"metadata": {
    "title": "A negative, inconclusive search for further shifted lonely runner covers at n = 39..94 (companion to n = 63)",
    "upload_type": "publication",
    "publication_type": "technicalnote",
    "description": (
        "<p>Computational negative-result note (Tier X; nothing new is claimed). After the exact shifted lonely runner "
        "counterexample at n = 63 (doi 10.5281/zenodo.24051700) we searched for a second n in 39..94 using bases not used there: "
        "multiples of 3, 4 and 6 and wider even pools, with shift menus c/q + j/D (q in 4, 6, 8, 12), exact CP-SAT set cover and two exact checkers. "
        "<b>No cover was found.</b> Controls: n = 63 and n = 95 are re-found (both checkers COVERED) and n = 44 is INFEASIBLE in the control family. "
        "Decided verdicts: the narrow-menu family (q = 8, offsets |j| &le; 4) is INFEASIBLE for n = 39..93 except n = 81 (UNKNOWN), <i>but it also fails the n = 63 positive control</i>, "
        "so it is evidence only about that narrow menu; the wide-menu (|j| = 8) and multiple-of-3/4/6 families are UNKNOWN at 45-90 s (solver-limited, uninformative). "
        "About 9.6 of a 12 core-hour kill budget was used, so the preregistered kill rule was not reached. <b>This does not show that no other n exists</b>; "
        "it is not evidence about the (unshifted) lonely runner conjecture. Producer is an AI agent; no independent audit, no Lean, no human review. "
        "Code, per-run logs (logs/runs.jsonl), control certificates and SHA-256 manifest are in the bundle.</p>"),
    "creators": [{"name": "Callens, Xavier", "affiliation": "SocrateAI Lab"}],
    "keywords": ["lonely runner conjecture", "shifted lonely runner", "negative result", "CP-SAT", "exact rational arithmetic",
                 "AI-assisted research"],
    "license": "cc-by-4.0",
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.24051700", "relation": "continues", "scheme": "doi"},
        {"identifier": "arXiv:2603.24784", "relation": "references", "scheme": "arxiv"},
        {"identifier": "arXiv:2609.23952", "relation": "references", "scheme": "arxiv"},
        {"identifier": "https://github.com/xaviercallens/AutoevolveAI", "relation": "isSupplementTo", "scheme": "url"},
    ],
    "notes": "Proposal 6, item SLR-GAP2 (2026-11-08..11). Preregistration PREREG_ITEM.md with sha256 in the bundle. To our knowledge only.",
}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", type=Path, required=True)
    ap.add_argument("--publish", action="store_true")
    a = ap.parse_args()
    token = tokens(a.token_file)
    bundle = build_bundle()
    dep = req("POST", f"{ZENODO}/deposit/depositions", token, b"{}")
    bucket = dep["links"]["bucket"]
    for f in (HERE / "RESULT.md", bundle):
        req("PUT", f"{bucket}/{f.name}", token, f.read_bytes(), "application/octet-stream")
    dep = req("PUT", f"{ZENODO}/deposit/depositions/{dep['id']}", token, json.dumps(META).encode())
    rep = {"id": dep["id"], "doi": dep.get("metadata", {}).get("prereserve_doi", {}).get("doi"),
           "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest()}
    if a.publish:
        dep = req("POST", f"{ZENODO}/deposit/depositions/{dep['id']}/actions/publish", token)
        rep.update({"state": dep.get("state"), "doi": dep.get("doi"), "html": dep.get("links", {}).get("html")})
    print(json.dumps(rep, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
