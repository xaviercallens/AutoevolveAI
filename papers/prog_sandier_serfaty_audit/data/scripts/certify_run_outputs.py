"""P1 WORK1: (1) compare the 22 printed pairs of our certificate run with the saved rows of certificate-record.txt;
(2) turn the printed pairs of a run into a LeanFlow data certificate (Lean `decide`, core Lean, fail-closed);
(3) the same claim on the negative-control run must be REJECTED.

Tier: A for the arithmetic statements about the PRINTED outward-rounded integer pairs (10^-7 display scale,
floor/ceil of the exact 144-bit endpoints). It is not a proof that the C++ run computed them correctly.
Usage: python certify_run_outputs.py OUTDIR
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/callensxavier_gmail_com/LeanFlow-wt-p1/src")
from leanflow_mcp.lean import LeanConfig, certify  # noqa: E402

RECORD = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math/preprints/Triangular-minimality-for-planar-Coulomb-renormalized-energy-September-23-2026/verification/data/certificate-record.txt")
POS_LOG = Path("/home/callensxavier_gmail_com/programmes-2026-10-25/P1/certificate-run/run.log")
NEG_LOG = Path("/home/callensxavier_gmail_com/programmes-2026-10-25/P1/negctl/run/run.log")
LEAN = "/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean"
LABELS = {
    "lambda,mu,K,bcon,f0(l),slope,f(l)": ["lambda", "mu", "K", "bcon", "f0l", "slope", "fl"],
    "bounds:": ["G", "Gd", "Gs", "Gdd", "Gss"],
    "gmin,drneg,factor,er_drop,gmin-factor,drneg+er_drop+K": ["gmin", "drneg", "factor", "er_drop", "gmin_minus_factor", "drneg_sum"],
    "hess hulls": ["g_dd", "g_dx", "g_xx", "det"],
}
SCALE = 10**7


def parse_log(path: Path) -> dict[str, tuple[int, int]]:
    lines = path.read_text().splitlines()
    out: dict[str, tuple[int, int]] = {}
    for i, ln in enumerate(lines):
        if ln in LABELS and i + 1 < len(lines) and lines[i + 1].startswith("["):
            pairs = [(int(a), int(b)) for a, b in re.findall(r"\((-?\d+), (-?\d+)\)", lines[i + 1])]
            names = LABELS[ln]
            assert len(pairs) == len(names), (ln, pairs)
            out.update(dict(zip(names, pairs)))
    return out


def parse_record() -> list[tuple[int, int]]:
    """All 22 saved pairs, in file order (the four tables are in label order)."""
    text = RECORD.read_text()
    start = text.index("### Saved output rows")
    return [(int(a), int(b)) for a, b in re.findall(r"`\((-?\d+), (-?\d+)\)`", text[start:])]


def claim_for(vals: dict[str, tuple[int, int]], name: str) -> dict:
    enc = {k: [f"{lo}/{SCALE}", f"{hi}/{SCALE}"] for k, (lo, hi) in vals.items()}
    A = []

    def a(label: str, endpoint: str, op: str, rhs: str) -> None:
        A.append({"label": label, "endpoint": endpoint, "op": op, "rhs": rhs})

    # run_certificate() asserts (on exact endpoints); the printed pairs are outward roundings of them.
    a("lambda > -6.731", "lambda.lo", ">", "-6731/1000")
    a("lambda < -6.729", "lambda.hi", "<", "-6729/1000")
    a("K < 0", "K.hi", "<", "0")
    a("f(l) > 0", "fl.lo", ">", "0")
    a("slope = -pi B(l) - lambda/2 > 0", "slope.lo", ">", "0")
    a("gmin - factor > 0 (m_* - E_0 - E_I > 0)", "gmin_minus_factor.lo", ">", "0")
    a("drneg + er_drop + K < 0", "drneg_sum.hi", "<", "0")
    # statements quoted in the manuscript (Section 6 table)
    a("m_* - E_0 - E_I >= 1.20e-5", "gmin_minus_factor.lo", ">=", "12/1000000")
    a("negative assertion lhs <= -4.585e-4", "drneg_sum.hi", "<=", "-4585/10000000")
    a("g_dd >= 1.0529222", "g_dd.lo", ">=", "10529222/10000000")
    a("g_xx >= 0.0128335", "g_xx.lo", ">=", "128335/10000000")
    a("det Hess(g) >= 0.0086252", "det.lo", ">=", "86252/10000000")
    # same inequality written as interval arithmetic on the printed pairs (stricter than the C++ full-precision difference)
    A.append({"label": "gmin.lo - factor.hi > 0 on printed pairs", "terms": [["1", "gmin.lo"], ["-1", "factor.hi"]], "op": ">", "rhs": "0"})
    # the negative-control run aborts before inside_hess, so only assertions about printed enclosures are kept
    A = [x for x in A if all(t[1].split(".")[0] in vals for t in x.get("terms", [["1", x.get("endpoint", "")]]))]
    return {"name": name, "enclosures": enc, "assertions": A}


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    pos, neg = parse_log(POS_LOG), parse_log(NEG_LOG)
    order = [n for names in LABELS.values() for n in names]
    pos_list = [pos[n] for n in order]
    rec = parse_record()
    match = pos_list == rec
    summary: dict[str, object] = {"n_pairs_log": len(pos_list), "n_pairs_record": len(rec), "log_equals_record": match}
    print("log pairs == saved record rows:", match, len(pos_list), len(rec))
    cfg = LeanConfig(lean_cmd=(LEAN,), timeout_s=600)
    rc = 0
    for tag, vals in (("positive_run", pos), ("negctl_run", neg)):
        claim = claim_for(vals, f"p1_{tag}")
        (out / f"claim_{tag}.json").write_text(json.dumps(claim, indent=1) + "\n")
        res = certify(claim, cfg)
        (out / f"result_{tag}.json").write_text(res.to_json() + "\n")
        rows = [(r["label"], r["lean_accepted"], r["oracle_true"]) for r in res.assertions]
        summary[tag] = {"status": res.status, "code": res.code, "tier": res.tier, "failed": list(res.failed),
                        "lean_version": res.lean_version, "seconds": res.seconds,
                        "n_accepted": sum(1 for r in rows if r[1]), "n_assertions": len(rows),
                        "statement_sha256": res.statement_sha256, "claim_sha256": res.claim_sha256}
        print(tag, res.status, res.code, res.tier, "failed:", res.failed)
        for lab, acc, orc in rows:
            print(("  ACCEPT " if acc else "  REJECT ") + lab + f"  (oracle {orc})")
        # positive run must verify; negative-control run must be rejected
        rc |= 0 if (tag == "positive_run") == res.verified else 1
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
