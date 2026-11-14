"""Consistency of dump2.txt with A1's dump.txt (same corpus, independent run): every scalar both contain and every
table node/cell of the old dump must be bit-identical; the printed global_grid / inside_hess pairs must reproduce the
certificate record (coarse_list at display scale 1e-7)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump2io import Dump2  # noqa: E402
from l1common import CONT, DUMP2, OLD_DUMP, Q, load_scalars, sha256  # noqa: E402


def coarse(a: tuple[int, int]) -> tuple[int, int]:
    return ((a[0] * 10**7) // Q, -((-(a[1] * 10**7)) // Q))


def main() -> int:
    new = Dump2(want={"node", "cell"})
    old_sc = load_scalars(OLD_DUMP)
    bad = []
    common = sorted(set(old_sc) & set(new.sc))
    for k in common:
        if old_sc[k] != new.sc[k]:
            bad.append(k)
    nn = nc = 0
    for line in OLD_DUMP.read_text().splitlines():
        p = line.split()
        if p[0] == "node":
            i = int(p[1])
            nums = list(map(int, p[2:]))
            pr = [(nums[2 * k], nums[2 * k + 1]) for k in range(len(nums) // 2)]
            if (pr[0], pr[1:]) != (new.node[i][1], new.node[i][2]):
                bad.append(f"node{i}")
            nn += 1
        elif p[0] == "cell":
            i = int(p[1])
            nums = list(map(int, p[2:]))
            pr = [(nums[2 * k], nums[2 * k + 1]) for k in range(len(nums) // 2)]
            if pr != new.cell[i]:
                bad.append(f"cell{i}")
            nc += 1
    rec = {"gg": [coarse(new.sc[k]) for k in ("gg_gmin", "gg_drneg", "gg_factor", "gg_er_drop", "gg_gmin_minus_factor", "gg_neg_lhs")],
           "ih": [coarse(new.sc[k]) for k in ("ih_dgl", "ih_glx", "ih_glxx", "ih_det")],
           "bounds": [coarse(new.sc[f"bound{k}"]) for k in range(5)]}
    expected = {"gg": [(134, 162), (24879, 24882), (0, 15), (0, 5343), (120, 162), (-9944, -4585)],
                "ih": [(10529222, 18021395), (335897, 1510293), (128335, 864224), (86252, 1342330)],
                "bounds": [(-417514, 5279383), (-74636170, 13847721), (-25091315, 18991156), (-1403742153, 1437890461), (-3151489689, 2934165113)]}
    rec_ok = all([tuple(x) for x in rec[k]] == expected[k] for k in expected)
    out = {"dump2_sha256": sha256(DUMP2), "old_dump_sha256": sha256(OLD_DUMP), "common_scalars": len(common),
           "old_nodes_compared": nn, "old_cells_compared": nc, "mismatches": bad, "record_pairs_reproduced": rec_ok}
    (CONT / "dump2_consistency.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))
    return 0 if not bad and rec_ok else 1


if __name__ == "__main__":
    sys.exit(main())
