"""Inventory of the external EG-CB68 route-1 certificates (kept OUTSIDE the bundle) and the LaTeX table of their names, sizes and sha256.

Reads the 12 gzip files in CERT_DIR, re-computes the gzip sha256 and (by streaming decompression) the plain sha256 and size, compares both
with the producer's data/logs/main/cert_sha256.txt and with the auditor's recorded hashes (data/audit/out/certs/*.gzsha.txt, *.plainsha.txt),
and writes data/certs_inventory.json and table_certs.tex. Run:  python3 -I make_cert_inventory.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
DATA = PAPER / "data"
CERT_DIR = Path("/home/callensxavier_gmail_com/EG-CB68_scratch/certs")


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_gz_plain(p: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    n = 0
    with gzip.open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    return h.hexdigest(), n


def producer_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (DATA / "logs" / "main" / "cert_sha256.txt").read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            out[Path(parts[1]).name] = parts[0]
    return out


def auditor_first_token(path: Path) -> str:
    return path.read_text().split()[0]


def main() -> int:
    prod = producer_hashes()
    rows = []
    for cap in range(30, 36):
        for o in (1, 2):
            name = f"T_cap{cap}_o{o}.cert"
            gz = CERT_DIR / f"{name}.gz"
            gsha = sha_file(gz)
            psha, plen = sha_gz_plain(gz)
            tag = f"T{cap}_o{o}"
            ad = DATA / "audit" / "out" / "certs"
            aud_gz = auditor_first_token(ad / f"{tag}.gzsha.txt")
            aud_plain = auditor_first_token(ad / f"{tag}.plainsha.txt")
            aud_verdict = (ad / f"{tag}.aud.txt").read_text().strip().split()[0]
            fast = json.loads((ad / f"{tag}.fast.txt").read_text())
            row = {"file": f"{name}.gz", "cap": cap, "orbit": o, "order": 2 * cap, "gz_bytes": gz.stat().st_size, "gz_sha256": gsha,
                   "plain_bytes": plen, "plain_sha256": psha,
                   "producer_gz_sha_equal": prod.get(f"{name}.gz") == gsha, "producer_plain_sha_equal": prod.get(name) == psha,
                   "auditor_gz_sha_equal": aud_gz == gsha, "auditor_plain_sha_equal": aud_plain == psha,
                   "auditor_checker_verdict": aud_verdict,
                   "producer_c_checker": {k: fast[k] for k in ("accepted", "cap", "orbit", "c6", "completions")}}
            if not (row["producer_gz_sha_equal"] and row["producer_plain_sha_equal"] and row["auditor_gz_sha_equal"] and row["auditor_plain_sha_equal"]):
                raise SystemExit(f"hash disagreement in {name}")
            rows.append(row)
    total = sum(r["gz_bytes"] for r in rows)
    inv = {"cert_dir": str(CERT_DIR), "n_files": len(rows), "total_gz_bytes": total, "total_gz_MiB": round(total / 2**20, 1),
           "note": "regenerable: cb_search CAP ORBIT A -cert FILE (data/code/cb_search.c.txt), then gzip; the stream is deterministic (same transcript hash and sha256)",
           "files": rows}
    (DATA / "certs_inventory.json").write_text(json.dumps(inv, indent=1))
    lines = [r"\begin{longtable}{@{}lrr@{}}", r"\toprule file (gzip) & bytes (gz) & bytes (plain) \\ \midrule \endhead"]
    for r in rows:
        lines.append(rf"\multicolumn{{3}}{{@{{}}l}}{{\texttt{{{r['file'].replace('_', chr(92) + '_')}}}}}\\")
        lines.append(rf"\multicolumn{{1}}{{@{{}}l}}{{\quad\texttt{{\tiny gz {r['gz_sha256']}}}}} & {r['gz_bytes']:,} & {r['plain_bytes']:,} \\".replace(",", r"\,"))
        lines.append(rf"\multicolumn{{3}}{{@{{}}l}}{{\quad\texttt{{\tiny plain {r['plain_sha256']}}}}}\\[2pt]")
    lines += [r"\bottomrule", r"\end{longtable}"]
    (PAPER / "table_certs.tex").write_text("\n".join(lines) + "\n")
    print(f"files {len(rows)}; total gz bytes {total} ({total / 2**20:.1f} MiB); all hashes agree (producer, auditor, recomputed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
