/* DH-Psi2 independent enumeration (pure integer arithmetic, no floating point).
 *
 * Written from eq. (trace) of the dyadic triangular Hilbert paper, not from the Python kernel.
 * Resolution N = 2, n = 4. In units of 1/64:
 *   S_w(F) = wT*|sum_{ijk} F0[i][j]F1[j][k]F2[k][i]|
 *          + 1*|sum_{ijk} F0F1F2 h(i)h(j)h(k)|                         (level 0, h(x) = x<2 ? +1 : -1)
 *          + 2*sum_{p,q} |sum_{i in p, j in q, k in p^q} F0F1F2 h1(i)h1(j)h1(k)|   (level 1, h1(x) = x&1 ? -1 : +1)
 * Haar-free form: h = h1 = 1.
 * Enumerates all F0, F1 with F[0][0] = +1 (sign symmetry F_v -> -F_v; every term is trilinear), and
 * for each pair takes max over F2 in {+-1}^16 via  max_{s in {+-1}^6, s_0=+1} sum_x |sum_t s_t c_t[x]|.
 * Optional self-check mode compares that with a literal loop over all 2^16 F2.
 *
 * Usage: psi_exhaust WT HAAR F0_LO F0_HI [bruteforce_pairs]
 * Output: one JSON object on stdout (max, histogram, violations > 192, argmax recomputed by triple sum).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define NT 6
#define HMAX 4096

static int sig[NT][4][4][4];
static int wts[NT];

static void build_terms(int wT, int haar) {
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            for (int k = 0; k < 4; k++) {
                int h0i = haar ? (i < 2 ? 1 : -1) : 1, h0j = haar ? (j < 2 ? 1 : -1) : 1, h0k = haar ? (k < 2 ? 1 : -1) : 1;
                int h1i = haar ? ((i & 1) ? -1 : 1) : 1, h1j = haar ? ((j & 1) ? -1 : 1) : 1, h1k = haar ? ((k & 1) ? -1 : 1) : 1;
                sig[0][i][j][k] = 1;
                sig[1][i][j][k] = h0i * h0j * h0k;
                int t = 2;
                for (int p = 0; p < 2; p++)
                    for (int q = 0; q < 2; q++, t++) {
                        int r = p ^ q;
                        int in = ((i >> 1) == p) && ((j >> 1) == q) && ((k >> 1) == r);
                        sig[t][i][j][k] = in ? h1i * h1j * h1k : 0;
                    }
            }
    wts[0] = wT;
    wts[1] = 1;
    for (int t = 2; t < NT; t++) wts[t] = 2;
}

static void decode(uint32_t mask15, int F[4][4]) {
    /* cell 0 fixed +1; bit b of mask -> cell b+1, bit set means -1 */
    for (int c = 0; c < 16; c++) {
        int neg = c == 0 ? 0 : (int)((mask15 >> (c - 1)) & 1u);
        F[c / 4][c % 4] = neg ? -1 : 1;
    }
}

static int full_value(int F0[4][4], int F1[4][4], int F2[4][4]) {
    int tot = 0;
    for (int t = 0; t < NT; t++) {
        int s = 0;
        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                for (int k = 0; k < 4; k++) s += F0[i][j] * F1[j][k] * F2[k][i] * sig[t][i][j][k];
        tot += wts[t] * abs(s);
    }
    return tot;
}

static void coeffs(int F0[4][4], int F1[4][4], int c[NT][16]) {
    for (int t = 0; t < NT; t++)
        for (int k = 0; k < 4; k++)
            for (int i = 0; i < 4; i++) {
                int s = 0;
                for (int j = 0; j < 4; j++) s += F0[i][j] * F1[j][k] * sig[t][i][j][k];
                c[t][k * 4 + i] = wts[t] * s;
            }
}

/* max over the 32 sign patterns (s_0 = +1) in Gray-code order; returns pattern bits in *pat */
static int pattern_max(int c[NT][16], int *pat) {
    int v[16];
    for (int x = 0; x < 16; x++) {
        int s = 0;
        for (int t = 0; t < NT; t++) s += c[t][x];
        v[x] = s;
    }
    int best = -1, bestp = 0, g = 0;
    for (int step = 0; step < 32; step++) {
        if (step > 0) {
            int bit = __builtin_ctz(step); /* flip s_{bit+1} */
            int t = bit + 1;
            int now_neg = (g >> bit) & 1;
            int d = now_neg ? 2 : -2; /* currently +: subtract 2c; currently -: add 2c */
            for (int x = 0; x < 16; x++) v[x] += d * c[t][x];
            g ^= 1 << bit;
        }
        int s = 0;
        for (int x = 0; x < 16; x++) s += v[x] < 0 ? -v[x] : v[x];
        if (s > best) { best = s; bestp = g; }
    }
    *pat = bestp;
    return best;
}

