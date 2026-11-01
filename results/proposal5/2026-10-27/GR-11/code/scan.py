import sys, subprocess, numpy as np, json, time
n = int(sys.argv[1]); res = int(sys.argv[2]); mod = int(sys.argv[3])
cmd = ['nauty-geng', '-c', '-q', str(n)] + ([f'{res}/{mod}'] if mod > 1 else [])
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
iu = np.tril_indices(n, -1)  # graph6 order: j then i<j
nb = n * (n - 1) // 2
B = 200000
stat = dict(n=n, res=res, mod=mod, count=0, viol20=0, viol21=0, tie20=0, tie21=0,
            ctl29=0, ctl_l1=0, ctl_rank=0, min_gap20=9e9, min_gap21=9e9)
ex = {}
FLAG = open(sys.argv[4], 'w') if len(sys.argv) > 4 else None

def dec(lines):
    w = (nb + 5) // 6
    b = np.frombuffer(b''.join(l[1:1 + w] for l in lines), dtype=np.uint8).reshape(len(lines), -1).astype(np.int16) - 63
    bits = ((b[:, :, None] >> np.arange(5, -1, -1)) & 1).reshape(len(lines), -1)[:, :nb]
    A = np.zeros((len(lines), n, n))
    A[:, iu[0], iu[1]] = bits
    return A + A.transpose(0, 2, 1)

def proc(lines):
    A = dec(lines); ev = np.linalg.eigvalsh(A)
    pos = ev > 1e-9; neg = ev < -1e-9
    npos = pos.sum(1); nneg = neg.sum(1); S = np.where(pos, ev, 0).sum(1)
    stat['count'] += len(lines)
    for k, c in (('20', npos), ('21', nneg)):
        gap = S - c
        stat['min_gap' + k] = min(stat['min_gap' + k], float(gap.min()))
        v = gap < -1e-6
        stat['viol' + k] += int(v.sum()); stat['tie' + k] += int((np.abs(gap) <= 1e-6).sum())
        fl = np.nonzero(gap < 1e-6)[0]
        if len(fl) and FLAG is not None:
            for i in fl:
                FLAG.write(k + ' ' + lines[int(i)].decode().strip() + '\n')
            FLAG.flush()
        if v.any() and 'v' + k not in ex:
            ex['v' + k] = lines[int(np.argmax(v))].decode().strip()
    deg = A.sum(2)
    stat['ctl_l1'] += int((ev[:, -1] < deg.mean(1) - 1e-9).sum())
    stat['ctl_rank'] += int((np.abs(ev).sum(1) < npos + nneg - 1e-9).sum())
    # Graffiti 29 (WoW p.23): Randic index <= number of NEGATIVE DISTANCE eigenvalues
    with np.errstate(divide='ignore', invalid='ignore'):
        w = 1 / np.sqrt(deg[:, :, None] * deg[:, None, :])
    R = np.where(A > 0, w, 0).sum((1, 2)) / 2
    Dm = np.full(A.shape, 99.0); idx = np.arange(n)
    Dm[:, idx, idx] = 0; Dm[A > 0] = 1
    for k in range(n):
        Dm = np.minimum(Dm, Dm[:, :, k:k + 1] + Dm[:, k:k + 1, :])
    dev = np.linalg.eigvalsh(Dm)
    dneg = (dev < -1e-9).sum(1)
    f = R > dneg + 1e-9
    stat['ctl29'] += int(f.sum())
    if f.any() and 'c29' not in ex:
        ex['c29'] = lines[int(np.argmax(f))].decode().strip()

t = time.time(); buf = []
for l in p.stdout:
    buf.append(l)
    if len(buf) >= B:
        proc(buf); buf = []
if buf:
    proc(buf)
stat['sec'] = time.time() - t; stat['examples'] = ex
print(json.dumps(stat))
