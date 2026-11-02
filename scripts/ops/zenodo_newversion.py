"""Create a new-version DRAFT of a published Zenodo record and empty its inherited files, ready for publish_one.py resume mode.

usage: zenodo_newversion.py <published deposition id>
prints: <draft id> <draft doi>
Does not publish anything.
"""
import json
import re
import sys
import urllib.request

t = open("/home/callensxavier_gmail_com/.token_workflow_token").read()
tok = re.search(r"ZENODO_TOKEN\s*[=:]\s*[\"']?([A-Za-z0-9]+)", t).group(1)
H = {"Authorization": "Bearer " + tok}
BASE = "https://zenodo.org/api/deposit/depositions/"


def call(url, data=None, method="GET"):
    req = urllib.request.Request(url, data=data, headers=H, method=method)
    with urllib.request.urlopen(req, timeout=300) as r:
        body = r.read()
        return json.loads(body) if body else {}


dep = sys.argv[1]
res = call(BASE + dep + "/actions/newversion", data=b"", method="POST")
latest = res["links"]["latest_draft"].rstrip("/").split("/")[-1]
draft = call(BASE + latest)
for f in draft.get("files", []):
    call(BASE + latest + "/files/" + f["id"], method="DELETE")
draft = call(BASE + latest)
doi = draft.get("metadata", {}).get("prereserve_doi", {}).get("doi") or draft.get("doi")
print(latest, doi, "files left:", len(draft.get("files", [])), "state:", draft.get("state"))
