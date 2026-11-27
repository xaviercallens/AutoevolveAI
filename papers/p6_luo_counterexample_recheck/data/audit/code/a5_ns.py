"""Auditor: Regina vertex normal surfaces (standard coords) of Guo's triangulation; quad supports."""
import json
import regina

T = regina.Triangulation3.fromIsoSig('cMcabbjak')
# rebuild with the paper's labelling instead of the isoSig relabelling
PAIRS = [(0, (1, 2, 3), 0, (2, 3, 0)), (1, (0, 1, 3), 1, (1, 2, 0)),
         (0, (0, 1, 3), 1, (3, 2, 1)), (0, (0, 1, 2), 1, (3, 2, 0))]
T = regina.Triangulation3()
tets = [T.newTetrahedron(), T.newTetrahedron()]
for t1, f1, t2, f2 in PAIRS:
    m = dict(zip(f1, f2))
    m[[v for v in range(4) if v not in f1][0]] = [v for v in range(4) if v not in f2][0]
    tets[t1].join([v for v in range(4) if v not in f1][0], tets[t2], regina.Perm4(*[m[i] for i in range(4)]))
out = []
for coords in (regina.NS_STANDARD, regina.NS_QUAD):
    L = regina.NormalSurfaces(T, coords)
    for s in L:
        quads = [str(s.quads(t, k)) for t in range(2) for k in range(3)]
        tris = [str(s.triangles(t, v)) for t in range(2) for v in range(4)]
        out.append(dict(coords=str(coords), quads=quads, tris=tris, euler=str(s.eulerChar()),
                        orientable=s.isOrientable(), connected=s.isConnected()))
print(json.dumps(out, indent=1))
json.dump(out, open('/tmp/luoaudit/a5.json', 'w'), indent=1)
