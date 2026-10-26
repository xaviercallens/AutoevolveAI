"""Build Tier-L citation claims from pdftotext output of arXiv PDFs that the producer fetched and read, and run the Elenchus citation gate.

Quotes are copied programmatically (lines located by a header prefix), so the gate tests fidelity against the fetched source. The page number is
found by searching the quote's first line in the per-page pdftotext output. Sources are kept outside the bundle (see sources/MANIFEST.md).
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I run_citation.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "citations"
OUT.mkdir(exist_ok=True)
TOOL = "/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/citation_check.py"
S1 = Path("/home/callensxavier_gmail_com/programmes-2026-10-26/B1/src")
S2 = Path("/home/callensxavier_gmail_com/programmes-2026-10-26/B1/src2")

SRC = {
    "astra": (S1 / "cond-mat_0608246v2", "arXiv:cond-mat/0608246v2 (G. E. Astrakharchik, J. Boronat, I. L. Kurbakov, Yu. E. Lozovik, Quantum phase transition in a two-dimensional system of dipoles)"),
    "prest": (S1 / "1809.07515v1", "arXiv:1809.07515v1 (S. Prestipino, A. Sergi, E. Bruno, Freezing of soft-core bosons at zero temperature: a variational theory)"),
    "henkel": (S2 / "1001.3250", "arXiv:1001.3250v2 (N. Henkel, R. Nath, T. Pohl, Three-dimensional roton excitations and supersolid formation in Rydberg-excited Bose-Einstein condensates)"),
    "zeiher": (S2 / "1602.06313", "arXiv:1602.06313v3 (J. Zeiher et al., Many-body interferometry of a Rydberg-dressed spin lattice)"),
}

# key, source, header prefix of first line, number of lines, line offset, kind, hypotheses, used_for
CLAIMS = [
    ("astra_lindemann", "astra", "pWe estimate the thermodynamic Lindemann", 5, 0, "numerical result",
     ["two-dimensional Bose systems at the quantum melting density, QMC", "a_L called 'the lattice length' in the source (our reading: nearest-neighbour distance, Tier C)"],
     "gamma_c band 0.23-0.28 for the harmonic Lindemann comparison"),
    ("prest_marginal", "prest", "n > 2 [37]. The Gaussian repulsion", 3, 0, "statement",
     ["mean-field (Gross-Pitaevskii/variational) theory of soft-core bosons at T = 0"], "Gaussian is the marginal GEM case; no cluster crystal in 2D/3D"),
    ("prest_swept", "prest", "potentials and the SVDW interaction. Looking at Table 1", 5, 0, "statement",
     ["mean-field theory, pressure-driven crystallisation of bosons at T = 0", "weak-coupling condensate state"], "mean-field crystallisation absent for n = 2"),
    ("prest_washed", "prest", "as a superfluid (these features also hold", 5, 0, "statement",
     ["mean-field theory, T = 0"], "freezing washed out in the Gaussian n = 2 case (conclusions)"),
    ("prest_mf", "prest", "In this paper we employ MF theory", 4, 0, "statement",
     ["scope of the mean-field assumption: weak interparticle forces"], "mean-field regime is the opposite of the one-particle-per-site crystal"),
    ("henkel_pot", "henkel", "surface is given by a sum of binary", 4, 0, "definition",
     ["Rydberg-dressed BEC, leading-order Born-Oppenheimer surface"], "dressed potential U = C6/(r^6 + Rc^6), a soft shoulder"),
    ("henkel_neg", "henkel", "due to the inner potential plateau", 2, 0, "statement",
     ["momentum-space potential of the dressed soft-core interaction"], "negative Fourier components of the dressed potential"),
    ("henkel_weak", "henkel", "[26] For the parameters of Fig.3c", 1, 0, "statement",
     ["parameters of their Fig. 3c"], "dressed BEC is deep in the mean-field regime"),
    ("zeiher_form", "zeiher", "Ui,j = U0 /(1+(R/Rc )6 ) denotes", 2, 0, "definition",
     ["Rydberg-dressed spins pinned on an optical lattice"], "soft-shoulder form used by the experiment"),
    ("zeiher_u0", "zeiher", "The resulting long-range spin interactions with U0", 2, 0, "numerical result",
     ["experimental dressing parameters of the paper"], "U0/2pi = 1.8 kHz"),
    ("zeiher_rc", "zeiher", "Neff contributing to the shift.", 4, 0, "numerical result",
     ["31P1/2 state"], "Rc/a_lat = 2.02"),
    ("zeiher_lat", "zeiher", "square optical lattice with alat = 532 nm", 2, 0, "numerical result",
     ["experimental setup"], "a_lat = 532 nm"),
    ("zeiher_rb", "zeiher", "rubidium-87 in the", 1, 0, "statement",
     ["experimental setup"], "species is rubidium-87"),
    ("zeiher_loss", "zeiher", "N (0), the extracted value of 130(20)", 4, 0, "numerical result",
     ["measured loss of the dressed atoms"], "measured dressed-state loss time 130(20) microseconds vs 2.2 ms anticipated"),
    ("zeiher_tau", "zeiher", "31PJ state (J = 1/2 or J = 3/2)", 2, 0, "numerical result",
     ["bare Rydberg state"], "bare Rydberg lifetime 27 microseconds"),
]


def page_of(pdf: Path, first_line: str) -> int | None:
    key = re.sub(r"\s+", " ", first_line)[:40]
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    for p in range(1, n + 1):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), str(pdf), "-"], capture_output=True, text=True).stdout
        if key in re.sub(r"\s+", " ", t):
            return p
    return None


def main() -> int:
    res: dict[str, dict] = {}
    texts: dict[str, tuple[list[str], str, Path]] = {}
    for k, (base, label) in SRC.items():
        raw = Path(str(base) + ".txt").read_bytes()
        texts[k] = (raw.decode("utf-8").splitlines(), "sha256:" + hashlib.sha256(raw).hexdigest(), Path(str(base) + ".pdf"))
    for key, sk, prefix, n, off, kind, hyp, used in CLAIMS:
        lines, dig, pdf = texts[sk]
        i = next(j for j, l in enumerate(lines) if l.startswith(prefix)) + off
        quote = "\n".join(lines[i:i + n])
        pg = page_of(pdf, lines[i])
        claim = {"source_id": f"{SRC[sk][1]}, p. {pg}", "source_sha256": dig, "kind": kind, "quote": quote, "hypotheses": hyp,
                 "statement_match": "match", "used_for": used,
                 "pdf_sha256": "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest(), "pdf_page": pg}
        path = OUT / f"claim_{key}.json"
        path.write_text(json.dumps(claim, indent=1, ensure_ascii=False))
        src_txt = Path(str(SRC[sk][0]) + ".txt")
        r = subprocess.run([sys.executable, "-I", TOOL, str(path), str(src_txt)], capture_output=True, text=True)
        # the gate admits only theorem-like kinds for Tier L; none of these sources states a theorem we use, so the real verdict is REFUSED (CITE_KIND).
        # We additionally run the same gate on a copy whose kind is relabelled 'proposition' ONLY to test that the quote is verbatim in the fetched text.
        vclaim = dict(claim, kind="proposition")
        vpath = OUT / f"verbatim_{key}.json"
        vpath.write_text(json.dumps(vclaim, indent=1, ensure_ascii=False))
        rv = subprocess.run([sys.executable, "-I", TOOL, str(vpath), str(src_txt)], capture_output=True, text=True)
        res[key] = {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr, "claim": claim,
                    "verbatim_only_check": {"note": "same gate, kind relabelled 'proposition' solely to test verbatim fidelity; NOT a Tier L acceptance",
                                            "rc": rv.returncode, "stdout": rv.stdout, "stderr": rv.stderr}}
        verdict = json.loads(r.stdout)["verdict"] if r.stdout.strip().startswith("{") else r.stdout.strip()[:80]
        vv = json.loads(rv.stdout)["verdict"] if rv.stdout.strip().startswith("{") else rv.stdout.strip()[:80]
        print(key, "page", pg, "real gate:", verdict, "| verbatim-only:", vv)
    (OUT / "citation_check.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
