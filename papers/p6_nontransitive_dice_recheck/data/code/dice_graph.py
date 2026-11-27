"""DICE-6: independent recomputation of Easlick (arXiv 2610.40321) dice graphs.
Usage: python dice_graph.py N   (writes data/graph_N.json)
Edge x->y iff #{(i,j): x_i>y_j} == n*n//2 + 1.
"""
import sys, json, itertools
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


def dice(n):
    return list(itertools.combinations_with_replacement(range(1, n + 1), n))


def counts(D, n):
    c = np.zeros((len(D), n + 2), dtype=np.int32)
    for k, d in enumerate(D):
        for v in d:
            c[k, v] += 1
    return c


def edges(D, n, chunk=2000):
    """W(x,y)=sum_v cnt_y(v) * #{i: x_i>v} ; independent of the paper's eq (6) only in form."""
    c = counts(D, n)
    # g[x,v] = #{i: x_i > v} for v=1..n
    cum = np.cumsum(c[:, :], axis=1)  # cum[x,v] = #{x_i<=v}
    g = n - cum[:, 1:n + 1]
    cy = c[:, 1:n + 1]
    target = n * n // 2 + 1
    src, dst = [], []
    for a in range(0, len(D), chunk):
        W = g[a:a + chunk].astype(np.int32) @ cy.T.astype(np.int32)
        ii, jj = np.nonzero(W == target)
        src.append(ii + a)
        dst.append(jj)
    return np.concatenate(src), np.concatenate(dst)


def main(n):
    D = dice(n)
    s, t = edges(D, n)
    N = len(D)
    A = csr_matrix((np.ones(len(s), dtype=np.int8), (s, t)), shape=(N, N))
    ncomp, lab = connected_components(A, directed=True, connection='strong')
    sizes = np.bincount(lab)
    sccs = {}
    for k in np.nonzero(sizes > 1)[0]:
        members = np.nonzero(lab == k)[0]
        inside = int(np.sum(np.isin(s, members) & np.isin(t, members)))
        sccs[int(k)] = {"vertices": int(sizes[k]), "edges": inside, "members": [list(map(int, D[m])) for m in members] if sizes[k] <= 50 else None}
    selfloops = int(np.sum(s == t))
    out = {"n": n, "vertices": N, "edges": int(len(s)), "selfloops": selfloops, "n_scc": int(ncomp),
           "nontrivial_scc": [{"vertices": v["vertices"], "edges": v["edges"]} for v in sccs.values()],
           "target_W": n * n // 2 + 1}
    if n <= 6:
        out["small_sccs"] = list(sccs.values())
        out["edge_list"] = [[list(map(int, D[a])), list(map(int, D[b]))] for a, b in zip(s.tolist(), t.tolist())]
    json.dump(out, open(f"../data/graph_{n}.json", "w"))
    print(n, N, len(s), ncomp, [(v["vertices"], v["edges"]) for v in sccs.values()][:5], "selfloops", selfloops)


if __name__ == "__main__":
    main(int(sys.argv[1]))
