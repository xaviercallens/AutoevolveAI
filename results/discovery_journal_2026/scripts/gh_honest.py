import json, subprocess, re, os
B = "/home/callensxavier_gmail_com/AutoevolveAI/.scratchpad/gh_inv/"
R = {x["name"]: x for x in json.load(open(B + "all_repos.json"))}
E = json.load(open(B + "enriched.json"))
KEY = re.compile(r"(honest|caveat|limitation|not (a )?proof|not proved|unverified|conditional|lesson|fail|negative|refut|retract|erratum|do(es)? not|no claim|scope|vacuous|vacuity|overclaim|learnt|learned)", re.I)
SECRET = re.compile(r"(ghp_|hf_[A-Za-z0-9]{10}|sk-[A-Za-z0-9]{10}|token\s*[:=]\s*\S{12,}|AKIA)", re.I)
res = {}
for n, e in E.items():
    r = R[n]
    if r["visibility"] != "PUBLIC":
        continue
    files = e.get("honest_files", [])
    # prioritise honest/lesson/caveat names and root-level
    files = sorted(files, key=lambda p: (p.count("/"), not re.search(r"honest|lesson|caveat", p, re.I)))[:3]
    res[n] = {}
    for p in files:
        o = subprocess.run(["gh", "api", f"repos/xaviercallens/{n}/contents/{p}", "-H", "Accept: application/vnd.github.raw"],
                           capture_output=True, text=True)
        if o.returncode:
            continue
        lines = o.stdout.splitlines()
        hits = []
        for l in lines[:400]:
            l = l.strip()
            if 25 < len(l) < 400 and KEY.search(l) and not SECRET.search(l):
                hits.append(l)
            if len(hits) >= 6:
                break
        res[n][p] = hits
json.dump(res, open(B + "honest.json", "w"), indent=1)
print({k: len(v) for k, v in res.items() if v})
