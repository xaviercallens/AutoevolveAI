"""Verify every arXiv reference against its arxiv.org abstract page (title, authors, date, journal-ref if any). Writes sources/refs_meta.json.

Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I verify_refs.py
"""
from __future__ import annotations

import html
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "sources"
OUT.mkdir(exist_ok=True)
IDS = ["cond-mat/0608246", "1809.07515", "1001.3250", "1602.06313", "1402.0840", "1201.0980", "2010.04631", "1107.0828", "2209.02802", "2307.09327", "2405.20128"]


def meta(aid: str) -> dict:
    req = urllib.request.Request(f"https://arxiv.org/abs/{aid}", headers={"User-Agent": "Mozilla/5.0 (reference verification)"})
    t = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")

    def g(pat: str) -> str:
        m = re.search(pat, t, re.S)
        return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""

    authors = re.findall(r'<meta name="citation_author" content="([^"]+)"', t)
    return {
        "id": aid,
        "title": html.unescape(re.search(r'<meta name="citation_title" content="([^"]+)"', t).group(1)) if 'citation_title' in t else g(r"<title>(.*?)</title>"),
        "authors": [html.unescape(a) for a in authors],
        "date": g(r'<meta name="citation_date" content="([^"]+)"') or (re.search(r'citation_date" content="([^"]+)"', t) or [None, ""])[1],
        "journal_ref": g(r'<td class="tablecell jref">(.*?)</td>'),
        "doi": g(r'<td class="tablecell doi">(.*?)</td>'),
    }


def main() -> int:
    out = []
    for aid in IDS:
        try:
            m = meta(aid)
        except Exception as e:  # network failure is reported, not hidden
            m = {"id": aid, "error": repr(e)}
        out.append(m)
        print(json.dumps(m, ensure_ascii=False)[:400])
        time.sleep(4)
    (OUT / "refs_meta.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
