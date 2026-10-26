"""Re-classify finished entries from their saved compile logs with the current `scheduler.classify`
(for use after a classifier fix; never re-runs Lean). Usage: reclassify.py [ID ...] (default: all `fail` entries)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scheduler as S  # noqa: E402


def main() -> int:
    cfg = S.load_config()
    entries = {e["id"]: e for e in S.load_entries(cfg)}
    ids = sys.argv[1:] or [i for i in entries if (S.read_status(i) or {}).get("state") == "fail"]
    for cid in ids:
        st = S.read_status(cid)
        jf = S.LOGS / (S.safe(cid) + ".json")
        if not st or not jf.exists() or cid not in entries:
            continue
        res = json.loads(jf.read_text())
        state, info = S.classify(entries[cid], res)
        st.update(state=state, **info, reclassified=S.now())
        S.write_json_atomic(S.status_path(cid), st)
        print(cid, state, info.get("verdict"))
    S.render_status(list(entries.values()), cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
