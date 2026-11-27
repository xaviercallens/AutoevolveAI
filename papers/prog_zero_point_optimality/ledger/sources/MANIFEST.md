# Tier-L source texts (not redistributed)

The Tier-L ledger rows quote two arXiv papers. Their full texts are not bundled; this file lets a reader re-fetch and re-check them.
Fetch `https://arxiv.org/pdf/<id>v1`, compare the PDF hash, then run `pdftotext <id>.pdf <id>.txt` (poppler 22.02.0, default options) and compare the text hash with `source_sha256` in `data/claim_*.json`.

| arXiv id | paper | pdf sha256 | pdftotext sha256 | text hash is a claim source_sha256 | re-extraction identical |
|---|---|---|---|---|---|
| arXiv:2302.05042v1 | S. Luo, J. Wei, On lattice hexagonal crystallization for non-monotone potentials | `e5bb3b069dc37fd7515acce76f2526d640c28e0f571a57009043574eb2c0b519` | `3781675f011a006249fb1ef7dbac50abca5eb748befcd8e4f40d00bc47a93b73` | yes | yes |
| arXiv:2411.17199v1 | K. Deng, S. Luo, Minimizing lattice energy and hexagonal crystallization | `4954a68190118a242d90afc7716da1e0c6fae91da9e5403169e1cdaa9fd5c388` | `9b8a1f5c10adfbc6e21b3e6516e1fa3ad04ba87731c49a89dfa5de3c2994932d` | yes | yes |

Local copies of the fetched files on the machine that produced the paper: `/home/callensxavier_gmail_com/programmes-2026-10-25/P2/g2/src_luowei/` and `.../src_dengluo/`.
The ledger quotations were copied programmatically from this default `pdftotext` output (`run_citation.py` next to those folders).
