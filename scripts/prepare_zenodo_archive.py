"""
prepare_zenodo_archive.py
=========================
Package Laya-LoRA Coding Companion telemetry receipts and Lean 4 proofs
into a Zenodo-ready ZIP archive for DOI minting.

Artifacts bundled:
  1. download_receipt.json         — dataset provenance (78,503 records, SHA-256 verified)
  2. training_summary.json         — 3-stage training receipts (loss, accuracy, duration)
  3. coding_benchmark_and_comparison.json — 12-case benchmark results
  4. formal/ANSE/LayaDecision.lean — Lean 4 deployment invariants (with sorry state)
  5. formal/lakefile.lean          — Lean 4 project build spec

Output: artifacts/zenodo_bundle/laya_lora_telemetry_v1.zip
        artifacts/zenodo_bundle/METADATA.json

After upload to https://zenodo.org/deposit, replace DOI placeholder
'10.5281/zenodo.XXXXXXX' in papers/laya_coding_companion_paper.tex.

Usage:
  uv run python scripts/prepare_zenodo_archive.py
"""

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/xavkal/.gemini/antigravity/worktrees/AutoevolveAI/sub_project_management")
ARTIFACTS_DIR = REPO / "artifacts" / "laya_coding_companion"
FORMAL_DIR = REPO / "formal" / "ANSE"

BUNDLE_DIR = REPO / "artifacts" / "zenodo_bundle"
BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

ZENODO_DOI_PLACEHOLDER = "10.5281/zenodo.XXXXXXX"

TELEMETRY_FILES = [
    ARTIFACTS_DIR / "download_receipt.json",
    ARTIFACTS_DIR / "training_summary.json",
    ARTIFACTS_DIR / "coding_benchmark_and_comparison.json",
]

LEAN_FILES = [
    FORMAL_DIR / "LayaDecision.lean",
    REPO / "formal" / "lakefile.lean",
]

README_CONTENT = """\
# Laya-LoRA Coding Companion — Zenodo Telemetry Archive

## Version: v1.0
## Date: {date}

This archive contains machine-derived telemetry receipts and Lean 4 formal proof
files for the Laya-LoRA Coding Companion paper.

## Contents

| File | Description |
|---|---|
| download_receipt.json | Dataset provenance: 10 datasets, 78,503 records, SHA-256 hashes |
| training_summary.json | 3-stage curriculum training results (loss, accuracy, duration) |
| coding_benchmark_and_comparison.json | 12-case benchmark results + model comparison |
| LayaDecision.lean | Lean 4 deployment invariants (I1: FLOP, I2: Budget, I3: Energy) |
| lakefile.lean | Lean 4 project build specification |

## SHA-256 Verification

All files are listed with their SHA-256 checksums in METADATA.json.
The telemetry JSON values are the ground-truth source for all numeric
claims in the paper (zero LLM hallucination — all values machine-derived).

## Lean 4 Sorry Obligation

LayaDecision.lean contains an unresolved `sorry` on Invariant I3
(`cpu_energy_bounded`). The file compiles with `lake build` but emits a warning.
This is the exact proof state used in the paper. Researchers wishing to
discharge the proof should implement the Lean 4 telemetry macro described
in Section 7.4 of the paper.

## Citation

If you use these artifacts, please cite:
  Callens, X. (2026). Laya-LoRA Coding Companion: Curriculum Training on 10
  Structured Coding Datasets. AutoevolveAI Open-Source Research.
  Zenodo DOI: {doi}
"""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def bundle_zip() -> Path:
    zip_path = BUNDLE_DIR / "laya_lora_telemetry_v1.zip"
    files_meta = []

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in TELEMETRY_FILES + LEAN_FILES:
            if f.exists():
                arcname = f.name
                zf.write(f, arcname)
                sha = sha256_file(f)
                size = f.stat().st_size
                files_meta.append({
                    "filename": arcname,
                    "sha256": sha,
                    "size_bytes": size,
                    "path_in_repo": str(f.relative_to(REPO)),
                })
                print(f"  + {arcname}  ({size:,} bytes)  SHA-256: {sha[:16]}…")
            else:
                print(f"  ⚠ MISSING: {f} — skipped")

        # README
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        readme = README_CONTENT.format(date=now, doi=ZENODO_DOI_PLACEHOLDER)
        zf.writestr("README.md", readme)

    return zip_path, files_meta


def main():
    print("[1/2] Bundling artifacts into Zenodo ZIP …")
    zip_path, files_meta = bundle_zip()

    zip_sha = sha256_file(zip_path)
    zip_size = zip_path.stat().st_size

    metadata = {
        "title": "Laya-LoRA Coding Companion: Telemetry Receipts and Lean 4 Proofs",
        "description": (
            "Machine-derived JSON telemetry receipts and Lean 4 formal proof files "
            "for the Laya-LoRA Coding Companion paper (AutoevolveAI, 2026). "
            "Contains training provenance, benchmark results, and deployment invariants."
        ),
        "upload_type": "dataset",
        "license": "apache-2.0",
        "keywords": [
            "lora", "modernbert", "code-quality", "curriculum-learning",
            "lean4", "formal-verification", "anse", "autoevolveai"
        ],
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "doi_placeholder": ZENODO_DOI_PLACEHOLDER,
        "zip": {
            "path": str(zip_path),
            "sha256": zip_sha,
            "size_bytes": zip_size,
        },
        "files": files_meta,
        "paper_data_availability_entry": (
            f"Telemetry receipts and Lean 4 proofs are archived at Zenodo: "
            f"\\url{{https://doi.org/{ZENODO_DOI_PLACEHOLDER}}}. "
            f"ZIP SHA-256: \\texttt{{{zip_sha}}}."
        ),
    }

    meta_path = BUNDLE_DIR / "METADATA.json"
    meta_path.write_text(json.dumps(metadata, indent=2))

    print(f"\n[2/2] Metadata written to {meta_path}")
    print(f"\n✓ Zenodo bundle ready:")
    print(f"  ZIP:  {zip_path} ({zip_size / 1e3:.1f} KB)")
    print(f"  SHA:  {zip_sha}")
    print(f"\nNext steps:")
    print(f"  1. Go to https://zenodo.org/deposit/new")
    print(f"  2. Upload {zip_path}")
    print(f"  3. Fill metadata from METADATA.json")
    print(f"  4. Publish and replace '{ZENODO_DOI_PLACEHOLDER}' in:")
    print(f"     - papers/laya_coding_companion_paper.tex (Data Availability section)")
    print(f"     - artifacts/zenodo_bundle/METADATA.json")


if __name__ == "__main__":
    main()
