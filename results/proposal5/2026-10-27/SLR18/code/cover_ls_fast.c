/*
 * Search v4 (float heuristic, Tier X; untrusted): C port of the coordinate fold-move
 * local search on the uncovered measure at fixed radius dstar (see cover_ls.py).
 *
 *   usage: cover_ls_fast n dnum dden seed budget_seconds out_file [random|zero] [v_1 ... v_n]
 *   radius dstar = dnum/dden (float); velocities default to 1..n.
 *   On success (float uncovered measure <= 1e-13) writes the shifts s_i (17 digits) to out_file
 *   and exits 0; otherwise exits 1 (best shifts still written).  Exact certification is done
 *   elsewhere by the two exact checkers.
 *
 * Data structure: all arcs (pieces normalised into [0,1)) in one array sorted by lo; moving
 * runner i = filter its pieces out and merge the new (already sorted) pieces in, O(N).
 * Best response of runner i: U_i = part of [0,1) not covered by the others (one O(N) sweep),
 * folded mod 1/v_i; the window of width 2 dstar/v_i maximising covered measure + breakout point
 * weights is found among breakpoints (sort + prefix sums).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

typedef struct { double lo, hi; int own; } Arc;

static int n;
static double *V, *S, D;
static Arc *arcs, *tmp, *mine;
static int na, cap;
static unsigned long long rs = 88172645463325252ULL;
static double P_WORSE = 0.3; static int RW_EVERY = 4; static int FULLSWAP = 0; /* overridable by env SLR_PWORSE, SLR_RW */

static double urand(void) {
    rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17;
    return (rs >> 11) * (1.0 / 9007199254740992.0);
}
static int irand(int m) { return (int)(urand() * m) % m; }

static double cpu(void) { return (double)clock() / CLOCKS_PER_SEC; }

