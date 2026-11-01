/* lrspec_scan.c: exhaustive search for near-tight (ML < 1/n) n-tuples of distinct positive speeds <= N.
 * Exact integer arithmetic. Written for LR-SPEC (see PREREG_ITEM.md).
 *
 * usage: lrspec_scan n N Bw strict mode part nparts out.txt
 *   strict : 0 = correct test (n*d >= b counts as "far enough", ML>=1/n is NOT near-tight)
 *            1 = CORRUPTED strictness (n*d > b), negative control N1
 *   mode   : 0 = full candidate set m = 1..D/2 ; 1 = truncated candidates m <= D/4 (negative control N2)
 *   part/nparts : only first elements a0 with a0 % nparts == part
 * Output: one line per primitive near-tight tuple: v1..vn p q k   (ML=p/q lowest terms, k=q-n*p)
 * Stats to stderr.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#ifndef NW
#define NW 4
#endif
#define MAXN 12
#define MAXV 400

static int n, N, Bw, strictmode, cand_mode;
static uint64_t mk[MAXV + 1][NW];
static int nwit;
static uint64_t cnt_tuples = 0, cnt_surv = 0, cnt_exact_reject = 0, cnt_nt = 0, cnt_nt_nonprim = 0;
static FILE *fout;
static int v[MAXN];

static int gcd(int a, int b) { while (b) { int t = a % b; a = b; b = t; } return a; }

/* "far enough": ||t v|| >= 1/n for t = x/D where x = (m*v) mod D already reduced; d = min(x,D-x) */
static inline int far_enough(long long d, long long D) {
    return strictmode ? (n * d > D) : (n * d >= D);
}

static void build_masks(void) {
    int idx = 0;
    memset(mk, 0, sizeof(mk));
    for (int b = 2; b <= Bw; b++)
        for (int a = 1; 2 * a <= b; a++) {
            if (gcd(a, b) != 1) continue;
            if (idx >= 64 * NW) { fprintf(stderr, "too many witnesses for NW=%d\n", NW); exit(2); }
            for (int s = 1; s <= N; s++) {
                long long x = ((long long)a * s) % b;
                long long d = x < b - x ? x : b - x;
                if (far_enough(d, b)) mk[s][idx >> 6] |= (1ULL << (idx & 63));
            }
            idx++;
        }
    nwit = idx;
}

/* exact stage: returns 1 if tuple is near-tight (no witness time among m/(vi+vj)) */
static int exact_neartight(const int *w) {
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            int D = w[i] + w[j];
            int mmax = cand_mode ? D / 4 : D / 2;
            for (int m = 1; m <= mmax; m++) {
                int ok = 1;
                for (int k = 0; k < n; k++) {
                    long long x = ((long long)m * w[k]) % D;
                    long long d = x < D - x ? x : D - x;
                    if (!far_enough(d, D)) { ok = 0; break; }
                }
                if (ok) return 0;
            }
        }
    return 1;
}

/* exact ML = max over pairs and m of min_k dist(m*w_k mod D)/D, as reduced fraction */
static void exact_ml(const int *w, long long *P, long long *Q) {
    long long bn = 0, bd = 1;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            int D = w[i] + w[j];
            for (int m = 1; m <= D / 2; m++) {
                long long mn = D;
                for (int k = 0; k < n; k++) {
                    long long x = ((long long)m * w[k]) % D;
                    long long d = x < D - x ? x : D - x;
                    if (d < mn) mn = d;
                }
                if (mn * bd > bn * D) { bn = mn; bd = D; }
            }
        }
    long long g = gcd((int)bn, (int)bd);
    *P = bn / g; *Q = bd / g;
}

static void survivor(void) {
    cnt_surv++;
    if (!exact_neartight(v)) { cnt_exact_reject++; return; }
    cnt_nt++;
    int g = v[0];
    for (int i = 1; i < n; i++) g = gcd(g, v[i]);
    if (g != 1) { cnt_nt_nonprim++; return; }
    long long p, q;
    exact_ml(v, &p, &q);
    for (int i = 0; i < n; i++) fprintf(fout, "%d ", v[i]);
    fprintf(fout, "%lld %lld %lld\n", p, q, q - (long long)n * p);
}

static void dfs(int depth, int last, const uint64_t *cur) {
    if (depth == n - 1) {
        for (int s = last + 1; s <= N; s++) {
            cnt_tuples++;
            uint64_t acc = 0;
            for (int w = 0; w < NW; w++) acc |= cur[w] & mk[s][w];
            if (!acc) { v[depth] = s; survivor(); }
        }
        return;
    }
    uint64_t nxt[NW];
    for (int s = last + 1; s <= N - (n - 1 - depth); s++) {
        for (int w = 0; w < NW; w++) nxt[w] = cur[w] & mk[s][w];
        v[depth] = s;
        dfs(depth + 1, s, nxt);
    }
}

int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "usage: n N Bw strict mode part nparts out\n"); return 1; }
    n = atoi(argv[1]); N = atoi(argv[2]); Bw = atoi(argv[3]);
    strictmode = atoi(argv[4]); cand_mode = atoi(argv[5]);
    int part = atoi(argv[6]), nparts = atoi(argv[7]);
    if (n > MAXN || N > MAXV) { fprintf(stderr, "bounds\n"); return 1; }
    fout = fopen(argv[8], "w");
    if (!fout) { perror("out"); return 1; }
    build_masks();
    uint64_t full[NW];
    for (int w = 0; w < NW; w++) full[w] = ~0ULL;
    for (int a0 = 1; a0 <= N - (n - 1); a0++) {
        if (a0 % nparts != part) continue;
        uint64_t nxt[NW];
        for (int w = 0; w < NW; w++) nxt[w] = full[w] & mk[a0][w];
        v[0] = a0;
        if (n == 1) continue;
        dfs(1, a0, nxt);
    }
    fclose(fout);
    fprintf(stderr, "n=%d N=%d Bw=%d nwit=%d strict=%d mode=%d part=%d/%d tuples=%llu survivors=%llu exact_rejected=%llu neartight_all=%llu nonprimitive=%llu\n",
            n, N, Bw, nwit, strictmode, cand_mode, part, nparts,
            (unsigned long long)cnt_tuples, (unsigned long long)cnt_surv, (unsigned long long)cnt_exact_reject,
            (unsigned long long)cnt_nt, (unsigned long long)cnt_nt_nonprim);
    return 0;
}
