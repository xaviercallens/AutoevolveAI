#!/usr/bin/env python3
"""Publish the kernel-checked DESI DR2 constraints paper (pilots P2, P3) and its evidence bundle to Zenodo.

Tokens come from a KEY=VALUE file (``ZENODO_TOKEN``) or the environment and are never printed.
``--dry-run`` builds the bundle and metadata and stops before any network write. ``--draft`` creates
the deposition, uploads the files and reserves a DOI without publishing (the DOI is then written to
papers/certified_desi_h0/zenodo_doi.txt so the PDF can be rebuilt with it). ``--publish-id``
publishes an existing draft after the rebuilt PDF has been re-uploaded with ``--update-id``.

Usage:
    python3 scripts/publish_certified_desi_h0.py --token-file ~/.token_workflow_token --dry-run
    python3 scripts/publish_certified_desi_h0.py --token-file ~/.token_workflow_token --draft
    python3 scripts/publish_certified_desi_h0.py --token-file ~/.token_workflow_token --update-id <id>
    python3 scripts/publish_certified_desi_h0.py --token-file ~/.token_workflow_token --publish-id <id>
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

REPO = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO / "papers" / "certified_desi_h0"
PAPER_PDF = PAPER_DIR / "certified_desi_h0.pdf"
BUNDLE_DIR = Path("/mnt/disks/disk-socrateai-local-1/SocrateAI-storage/lab-archive/certified_desi_h0_2026-10")
BUNDLE_NAME = "certified_desi_h0_2026-10.tar.gz"
ZENODO = "https://zenodo.org/api"
KEEP_SUFFIXES = {".json", ".jsonl", ".md", ".tsv", ".py", ".tex", ".pdf", ".txt", ".lean", ".js", ".rs", ".toml", ".lock"}
SKIP_DIRS = {"scratch_olean", "lock_root", "__pycache__", ".lake", ".olean_out", "target"}


def load_tokens(path: Path | None) -> dict[str, str]:
    out = {k: os.environ[k] for k in ("ZENODO_TOKEN",) if os.environ.get(k)}
    if path and path.exists():
        for raw in path.read_text().splitlines():
            line = raw.strip().removeprefix("export ")
            if "=" in line and not line.startswith("#"):
                key, _, val = line.partition("=")
                out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def bundle_members() -> list[Path]:
    """Small text artifacts only: no oleans, no checkpoints, no upstream source copies, no tokens."""
    dirs = [
        PAPER_DIR,
        REPO / "formal_cert" / "BAOCert",
        REPO / "results" / "certified_numerics" / "P2_likelihood",
        REPO / "results" / "certified_numerics" / "P3_h0",
        REPO / "scripts" / "certified_numerics",
        REPO / "results" / "certified_numerics",
    ]
    files = [REPO / "docs" / "OPENAI_MATH_CROSSWALK_2026-10-08.md",
             REPO / "docs" / "RESEARCH_DIRECTIONS_2026-10-08.md",
             REPO / "formal_cert" / ".gitignore"]
    members: list[Path] = []
    for d in dirs:
        if d.exists():
            members += [p for p in d.rglob("*")
                        if p.is_file() and p.suffix in KEEP_SUFFIXES and not (SKIP_DIRS & set(p.parts))
                        and p.stat().st_size < 5_000_000]
    members += [f for f in files if f.exists()]
    return sorted(set(members))


def build_bundle() -> tuple[Path, Path]:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    members = bundle_members()
    manifest = {str(p.relative_to(REPO)): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in members}
    manifest_path = BUNDLE_DIR / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=1))
    tar_path = BUNDLE_DIR / BUNDLE_NAME
    with tarfile.open(tar_path, "w:gz") as tar:
        for p in members:
            tar.add(p, arcname=str(p.relative_to(REPO)))
        tar.add(manifest_path, arcname="MANIFEST.json")
    return tar_path, manifest_path


def zenodo_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    return {"metadata": {
        "title": meta["title"],
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": meta["description"],
        "creators": [{"name": "Callens, Xavier", "affiliation": "SocrateAI Lab"}],
        "keywords": meta["keywords"],
        "license": "cc-by-4.0",
        "related_identifiers": [
            {"identifier": "https://github.com/xaviercallens/AutoevolveAI", "relation": "isSupplementTo", "scheme": "url"},
            {"identifier": "https://github.com/openai/math", "relation": "references", "scheme": "url"},
            {"identifier": "10.5281/zenodo.23247730", "relation": "continues", "scheme": "doi"},
        ],
        "notes": meta.get("notes", ""),
    }}


def zenodo_request(method: str, url: str, token: str, data: bytes | None = None,
                   content_type: str = "application/json") -> dict[str, Any]:
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": content_type})
    with urllib.request.urlopen(req, timeout=600) as r:
        body = r.read()
        return json.loads(body) if body else {}


def summary(dep: dict[str, Any]) -> dict[str, Any]:
    return {"id": dep.get("id"), "doi": dep.get("doi") or dep.get("metadata", {}).get("prereserve_doi", {}).get("doi"),
            "state": dep.get("state"), "submitted": dep.get("submitted"), "html": dep.get("links", {}).get("html")}


def upload(token: str, dep: dict[str, Any], files: list[Path]) -> None:
    bucket = dep["links"]["bucket"]
    for f in files:
        with open(f, "rb") as fh:
            zenodo_request("PUT", f"{bucket}/{f.name}", token, fh.read(), "application/octet-stream")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", type=Path)
    ap.add_argument("--meta", type=Path, default=PAPER_DIR / "publication_meta.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--draft", action="store_true", help="create the deposition, upload, reserve the DOI; do not publish")
    ap.add_argument("--update-id", type=int, help="re-upload the bundle and PDF into an existing draft")
    ap.add_argument("--publish-id", type=int, help="publish an existing draft (mints the DOI; irreversible)")
    args = ap.parse_args()
    meta = json.loads(args.meta.read_text())
    if args.publish_id:
        # Publishing must not rebuild the local archive: the record holds the files uploaded earlier,
        # and a rebuild (tar/gzip are not byte-reproducible) would leave the local copy different.
        token = load_tokens(args.token_file)["ZENODO_TOKEN"]
        dep = zenodo_request("POST", f"{ZENODO}/deposit/depositions/{args.publish_id}/actions/publish", token)
        print(json.dumps({"zenodo": summary(dep)}, indent=2))
        return 0
    tar_path, manifest = build_bundle()
    report: dict[str, Any] = {"bundle": str(tar_path), "bundle_sha256": sha256(tar_path), "bundle_bytes": tar_path.stat().st_size,
                              "files_in_manifest": len(json.loads(manifest.read_text())), "paper_pdf_sha256": sha256(PAPER_PDF)}
    if args.dry_run:
        report["zenodo_metadata"] = zenodo_metadata(meta)
        print(json.dumps(report, indent=2))
        return 0
    token = load_tokens(args.token_file)["ZENODO_TOKEN"]
    files = [PAPER_PDF, tar_path, manifest]
    if args.draft:
        dep = zenodo_request("POST", f"{ZENODO}/deposit/depositions", token, b"{}")
        upload(token, dep, files)
        dep = zenodo_request("PUT", f"{ZENODO}/deposit/depositions/{dep['id']}", token, json.dumps(zenodo_metadata(meta)).encode())
        report["zenodo"] = summary(dep)
        doi = report["zenodo"]["doi"]
        if doi:
            (PAPER_DIR / "zenodo_doi.txt").write_text(doi + "\n")
    elif args.update_id:
        dep = zenodo_request("GET", f"{ZENODO}/deposit/depositions/{args.update_id}", token)
        for f in dep.get("files", []):
            zenodo_request("DELETE", f"{ZENODO}/deposit/depositions/{args.update_id}/files/{f['id']}", token)
        upload(token, dep, files)
        dep = zenodo_request("PUT", f"{ZENODO}/deposit/depositions/{args.update_id}", token, json.dumps(zenodo_metadata(meta)).encode())
        report["zenodo"] = summary(dep)
        report["zenodo"]["files"] = [f["filename"] for f in zenodo_request("GET", f"{ZENODO}/deposit/depositions/{args.update_id}", token).get("files", [])]
    elif args.publish_id:
        dep = zenodo_request("POST", f"{ZENODO}/deposit/depositions/{args.publish_id}/actions/publish", token)
        report["zenodo"] = summary(dep)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
