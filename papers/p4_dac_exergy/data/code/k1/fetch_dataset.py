"""Fetch the 51 dataset members used for the Table 2 materials from the public Zenodo record 10.5281/zenodo.14452152
(CC-BY-4.0, A. McDannald and D. W. Siderius, NIST) and verify them against data/zenodo_members_SHA256SUMS.json.

The files are not redistributed in this paper's bundle. The record holds one 3.45 GB archive (DAC_data.tar.gz, md5
a2520f520140c60f8a4663d5b403966c); this script streams it once and extracts only the listed members.

Usage: python -I fetch_dataset.py <sha256sums.json> <output_dir>
"""

from __future__ import annotations

import hashlib
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

URL = "https://zenodo.org/api/records/14452152/files/DAC_data.tar.gz/content"


def main() -> int:
    sums: dict[str, str] = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    bad: list[str] = []
    seen: set[str] = set()
    with urllib.request.urlopen(URL, timeout=120) as resp, tarfile.open(fileobj=resp, mode="r|gz") as tar:
        for m in tar:
            if not m.isfile():
                continue
            rel = next((k for k in sums if m.name == k or m.name.endswith("/" + k)), None)
            if rel is None:
                continue
            fh = tar.extractfile(m)
            if fh is None:
                continue
            data = fh.read()
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            seen.add(rel)
            if hashlib.sha256(data).hexdigest() != sums[rel]:
                bad.append(rel)
            if len(seen) == len(sums):
                break
    missing = sorted(set(sums) - seen)
    print(json.dumps({"extracted": len(seen), "sha256_mismatch": bad, "missing": missing}, indent=1))
    return 1 if bad or missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
