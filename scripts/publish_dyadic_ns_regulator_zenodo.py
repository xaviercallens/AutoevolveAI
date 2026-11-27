#!/usr/bin/env python3
"""Publish the `dyadic_ns_regulator_elenchus` PhD paper and replication bundle to Zenodo.

Reads `ZENODO_TOKEN` from `--token-file` (default `~/.env` or `~/.zenodo_token`) or the
environment without printing any token value. Builds a reproducible tarball and SHA-256
`MANIFEST.json`, uploads `Dyadic_NavierStokes_Regulator_Elenchus_Paper.pdf`,
`autoevolve_dyadic_ns_regulator_elenchus_2026-10.tar.gz`, and `MANIFEST.json` to Zenodo,
and publishes the deposition when `--publish` is passed.
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
BUNDLE_DIR = REPO / "dist" / "dyadic_ns_regulator_elenchus_2026-10"
PAPER_PDF = REPO / "papers" / "dyadic_ns_regulator_elenchus" / "Dyadic_NavierStokes_Regulator_Elenchus_Paper.pdf"
META_PATH = REPO / "papers" / "dyadic_ns_regulator_elenchus" / "publication_meta.json"
RECEIPT_PATH = REPO / "results" / "dyadic_ns_regulator_elenchus" / "zenodo_publication_receipt.json"
ZENODO = "https://zenodo.org/api"


def load_zenodo_token(path: Path | None = None) -> str:
    if os.environ.get("ZENODO_TOKEN"):
        return os.environ["ZENODO_TOKEN"].strip()
    candidates = [
        path,
        Path.home() / ".env",
        Path.home() / ".zenodo_token",
        Path.home() / ".config" / "zenodo" / "token",
    ]
    for p in candidates:
        if p and p.exists():
            for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw.strip().removeprefix("export ").strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, val = line.partition("=")
                    if key.strip() in ("ZENODO_TOKEN", "ZENODO_API_TOKEN"):
                        return val.strip().strip('"').strip("'")
                else:
                    return line.strip('"').strip("'")
    raise RuntimeError("No ZENODO_TOKEN found in environment or token files.")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def bundle_members() -> list[Path]:
    members: list[Path] = []
    for sub in (
        "results/dyadic_ns_regulator_elenchus",
        "papers/dyadic_ns_regulator_elenchus",
        "scripts/dyadic_ns_regulator_elenchus",
    ):
        d = REPO / sub
        if d.exists():
            members += [
                p
                for p in d.rglob("*")
                if p.is_file() and p.suffix not in {".aux", ".log", ".out", ".pyc"}
                and not any(part.startswith("review") or part == "__pycache__" for part in p.relative_to(REPO).parts)
                and p.name != "zenodo_publication_receipt.json"
            ]
    extra_files = [
        REPO / "formal" / "ANSE" / "DyadicNavierStokesRegulatorSpec.lean",
        REPO / "formal" / "ANSE" / "DyadicNavierStokesRegulator.lean",
    ]
    members += [p for p in extra_files if p.exists()]
    return sorted(set(members))


def build_bundle() -> tuple[Path, Path]:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    members = bundle_members()
    manifest = {
        str(p.relative_to(REPO)): {"sha256": sha256(p), "bytes": p.stat().st_size}
        for p in members
    }
    manifest_path = BUNDLE_DIR / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    tar_path = BUNDLE_DIR / "autoevolve_dyadic_ns_regulator_elenchus_2026-10.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        for p in members:
            tar.add(p, arcname=str(p.relative_to(REPO)))
        tar.add(manifest_path, arcname="MANIFEST.json")
    return tar_path, manifest_path


def zenodo_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "metadata": {
            "title": meta["title"],
            "upload_type": "publication",
            "publication_type": "preprint",
            "description": meta["description"],
            "creators": [{"name": "Callens, Xavier", "affiliation": "SocrateAI Lab"}],
            "keywords": meta.get("keywords", []),
            "license": "cc-by-4.0",
            "related_identifiers": [
                {
                    "identifier": "https://github.com/xaviercallens/AutoevolveAI",
                    "relation": "isSupplementTo",
                    "scheme": "url",
                },
                {"identifier": "10.5281/zenodo.23458238", "relation": "isNewVersionOf", "scheme": "doi"},
            ],
            "version": meta.get("version", "2.1"),
            "notes": meta.get("notes", ""),
        }
    }


def zenodo_request(
    method: str,
    url: str,
    token: str,
    data: bytes | None = None,
    content_type: str = "application/json",
) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        },
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        body = r.read()
        return json.loads(body) if body else {}


def publish_zenodo(
    token: str,
    files: list[Path],
    meta: dict[str, Any],
    publish: bool,
    new_version_of: int | None = None,
) -> dict[str, Any]:
    if new_version_of is not None:
        nv = zenodo_request("POST", f"{ZENODO}/deposit/depositions/{new_version_of}/actions/newversion", token)
        dep = zenodo_request("GET", nv["links"]["latest_draft"], token)
        for old in dep.get("files", []):
            zenodo_request("DELETE", f"{ZENODO}/deposit/depositions/{dep['id']}/files/{old['id']}", token)
    else:
        dep = zenodo_request("POST", f"{ZENODO}/deposit/depositions", token, b"{}")
    bucket = dep["links"]["bucket"]
    for f in files:
        with open(f, "rb") as fh:
            zenodo_request(
                "PUT",
                f"{bucket}/{f.name}",
                token,
                fh.read(),
                "application/octet-stream",
            )
    dep = zenodo_request(
        "PUT",
        f"{ZENODO}/deposit/depositions/{dep['id']}",
        token,
        json.dumps(zenodo_metadata(meta)).encode("utf-8"),
    )
    if publish:
        dep = zenodo_request(
            "POST",
            f"{ZENODO}/deposit/depositions/{dep['id']}/actions/publish",
            token,
        )
    return {
        "id": dep.get("id"),
        "doi": dep.get("doi") or dep.get("metadata", {}).get("prereserve_doi", {}).get("doi"),
        "conceptrecid": dep.get("conceptrecid"),
        "state": dep.get("state"),
        "submitted": dep.get("submitted"),
        "html": dep.get("links", {}).get("html") or dep.get("links", {}).get("record_html"),
        "doi_url": dep.get("links", {}).get("doi"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", type=Path, default=None)
    ap.add_argument("--meta", type=Path, default=META_PATH)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--publish", action="store_true", help="publish deposition on Zenodo (mints permanent DOI)")
    ap.add_argument("--new-version-of", type=int, default=None, help="deposition id to create a new version of (keeps that record's concept DOI)")
    args = ap.parse_args()

    meta = json.loads(args.meta.read_text(encoding="utf-8"))
    tar_path, manifest_path = build_bundle()
    report: dict[str, Any] = {
        "bundle": str(tar_path.relative_to(REPO)),
        "bundle_sha256": sha256(tar_path),
        "bundle_bytes": tar_path.stat().st_size,
        "manifest": str(manifest_path.relative_to(REPO)),
        "files_in_manifest": len(json.loads(manifest_path.read_text(encoding="utf-8"))),
        "paper_pdf": str(PAPER_PDF.relative_to(REPO)),
        "paper_pdf_sha256": sha256(PAPER_PDF),
        "paper_pdf_bytes": PAPER_PDF.stat().st_size,
    }
    if args.dry_run:
        report["zenodo_metadata"] = zenodo_metadata(meta)
        print(json.dumps(report, indent=2))
        return 0

    token = load_zenodo_token(args.token_file)
    report["zenodo"] = publish_zenodo(
        token,
        [PAPER_PDF, tar_path, manifest_path],
        meta,
        publish=args.publish,
        new_version_of=args.new_version_of,
    )
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
