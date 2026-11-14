import json
B = "/home/callensxavier_gmail_com/AutoevolveAI/.scratchpad/gh_inv/"
R = {x["name"]: x for x in json.load(open(B + "all_repos.json"))}
E = json.load(open(B + "enriched.json"))
for n, e in E.items():
    r = R[n]
    pl = (r["primaryLanguage"] or {}).get("name")
    print(f"{n}|{r['visibility'][0]}|{r['createdAt'][:10]}|{r['pushedAt'][:10]}|{pl}|kb{r['diskUsage']}|c{e.get('commits_last_year')}|pr{e.get('merged_prs')}|lean{e.get('lean_files')}|rs{e.get('rs_files')}|nb{e.get('notebooks')}|tex{e.get('tex_files')}|hon{len(e.get('honest_files',[]))}|{(r['description'] or '')[:110]}")