static void f2_from(int c[NT][16], int pat, int F2[4][4]) {
    for (int x = 0; x < 16; x++) {
        int s = c[0][x];
        for (int t = 1; t < NT; t++) s += ((pat >> (t - 1)) & 1) ? -c[t][x] : c[t][x];
        F2[x / 4][x % 4] = s >= 0 ? 1 : -1; /* x = k*4 + i  ->  F2[k][i] */
    }
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s WT HAAR F0_LO F0_HI [bruteforce_pairs]\n", argv[0]); return 2; }
    int wT = atoi(argv[1]), haar = atoi(argv[2]);
    uint32_t lo = (uint32_t)strtoul(argv[3], 0, 10), hi = (uint32_t)strtoul(argv[4], 0, 10);
    int nbf = argc > 5 ? atoi(argv[5]) : 0;
    build_terms(wT, haar);
    const int thr = 192;

    if (nbf > 0) { /* self-check: pattern max vs literal max over all 2^16 F2 */
        srand(20261028u);
        int agree = 0;
        for (int r = 0; r < nbf; r++) {
            int F0[4][4], F1[4][4], F2[4][4], c[NT][16], pat;
            decode((uint32_t)rand() & 0x7fffu, F0);
            decode((uint32_t)rand() & 0x7fffu, F1);
            coeffs(F0, F1, c);
            int pm = pattern_max(c, &pat);
            int bm = -1;
            for (uint32_t m = 0; m < 65536u; m++) {
                for (int x = 0; x < 16; x++) F2[x / 4][x % 4] = ((m >> x) & 1u) ? -1 : 1;
                int v = full_value(F0, F1, F2);
                if (v > bm) bm = v;
            }
            f2_from(c, pat, F2);
            agree += (pm == bm) && (full_value(F0, F1, F2) == pm);
        }
        printf("{\"bruteforce_pairs\": %d, \"agree\": %d, \"wT\": %d, \"haar\": %d}\n", nbf, agree, wT, haar);
        return agree == nbf ? 0 : 1;
    }

    static uint64_t hist[HMAX];
    uint64_t viol_pairs = 0, recheck_fail = 0;
    int best = -1, bF0 = 0, bF1 = 0, bpat = 0;
    for (uint32_t a = lo; a < hi; a++) {
        int F0[4][4];
        decode(a, F0);
        for (uint32_t b = 0; b < 32768u; b++) {
            int F1[4][4], c[NT][16], pat;
            decode(b, F1);
            coeffs(F0, F1, c);
            int m = pattern_max(c, &pat);
            hist[m]++;
            if (m > thr) viol_pairs++;
            if (m > best) {
                int F2[4][4];
                f2_from(c, pat, F2);
                if (full_value(F0, F1, F2) != m) recheck_fail++;
                best = m; bF0 = (int)a; bF1 = (int)b; bpat = pat;
            }
        }
    }
    int F0[4][4], F1[4][4], F2[4][4], c[NT][16];
    decode((uint32_t)bF0, F0);
    decode((uint32_t)bF1, F1);
    coeffs(F0, F1, c);
    f2_from(c, bpat, F2);
    int rv = full_value(F0, F1, F2);
    printf("{\"wT\": %d, \"haar\": %d, \"f0_lo\": %u, \"f0_hi\": %u, \"max_S\": %d, \"violating_pairs_gt192\": %llu, "
           "\"argmax_triple_sum\": %d, \"recheck_fail\": %llu, \"argmax\": [",
           wT, haar, lo, hi, best, (unsigned long long)viol_pairs, rv, (unsigned long long)recheck_fail);
    int (*Ms[3])[4] = {F0, F1, F2};
    for (int v = 0; v < 3; v++) {
        printf("%s[", v ? ", " : "");
        for (int i = 0; i < 4; i++) {
            printf("%s[", i ? ", " : "");
            for (int j = 0; j < 4; j++) printf("%s%d", j ? ", " : "", Ms[v][i][j]);
            printf("]");
        }
        printf("]");
    }
    printf("], \"hist\": {");
    int first = 1;
    for (int h = 0; h < HMAX; h++)
        if (hist[h]) { printf("%s\"%d\": %llu", first ? "" : ", ", h, (unsigned long long)hist[h]); first = 0; }
    printf("}}\n");
    return 0;
}
