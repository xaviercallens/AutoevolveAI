"""Independent GR-11 audit scanner (auditor's own code).
Exact inertia: integer characteristic polynomial by Faddeev-LeVerrier in float64 with a
2^52 exactness guard, then Descartes' rule (adjacency is real-rooted, so exact).
S+ = sum of the top n_+ (exact) eigenvalues, computed with LAPACK dgeev (np.linalg.eigvals,
nonsymmetric QR) and cross-checked against dsyevd (np.linalg.eigvalsh).
Distance matrix by BFS-layer reachability (not Floyd)."""
import sys, json, subprocess, time
import numpy as np


def pairs(n: int) -> tuple[np.ndarray, np.ndarray]:
    I, J = [], []
    for j in range(1, n):
        for i in range(j):
            I.append(i); J.append(j)
    return np.array(I), np.array(J)


def decode(lines: list[bytes], n: int, I: np.ndarray, J: np.ndarray) -> np.ndarray:
    nb = n * (n - 1) // 2
    w = (nb + 5) // 6
    raw = np.frombuffer(b''.join(l[1:1 + w] for l in lines), dtype=np.uint8).reshape(len(lines), w) - 63
    bits = np.unpackbits(raw[:, :, None], axis=2)[:, :, 2:].reshape(len(lines), 6 * w)[:, :nb]
    A = np.zeros((len(lines), n, n))
    A[:, I, J] = bits; A[:, J, I] = bits
    return A


def charpoly(A: np.ndarray) -> np.ndarray:
    """c[:,k] = coefficient of x^{n-k} in det(xI-A); exact integers (guarded)."""
    B, n, _ = A.shape
    c = np.zeros((B, n + 1)); c[:, 0] = 1
    M = np.zeros_like(A); eye = np.eye(n)
    for k in range(1, n + 1):
        M = M + c[:, k - 1, None, None] * eye
        assert n * np.abs(M).max() < 2.0 ** 52
        AM = A @ M
        t = -np.trace(AM, axis1=1, axis2=2)
        assert np.all(np.abs(t) < 2.0 ** 52)
        q = t / k
        assert np.all(q == np.round(q)), 'non-integer coefficient'
        c[:, k] = q
        M = AM
    return c


def sign_changes(c: np.ndarray) -> np.ndarray:
    s = np.sign(c)
    out = np.zeros(len(c), dtype=int)
    last = np.zeros(len(c))
    for k in range(c.shape[1]):
        sk = s[:, k]
        nz = sk != 0
        out += (nz & (last != 0) & (sk != last))
        last = np.where(nz, sk, last)
    return out


