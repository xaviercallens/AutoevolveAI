/*
 * fiber_check.c -- LR-IND second program: direct exhaustive check of the conclusion of
 * Sungkawichai--Trakulthongchai Proposition 4.4 at a given prime p (no use of the polynomial method):
 *
 *   every u in (Z_{Lp})^k with u_i = i (mod p) for i = 1..k is (k,p,L)-proper,
 *
 * where L is a prime different from p.  For L = k+1 = 11 this is exactly Prop. 4.4 at p; for a prime L with
 * (k+1) not dividing L*p, Remark 3.2 forces (1,...,k) itself to be improper (negative control).
 *
 * CRT: Z_{Lp} = Z_L x Z_p.  u is fixed by w = u mod L in (Z_L)^k.  Multiplying w by c in Z_L^* and the
 * time a = (s, r) by (s c^{-1}, r) leaves every residue a*u_i mod Lp unchanged, and does not change which
 * coordinates are 0 mod L; so properness is invariant under w -> c w and we enumerate w = 0 plus all w whose
 * first nonzero coordinate is 1.
 *
 * Properness (Def. 2.1): gcd test: some i with gcd(L, u_j : j != i) > 1, i.e. at most one u_j is nonzero
 * mod L (L prime); time test: some a in [1, Lp/2] with (k+1)*min(r, N-r) >= N, r = a*u_i mod N, N = Lp.
 *
 * Usage: fiber_check K P L     -> one JSON object on stdout.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

typedef uint64_t u64;
#define MAXK 16
#define MAXW 160

static int K, P, L, W;
static long N;
static u64 *G;           /* G[(i*L + w)*W ..] good-time bitset of coordinate i with residue w mod L */
static long long leaves = 0, improper = 0, gcd_saved = 0;
static int first_bad[MAXK], have_bad = 0;

static int is_prime(long x) { if (x < 2) return 0; for (long q = 2; q * q <= x; q++) if (x % q == 0) return 0; return 1; }

static long crt(long a_mod_p, long b) {
    /* x mod p = a, x mod L = b */
    for (long t = 0; t < L; t++) { long x = a_mod_p + t * P; if (x % L == b) return x; }
    return -1;
}

static void rec(int i, int nonzero_seen, int nnz, int *w, const u64 *acc) {
    if (i == K) {
        leaves++;
        int empty = 1;
        for (int q = 0; q < W; q++) if (acc[q]) { empty = 0; break; }
        if (!empty) return;
        if (nnz <= 1) { gcd_saved++; return; }
        improper++;
        if (!have_bad) { memcpy(first_bad, w, K * sizeof(int)); have_bad = 1; }
        return;
    }
    u64 nacc[MAXW];
    int lo = 0, hi = L - 1;
    if (!nonzero_seen) hi = 1; /* first nonzero coordinate normalised to 1 */
    for (int v = lo; v <= hi; v++) {
        const u64 *g = G + ((size_t)i * L + v) * W;
        for (int q = 0; q < W; q++) nacc[q] = acc[q] & g[q];
        w[i] = v;
        rec(i + 1, nonzero_seen || v != 0, nnz + (v != 0), w, nacc);
    }
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: fiber_check K P L\n"); return 1; }
    K = atoi(argv[1]); P = atoi(argv[2]); L = atoi(argv[3]);
    if (!is_prime(P) || !is_prime(L) || P == L || K < 2 || K > MAXK || K >= P) { fprintf(stderr, "bad args\n"); return 1; }
    N = (long)L * P;
    long half = N / 2;
    W = (int)((half + 64) / 64);
    if (W > MAXW) { fprintf(stderr, "too large\n"); return 1; }
    struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
    G = calloc((size_t)K * L * W, sizeof(u64));
    for (int i = 0; i < K; i++)
        for (int v = 0; v < L; v++) {
            long u = crt((i + 1) % P, v);
            for (long a = 1; a <= half; a++) {
                long r = a * u % N; long d = r < N - r ? r : N - r;
                if ((long)(K + 1) * d >= N) G[((size_t)i * L + v) * W + (a >> 6)] |= 1ULL << (a & 63);
            }
        }
    u64 all[MAXW];
    memset(all, 0, sizeof all);
    for (long a = 1; a <= half; a++) all[a >> 6] |= 1ULL << (a & 63);
    int w[MAXK];
    rec(0, 0, 0, w, all);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf("{\"k\":%d,\"p\":%d,\"L\":%d,\"leaves\":%lld,\"gcd_proper\":%lld,\"improper\":%lld,\"first_improper_w\":",
           K, P, L, leaves, gcd_saved, improper);
    if (have_bad) { putchar('['); for (int i = 0; i < K; i++) printf("%s%d", i ? "," : "", first_bad[i]); putchar(']'); }
    else printf("null");
    printf(",\"seconds\":%.3f}\n", (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
    return 0;
}
