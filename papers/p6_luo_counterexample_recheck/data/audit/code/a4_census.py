"""Auditor: brute-force census of all 1- and 2-tetrahedron closed gluings; which are L(3,1)?"""
import itertools, json
import regina

FACES_PERMS = list(itertools.permutations(range(3)))


def matchings(items: list):
    if not items:
        yield []
        return
    a = items[0]
    for k in range(1, len(items)):
        b = items[k]
        rest = items[1:k] + items[k + 1:]
        for m in matchings(rest):
            yield [(a, b)] + m


def gluing_perm(fa: int, fb: int, sigma: tuple) -> regina.Perm4:
    va = [v for v in range(4) if v != fa]
    vb = [v for v in range(4) if v != fb]
    img = [0] * 4
    for i in range(3):
        img[va[i]] = vb[sigma[i]]
    img[fa] = fb
    return regina.Perm4(*img)


def census(n: int) -> dict:
    faces = [(t, f) for t in range(n) for f in range(4)]
    found: dict = {}
    total = 0
    closed_orient = 0
    for m in matchings(faces):
        for sigmas in itertools.product(FACES_PERMS, repeat=len(m)):
            T = regina.Triangulation3()
            tets = [T.newTetrahedron() for _ in range(n)]
            for ((ta, fa), (tb, fb)), s in zip(m, sigmas):
                tets[ta].join(fa, tets[tb], gluing_perm(fa, fb, s))
            total += 1
            if not (T.isValid() and T.isClosed() and T.isOrientable() and T.isConnected()):
                continue
            closed_orient += 1
            sig = T.isoSig()
            if sig in found:
                continue
            found[sig] = dict(H1=str(T.homology()), nverts=T.countVertices(),
                              degrees=sorted(e.degree() for e in T.edges()))
    return dict(total=total, closed_orientable=closed_orient, classes=found)


out = {}
for n in (1, 2):
    c = census(n)
    out[f'n{n}'] = dict(total=c['total'], closed_orientable=c['closed_orientable'], n_iso_classes=len(c['classes']),
                        H1_list=sorted({v['H1'] for v in c['classes'].values()}),
                        Z3=[dict(sig=s, **v) for s, v in c['classes'].items() if v['H1'] == 'Z_3'])
    for item in out[f'n{n}']['Z3']:
        T = regina.Triangulation3.fromIsoSig(item['sig'])
        item['pi1'] = str(T.group())
        try:
            item['census'] = [h.name() for h in regina.Census.lookup(item['sig'])]
        except Exception as ex:
            item['census'] = 'err ' + str(ex)
json.dump(out, open('/tmp/luoaudit/a4.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