def main() -> None:
    n = int(sys.argv[1]); res = int(sys.argv[2]); mod = int(sys.argv[3]); outp = sys.argv[4]
    cmd = ['nauty-geng', '-c', '-q', str(n)] + ([f'{res}/{mod}'] if mod > 1 else [])
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    I, J = pairs(n)
    st = dict(n=n, res=res, mod=mod, count=0, viol20=0, viol21=0, min_m20=9e9, min_m21=9e9,
              min_m21_nonK=9e9, argmin20='', argmin21_nonK='', eq21_lt1e6=[], near1e2=[],
              inertia_mismatch_float=0, small_ev_lt1e8=0, min_abs_nonzero_ev=9e9,
              max_dSplus_geev_syevd=0.0, ctl29=0, ctl29_first='', ctl29_near=0,
              neg_l1=0, neg_rank=0, bad_factor=0)
    alt = np.array([(-1) ** (n - k) for k in range(n + 1)])[None, :]

    def proc(lines: list[bytes]) -> None:
        A = decode(lines, n, I, J)
        c = charpoly(A)
        npos = sign_changes(c)
        nneg = sign_changes(c * alt)
        nzero = np.zeros(len(c), dtype=int)
        for k in range(1, n + 1):
            nzero += np.all(c[:, k:] == 0, axis=1)
        assert np.all(npos + nneg + nzero == n)
        ev = np.sort(np.linalg.eigvals(A).real, axis=1)[:, ::-1]   # dgeev
        ev2 = np.linalg.eigvalsh(A)[:, ::-1]                        # dsyevd
        idx = np.arange(n)[None, :]
        Sp = np.where(idx < npos[:, None], ev, 0).sum(1)
        Sp2 = np.where(idx < npos[:, None], ev2, 0).sum(1)
        st['max_dSplus_geev_syevd'] = max(st['max_dSplus_geev_syevd'], float(np.abs(Sp - Sp2).max()))
        fpos = (ev2 > 1e-9).sum(1); fneg = (ev2 < -1e-9).sum(1)
        st['inertia_mismatch_float'] += int(((fpos != npos) | (fneg != nneg)).sum())
        st['small_ev_lt1e8'] += int((np.abs(ev2) < 1e-8).any(1).sum())
        aev = np.sort(np.abs(ev2), axis=1)
        full = nzero < n
        mnz = aev[np.arange(len(aev)), np.minimum(nzero, n - 1)][full]
        st['min_abs_nonzero_ev'] = min(st['min_abs_nonzero_ev'], float(mnz.min()))
        st['count'] += len(lines)
        m20 = Sp - npos; m21 = Sp - nneg
        st['viol20'] += int((m20 < 0).sum()); st['viol21'] += int((m21 < 0).sum())
        i = int(np.argmin(m20))
        if m20[i] < st['min_m20']:
            st['min_m20'] = float(m20[i]); st['argmin20'] = lines[i].decode().strip()
        st['min_m21'] = min(st['min_m21'], float(m21.min()))
        complete = A.sum((1, 2)) == n * (n - 1)
        m21n = np.where(complete, 9e9, m21)
        i = int(np.argmin(m21n))
        if m21n[i] < st['min_m21_nonK']:
            st['min_m21_nonK'] = float(m21n[i]); st['argmin21_nonK'] = lines[i].decode().strip()
        for i in np.nonzero(np.abs(m21) < 1e-6)[0]:
            st['eq21_lt1e6'].append(lines[int(i)].decode().strip())
        for i in np.nonzero((m20 < 1e-2) | (m21 < 1e-2))[0]:
            if len(st['near1e2']) < 200:
                st['near1e2'].append(lines[int(i)].decode().strip())
        deg = A.sum(2)
        st['neg_l1'] += int((ev2[:, 0] < deg.mean(1) - 1e-9).sum())
        st['neg_rank'] += int((np.abs(ev2).sum(1) < npos + nneg - 1e-9).sum())
        # Graffiti 29: Randic <= #negative distance eigenvalues; distance via BFS layers
        R = ((A / np.sqrt(deg[:, :, None])) / np.sqrt(deg[:, None, :])).sum((1, 2)) / 2
        reach = np.broadcast_to(np.eye(n, dtype=bool), A.shape).copy()
        D = np.zeros(A.shape)
        for _ in range(n - 1):
            D += ~reach
            reach = reach | ((reach.astype(np.float64) @ A) > 0)
        assert reach.all()
        dev = np.linalg.eigvals(D).real
        dneg = (dev < -1e-6).sum(1)
        st['ctl29_near'] += int(((np.abs(dev) < 1e-6).any(1) | (np.abs(R - dneg) < 1e-9)).sum())
        f = R > dneg + 1e-9
        st['ctl29'] += int(f.sum())
        if f.any() and not st['ctl29_first']:
            st['ctl29_first'] = lines[int(np.argmax(f))].decode().strip()

    t = time.time(); buf = []
    for l in p.stdout:
        buf.append(l)
        if len(buf) >= 100000:
            proc(buf); buf = []
    if buf:
        proc(buf)
    st['sec'] = time.time() - t
    json.dump(st, open(outp, 'w'))
    print(json.dumps({k: v for k, v in st.items() if k not in ('near1e2',)}))


if __name__ == '__main__':
    main()
