"""List Graffiti-29 firings at a given n with exact-ish detail (mpmath 50 digits)."""
import sys, subprocess
import numpy as np
import mpmath as mp
sys.path.insert(0, '/tmp/gr11audit/code')
from audit_scan import pairs, decode

mp.mp.dps = 50
n = int(sys.argv[1])
lines = subprocess.run(['nauty-geng', '-c', '-q', str(n)], capture_output=True).stdout.splitlines(keepends=True)
I, J = pairs(n)
A = decode(lines, n, I, J)
deg = A.sum(2)
R = ((A / np.sqrt(deg[:, :, None])) / np.sqrt(deg[:, None, :])).sum((1, 2)) / 2
reach = np.broadcast_to(np.eye(n, dtype=bool), A.shape).copy()
D = np.zeros(A.shape)
for _ in range(n - 1):
    D += ~reach
    reach = reach | ((reach.astype(np.float64) @ A) > 0)
dev = np.linalg.eigvalsh(D)
for thr in (1e-6, 1e-9):
    dneg = (dev < -thr).sum(1)
    f = np.nonzero(R > dneg - 1e-9)[0]
    print('thr', thr, 'R>dneg-1e-9 count', len(f))
    for i in f:
        a = A[i]
        Rm = mp.fsum(1 / mp.sqrt(int(deg[i, u]) * int(deg[i, v])) for u in range(n) for v in range(u + 1, n) if a[u, v])
        M = mp.matrix(D[i].astype(int).tolist())
        E = mp.eigsy(M, eigvals_only=True)
        dn = sum(1 for e in E if e < 0)
        print(lines[i].decode().strip(), 'R=', mp.nstr(Rm, 20), 'dneg_float=', int(dneg[i]), 'dneg_mp=', dn,
              'min|ev|=', mp.nstr(min(abs(e) for e in E), 5), 'fires_exact=', Rm > dn)
