"""Extract two provenance records for the cosmology synthesis paper.

1. rust_crosscheck.json: the DESI DR2 flat-LCDM table and solver findings from the
   rusty-SUNDIALS qf-bao-distances README, parsed (not retyped), with file hashes
   and the git commits that carry the port (c46a680) and the cvode fix (d22cf01).
2. model_tier_provenance.json: the orchestrator status line that states which
   workflow stages ran on which model tier. This is the only place the tiers are
   recorded; no result artifact records them.

Run: /mnt/disks/disk-socrateai-local-1/venv-cosmo/bin/python extract_provenance.py
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUST_WT = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-cosmo")
README = RUST_WT / "crates/qf-bao-distances/README.md"
VALIDATION = RUST_WT / "crates/qf-bao-distances/tests/validation.rs"
TIMELINE = Path("/home/callensxavier_gmail_com/.claude/jobs/4d188676/timeline.jsonl")
TIER_NEEDLE = "Lean and the refuting review run on Fable"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_show(ref: str, fmt: str) -> str:
    out = subprocess.run(
        ["git", "log", "-1", f"--format={fmt}", "--date=iso-strict", ref],
        cwd=RUST_WT, capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def git_log_paths(paths: list[str]) -> list[str]:
    out = subprocess.run(
        ["git", "log", "--format=%h %ad %s", "--date=iso-strict", "--", *paths],
        cwd=RUST_WT, capture_output=True, text=True, check=True,
    )
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def parse_pm(cell: str) -> tuple[float, float]:
    m = re.search(r"([-0-9.]+)\s*±\s*([0-9.]+)", cell)
    if m is None:
        raise ValueError(f"no value±error in {cell!r}")
    return float(m.group(1)), float(m.group(2))


def parse_fit_table(text: str) -> dict[str, dict[str, float | str]]:
    start = text.index("### DESI DR2 flat-ΛCDM best fit")
    rows: dict[str, dict[str, float | str]] = {}
    for line in text[start:].splitlines()[1:]:
        if line.startswith("### ") or line.startswith("The test asserts"):
            break
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or "±" not in cells[1]:
            continue
        label = cells[0].replace("**", "").strip()
        om, s_om = parse_pm(cells[1])
        hrd, s_hrd = parse_pm(cells[2])
        row: dict[str, float | str] = {"Om": om, "sigma_Om": s_om, "hrd": hrd, "sigma_hrd": s_hrd}
        if len(cells) > 3 and cells[3] not in ("—", ""):
            row["corr"] = float(cells[3].replace("−", "-"))
        if len(cells) > 4 and "/" in cells[4]:
            row["chi2_min"] = float(cells[4].split("/")[0])
        rows[label] = row
    return rows


def parse_eds_cvode(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    m = re.search(r"measured ([0-9.]+e-[0-9]+)\)\. That test", text)
    if m:
        found["cvode_eds_worst_rel_err_at_rtol_1e-7"] = m.group(1)
    m = re.search(r"([0-9.]+e-[0-9]+) relative at `rtol = 1e-7` after about ([0-9,]+) steps", text)
    if m:
        found["adams_rel_err_at_rtol_1e-7"] = m.group(1)
        found["adams_steps_at_rtol_1e-7"] = m.group(2)
    m = re.search(r"Output of `cargo test -p qf-bao-distances -- --nocapture` \(debug build\)\. (\d+) passed and (\d+) ignored", text)
    if m:
        found["cargo_tests_passed"] = m.group(1)
        found["cargo_tests_ignored"] = m.group(2)
    return found


def main() -> None:
    text = README.read_text()
    rust = {
        "source_readme": str(README),
        "source_readme_sha256": sha256_file(README),
        "source_validation_rs": str(VALIDATION),
        "source_validation_rs_sha256": sha256_file(VALIDATION),
        "readme_and_validation_git_history": git_log_paths(
            ["crates/qf-bao-distances/README.md", "crates/qf-bao-distances/tests/validation.rs"]
        ),
        "commit_port": {"ref": "c46a680", "date": git_show("c46a680", "%ad"), "subject": git_show("c46a680", "%s")},
        "commit_cvode_fix_pr60": {"ref": "d22cf01", "date": git_show("d22cf01", "%ad"), "subject": git_show("d22cf01", "%s")},
        "cvode_fix_text_from_pr60_commit": [
            ln.strip() for ln in git_show("d22cf01", "%B").splitlines()
            if "tout truncation" in ln or "rtol<=1e-8 now works" in ln or "rescaling it" in ln
        ],
        "dr2_flat_lcdm_fit_table": parse_fit_table(text),
        "readme_solver_findings_parsed": parse_eds_cvode(text),
        "note": "README was last changed in the port commit, before the PR #60 cvode fix; its solver measurements are pre-fix and were not re-measured after the fix.",
    }
    (HERE / "rust_crosscheck.json").write_text(json.dumps(rust, indent=1) + "\n")

    tier: dict[str, str | int] = {"source": str(TIMELINE), "status": "NOT_FOUND"}
    for lineno, line in enumerate(TIMELINE.read_text().splitlines(), start=1):
        if TIER_NEEDLE in line:
            rec = json.loads(line)
            body = rec.get("text", "")
            idx = body.index(TIER_NEEDLE)
            sent_start = body.rfind("\n", 0, idx) + 1
            sent_end = body.find("\n", idx)
            quote = body[sent_start:sent_end if sent_end != -1 else None]
            tier = {
                "source": str(TIMELINE),
                "line_number": lineno,
                "timestamp_utc": rec.get("at", ""),
                "quote_verbatim": quote,
                "quote_sha256": hashlib.sha256(quote.encode()).hexdigest(),
                "status": "FOUND",
                "caveat": "Orchestrator status message, not a result artifact. The identity of the 'default model' is not recorded anywhere.",
            }
            break
    (HERE / "model_tier_provenance.json").write_text(json.dumps(tier, indent=1) + "\n")
    print(json.dumps({"rust_rows": list(rust["dr2_flat_lcdm_fit_table"].keys()), "tier_status": tier["status"]}))


if __name__ == "__main__":
    main()
