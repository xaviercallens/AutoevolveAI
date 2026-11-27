"""Write data/result_audited.json: a copy of the producer's data/result.json (kept unmodified) with the audit's corrections 2, 4 and 5 applied."""
from __future__ import annotations

import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def main() -> int:
    d = json.loads((DATA / "result.json").read_text())
    old = d["sha256"].pop("logs/make_result.out", None)
    d["tiers"] = {
        "configuration_statement_v_le_34": "C (exhaustive search + witness checkers; producer != verifier satisfied by the 2026-10-31 AI audit, see AUDIT.md; no human audit)",
        "graph_statement_le_60_route1": "C (+ Moore lemma)",
        "graph_statement_62_68_route1": "C conditional on Tier L n(3,10)=70 (O'Keefe-Wong 1980, read via Exoo-Jajcay DS16 only)",
        "graph_statement_le_68_route2": "C (arbitrary root, no premise; cap-34 stream accepted by cb_check_fast and by the auditor's independent aud_check, same stream sha256)"}
    d["producer_ne_verifier"] = (
        "satisfied by the 2026-10-31 independent audit (separate AI agent instance, AUDIT.md): an independent search reproduced all counters and transcript hashes "
        "(route 1 caps 29-35, route 2 caps 29-34); the independent checker aud_check accepted the 12 route-1 certificates and the regenerated route-2 cap-34 stream "
        "(sha256 0112b808...fad5). Not a human audit. The coverage lemma is not formalised; the auditor shares the Prop. 10 schedule.")
    d["R34_streams_identical"] = ("the producer-side Python check never completed; the auditor regenerated the stream, obtained the same sha256 "
                                  "0112b8085b969bcfa75335fdb2aedc5d4b5b0e80c6dddf2d5d9ead8f5a18fad5 and accepted it with aud_check")
    d["git_ignored_logs_local_only"] = {
        "files": ["logs/make_result.out", "logs/rcert34_fast.out", "logs/rcert34_py.out", "logs/rcert35_fast.out", "logs/run_controls.out",
                  "logs/run_controls2.out", "logs/run_ext.out", "logs/run_extB.out", "logs/run_main.out"],
        "note": "git-ignored (.gitignore *.out): LOCAL ONLY in the lane directory; shipped in the paper bundle as data/logs/*.out.txt copies (audit correction 5)"}
    d["audit"] = {"report": "AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS", "auditor": "separate AI agent instance (Claude Opus), 2026-10-31, not a person",
                  "note": "audited-fields copy of result.json; the original is kept unmodified as data/result.json"}
    d["audited_fields_changes"] = {"removed_sha256_entry": {"logs/make_result.out": old},
                                   "reason": "e3b0c442... is the sha256 of the EMPTY file: it was hashed while make_result.py was still writing it, and a file cannot hash itself (audit correction 4)"}
    (DATA / "result_audited.json").write_text(json.dumps(d, indent=1))
    print("removed entry:", old)
    return 0


if __name__ == "__main__":
    sys.exit(main())
