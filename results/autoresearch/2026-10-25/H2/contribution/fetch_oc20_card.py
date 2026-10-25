"""Download the dataset card (README.md) of colabfit/OC20_IS2RES_val_id at the pinned revision and grep its DOIs.

Usage: python -I fetch_oc20_card.py OUT_DIR OUT_JSON
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from huggingface_hub import hf_hub_download

REPO = "colabfit/OC20_IS2RES_val_id"
REV = "6a1dfef12aec878b4cda99edd54b16a6a254e135"


def main(out_dir: str, out_json: str) -> int:
    p = Path(hf_hub_download(REPO, "README.md", repo_type="dataset", revision=REV, local_dir=out_dir))
    raw = p.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    dois = sorted(set(re.findall(r"10\.\d{4,9}/[A-Za-z0-9._\-/]+[A-Za-z0-9]", text)))
    ctx = {d: [l.strip() for l in text.splitlines() if d in l][:3] for d in dois}
    rec = {"repo": REPO, "revision": REV, "file": "README.md", "sha256": hashlib.sha256(raw).hexdigest(),
           "bytes": len(raw), "dois": dois, "doi_lines": ctx}
    Path(out_json).write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
