"""Create a new version of a published Zenodo record, replace its files, update metadata; publish is a separate step.

Token from ~/.token_workflow_token (ZENODO_TOKEN), never printed.
  python scripts/zenodo_new_version.py draft   <published_record_id>        -> prints new draft id + reserved DOI
  python scripts/zenodo_new_version.py upload  <draft_id> <meta.json> <file>...  (replaces all files, sets metadata)
  python scripts/zenodo_new_version.py readback <draft_id>
  python scripts/zenodo_new_version.py publish <draft_id>
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

Z = "https://zenodo.org/api"


def token() -> str:
    for raw in Path("/home/callensxavier_gmail_com/.token_workflow_token").read_text().splitlines():
        line = raw.strip().removeprefix("export ")
        if line.startswith("ZENODO_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("ZENODO_TOKEN not found")


def req(method: str, url: str, data: bytes | None = None, ctype: str = "application/json") -> dict:
    r = urllib.request.Request(url, data=data, method=method, headers={"Authorization": f"Bearer {token()}", "Content-Type": ctype})
    with urllib.request.urlopen(r, timeout=600) as resp:
        body = resp.read()
        return json.loads(body) if body else {}


def main() -> None:
    cmd = sys.argv[1]
    if cmd == "draft":
        d = req("POST", f"{Z}/deposit/depositions/{sys.argv[2]}/actions/newversion")
        draft = req("GET", d["links"]["latest_draft"])
        print(json.dumps({"draft_id": draft["id"], "doi": draft["metadata"].get("prereserve_doi", {}).get("doi"),
                          "state": draft["state"]}, indent=1))
    elif cmd == "upload":
        did, meta_path, files = sys.argv[2], sys.argv[3], sys.argv[4:]
        dep = req("GET", f"{Z}/deposit/depositions/{did}")
        for f in dep.get("files", []):
            req("DELETE", f"{Z}/deposit/depositions/{did}/files/{f['id']}")
        for f in files:
            p = Path(f)
            req("PUT", f"{dep['links']['bucket']}/{p.name}", p.read_bytes(), "application/octet-stream")
        md = dep["metadata"]
        new = json.loads(Path(meta_path).read_text())
        md.update({k: new[k] for k in ("title", "description", "keywords", "notes", "version") if k in new})
        md.pop("doi", None)
        req("PUT", f"{Z}/deposit/depositions/{did}", json.dumps({"metadata": md}).encode())
        dep = req("GET", f"{Z}/deposit/depositions/{did}")
        print(json.dumps({"files": [(f["filename"], f["filesize"], f["checksum"]) for f in dep["files"]],
                          "version": dep["metadata"].get("version"), "doi": dep["metadata"].get("prereserve_doi", {}).get("doi")}, indent=1))
    elif cmd == "readback":
        dep = req("GET", f"{Z}/deposit/depositions/{sys.argv[2]}")
        m = dep["metadata"]
        print(json.dumps({"state": dep["state"], "doi": m.get("prereserve_doi", {}).get("doi"), "title": m["title"],
                          "version": m.get("version"), "creators": m["creators"], "license": m.get("license"),
                          "files": [(f["filename"], f["filesize"], f["checksum"]) for f in dep["files"]],
                          "related": [(r["relation"], r["identifier"]) for r in m.get("related_identifiers", [])]}, indent=1))
    elif cmd == "publish":
        dep = req("POST", f"{Z}/deposit/depositions/{sys.argv[2]}/actions/publish")
        print(json.dumps({"id": dep["id"], "doi": dep.get("doi"), "state": dep["state"], "html": dep["links"].get("html")}, indent=1))


if __name__ == "__main__":
    main()
