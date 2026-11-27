import json, subprocess, sys
OUT = "/home/callensxavier_gmail_com/AutoevolveAI/.scratchpad/gh_inv/all_repos.json"
fields = "name,visibility,isFork,isArchived,createdAt,pushedAt,description,primaryLanguage,diskUsage,stargazerCount,url"
r = subprocess.run(["gh", "repo", "list", "xaviercallens", "-L", "1000", "--json", fields],
                   capture_output=True, text=True)
if r.returncode:
    print(r.stderr); sys.exit(1)
repos = json.loads(r.stdout)
json.dump(repos, open(OUT, "w"))
SINCE = "2025-10-26"
kept = [x for x in repos if (x["createdAt"][:10] >= SINCE or x["pushedAt"][:10] >= SINCE) and not x["isFork"]]
print("total", len(repos))
print("forks", sum(x["isFork"] for x in repos))
print("private", sum(x["visibility"] != "PUBLIC" for x in repos))
print("kept", len(kept), "kept private", sum(x["visibility"] != "PUBLIC" for x in kept))
nf = [x for x in repos if not x["isFork"]]
print("nonfork old", len(nf) - len(kept))
