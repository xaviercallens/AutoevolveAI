"""Apply the stage-5 audit corrections (C1, C2, C3 count, OC20 journal DOI, ledger counts) to publication_meta.json.

Ledger counts are read from the re-run gate output, not typed. Usage: python -I update_meta_stage5.py PAPER_DIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def sub(s: str, old: str, new: str) -> str:
    if s.count(old) != 1:
        raise SystemExit(f"expected exactly one occurrence of: {old!r}")
    return s.replace(old, new)


def main(paper_dir: str) -> int:
    d = Path(paper_dir)
    p = d / "publication_meta.json"
    meta = json.loads(p.read_text())
    gate = json.loads((d / "ledger/gate_output.json").read_text())
    exit_code = (d / "ledger/gate_exit_code.txt").read_text().strip()
    n_claims = gate["claims"]
    n_flags = sum(1 for f in gate["findings"] if f["severity"] == "flag")
    n_blocks = sum(1 for f in gate["findings"] if f["severity"] == "block")
    desc = meta["description"]
    desc = sub(desc, "Elenchus claim ledger (24 claims)", f"Elenchus claim ledger ({n_claims} claims)")
    desc = sub(desc, "<li>negative controls: the sign condition on the weights cannot be dropped.</li>",
               "<li>negative controls: the admissibility lemma needs the sign condition on the weights; g<sub>1</sub> &minus; "
               "2g<sub>2</sub> is not admissible, so the theorem does not apply to it (this does not show that optimality fails "
               "for it).</li>")
    desc = sub(desc, "and none fell below the exact triangular energy.",
               "and none fell below the exact triangular energy beyond f64 resolution (one stage, the perfect lattice at "
               "&kappa; = 1, sits at gap 0 within rounding).")
    desc = sub(desc, "The Elenchus ledger gate exits 1 with 0 blocking findings and 11 flags.",
               f"The Elenchus ledger gate exits {exit_code} with {n_blocks} blocking findings and {n_flags} flags.")
    meta["description"] = desc
    notes = meta["notes"]
    notes = sub(notes, "exit 1, 0 blocks, 11 flags", f"exit {exit_code}, {n_blocks} blocks, {n_flags} flags")
    notes += (" Revised after an independent AI audit (papers/ar_yukawa_crystal/AUDIT.md, REVISION.md): wording and "
              "traceability only; no Tier A statement or reported number changed. The Lean files must be committed before "
              "upload so that the cited sha256 values are reproducible from git.")
    meta["notes"] = notes
    ids = [r["identifier"] for r in meta["related_identifiers"]]
    if "10.1021/acscatal.0c04525" not in ids:
        meta["related_identifiers"].append({"identifier": "10.1021/acscatal.0c04525", "relation": "references", "scheme": "doi"})
    p.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    print(f"updated: claims {n_claims}, exit {exit_code}, blocks {n_blocks}, flags {n_flags}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
