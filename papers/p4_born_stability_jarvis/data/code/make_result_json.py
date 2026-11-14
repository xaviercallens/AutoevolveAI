"""Write result.json with sha256 of every M2 file (repo files plus the external dataset and per-entry file).
Usage: python make_result_json.py <m2_dir> <extra_file>...  (extra files are hashed by absolute path)"""
from __future__ import annotations

import hashlib
import json
import os
import sys


def sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(m2: str, extras: list[str]) -> int:
    files: dict[str, str] = {}
    for root, _, names in os.walk(m2):
        if "__pycache__" in root:
            continue
        for n in sorted(names):
            if n == "result.json":
                continue
            p = os.path.join(root, n)
            files[os.path.relpath(p, m2)] = sha(p)
    lean_dir = os.path.join(m2, "..", "..", "..", "..", "formal_cert", "Programmes", "BornM2")
    for n in sorted(os.listdir(lean_dir)):
        if n.endswith(".lean"):
            files["formal_cert/Programmes/BornM2/" + n] = sha(os.path.join(lean_dir, n))
    ext = {p: sha(p) for p in extras}
    summary = json.load(open(os.path.join(m2, "data", "summary.json")))
    fin = json.load(open(os.path.join(m2, "data", "final_summary.json")))
    out = {
        "item": "M2", "outcome": "KEEP (by preregistered rule; producer, unaudited)",
        "prereg_sha256": files["prereg_M2.json"],
        "N_tensors": summary["N"], "exact_PD": summary["exact_PD"], "exact_NOT_PD": summary["exact_NOT_PD"],
        "exact_NOT_PD_fraction": summary["exact_NOT_PD_fraction"],
        "interval": summary["interval"], "linear_pass_but_exact_NOT_PD": summary["linear_pass_but_exact_NOT_PD"],
        "null_tensors": fin["numerically_null_tensors_max_abs_lt_1e-6"],
        "exact_NOT_PD_excluding_null": fin["exact_NOT_PD_excluding_null"],
        "float_disagreements": {k: summary[f"float_{k}_disagree"] for k in ("F0", "F1", "F2")},
        "born_class_disagree": [summary["born_class_total_disagree"], summary["born_class_applicable"]],
        "tiers": {"exact_rational_counts": "C", "lean_sample_and_controls": "A (unaudited)", "float_and_context": "X"},
        "lean": {"witnesses": 12, "ldl_identities": 6, "controls": 2, "tampered_rejected": 3},
        "files_sha256": files, "external_files_sha256": ext,
    }
    json.dump(out, open(os.path.join(m2, "result.json"), "w"), indent=1)
    print(len(files), "files hashed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:]))
