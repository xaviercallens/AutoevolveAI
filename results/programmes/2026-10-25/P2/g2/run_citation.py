"""Build Tier-L citation claims from the fetched arXiv text of Luo-Wei (2302.05042v1) and run the Elenchus citation gate.

usage: python3 run_citation.py OUT.json
The quotes are copied programmatically from the pdftotext extraction (lines located by their headers), so the gate
tests faithfulness against the caller-fetched source, not against a model's paraphrase.
"""

import hashlib
import json
import subprocess
import sys

SRC = "/home/callensxavier_gmail_com/programmes-2026-10-25/P2/g2/src_luowei/2302.05042v1.txt"
TOOL = "/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/citation_check.py"
OUTDIR = "/home/callensxavier_gmail_com/programmes-2026-10-25/P2/g2"

data = open(SRC, "rb").read()
lines = data.decode("utf-8").splitlines()
digest = "sha256:" + hashlib.sha256(data).hexdigest()


def block(header: str, n: int) -> str:
    i = next(k for k, l in enumerate(lines) if l.startswith(header))
    return "\n".join(lines[i : i + n])


claims = {
    "luowei_cor_1_1": {
        "source_id": "arXiv:2302.05042v1 (S. Luo, J. Wei, On lattice hexagonal crystallization for non-monotone potentials), p. 3",
        "source_sha256": digest,
        "kind": "corollary",
        "quote": block("Corollary 1.1. For any", 5),
        "hypotheses": ["L ranges over two-dimensional lattices of unit density (|L| = 1)", "alpha >= 1"],
        "statement_match": "match",
        "used_for": "PROOF.md 3.3 Consequence 1: for a <= 1 the triangular lattice maximises <tr D> = 4 pi a - (4 pi^2/a) S(1/a; L)",
    },
    "luowei_lemma_3_5": {
        "source_id": "arXiv:2302.05042v1 (S. Luo, J. Wei), p. 12, Lemma 3.5",
        "source_sha256": digest,
        "kind": "lemma",
        "quote": block("Lemma 3.5. For b =", 4),
        "hypotheses": ["b = 1/(2 pi)", "z in the upper half plane H (unit-density lattice of shape z)"],
        "statement_match": "match",
        "used_for": "PROOF.md 3.3 Consequence 2: S(1; L) = theta(1; L)/(2 pi), i.e. <tr D> = 4 pi - 2 pi theta(1; L) at a = 1",
    },
}
SRC2 = "/home/callensxavier_gmail_com/programmes-2026-10-25/P2/g2/src_dengluo/2411.17199v1.txt"
data2 = open(SRC2, "rb").read()
lines2 = data2.decode("utf-8").splitlines()
i2 = next(k for k, l in enumerate(lines2) if l.startswith("Theorem A (Montgomery"))
claims["montgomery_via_dengluo"] = {
    "source_id": "arXiv:2411.17199v1 (K. Deng, S. Luo, Minimizing lattice energy and hexagonal crystallization), p. 3, restating H. Montgomery, Glasgow Math. J. 30 (1988) 75-85",
    "source_sha256": "sha256:" + hashlib.sha256(data2).hexdigest(),
    "kind": "theorem",
    "quote": "\n".join(lines2[i2 : i2 + 5]),
    "hypotheses": ["alpha > 0", "z ranges over the upper half plane H (unit-density two-dimensional lattices), minimum up to rotations and translations"],
    "statement_match": "match",
    "used_for": "PROOF.md 3.2 (Lap E_static(rho) >= 0) and 3.3 Consequence 2 (unique maximiser of <tr D> at a = 1); secondary source, original not opened",
}
srcs = {"montgomery_via_dengluo": SRC2}
res = {}
for name, c in claims.items():
    path = f"{OUTDIR}/claim_{name}.json"
    json.dump(c, open(path, "w"), indent=1, ensure_ascii=False)
    r = subprocess.run([sys.executable, "-I", TOOL, path, srcs.get(name, SRC)], capture_output=True, text=True)
    res[name] = {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr, "claim": c}
    print(name, r.returncode, r.stdout.strip()[:600], r.stderr.strip()[:300])
json.dump(res, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
