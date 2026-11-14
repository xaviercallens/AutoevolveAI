#!/usr/bin/env python3
"""Hourly verify-and-merge for the owner's own pull requests (rusty-SUNDIALS and LeanFlow).

Safety rules (all must hold for a merge):
  - repo is in REPOS; PR is open, not a draft, authored by OWNER, targets the repo's default branch;
  - no label 'no-auto-merge'; title does not start with WIP/DRAFT;
  - the PR does not touch .github/ (a workflow change could widen this job's own powers);
  - the diff contains no token-like strings;
  - every check has completed and succeeded (SKIPPED/NEUTRAL allowed); pending checks wait, failures are reported;
  - the branch is up to date with the base (otherwise the job updates it and waits for CI on the next pass);
  - conflicts are reported for a human, never resolved here.
At most one merge per repo per pass (the next PR is then behind and gets updated).
Kill switches: the file ~/ops/PAUSE stops everything; the label 'no-auto-merge' skips one PR.
Log: ~/ops/logs/hourly_merge.jsonl (one JSON object per decision). Use --dry-run to only report.
"""
import datetime
import json
import os
import re
import subprocess
import sys

OWNER = "xaviercallens"
REPOS = ["xaviercallens/rusty-SUNDIALS", "xaviercallens/SocrateAI-Scientific-Agora-LeanFlow"]
OPS = os.path.expanduser("~/ops")
LOG = os.path.join(OPS, "logs", "hourly_merge.jsonl")
SECRET = re.compile(r"ghp_[A-Za-z0-9]{30}|github_pat_[A-Za-z0-9_]{20}|hf_[A-Za-z0-9]{30}|sk-[A-Za-z0-9]{32}|AKIA[0-9A-Z]{16}"
                    r"|AIza[0-9A-Za-z_-]{35}|xox[baprs]-[0-9A-Za-z-]{10}|-----BEGIN [A-Z ]*PRIVATE KEY-----|ZENODO_TOKEN=\S")
DRY = "--dry-run" in sys.argv


def load_token():
    """Use GH_TOKEN from the environment, else a least-privilege GH_PR_TOKEN from ~/.token_workflow_token (never printed)."""
    if os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"):
        return True
    path = os.path.expanduser("~/.token_workflow_token")
    try:
        for line in open(path):
            m = re.match(r"\s*(?:export\s+)?GH_PR_TOKEN\s*[=:]\s*[\"']?([A-Za-z0-9_]+)", line)
            if m:
                os.environ["GH_TOKEN"] = m.group(1)
                return True
    except OSError:
        pass
    return False


def gh(*args, check=False):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=300)
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    return r


def log(**kw):
    kw["time"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(kw) + "\n")
    print(json.dumps(kw))


def checks_state(rollup):
    pending, failed = [], []
    for c in rollup or []:
        name = c.get("name") or c.get("context") or "?"
        status = c.get("status")
        concl = c.get("conclusion") or c.get("state")
        if status and status != "COMPLETED":
            pending.append(name)
        elif concl in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            continue
        elif concl in ("PENDING", "EXPECTED", None):
            pending.append(name)
        else:
            failed.append(f"{name}:{concl}")
    return pending, failed


def process(repo):
    info = json.loads(gh("api", f"repos/{repo}", check=True).stdout)
    base = info["default_branch"]
    method = "--squash" if info.get("allow_squash_merge") else ("--merge" if info.get("allow_merge_commit") else "--rebase")
    fields = "number,title,isDraft,author,baseRefName,labels,mergeable,mergeStateStatus,statusCheckRollup,files,changedFiles,additions,headRefName"
    prs = json.loads(gh("pr", "list", "-R", repo, "--state", "open", "--limit", "50", "--json", fields, check=True).stdout)
    merged_here = False
    for pr in sorted(prs, key=lambda p: p["number"]):
        n, t = pr["number"], pr["title"]
        base_log = dict(repo=repo, pr=n, title=t[:70])
        labels = [l["name"] for l in pr.get("labels", [])]
        if pr["author"]["login"] != OWNER or pr["isDraft"] or pr["baseRefName"] != base:
            log(**base_log, action="skip", reason="not an eligible owner PR (author/draft/base)")
            continue
        if "no-auto-merge" in labels or re.match(r"(?i)^(wip|draft)\b", t):
            log(**base_log, action="skip", reason="opted out (label or WIP title)")
            continue
        if pr["changedFiles"] == 0:
            log(**base_log, action="needs-human", reason="empty diff: nothing to merge; close it or add commits")
            continue
        touched = [f["path"] for f in pr.get("files", [])]
        if any(p.startswith(".github/") for p in touched):
            log(**base_log, action="needs-human", reason="touches .github/ (workflow change): review by a person")
            continue
        state = pr["mergeStateStatus"]
        if pr["mergeable"] == "CONFLICTING" or state == "DIRTY":
            log(**base_log, action="needs-human", reason="merge conflict")
            continue
        if state == "BEHIND":
            if DRY:
                log(**base_log, action="would-update-branch")
            else:
                r = gh("api", "-X", "PUT", f"repos/{repo}/pulls/{n}/update-branch")
                log(**base_log, action="update-branch", ok=r.returncode == 0, note=(r.stderr or r.stdout)[:120])
            continue
        pending, failed = checks_state(pr.get("statusCheckRollup"))
        if failed:
            log(**base_log, action="needs-human", reason="checks failed", failed=failed[:5])
            continue
        if pending or pr["mergeable"] == "UNKNOWN" or state in ("UNKNOWN",):
            log(**base_log, action="wait", reason="checks pending or state not computed", pending=pending[:5], state=state)
            continue
        diff = gh("pr", "diff", str(n), "-R", repo).stdout
        added = "\n".join(l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
        if SECRET.search(added):
            log(**base_log, action="needs-human", reason="token-like string in the diff")
            continue
        if merged_here:
            log(**base_log, action="wait", reason="one merge per repo per pass; will update next pass")
            continue
        if DRY:
            log(**base_log, action="would-merge", method=method)
            merged_here = True
            continue
        r = gh("pr", "merge", str(n), "-R", repo, method)
        ok = r.returncode == 0
        log(**base_log, action="merge", method=method, ok=ok, note=(r.stderr or r.stdout)[:160])
        merged_here = merged_here or ok


def main():
    if os.path.exists(os.path.join(OPS, "PAUSE")):
        log(action="paused", reason="~/ops/PAUSE exists")
        return
    if not load_token():
        log(action="no-auth", reason="no GH_TOKEN and no GH_PR_TOKEN in ~/.token_workflow_token: add a fine-grained token (pull requests: write, contents: read) scoped to the two repos")
        return
    for repo in REPOS:
        try:
            process(repo)
        except Exception as e:  # keep going with the other repo
            log(repo=repo, action="error", error=str(e)[:200])


if __name__ == "__main__":
    main()
