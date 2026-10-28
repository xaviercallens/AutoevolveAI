/*
 * census_fast.c -- C1b (Proposal 4, addendum 2): fast implementation of the SAME certified decision rule as
 * C1's census_enclosure.py (results/proposal4/2026-10-27/C1/code, audit-revised copy with the overflow guard).
 *
 * Reads graph6 lines (one connected graph on N vertices per line, e.g. from `nauty-geng -cq N res/mod`) on stdin.
 *
 * Criterion (Allen et al., arXiv 1906.01036v1, eqs. (5),(6),(9); definition p. 8): amplifier of weak selection
 * for death-Birth iff N_eff > N.  Rule (floating point only PROPOSES, exact integers DECIDE):
 *   Scaled integer system for i<j (eq. 5 times 2 k_i k_j):
 *     2 k_i k_j tau_ij - k_j sum_{k~i,k!=j} tau_jk - k_i sum_{k~j,k!=i} tau_ik = 2 k_i k_j.
 *   1. float64 solve (Cholesky; A_s is symmetric -- correctness never depends on it, only the proposal quality);
 *   2. t = rint(x 2^30) (int64) after the audit guard: x finite and |x| 2^30 < 2^50, else the graph is a CANDIDATE;
 *   3. exact residual res = 2^30 rhs - A_s t in __int128; E = max |res|; eps = E / 2^31;
 *   4. A = I - M, M >= 0 substochastic, A^{-1} >= 0, A^{-1} 1 = tau => |tau - t/2^30| <= eps tau_max,
 *      tau_max <= X / (2^30 (1 - eps)), X = max t;
 *   5. N_eff = 1 + sum_{directed edges i->j} w_ij tau_ij / Den with sum w/Den = 1 (correct: w = 1, Den = 2m, the identity
 *      pi_i p_ij = 1/2m), so |N_eff - N^| <= eps tau_max. EXCLUDED (N_eff < N certified) iff, in exact integers,
 *      (Den 2^30 + W)(2^31 - E) + Den E X < N Den 2^30 (2^31 - E),  W = sum w t, and the graph is not regular.
 *      With Den = 2m, W = 2S this is exactly C1's inequality multiplied by 2.
 *   Everything not excluded is a CANDIDATE, to be solved exactly with Fractions (finish_candidates.py).
 * NEGATIVE CONTROL (--corrupt uniform_pi): replaces pi_i = k_i/2m by 1/N (w_ij = L/k_i, Den = N L, L = 2520). The
 *   certified path is unchanged (sum w/Den = 1 still holds), so it certifies the corrupted functional; it must change verdicts.
 *
 * Usage: census_fast N OUT.json [--verbose PER_GRAPH.tsv] [--near-margin 1e-3] [--corrupt uniform_pi] < graphs.g6
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 12
#define MAXP 66
#define MAXNZ 24
#define TOPK 25
#define MAXCAND 2000000
#define MAXNEAR 2000000

typedef __int128 i128;

typedef struct {
    double key;
    double val;
    char g6[24];
} item_t;

typedef struct {
    char g6[24];
    int regular;
    double neff;
    long long e;
    int reason; /* 0 not excluded by the inequality, 1 regular, 2 overflow guard, 3 Cholesky pivot <= 0 */
} cand_t;

typedef struct {
    char g6[24];
    double neff;
    double ub;
} near_t;

static int n_glob, npairs;
static int pidx[MAXN][MAXN];
static int pi_of[MAXP], pj_of[MAXP];

static void top_insert(item_t *arr, int *cnt, double key, double val, const char *g6) {
    /* keep the TOPK largest keys */
    if (*cnt < TOPK) {
        arr[*cnt].key = key;
        arr[*cnt].val = val;
        strncpy(arr[*cnt].g6, g6, 23);
        arr[*cnt].g6[23] = 0;
        (*cnt)++;
        return;
    }
    int mi = 0;
    for (int a = 1; a < TOPK; a++)
        if (arr[a].key < arr[mi].key) mi = a;
    if (key > arr[mi].key) {
        arr[mi].key = key;
        arr[mi].val = val;
        strncpy(arr[mi].g6, g6, 23);
        arr[mi].g6[23] = 0;
    }
}

/* graph6 uses characters 63..126, which include the backslash: escape it (and '"', for safety) for JSON */
static const char *jesc(const char *s, char *buf) {
    char *o = buf;
    for (; *s; s++) {
        if (*s == '\\' || *s == '"') *o++ = '\\';
        *o++ = *s;
    }
    *o = 0;
    return buf;
}

