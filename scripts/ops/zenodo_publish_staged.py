"""Publish one paper to Zenodo: dry-run + secret scan -> draft -> stamp DOI + rebuild -> upload -> md5 check -> publish.

Usage: publish_one.py PAPER_DIR LANE_DIR   (paths relative to the AutoevolveAI worktree)
"""
import hashlib
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
TOK = "/home/callensxavier_gmail_com/.token_workflow_token"
SECRET = re.compile(rb"ZENODO_TOKEN=|hf_[A-Za-z0-9]{30}|ghp_[A-Za-z0-9]{30}|github_pat_")
paper_rel, lane_rel = sys.argv[1], sys.argv[2]
d = REPO / paper_rel


def pub(*extra: str) -> dict:
    r = subprocess.run(["python3", "-I", "scripts/publish_ar_paper.py", "--paper-dir", paper_rel, "--lane-dir",
                        lane_rel, "--token-file", TOK, *extra], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stderr[-800:])
    return json.loads(r.stdout)


dry = pub("--dry-run")
with tarfile.open(dry["bundle"]) as t:
    hits = [m.name for m in t.getmembers() if (f := t.extractfile(m)) and SECRET.search(f.read())]
assert not hits, hits
print("bundle", dry["files_in_manifest"], dry["bundle_bytes"], "no secrets")
if len(sys.argv) > 3:
    dep, doi = int(sys.argv[3]), sys.argv[4]
else:
    r = pub("--draft")
    dep, doi = r["zenodo"]["id"], r["zenodo"]["doi"]
cov = d / "cadre" / "couverture.tex"
tex = (d / "main.tex").read_text()
if cov.exists() and "\\maketitle" not in tex:
    ct = cov.read_text()
    if doi not in ct:
        for a, b in (("Ce livre n'a pas encore de DOI.", "DOI~: " + doi + "."), ("This book does not have a DOI yet.", "DOI: " + doi + ".")):
            ct = ct.replace(a, b)
        assert doi in ct
        cov.write_text(ct)
elif doi not in tex:
    line = "\n\\begin{center}\\small doi:" + doi + " \\quad (not peer reviewed)\\end{center}\n"
    tex, n = re.subn(r"\\maketitle", lambda m: m.group(0) + line, tex, count=1)
    assert n == 1
    (d / "main.tex").write_text(tex)
rcs = [subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=d,
                      capture_output=True).returncode for _ in range(3)]
log = (d / "main.log").read_text(errors="ignore")
for f in ("main.aux", "main.log", "main.out", "main.toc"):
    (d / f).unlink(missing_ok=True)
first = subprocess.run(["pdftotext", "-f", "1", "-l", "8", "main.pdf", "-"], cwd=d, capture_output=True).stdout
assert rcs == [0, 0, 0] and doi.encode() in first, rcs
up = pub("--update-id", str(dep))
b = Path("/home/callensxavier_gmail_com/zenodo-bundles") / d.name
ok = all(f["md5"].split(":")[-1] == hashlib.md5((b / f["name"]).read_bytes()).hexdigest() for f in up["zenodo"]["files"])
assert ok
done = pub("--publish-id", str(dep))
print(d.name, doi, done["zenodo"]["state"], "undefined:", len(re.findall("undefined", log)), "md5 ok:", ok)
