def lrat_check(cnf_cls, lrat_path):
    """Minimal LRAT checker (RUP hints only; RAT steps rejected)."""
    db = {i + 1: list(c) for i, c in enumerate(cnf_cls)}
    steps = 0
    empty = False
    for line in open(lrat_path):
        t = line.split()
        if not t:
            continue
        cid = int(t[0])
        if t[1] == "d":
            for x in t[2:-1]:
                db.pop(int(x), None)
            continue
        k = t.index("0", 1)
        lits = [int(x) for x in t[1:k]]
        hints = [int(x) for x in t[k + 1:-1]]
        if any(h < 0 for h in hints):
            return False, f"RAT hint at {cid}"
        assign = {-l for l in lits}
        ok = False
        for h in hints:
            cl = db[h]
            unassigned = [l for l in cl if -l not in assign]
            if any(l in assign for l in cl):
                return False, f"hint {h} satisfied at step {cid}"
            if len(unassigned) == 0:
                ok = True
                break
            if len(unassigned) == 1:
                assign.add(unassigned[0])
            else:
                return False, f"hint {h} not unit at step {cid}"
        if not ok:
            return False, f"no conflict at step {cid}"
        db[cid] = lits
        steps += 1
        if not lits:
            empty = True
            break
    return empty, f"{steps} lemmas checked"


