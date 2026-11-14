"""Copy lane records, producer code, auditor scripts into papers/ph2_validated_robertson/data and verify result.json hashes."""
import hashlib
import json
import shutil
from pathlib import Path

WT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
LANE = WT / "results/proposal7/2026-11-11/PH2"
PAPER = WT / "papers/ph2_validated_robertson"
DATA = PAPER / "data"
AUD = Path("/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/ph2audit")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


DATA.mkdir(parents=True, exist_ok=True)
for n in ("AUDIT.md", "PREREG_ITEM.md", "PREREG_ITEM.md.sha256", "PREREG_DRAFT.md", "PRIOR_ART.md", "RESULT.md",
          "result.json", "enclosures.json", "comparison.json", "cvode_runs.json"):
    shutil.copy2(LANE / n, DATA / n)
cp = DATA / "code_producer"
cp.mkdir(exist_ok=True)
for p in (LANE / "code").glob("*"):
    if p.is_file():
        shutil.copy2(p, cp / p.name)
rr = cp / "rob_runner"
(rr / "src").mkdir(parents=True, exist_ok=True)
for n in ("Cargo.toml", "Cargo.lock"):
    shutil.copy2(LANE / "code/rob_runner" / n, rr / n)
shutil.copy2(LANE / "code/rob_runner/src/main.rs", rr / "src/main.rs")
lg = DATA / "logs"
lg.mkdir(exist_ok=True)
CK = "enclosure_ckpt.json"
for p in (LANE / "logs").glob("*"):
    if p.is_file() and p.name != CK and p.stat().st_size > 0:
        shutil.copy2(p, lg / p.name)
ck = LANE / "logs" / CK
(lg / "enclosure_ckpt.json.SHA256.txt").write_text(
    f"{sha(ck)}  {ck.stat().st_size} bytes  logs/{CK}\n"
    "The 13 MB checkpoint (exact rational state and the every-20th-step history) is NOT in the bundle; "
    "only this hash is stored. It stays in the lane directory of the repository working tree.\n")
ca = DATA / "code_auditor"
ca.mkdir(exist_ok=True)
for p in AUD.glob("*"):
    if p.is_file():
        shutil.copy2(p, ca / p.name)
# verify result.json hashes against the copies
res = json.loads((LANE / "result.json").read_text())
report = []
for rel, h in res["sha256"].items():
    src = LANE / rel
    status = "MATCH" if sha(src) == h else "DIFFERS"
    report.append(f"{status}  {rel}  recorded={h[:12]}  now={sha(src)[:12]}")
(DATA / "logs" / "result_json_hash_check.txt").write_text("\n".join(report) + "\n")
print("\n".join(report))
for sub in ("code_producer", "code_auditor", "logs"):
    print(sub, sorted(x.name for x in (DATA / sub).iterdir()))
