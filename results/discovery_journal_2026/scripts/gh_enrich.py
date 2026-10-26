import json, subprocess, re, time, base64, os
BASE = "/home/callensxavier_gmail_com/AutoevolveAI/.scratchpad/gh_inv/"
SINCE = "2025-10-26"
repos = json.load(open(BASE + "all_repos.json"))
kept = [x for x in repos if (x["createdAt"][:10] >= SINCE or x["pushedAt"][:10] >= SINCE) and not x["isFork"]]
kept.sort(key=lambda x: x["name"])
OWN = "xaviercallens/"
HON = re.compile(r"(honest|lesson|caveat|limitation|audit|assessment|erratum|known_issue|status)", re.I)

def gh(args, timeout=120):
    for attempt in range(3):
        r = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0:
            return r.stdout
        if "rate limit" in r.stderr.lower():
            time.sleep(60); continue
        return None
    return None

def jget(path):
    o = gh(["api", path])
    try:
        return json.loads(o) if o else None
    except Exception:
        return None

out = {}
if os.path.exists(BASE + "enriched.json"):
    out = json.load(open(BASE + "enriched.json"))
for x in kept:
    n = x["name"]
    if n in out:
        continue
    e = {}
    rd = gh(["api", f"repos/{OWN}{n}/readme", "-H", "Accept: application/vnd.github.raw"])
    e["readme_head"] = "\n".join(rd.splitlines()[:150])[:9000] if rd else None
    t = jget(f"repos/{OWN}{n}/git/trees/HEAD?recursive=1")
    if t and "tree" in t:
        paths = [p["path"] for p in t["tree"] if p["type"] == "blob"]
        e["tree_truncated"] = bool(t.get("truncated"))
        e["n_files"] = len(paths)
        e["lean_files"] = sum(p.endswith(".lean") for p in paths)
        e["lakefile"] = [p for p in paths if p.split("/")[-1] in ("lakefile.lean", "lakefile.toml")][:3]
        e["lean_toolchain"] = [p for p in paths if p.endswith("lean-toolchain")][:3]
        e["cargo"] = [p for p in paths if p.endswith("Cargo.toml")][:5]
        e["rs_files"] = sum(p.endswith(".rs") for p in paths)
        e["py_files"] = sum(p.endswith(".py") for p in paths)
        e["notebooks"] = sum(p.endswith(".ipynb") for p in paths)
        e["tex_files"] = sum(p.endswith(".tex") for p in paths)
        e["data_files"] = sum(p.endswith((".csv", ".json", ".parquet", ".h5", ".npz", ".jsonl", ".fits")) for p in paths)
        e["sundials_hit"] = any("sundials" in p.lower() for p in paths) or bool(rd and "sundials" in rd.lower())
        e["honest_files"] = [p for p in paths if p.endswith((".md", ".txt")) and HON.search(p.split("/")[-1])][:12]
        e["top_dirs"] = sorted({p.split("/")[0] for p in paths if "/" in p})[:25]
    else:
        e["tree_error"] = True
    # commits since
    c = gh(["api", f"repos/{OWN}{n}/commits?since={SINCE}T00:00:00Z&per_page=100", "--paginate", "-q", "length"])
    try:
        e["commits_last_year"] = sum(int(v) for v in c.split()) if c else None
    except Exception:
        e["commits_last_year"] = None
    # merged PRs
    pr = gh(["api", f"repos/{OWN}{n}/pulls?state=closed&per_page=100", "--paginate", "-q", "[.[]|select(.merged_at!=null)]|length"])
    try:
        e["merged_prs"] = sum(int(v) for v in pr.split()) if pr else None
    except Exception:
        e["merged_prs"] = None
    out[n] = e
    json.dump(out, open(BASE + "enriched.json", "w"))
    print(n, e.get("commits_last_year"), e.get("lean_files"), flush=True)
print("done", len(out))
