#!/usr/bin/env python3
"""Publish the C1 certification paper (independent certification of the PH-2 Robertson enclosure) and its evidence bundle to Zenodo.

Tokens come from a KEY=VALUE file (``ZENODO_TOKEN``) or the environment and are never printed.
``--dry-run`` builds the bundle and metadata and stops before any network write. ``--draft`` creates the deposition,
uploads the files and reserves a DOI without publishing. ``--update-id`` re-uploads into an existing draft.
``--new-version`` opens a new-version draft of a published record, replaces its files and metadata (DOI reserved, not published).
``--publish-id`` publishes a draft (mints the DOI; irreversible): run it only after the audit is attached and the PDF carries the DOI.

Usage:
    python3 scripts/publish_c1_certified_robertson.py --token-file ~/.token_workflow_token --dry-run
    python3 scripts/publish_c1_certified_robertson.py --token-file ~/.token_workflow_token --draft
    python3 scripts/publish_c1_certified_robertson.py --token-file ~/.token_workflow_token --update-id <id>
    python3 scripts/publish_c1_certified_robertson.py --token-file ~/.token_workflow_token --publish-id <id>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tarfile
import urllib.request
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO / "papers" / "c1_certified_robertson"
PAPER_PDF = PAPER_DIR / "main.pdf"
SOURCE_ROOT = Path("/home/callensxavier_gmail_com/numerica_repo")
BUNDLE_DIR = Path("/home/callensxavier_gmail_com/c1_bundle")
BUNDLE_NAME = "c1_certified_robertson_v2_2026-11.tar.gz"
ZENODO = "https://zenodo.org/api"
KEEP_SUFFIXES = {".lean", ".md", ".json", ".py", ".sh", ".rs", ".toml", ".txt", ".jsonl", ".tex", ".lock", ".log", ".out", ".err"}
SKIP_DIRS = {"target", ".lake", "__pycache__", "c1_target", "tmp"}
MAX_BYTES = 5_000_000
PHASE1 = ("lean_onestep_2026-11-20", "lean_L5_2026-11-21", "lean_L5_2026-11-22", "lean_L6_2026-11-23", "lean_L6b_2026-11-23", "lean_multistep_2026-11-26")
DOCS = re.compile(r"(10|11|16|17|18|19)_")
PRIVATE = re.compile(r"veridials|socrate-?numerica|lanyon|pricing|business case|investor|seed round|go-to-market|trademark", re.I)


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


def bundle_members() -> tuple[list[Path], list[Path]]:
    """Small text artefacts only (no binaries, no build output, no oversized records, no business documents)."""
    roots = [SOURCE_ROOT / "phase1" / d for d in PHASE1] + [SOURCE_ROOT / "phase3" / "c1_checker"]
    members: list[Path] = []
    skipped: list[Path] = []
    for root in roots:
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in KEEP_SUFFIXES and not (SKIP_DIRS & set(p.parts)):
                (skipped if p.stat().st_size > MAX_BYTES else members).append(p)
    members += [p for p in (SOURCE_ROOT / "docs").glob("*.md") if DOCS.match(p.name)]
    members += [PAPER_DIR / "main.tex", PAPER_DIR / "publication_meta.json"]
    for extra in ("AUDIT.md", "AUDIT_RESPONSE.md"):
        if (PAPER_DIR / extra).exists():
            members.append(PAPER_DIR / extra)
    return sorted(set(members)), sorted(skipped)


def private_hits(members: list[Path]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for p in members:
        found = sorted({m.group(0).lower() for m in PRIVATE.finditer(p.read_text(encoding="utf-8", errors="replace"))})
        if found:
            hits[str(p)] = found
    return hits


def arcname(p: Path) -> str:
    for base in (SOURCE_ROOT, REPO):
        try:
            return str(p.relative_to(base))
        except ValueError:
            continue
    return p.name


def build_bundle() -> tuple[Path, Path, list[Path]]:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    members, skipped = bundle_members()
    hits = private_hits(members)
    if hits:
        raise SystemExit(f"refusing to bundle files with private-product words: {hits}")
    manifest = {arcname(p): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in members}
    for p in skipped:
        manifest[arcname(p) + " (NOT INCLUDED, over 5 MB)"] = {"sha256": sha256(p), "bytes": p.stat().st_size}
    manifest_path = BUNDLE_DIR / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=1))
    tar_path = BUNDLE_DIR / BUNDLE_NAME
    with tarfile.open(tar_path, "w:gz") as tar:
        for p in members:
            tar.add(p, arcname=arcname(p))
        tar.add(manifest_path, arcname="MANIFEST.json")
    return tar_path, manifest_path, skipped


def zenodo_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    return {"metadata": {
        "title": meta["title"],
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": meta["description"],
        "creators": [{"name": "Callens, Xavier", "affiliation": "SocrateAI Lab"}],
        "keywords": meta["keywords"],
        "license": "cc-by-4.0",
        "related_identifiers": meta.get("related_identifiers", []),
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
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--update-id", type=int)
    ap.add_argument("--publish-id", type=int)
    ap.add_argument("--new-version", type=int, help="id of a published record: create a new-version draft of it and fill it")
    args = ap.parse_args()
    meta = json.loads(args.meta.read_text())
    if args.publish_id:
        token = load_tokens(args.token_file)["ZENODO_TOKEN"]
        dep = zenodo_request("POST", f"{ZENODO}/deposit/depositions/{args.publish_id}/actions/publish", token)
        print(json.dumps({"zenodo": summary(dep)}, indent=2))
        return 0
    tar_path, manifest, skipped = build_bundle()
    report: dict[str, Any] = {"bundle": str(tar_path), "bundle_sha256": sha256(tar_path), "bundle_bytes": tar_path.stat().st_size,
                              "files_in_manifest": len(json.loads(manifest.read_text())), "paper_pdf_sha256": sha256(PAPER_PDF),
                              "not_included": [p.name for p in skipped]}
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
        if report["zenodo"]["doi"]:
            (PAPER_DIR / "zenodo_doi.txt").write_text(report["zenodo"]["doi"] + "\n")
    elif args.new_version:
        old = zenodo_request("POST", f"{ZENODO}/deposit/depositions/{args.new_version}/actions/newversion", token)
        dep = zenodo_request("GET", old["links"]["latest_draft"], token)
        for f in dep.get("files", []):
            zenodo_request("DELETE", f"{ZENODO}/deposit/depositions/{dep['id']}/files/{f['id']}", token)
        upload(token, dep, files)
        dep = zenodo_request("PUT", f"{ZENODO}/deposit/depositions/{dep['id']}", token, json.dumps(zenodo_metadata(meta)).encode())
        report["zenodo"] = summary(dep)
        if report["zenodo"]["doi"]:
            (PAPER_DIR / "zenodo_doi_v2.txt").write_text(report["zenodo"]["doi"] + "\n")
    elif args.update_id:
        dep = zenodo_request("GET", f"{ZENODO}/deposit/depositions/{args.update_id}", token)
        for f in dep.get("files", []):
            zenodo_request("DELETE", f"{ZENODO}/deposit/depositions/{args.update_id}/files/{f['id']}", token)
        upload(token, dep, files)
        dep = zenodo_request("PUT", f"{ZENODO}/deposit/depositions/{args.update_id}", token, json.dumps(zenodo_metadata(meta)).encode())
        report["zenodo"] = summary(dep)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
