# Tier-L and quoted source texts (not redistributed)

The ledger quotes the papers below. Their full texts are not bundled. Fetch `https://arxiv.org/pdf/<id>` on 2026-10-26 (the versions below), run `pdftotext <id>.pdf <id>.txt` (default options, poppler on this machine), and compare the hashes.
Local copies on the producing machine: `/home/callensxavier_gmail_com/p2-b3-sources/`. The quotations were located programmatically in these texts by `ledger/run_citations.py`; the theorem-like ones were accepted by `SocrateAI-Scientific-Elenchus/tools/citation_check.py` (`data/citation_check.json`).

| arXiv id | paper | used for | pdf sha256 | pdftotext sha256 |
|---|---|---|---|---|
| 2610.29732v1 | Muratov, Novaga, BCC optimality for the three-dimensional Coulomb lattice energy | L-0001, L-0002, C-0005 | `2f603bd7c6c9a536d287ad421bfdc036716fa4b08d4bfe3c718cbc8123cff6f0` | `6a6cc8d65b9dd0f2de3d4a1e81e56bb55e3404c1b2bfa7daca08c9fc2f9aaefb` |
| 2610.31456v1 | Luo, Wei, On exact solutions to three-dimensional Yukawa lattice model and BCC to FCC phase transitions | L-0003 | `857e9ba2ee55f2491e34aea93571457f681c3c246f59f278913dfb1fdb806e99` | `b8d93df5d81b14ade22ad25c5d8321367ebe96d15069bb7714fdf0529b5d721d` |
| 1307.2805v5 | Rougerie, Serfaty, Higher dimensional Coulomb gases and renormalized energy functionals | L-0004, C-0004 | `1284d13a2d3840bf6f47ee4a2a635b5775ce15350c4822063bf4d60e48ad9e3f` | `b478c8be178a9d9d6ec106cc3a78f7f624f03e96ac82a8e767c7b0750350bdc7` |
| 1504.01153v2 | Blanc, Lewin, The crystallization conjecture: a review | C-0001 | `576d96791241a7e42d0e99c4b004f277e0dd7b0ff8db02bc19260303c9cdd1d6` | `a02c7b7364d3fb3e4e0a4e4c350b47512f1fd05907cc79eb4f1950610a31340e` |
| 2202.09240v2 | Lewin, survey (J. Math. Phys. 63 (2022) 061101) | C-0002 | `c3c70314375884c55f43cf90786a0f573484e343ae88bf993fc12842e075c2b3` | `9fc9fcd75576a5b6dcc2e1acaa5cfe561738f6982addc7cf5e3355027de73b5e` |
| 2610.28547v1 | Aydin, Iacobelli, Local crystallization in three-dimensional quantization | C-0003 | `f8129ef25efa5016d9e486c53c85e3e29d9f7dcd7075f34761c2cd7ff5fd7018` | `5ccb4f2e143ef568b60d594249226464052bcfbcff67485abeabaa9457b5f8e1` |
| math/9811079v3 | Hales, McLaughlin, The dodecahedral conjecture (abstract and first page only) | C-0006 | `9c7640421e48679fe7262cc71ab1a11e5c42c0bf2d1f2b1e300fbf67e48a1904` | `8d219df0d230ae8ae6dffe277f7a62741cfeee7f1dffe33729f993e3fa7139ff` |

Not read and not cited: Graf-Schenker (bibliographic data only, via Lewin); the original Lieb-Narnhofer 1975 paper; the openai/math manuscript (not re-read at paper stage; see data/FEASIBILITY.md and the P1 audit).
