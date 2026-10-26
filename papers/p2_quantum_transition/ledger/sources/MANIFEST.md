# Literature source texts (not redistributed)

The fifteen quotation rows (B1-C-0101 ... B1-C-0115) quote four arXiv papers that the producer fetched from arxiv.org and read. The full texts are not bundled.
To re-check: fetch `https://arxiv.org/pdf/<id>` (version as below), compare the PDF hash, run `pdftotext <file>.pdf <file>.txt` (poppler, default options) and compare the text hash with
`source_sha256` in `ledger/citations/claim_*.json`. Local copies on the producing machine: `/home/callensxavier_gmail_com/programmes-2026-10-26/B1/src/` and `.../src2/`.
`ledger/run_citation.py` copies each quotation programmatically from this text output and runs the Elenchus citation gate twice (real kind: REFUSED because the kind is not theorem-like;
kind relabelled only to test verbatim fidelity: ACCEPTED). Neither result is a Tier L acceptance.

| arXiv id (version fetched) | paper | pdf sha256 | pdftotext sha256 |
|---|---|---|---|
| cond-mat/0608246v2 | G. E. Astrakharchik, J. Boronat, I. L. Kurbakov, Yu. E. Lozovik, Quantum phase transition in a two-dimensional system of dipoles (PRL 98, 060405) | `0a5471b511c8e708ad2d83224542b07f13987b113eb349862ca3518b8990b0a3` | `ac9917c85b597651b8f49f283469fec2f31b1657645f68d9c23b1361b3f0b170` |
| 1809.07515v1 | S. Prestipino, A. Sergi, E. Bruno, Freezing of soft-core bosons at zero temperature: a variational theory (PRB 98, 104104) | `aac45813acde04432fc8a9e826dbfd914f2728cbee0d788f6c16864c500b1bee` | `44261cc581461c9cf20748cd8e353b9f85621e42190b0ff9f11c917e3e8dbcbe` |
| 1001.3250v2 | N. Henkel, R. Nath, T. Pohl, Three-dimensional roton excitations and supersolid formation in Rydberg-excited BECs (PRL 104, 195302) | `99131c1417433c87dc727149c8c3fc1411055998972e29a4d82b453248fa8c76` | `0f0c8a78fcf6fc91f187421c9e1091f2cc4f86b6e7c562d677971f5001449a2f` |
| 1602.06313v3 | J. Zeiher et al., Many-body interferometry of a Rydberg-dressed spin lattice | `e92579916d4d6c2d09bdb426402bbee33101edf13b8c8f96f16f9ad2e1423d5b` | `b921dc2229f5838a0afe9470008af2bc200882f3f96643e3d18ff90497fd8ef2` |

Page numbers in the ledger are PDF page indices found by searching the first line of each quotation in per-page pdftotext output.

Not found in the source text: the definition of the lattice length `a_L` in the Astrakharchik et al. Lindemann sentence (the producer's note claimed a page-3 definition `a_L^-1 = (sqrt(3) n/2)^(1/2)`;
pdftotext shows only "(aL is the lattice length)"). The reading `a_L` = nearest-neighbour distance is therefore recorded as an assumption (B1-C-0011).

Other references (sub-agent read, never re-read by us, in no ledger row): arXiv:1402.0840, 1201.0980, 2010.04631, 1107.0828, 2209.02802. Their titles, authors, dates and journal references were
checked against arxiv.org abstract pages by `ledger/verify_refs.py` (output `ledger/sources/refs_meta.json`); their content was not.