static int cmp_item_desc(const void *a, const void *b) {
    double x = ((const item_t *)a)->key, y = ((const item_t *)b)->key;
    return (x < y) - (x > y);
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: census_fast N OUT.json [--verbose F] [--near-margin d] [--corrupt uniform_pi]\n");
        return 2;
    }
    int n = atoi(argv[1]);
    const char *out_path = argv[2];
    const char *verbose_path = NULL;
    double near_margin = 1e-3;
    int corrupt = 0;
    for (int a = 3; a < argc; a++) {
        if (!strcmp(argv[a], "--verbose") && a + 1 < argc) verbose_path = argv[++a];
        else if (!strcmp(argv[a], "--near-margin") && a + 1 < argc) near_margin = atof(argv[++a]);
        else if (!strcmp(argv[a], "--corrupt") && a + 1 < argc) {
            a++;
            if (!strcmp(argv[a], "uniform_pi")) corrupt = 1;
            else { fprintf(stderr, "unknown corruption\n"); return 2; }
        } else { fprintf(stderr, "bad argument %s\n", argv[a]); return 2; }
    }
    if (n < 2 || n > 11) { fprintf(stderr, "N must be 2..11\n"); return 2; }
    n_glob = n;
    npairs = 0;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) pidx[i][j] = -1;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            pidx[i][j] = pidx[j][i] = npairs;
            pi_of[npairs] = i;
            pj_of[npairs] = j;
            npairs++;
        }
    const int P = npairs;
    const int nb = n * (n - 1) / 2;
    const int nchar = (nb + 5) / 6;
    const i128 two30 = (i128)1 << 30;
    const i128 two31 = (i128)1 << 31;
    const double two30d = 1073741824.0;
    const double lim50 = 1125899906842624.0; /* 2^50 */
    const long long LCM = 2520;

    FILE *vf = NULL;
    if (verbose_path) {
        vf = fopen(verbose_path, "w");
        if (!vf) { perror("verbose"); return 1; }
    }
    cand_t *cands = malloc(sizeof(cand_t) * MAXCAND);
    near_t *nears = malloc(sizeof(near_t) * MAXNEAR);
    if (!cands || !nears) { fprintf(stderr, "oom\n"); return 1; }
    long long ncand = 0, nnear = 0;
    item_t top[TOPK], nearest[TOPK];
    int ntop = 0, nnearest = 0;
    long long total = 0, excluded = 0, nregular = 0, nguard = 0, nchol = 0, nbadline = 0;
    double max_eps = 0.0, min_gap = 1e300;
    int have_gap = 0;
    clock_t c0 = clock();
    time_t w0 = time(NULL);

    char line[256];
    int adj[MAXN][MAXN];
    int deg[MAXN];
    static double A[MAXP][MAXP];
    double x[MAXP], b[MAXP];
    long long t[MAXP];
    long long rhs[MAXP];
    int nzc[MAXP][MAXNZ];
    long long nzv[MAXP][MAXNZ];
    int nnz[MAXP];

    while (fgets(line, sizeof line, stdin)) {
        size_t len = strlen(line);
        while (len && (line[len - 1] == '\n' || line[len - 1] == '\r')) line[--len] = 0;
        if (len == 0) continue;
        if ((int)line[0] - 63 != n || (int)len != 1 + nchar) { nbadline++; continue; }
        total++;
        /* decode graph6 */
        memset(adj, 0, sizeof adj);
        {
            int idx = 0;
            for (int j = 1; j < n; j++)
                for (int i = 0; i < j; i++) {
                    int c = line[1 + idx / 6] - 63;
                    int bit = (c >> (5 - idx % 6)) & 1;
                    adj[i][j] = adj[j][i] = bit;
                    idx++;
                }
        }
        int dmin = 1000, dmax = -1, m2 = 0;
        for (int i = 0; i < n; i++) {
            int d = 0;
            for (int j = 0; j < n; j++) d += adj[i][j];
            deg[i] = d;
            m2 += d;
            if (d < dmin) dmin = d;
            if (d > dmax) dmax = d;
        }
        int regular = (dmin == dmax);
        if (regular) nregular++;
        /* scaled integer system */
        for (int p = 0; p < P; p++) {
            int i = pi_of[p], j = pj_of[p];
            long long ki = deg[i], kj = deg[j];
            for (int q = 0; q < P; q++) A[p][q] = 0.0;
            nnz[p] = 0;
            nzc[p][nnz[p]] = p;
            nzv[p][nnz[p]] = 2 * ki * kj;
            nnz[p]++;
            for (int k = 0; k < n; k++) {
                if (adj[i][k] && k != j) { /* -(1/2) p_ik tau_jk, scaled: -k_j */
                    nzc[p][nnz[p]] = pidx[j][k];
                    nzv[p][nnz[p]] = -kj;
                    nnz[p]++;
                }
                if (adj[j][k] && k != i) { /* -(1/2) p_jk tau_ik, scaled: -k_i */
                    nzc[p][nnz[p]] = pidx[i][k];
                    nzv[p][nnz[p]] = -ki;
                    nnz[p]++;
                }
            }
            for (int a = 0; a < nnz[p]; a++) A[p][nzc[p][a]] += (double)nzv[p][a];
            rhs[p] = 2 * ki * kj;
            b[p] = (double)rhs[p];
        }
        /* float proposal: Cholesky (lower triangle) */
        int chol_ok = 1;
        for (int j = 0; j < P && chol_ok; j++) {
            double s = A[j][j];
            for (int k = 0; k < j; k++) s -= A[j][k] * A[j][k];
            if (!(s > 0.0)) { chol_ok = 0; break; }
            double ljj = sqrt(s);
            A[j][j] = ljj;
            double inv = 1.0 / ljj;
            for (int i = j + 1; i < P; i++) {
                double v = A[i][j];
                const double *ri = A[i], *rj = A[j];
                for (int k = 0; k < j; k++) v -= ri[k] * rj[k];
                A[i][j] = v * inv;
            }
        }
        char reason_c = 0;
        int guard_ok = 1;
        long long E = 0, X = 0;
        i128 W = 0, Den = 0;
        int ok = 0;
        double neff_hat = NAN, ub = NAN;
        if (!chol_ok) {
            nchol++;
            reason_c = 3;
        } else {
            for (int i = 0; i < P; i++) {
                double s = b[i];
                for (int k = 0; k < i; k++) s -= A[i][k] * x[k];
                x[i] = s / A[i][i];
            }
            for (int i = P - 1; i >= 0; i--) {
                double s = x[i];
                for (int k = i + 1; k < P; k++) s -= A[k][i] * x[k];
                x[i] = s / A[i][i];
            }
            for (int p = 0; p < P; p++)
                if (!isfinite(x[p]) || fabs(x[p]) * two30d >= lim50) guard_ok = 0;
            if (!guard_ok) {
                nguard++;
                reason_c = 2;
            } else {
                for (int p = 0; p < P; p++) t[p] = llrint(x[p] * two30d);
                i128 Emax = 0;
                for (int p = 0; p < P; p++) {
                    i128 r = ((i128)rhs[p] << 30);
                    for (int a = 0; a < nnz[p]; a++) r -= (i128)nzv[p][a] * (i128)t[nzc[p][a]];
                    if (r < 0) r = -r;
                    if (r > Emax) Emax = r;
                }
                E = (Emax > (i128)INT64_MAX) ? INT64_MAX : (long long)Emax;
                X = t[0];
                for (int p = 1; p < P; p++)
                    if (t[p] > X) X = t[p];
                if (!corrupt) {
                    Den = m2; /* 2m */
                    for (int p = 0; p < P; p++)
                        if (adj[pi_of[p]][pj_of[p]]) W += 2 * (i128)t[p];
                } else {
                    Den = (i128)n * LCM;
                    for (int i = 0; i < n; i++) {
                        long long wi = LCM / deg[i];
                        for (int j = 0; j < n; j++)
                            if (adj[i][j]) W += (i128)wi * (i128)t[pidx[i][j]];
                    }
                }
                i128 Ei = E, Xi = X;
                ok = (Ei < two31) && ((Den * two30 + W) * (two31 - Ei) + Den * Ei * Xi < (i128)n * Den * two30 * (two31 - Ei));
                neff_hat = 1.0 + (double)W / ((double)Den * two30d);
                double eps = (double)E / 2147483648.0;
                ub = neff_hat + eps * (double)X / (two30d * (1.0 - eps));
                if (eps > max_eps) max_eps = eps;
                top_insert(top, &ntop, neff_hat / n, neff_hat, line);
                if (!ok) reason_c = 0;
                else if (regular) reason_c = 1;
            }
        }
        int excl = ok && !regular && chol_ok && guard_ok;
        if (excl) {
            excluded++;
            double gap = (double)n - ub;
            if (!have_gap || gap < min_gap) { min_gap = gap; have_gap = 1; }
            top_insert(nearest, &nnearest, -gap, neff_hat, line);
            if (ub >= (double)n - near_margin) {
                if (nnear < MAXNEAR) {
                    strncpy(nears[nnear].g6, line, 23);
                    nears[nnear].g6[23] = 0;
                    nears[nnear].neff = neff_hat;
                    nears[nnear].ub = ub;
                }
                nnear++;
            }
        } else {
            if (ncand < MAXCAND) {
                strncpy(cands[ncand].g6, line, 23);
                cands[ncand].g6[23] = 0;
                cands[ncand].regular = regular;
                cands[ncand].neff = neff_hat;
                cands[ncand].e = E;
                cands[ncand].reason = reason_c;
            }
            ncand++;
        }
        if (vf) fprintf(vf, "%s\t%c\t%.15g\t%.15g\t%lld\t%lld\n", line, excl ? 'X' : 'C', neff_hat, ub, E, X);
    }
    if (vf) fclose(vf);
    double cpu = (double)(clock() - c0) / CLOCKS_PER_SEC;
    double wall = difftime(time(NULL), w0);
    if (ncand > MAXCAND || nnear > MAXNEAR) fprintf(stderr, "WARNING: candidate/near list truncated\n");
    qsort(top, ntop, sizeof(item_t), cmp_item_desc);
    qsort(nearest, nnearest, sizeof(item_t), cmp_item_desc);
    char eb[64];
    FILE *fo = fopen(out_path, "w");
    if (!fo) { perror("out"); return 1; }
    fprintf(fo, "{\n \"implementation\": \"census_fast.c\",\n \"N\": %d,\n \"corrupt\": \"%s\",\n \"graphs\": %lld,\n", n,
            corrupt ? "uniform_pi" : "none", total);
    fprintf(fo, " \"bad_lines\": %lld,\n \"excluded_certified\": %lld,\n \"regular\": %lld,\n \"guard_fail\": %lld,\n \"chol_fail\": %lld,\n",
            nbadline, excluded, nregular, nguard, nchol);
    fprintf(fo, " \"max_eps\": %.17g,\n \"min_certified_gap_among_excluded\": ", max_eps);
    if (have_gap) fprintf(fo, "%.17g,\n", min_gap);
    else fprintf(fo, "null,\n");
    fprintf(fo, " \"near_margin\": %.17g,\n \"n_near\": %lld,\n \"n_candidates\": %lld,\n \"candidates\": [", near_margin, nnear, ncand);
    for (long long a = 0; a < ncand && a < MAXCAND; a++)
        fprintf(fo, "%s\n  {\"graph6\": \"%s\", \"regular\": %s, \"neff_float\": %.17g, \"E\": %lld, \"reason\": %d}", a ? "," : "",
                jesc(cands[a].g6, eb), cands[a].regular ? "true" : "false", isfinite(cands[a].neff) ? cands[a].neff : -1.0, cands[a].e,
                cands[a].reason);
    fprintf(fo, "\n ],\n \"near\": [");
    for (long long a = 0; a < nnear && a < MAXNEAR; a++)
        fprintf(fo, "%s\n  {\"graph6\": \"%s\", \"neff_float\": %.17g, \"ub\": %.17g}", a ? "," : "", jesc(nears[a].g6, eb), nears[a].neff, nears[a].ub);
    fprintf(fo, "\n ],\n \"top_by_float_neff\": [");
    for (int a = 0; a < ntop; a++) fprintf(fo, "%s[%.17g, \"%s\"]", a ? ", " : "", top[a].key, jesc(top[a].g6, eb));
    fprintf(fo, "],\n \"nonregular_nearest_to_N\": [");
    for (int a = 0; a < nnearest; a++)
        fprintf(fo, "%s\n  {\"gap_lower\": %.17g, \"graph6\": \"%s\", \"neff_float\": %.17g}", a ? "," : "", -nearest[a].key, jesc(nearest[a].g6, eb),
                nearest[a].val);
    fprintf(fo, "\n ],\n \"cpu_seconds\": %.3f,\n \"seconds\": %.0f\n}\n", cpu, wall);
    fclose(fo);
    fprintf(stderr, "done N=%d graphs %lld excluded %lld candidates %lld near %lld cpu %.1fs\n", n, total, excluded, ncand, nnear, cpu);
    return 0;
}
