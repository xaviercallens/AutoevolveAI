#!/usr/bin/env python3
"""Publish the student textbook "The Triangular Lattice and Universal Optimality" and its evidence bundle to Zenodo.

Reuses the token, upload and request helpers of publish_universal_optimality_tiered.py. Same flow:
``--dry-run`` builds the bundle and prints the metadata; ``--draft`` creates the deposition, uploads and reserves the
DOI (written to papers/textbook_universal_optimality/zenodo_doi.txt so the title page can carry it); ``--update-id``
re-uploads the rebuilt PDF and bundle; ``--publish-id`` publishes (irreversible). Tokens are never printed.

Usage:
    python3 -I scripts/publish_textbook_universal_optimality.py --token-file ~/.token_workflow_token --dry-run
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import tarfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
BOOK_DIR = REPO / "papers" / "textbook_universal_optimality"
BOOK_PDF = BOOK_DIR / "main.pdf"
PUBLISHED_PDF_NAME = "triangular_lattice_universal_optimality_textbook.pdf"
BUNDLE_DIR = Path("/mnt/disks/disk-socrateai-local-1/SocrateAI-storage/lab-archive/textbook_universal_optimality_2026-10")
BUNDLE_NAME = "textbook_universal_optimality_2026-10.tar.gz"
# The book pins its Rust listings to rusty-SUNDIALS b7e4380 (branch physics/jellium-wigner-2026-10-11); this worktree
# is checked out at that commit.
CRATE = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-jellium/crates/qf-yukawa-crystal")
KEEP_SUFFIXES = {".json", ".jsonl", ".md", ".py", ".tex", ".lean", ".txt", ".rs", ".toml", ".csv"}
SKIP_DIRS = {"scratch_olean", "__pycache__", ".lake", ".olean_out", "target"}

_spec = importlib.util.spec_from_file_location("tiered", REPO / "scripts" / "publish_universal_optimality_tiered.py")
assert _spec is not None and _spec.loader is not None
tiered = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tiered)


def members() -> list[tuple[Path, str]]:
    """(path, archive name) pairs: book sources and code, the Lean files, D1-D4 records, the pinned Rust crate."""
    out: list[tuple[Path, str]] = []
    for d in (BOOK_DIR, REPO / "formal_cert" / "Triangular", REPO / "results" / "discovery"):
        for p in d.rglob("*"):
            if p.is_file() and p.suffix in KEEP_SUFFIXES and not (SKIP_DIRS & set(p.parts)) and p.stat().st_size < 5_000_000:
                out.append((p, str(p.relative_to(REPO))))
    out.append((REPO / "scripts" / "certified_numerics" / "lean_pinned.py", "scripts/certified_numerics/lean_pinned.py"))
    for p in CRATE.rglob("*"):
        if p.is_file() and p.suffix in KEEP_SUFFIXES and "target" not in p.parts:
            out.append((p, "rusty-SUNDIALS/crates/qf-yukawa-crystal/" + str(p.relative_to(CRATE))))
    return sorted(set(out), key=lambda t: t[1])


def build_bundle() -> tuple[Path, Path, Path]:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    pairs = members()
    manifest = {name: {"sha256": tiered.sha256(p), "bytes": p.stat().st_size} for p, name in pairs}
    manifest_path = BUNDLE_DIR / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=1))
    tar_path = BUNDLE_DIR / BUNDLE_NAME
    with tarfile.open(tar_path, "w:gz") as tar:
        for p, name in pairs:
            tar.add(p, arcname=name)
        tar.add(manifest_path, arcname="MANIFEST.json")
    pdf_copy = BUNDLE_DIR / PUBLISHED_PDF_NAME
    pdf_copy.write_bytes(BOOK_PDF.read_bytes())
    return tar_path, manifest_path, pdf_copy


def zenodo_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    return {"metadata": {
        "title": meta["title"],
        "upload_type": "publication",
        "publication_type": "book",
        "description": meta["description"],
        "creators": [{"name": "Callens, Xavier", "affiliation": "SocrateAI Lab"}],
        "keywords": meta["keywords"],
        "license": "cc-by-4.0",
        "version": meta.get("version", "v1"),
        "related_identifiers": [
            {"identifier": "10.5281/zenodo.23293429", "relation": "isSupplementTo", "scheme": "doi"},
            {"identifier": "10.5281/zenodo.23285631", "relation": "references", "scheme": "doi"},
            {"identifier": "https://github.com/xaviercallens/AutoevolveAI", "relation": "isSupplementTo", "scheme": "url"},
            {"identifier": "https://github.com/openai/math", "relation": "references", "scheme": "url"},
            {"identifier": "https://github.com/xaviercallens/rusty-SUNDIALS", "relation": "references", "scheme": "url"},
            {"identifier": "https://github.com/xaviercallens/SocrateAI-Scientific-Elenchus", "relation": "references", "scheme": "url"},
            {"identifier": "10.4007/annals.2022.196.3.3", "relation": "references", "scheme": "doi"},
        ],
        "notes": meta.get("notes", ""),
    }}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", type=Path)
    ap.add_argument("--meta", type=Path, default=BOOK_DIR / "publication_meta.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--update-id", type=int)
    ap.add_argument("--publish-id", type=int)
    args = ap.parse_args()
    meta = json.loads(args.meta.read_text())
    Z = tiered.ZENODO
    if args.publish_id:
        token = tiered.load_tokens(args.token_file)["ZENODO_TOKEN"]
        dep = tiered.zenodo_request("POST", f"{Z}/deposit/depositions/{args.publish_id}/actions/publish", token)
        print(json.dumps({"zenodo": tiered.summary(dep)}, indent=2))
        return 0
    tar_path, manifest, pdf_copy = build_bundle()
    report: dict[str, Any] = {"bundle": str(tar_path), "bundle_sha256": tiered.sha256(tar_path),
                              "bundle_bytes": tar_path.stat().st_size,
                              "files_in_manifest": len(json.loads(manifest.read_text())),
                              "book_pdf_sha256": tiered.sha256(pdf_copy)}
    if args.dry_run:
        report["zenodo_metadata"] = zenodo_metadata(meta)
        print(json.dumps(report, indent=2))
        return 0
    token = tiered.load_tokens(args.token_file)["ZENODO_TOKEN"]
    files = [pdf_copy, tar_path, manifest]
    if args.draft:
        dep = tiered.zenodo_request("POST", f"{Z}/deposit/depositions", token, b"{}")
        tiered.upload(token, dep, files)
        dep = tiered.zenodo_request("PUT", f"{Z}/deposit/depositions/{dep['id']}", token,
                                    json.dumps(zenodo_metadata(meta)).encode())
        report["zenodo"] = tiered.summary(dep)
        if report["zenodo"]["doi"]:
            (BOOK_DIR / "zenodo_doi.txt").write_text(report["zenodo"]["doi"] + "\n")
    elif args.update_id:
        dep = tiered.zenodo_request("GET", f"{Z}/deposit/depositions/{args.update_id}", token)
        for f in dep.get("files", []):
            tiered.zenodo_request("DELETE", f"{Z}/deposit/depositions/{args.update_id}/files/{f['id']}", token)
        tiered.upload(token, dep, files)
        dep = tiered.zenodo_request("PUT", f"{Z}/deposit/depositions/{args.update_id}", token,
                                    json.dumps(zenodo_metadata(meta)).encode())
        report["zenodo"] = tiered.summary(dep)
        listing = tiered.zenodo_request("GET", f"{Z}/deposit/depositions/{args.update_id}", token).get("files", [])
        report["zenodo"]["files"] = [{"name": f["filename"], "md5": f["checksum"]} for f in listing]
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
