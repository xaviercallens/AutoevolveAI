#!/usr/bin/env python3
"""Publish one autoresearch contribution paper (papers/ar_<slug>/) and its evidence bundle to Zenodo.

Reuses the token, upload and request helpers of publish_universal_optimality_tiered.py. Flow: ``--dry-run`` (bundle
and metadata only), ``--draft`` (create the deposition, upload, reserve a DOI, written to papers/ar_<slug>/zenodo_doi.txt),
``--update-id`` (re-upload after the PDF is rebuilt with the DOI), ``--publish-id`` (irreversible). Tokens are never
printed.

Usage:
    python3 -I scripts/publish_ar_paper.py --slug dipolar_exciton --token-file ~/.token_workflow_token --dry-run
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import tarfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
ARCHIVE = Path("/home/callensxavier_gmail_com/zenodo-bundles")
KEEP_SUFFIXES = {".json", ".jsonl", ".md", ".py", ".tex", ".lean", ".txt", ".rs", ".toml", ".csv", ".tsv"}
SKIP_DIRS = {"scratch", "scratch_olean", "__pycache__", ".lake", ".olean_out", "target"}
LANE_ID = {"dipolar_exciton": "H1", "yukawa_crystal": "H2", "keldysh_tmd": "H3", "sigma3_enstrophy": "H7",
           "bogoliubov_sk": "H8"}

_spec = importlib.util.spec_from_file_location("tiered", REPO / "scripts" / "publish_universal_optimality_tiered.py")
assert _spec is not None and _spec.loader is not None
tiered = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tiered)


def members(paper: Path, lane: Path) -> list[tuple[Path, str]]:
    """Paper sources and data, the lane's records, and the Lean files (Autoresearch or Programmes) the paper cites."""
    out: list[tuple[Path, str]] = []
    for d in (paper, lane):
        for p in d.rglob("*"):
            if (p.is_file() and p.suffix in KEEP_SUFFIXES and not (SKIP_DIRS & set(p.parts))
                    and p.stat().st_size < 20_000_000):
                out.append((p, str(p.relative_to(REPO))))
    tex = (paper / "main.tex").read_text(errors="ignore") if (paper / "main.tex").exists() else ""
    for p in sorted(list((REPO / "formal_cert" / "Autoresearch").glob("*.lean"))
                    + list((REPO / "formal_cert" / "Programmes").rglob("*.lean"))):
        if p.stem in tex or p.stem.replace("Controls", "") in tex:
            out.append((p, str(p.relative_to(REPO))))
    for rel in ("scripts/certified_numerics/lean_pinned.py", "results/autoresearch/2026-10-25/program.md",
                "results/autoresearch/2026-10-25/preregistration.json"):
        out.append((REPO / rel, rel))
    return sorted(set(out), key=lambda t: t[1])


def build_bundle(paper: Path, lane: Path) -> tuple[Path, Path, Path]:
    bname = paper.name
    d = ARCHIVE / bname
    d.mkdir(parents=True, exist_ok=True)
    pairs = members(paper, lane)
    manifest = {arc: {"sha256": tiered.sha256(p), "bytes": p.stat().st_size} for p, arc in pairs}
    mpath = d / "MANIFEST.json"
    mpath.write_text(json.dumps(manifest, indent=1))
    tar_path = d / f"{bname}_2026-10-25.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        for p, arc in pairs:
            tar.add(p, arcname=arc)
        tar.add(mpath, arcname="MANIFEST.json")
    pdf = d / f"{bname}.pdf"
    pdf.write_bytes((paper / "main.pdf").read_bytes())
    return tar_path, mpath, pdf


def zenodo_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    rel = list(meta.get("related_identifiers", []))
    rel.append({"identifier": "https://github.com/xaviercallens/AutoevolveAI", "relation": "isSupplementTo", "scheme": "url"})
    return {"metadata": {
        "title": meta["title"], "upload_type": "publication",
        "publication_type": meta.get("publication_type", "preprint"),
        "description": meta["description"],
        "creators": [{"name": "Callens, Xavier", "affiliation": "SocrateAI Lab"}],
        "keywords": meta["keywords"], "license": "cc-by-4.0", "version": meta.get("version", "v1"),
        "related_identifiers": rel, "notes": meta.get("notes", ""),
    }}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="autoresearch slug (papers/ar_<slug>, lane from LANE_ID)")
    ap.add_argument("--paper-dir", type=Path, help="paper directory (overrides --slug)")
    ap.add_argument("--lane-dir", type=Path, help="lane records directory (required with --paper-dir)")
    ap.add_argument("--token-file", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--update-id", type=int)
    ap.add_argument("--publish-id", type=int)
    args = ap.parse_args()
    if args.paper_dir:
        paper, lane = args.paper_dir.resolve(), args.lane_dir.resolve()
    else:
        paper = REPO / "papers" / f"ar_{args.slug}"
        lane = REPO / "results" / "autoresearch" / "2026-10-25" / LANE_ID[args.slug]
    meta = json.loads((paper / "publication_meta.json").read_text())
    Z = tiered.ZENODO
    if args.publish_id:
        token = tiered.load_tokens(args.token_file)["ZENODO_TOKEN"]
        dep = tiered.zenodo_request("POST", f"{Z}/deposit/depositions/{args.publish_id}/actions/publish", token)
        print(json.dumps({"zenodo": tiered.summary(dep)}, indent=2))
        return 0
    tar_path, mpath, pdf = build_bundle(paper, lane)
    report: dict[str, Any] = {"bundle": str(tar_path), "bundle_bytes": tar_path.stat().st_size,
                              "files_in_manifest": len(json.loads(mpath.read_text())), "pdf_sha256": tiered.sha256(pdf)}
    if args.dry_run:
        report["zenodo_metadata"] = zenodo_metadata(meta)
        print(json.dumps(report, indent=2))
        return 0
    token = tiered.load_tokens(args.token_file)["ZENODO_TOKEN"]
    files = [pdf, tar_path, mpath]
    if args.draft:
        dep = tiered.zenodo_request("POST", f"{Z}/deposit/depositions", token, b"{}")
        tiered.upload(token, dep, files)
        dep = tiered.zenodo_request("PUT", f"{Z}/deposit/depositions/{dep['id']}", token,
                                    json.dumps(zenodo_metadata(meta)).encode())
        report["zenodo"] = tiered.summary(dep)
        if report["zenodo"]["doi"]:
            (paper / "zenodo_doi.txt").write_text(report["zenodo"]["doi"] + "\n")
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