static int cmp_arc(const void *a, const void *b) {
    double x = ((const Arc *)a)->lo, y = ((const Arc *)b)->lo;
    return (x > y) - (x < y);
}
static int cmp_d(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

/* pieces of runner i, sorted by lo, into buf; returns count */
static int make_pieces(int i, Arc *buf) {
    int m = 0;
    double v = V[i], h = D / v;
    double c0 = -S[i] / v;
    c0 -= floor(c0);
    for (int k = 0; k < (int)v; k++) {
        double c = c0 + k / v;
        if (c >= 1.0) c -= 1.0;
        double lo = c - h, hi = c + h;
        if (lo < 0) {
            buf[m++] = (Arc){0.0, hi, i};
            buf[m++] = (Arc){lo + 1.0, 1.0, i};
        } else if (hi > 1.0) {
            buf[m++] = (Arc){lo, 1.0, i};
            buf[m++] = (Arc){0.0, hi - 1.0, i};
        } else {
            buf[m++] = (Arc){lo, hi, i};
        }
    }
    qsort(buf, m, sizeof(Arc), cmp_arc);
    return m;
}

static void rebuild(void) {
    na = 0;
    for (int i = 0; i < n; i++) na += make_pieces(i, arcs + na);
    qsort(arcs, na, sizeof(Arc), cmp_arc);
}

static void move_runner(int i, double s_new) {
    S[i] = s_new;
    int m = make_pieces(i, mine);
    int a = 0, b = 0, t = 0;
    while (a < na || b < m) {
        if (a < na && arcs[a].own == i) { a++; continue; }
        if (b >= m || (a < na && arcs[a].lo <= mine[b].lo)) tmp[t++] = arcs[a++];
        else tmp[t++] = mine[b++];
    }
    Arc *sw = arcs; arcs = tmp; tmp = sw; na = t;
}

/* uncovered intervals of [0,1) by arcs with own != skip; returns count; total measure in *U */
static int gaps(int skip, double *ga, double *gb, double *U) {
    double reach = 0.0; int g = 0; double tot = 0.0;
    for (int j = 0; j < na; j++) {
        if (arcs[j].own == skip) continue;
        if (arcs[j].lo > reach) { ga[g] = reach; gb[g] = arcs[j].lo; tot += arcs[j].lo - reach; g++; }
        if (arcs[j].hi > reach) reach = arcs[j].hi;
    }
    if (reach < 1.0) { ga[g] = reach; gb[g] = 1.0; tot += 1.0 - reach; g++; }
    *U = tot;
    return g;
}

/* breakout points */
static double *PX, *PW; static int np, pcap;

static double *fa, *fb, *As, *Bs, *cA, *cAA, *cB, *cBB, *cand;
static int fcap;

static void ensure(int m) {
    if (m <= fcap) return;
    fcap = 2 * m + 64;
    fa = realloc(fa, fcap * sizeof(double)); fb = realloc(fb, fcap * sizeof(double));
    As = realloc(As, 3 * fcap * sizeof(double)); Bs = realloc(Bs, 3 * fcap * sizeof(double));
    cA = realloc(cA, (3 * fcap + 1) * sizeof(double)); cAA = realloc(cAA, (3 * fcap + 1) * sizeof(double));
    cB = realloc(cB, (3 * fcap + 1) * sizeof(double)); cBB = realloc(cBB, (3 * fcap + 1) * sizeof(double));
}

static int ub(const double *x, int m, double key) { /* number of x[j] <= key */
    int lo = 0, hi = m;
    while (lo < hi) { int mid = (lo + hi) >> 1; if (x[mid] <= key) lo = mid + 1; else hi = mid; }
    return lo;
}

typedef struct { double x, w; } PW_t;
static int cmp_pw(const void *a, const void *b) {
    double x = ((const PW_t *)a)->x, y = ((const PW_t *)b)->x;
    return (x > y) - (x < y);
}
static PW_t *fp; static double *fpx, *fpc; static int fpcap;

/* best centre in [0,P) for window half-width h; returns c */
static double last_F;
static double best_centre(int g, const double *ga, const double *gb, double P, double h, double lam) {
    int m = 0;
    ensure(4 * g + 16 + (int)(1.0 / P) * 2);
    for (int j = 0; j < g; j++) {
        double x = ga[j], y = gb[j];
        double q = floor(x / P);
        double x0 = x - q * P, y0 = y - q * P;
        while (y0 > P) {
            if (m + 2 >= fcap) ensure(m + 4);
            fa[m] = x0; fb[m] = P; m++;
            x0 = 0.0; y0 -= P;
        }
        if (m + 2 >= fcap) ensure(m + 4);
        fa[m] = x0; fb[m] = y0; m++;
    }
    ensure(m + 4);
    int M = 3 * m;
    for (int r = 0; r < 3; r++)
        for (int j = 0; j < m; j++) { As[r * m + j] = fa[j] + (r - 1) * P; Bs[r * m + j] = fb[j] + (r - 1) * P; }
    qsort(As, M, sizeof(double), cmp_d);
    qsort(Bs, M, sizeof(double), cmp_d);
    cA[0] = cAA[0] = cB[0] = cBB[0] = 0.0;
    for (int j = 0; j < M; j++) {
        cA[j + 1] = cA[j] + 1.0; cAA[j + 1] = cAA[j] + As[j];
        cB[j + 1] = cB[j] + 1.0; cBB[j + 1] = cBB[j] + Bs[j];
    }
    /* breakout points inside U_i, folded */
    int q = 0;
    if (np > 0 && lam > 0) {
        if (fpcap < 3 * np + 3) {
            fpcap = 3 * np + 3;
            fp = realloc(fp, fpcap * sizeof(PW_t)); fpx = realloc(fpx, fpcap * sizeof(double)); fpc = realloc(fpc, (fpcap + 1) * sizeof(double));
        }
        for (int p = 0; p < np; p++) {
            double x = PX[p];
            int j = ub(ga, g, x) - 1;
            if (j < 0 || x >= gb[j]) continue;
            double xf = x - floor(x / P) * P;
            for (int r = 0; r < 3; r++) { fp[q].x = xf + (r - 1) * P; fp[q].w = PW[p]; q++; }
        }
        qsort(fp, q, sizeof(PW_t), cmp_pw);
        fpc[0] = 0.0;
        for (int j = 0; j < q; j++) { fpx[j] = fp[j].x; fpc[j + 1] = fpc[j] + fp[j].w; }
    }
    int nc = 0;
    static int candcap = 0;
    int ccap = 4 * m + 2 * q + 16;
    if (ccap > candcap) { candcap = 2 * ccap; cand = realloc(cand, candcap * sizeof(double)); }
    for (int j = 0; j < m && nc + 4 < ccap; j++) {
        cand[nc++] = fa[j] + h; cand[nc++] = fa[j] - h; cand[nc++] = fb[j] + h; cand[nc++] = fb[j] - h;
    }
    for (int j = 0; j < q && nc + 2 < ccap; j += 3) {
        double x = fpx[j] < 0 ? fpx[j] + P : fpx[j];
        cand[nc++] = x + 0.999 * h; cand[nc++] = x - 0.999 * h;
    }
    double best = -1.0, bc = 0.0; int ties = 0;
    for (int j = 0; j < nc; j++) {
        double c = cand[j] - floor(cand[j] / P) * P;
        double x1 = c + h, x0 = c - h;
        int a1 = ub(As, M, x1), b1 = ub(Bs, M, x1), a0 = ub(As, M, x0), b0 = ub(Bs, M, x0);
        double G1 = (x1 * cA[a1] - cAA[a1]) - (x1 * cB[b1] - cBB[b1]);
        double G0 = (x0 * cA[a0] - cAA[a0]) - (x0 * cB[b0] - cBB[b0]);
        double F = G1 - G0;
        if (q > 0) {
            int u1 = ub(fpx, q, x1), u0 = ub(fpx, q, x0);
            F += lam * (fpc[u1] - fpc[u0]);
        }
        if (F > best + 1e-15) { best = F; bc = c; ties = 1; }
        else if (F > best - 1e-15) { ties++; if (irand(ties) == 0) bc = c; }
    }
    last_F = best;
    return bc;
}

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage\n"); return 2; }
    if (getenv("SLR_PWORSE")) P_WORSE = atof(getenv("SLR_PWORSE"));
    if (getenv("SLR_RW")) RW_EVERY = atoi(getenv("SLR_RW"));
    if (getenv("SLR_FULLSWAP")) FULLSWAP = atoi(getenv("SLR_FULLSWAP"));
    n = atoi(argv[1]);
    D = atof(argv[2]) / atof(argv[3]);
    rs ^= (unsigned long long)atoll(argv[4]) * 0x9E3779B97F4A7C15ULL;
    for (int i = 0; i < 20; i++) urand();
    double budget = atof(argv[5]);
    const char *out = argv[6];
    V = malloc(n * sizeof(double)); S = malloc(n * sizeof(double));
    double sv = 0;
    /* optional argv[7]: init mode 'random' (default) or 'zero' (s = 0 + 1e-9 noise); then optional velocities */
    int vbase = 7; int zero_init = 0; int wmax = 0;
    if (argc > 7 && (strcmp(argv[7], "zero") == 0 || strcmp(argv[7], "random") == 0 || strncmp(argv[7], "swap", 4) == 0)) {
        zero_init = strcmp(argv[7], "zero") == 0; vbase = 8;
        if (strncmp(argv[7], "swap", 4) == 0) wmax = atoi(argv[7] + 4);
        if (getenv("SLR_ZERO")) zero_init = 1;
    }
    for (int i = 0; i < n; i++) {
        V[i] = (argc > vbase + i) ? atof(argv[vbase + i]) : (double)(i + 1); sv += V[i];
        S[i] = zero_init ? 1e-9 * urand() : urand();
    }
    cap = (int)(2 * sv + 16);
    if (wmax > 0) cap = 2 * n * wmax + 16;
    char *used = calloc((wmax > 0 ? wmax : 1) + 2, 1);
    if (wmax > 0) for (int i = 0; i < n; i++) if ((int)V[i] <= wmax) used[(int)V[i]] = 1;
    if (getenv("SLR_INIT")) { /* init state file: n lines 'v s' */
        FILE *fi = fopen(getenv("SLR_INIT"), "r");
        if (!fi) { fprintf(stderr, "cannot open init\n"); return 2; }
        for (int i = 0; i < n; i++) { if (fscanf(fi, "%lf %lf", &V[i], &S[i]) != 2) { fprintf(stderr, "bad init\n"); return 2; } }
        fclose(fi);
        if (wmax > 0) { memset(used, 0, wmax + 2); for (int i = 0; i < n; i++) if ((int)V[i] <= wmax) used[(int)V[i]] = 1; }
        double sv2 = 0; for (int i = 0; i < n; i++) sv2 += V[i];
        if (2 * sv2 + 16 > cap) { fprintf(stderr, "init velocities too large for cap\n"); return 2; }
    }
    double *bestV = malloc(n * sizeof(double)); memcpy(bestV, V, n * sizeof(double));
    arcs = malloc(cap * sizeof(Arc)); tmp = malloc(cap * sizeof(Arc)); mine = malloc(cap * sizeof(Arc));
    double *ga = malloc(cap * sizeof(double)), *gb = malloc(cap * sizeof(double));
    pcap = 4096; PX = malloc(pcap * sizeof(double)); PW = malloc(pcap * sizeof(double)); np = 0;
    rebuild();
    double U; int g = gaps(-1, ga, gb, &U);
    double bestU = U; double *bestS = malloc(n * sizeof(double)); memcpy(bestS, S, n * sizeof(double));
    int *order = malloc(n * sizeof(int));
    long it = 0; int stall = 0;
    double t0 = cpu();
    while (U > 1e-13 && cpu() - t0 < budget) {
        it++;
        for (int i = 0; i < n; i++) order[i] = i;
        for (int i = n - 1; i > 0; i--) { int j = irand(i + 1); int t = order[i]; order[i] = order[j]; order[j] = t; }
        double Ustart = U;
        double lam = 0.0;
        if (g > 0) lam = U / g * 0.5;
        for (int r = 0; r < n; r++) {
            int i = order[r];
            double Ui;
            int gi = gaps(i, ga, gb, &Ui);
            if (gi == 0) continue;
            double P = 1.0 / V[i], h = D / V[i];
            double c = best_centre(gi, ga, gb, P, h, lam);
            double bestw = V[i], bestF = last_F;
            int full = FULLSWAP && stall > 0;
            if (wmax > 0 && (full || urand() < 0.25)) {
                int ntr = full ? wmax : 4;
                for (int tr = 0; tr < ntr; tr++) {
                    int w = full ? tr + 1 : 1 + irand(wmax);
                    if (used[w]) continue;
                    double cw = best_centre(gi, ga, gb, 1.0 / w, D / w, lam);
                    if (last_F > bestF + 1e-15) { bestF = last_F; bestw = w; c = cw; }
                }
            }
            double v_old = V[i];
            if (bestw != V[i]) { used[(int)V[i]] = 0; used[(int)bestw] = 1; V[i] = bestw; }
            if (bestw == v_old) { c = best_centre(gi, ga, gb, P, h, lam); }
            double sn = -c * V[i]; sn -= floor(sn);
            double s_old = S[i], U_old = U;
            move_runner(i, sn);
            g = gaps(-1, ga, gb, &U);
            if (U > U_old + 1e-15 && urand() >= P_WORSE) {
                if (V[i] != v_old) { used[(int)V[i]] = 0; used[(int)v_old] = 1; V[i] = v_old; }
                move_runner(i, s_old); g = gaps(-1, ga, gb, &U);
            }
            if (U < bestU) { bestU = U; memcpy(bestS, S, n * sizeof(double)); memcpy(bestV, V, n * sizeof(double)); }
            if (U <= 1e-13) break;
        }
        if (U <= 1e-13) break;
        if (U >= Ustart - 1e-15) {
            stall++;
            for (int j = 0; j < g; j++) {
                if (np >= pcap) { pcap *= 2; PX = realloc(PX, pcap * sizeof(double)); PW = realloc(PW, pcap * sizeof(double)); }
                PX[np] = 0.5 * (ga[j] + gb[j]); PW[np] = 1.0; np++;
            }
            if (stall % RW_EVERY == 0 && g > 0) {
                int j = irand(g);
                double u = ga[j] + urand() * (gb[j] - ga[j]);
                int i = irand(n);
                double sn = -u * V[i]; sn -= floor(sn);
                move_runner(i, sn);
                g = gaps(-1, ga, gb, &U);
            }
            if (stall % 60 == 0 || np > 40 * (g + 1)) np = 0;
            if (stall % 600 == 0) { /* restart from best with a big kick */
                memcpy(S, bestS, n * sizeof(double)); memcpy(V, bestV, n * sizeof(double));
                if (wmax > 0) { memset(used, 0, wmax + 2); for (int k = 0; k < n; k++) if ((int)V[k] <= wmax) used[(int)V[k]] = 1; }
                for (int k = 0; k < 1 + n / 10; k++) S[irand(n)] = urand();
                rebuild(); g = gaps(-1, ga, gb, &U); np = 0;
            }
        } else stall = 0;
        if (it % 2000 == 0) { fprintf(stderr, "it=%ld U=%.3e best=%.3e gaps=%d np=%d cpu=%.1f\n", it, U, bestU, g, np, cpu() - t0); }
    }
    FILE *f = fopen(out, "w");
    double *w = (U <= 1e-13) ? S : bestS;
    double *wv = (U <= 1e-13) ? V : bestV;
    for (int i = 0; i < n; i++) fprintf(f, "%d %.17g\n", (int)wv[i], w[i]);
    fclose(f);
    fprintf(stderr, "END n=%d U=%.3e best=%.3e it=%ld cpu=%.1f\n", n, U, bestU, it, cpu() - t0);
    return U <= 1e-13 ? 0 : 1;
}
