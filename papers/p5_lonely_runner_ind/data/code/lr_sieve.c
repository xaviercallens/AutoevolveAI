/*
 * lr_sieve.c -- independent implementation (LR-IND, Proposal 5) of the modular sieve used by
 * Sungkawichai--Trakulthongchai (arXiv 2604.23906 v2) to show J(k,p) = {} for LRC(k).
 *
 * Written ONLY from the paper's definitions (Def. 2.1, 2.3, Prop. 3.1, Sec. 5.1, 5.2); the authors'
 * repository was not read.  All arithmetic is exact integer arithmetic.
 *
 * Definitions used (paper notation):
 *   N = l*p.  A tuple u in (Z_N)^k with no coordinate = 0 mod p is (k,p,l)-PROPER iff
 *     (gcd)  there is i with gcd(l, u_j : j != i) > 1, or
 *     (time) there is a in Z_N with || a*u_i / N || >= 1/(k+1) for all i,
 *            i.e. (k+1) * min(r, N-r) >= N where r = a*u_i mod N.
 *   I(k,p,l) = improper tuples.
 *   Lifting by c: S' = { u' in pi^{-1}_{cN -> N}(S) : u' is (k,p,cl)-improper }.
 *   Projection:   S' = pi_{N -> p}(S).
 *
 * Phase 1 enumerates one representative per equivalence class (permutation, sign flip, multiplication
 * by a unit of Z_p) of I(k,p,1).  Representatives are multisets over [1,(p-1)/2] containing 1 that are
 * lexicographically minimal among their normalisations x^{-1}*T (x in T), folded by v -> min(v,p-v).
 *
 * Enumeration: a tuple is improper at l = 1 iff its support set U kills every time a in [1,H]
 * (H = (p-1)/2; times a and p-a are equivalent).  We enumerate supports U containing 1 by a
 * "hitting set" branch: pick a surviving time a, branch on which element of U kills a, with
 * exclusion of earlier siblings.  Each support U of size <= k is reached at exactly one leaf
 * (the first node where all times are killed); supersets/multiplicities are expanded at that leaf.
 *
 * Usage:  lr_sieve K P PLAN [MUT]
 *   PLAN: comma list of steps, each "c" (lift by integer c >= 2) or "/" (project back to Z_p).
 *         Example k=10: 2,2,2,/
 *   MUT : 0 = correct rule; 1 = literal mutation (bad iff ||x|| <= 1/(k+1) instead of <);
 *         2 = rounding mutation (good iff d >= floor(N/(k+1)) instead of ceil).
 * Output: one JSON object on stdout.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

typedef uint64_t u64;
#define MAXK 16
#define MAXBW 128 /* bitset words: up to 8192 bits */

static int K, P, H, MUT;

static int is_good(long d, long N) {
    /* d = min(r, N-r) in [0, N/2]; returns 1 iff ||r/N|| >= 1/(K+1) (MUT==0) */
    if (MUT == 0) return (long)(K + 1) * d >= N;
    if (MUT == 1) return (long)(K + 1) * d > N;
    return d >= N / (K + 1);
}

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

/* ---------------- tuple store ---------------- */
typedef struct {
    uint16_t *d;
    size_t n, cap;
} Store;

static void st_push(Store *s, const uint16_t *t) {
    if (s->n == s->cap) {
        s->cap = s->cap ? 2 * s->cap : 1024;
        s->d = realloc(s->d, s->cap * K * sizeof(uint16_t));
        if (!s->d) { fprintf(stderr, "out of memory\n"); exit(2); }
    }
    memcpy(s->d + s->n * K, t, K * sizeof(uint16_t));
    s->n++;
}

/* ---------------- modular helpers ---------------- */
static int inv_mod(int x, int m) {
    long a = x % m, b = m, u = 1, v = 0;
    if (a < 0) a += m;
    while (a) {
        long q = b / a, t = b - q * a; b = a; a = t;
        t = v - q * u; v = u; u = t;
    }
    if (b != 1) { fprintf(stderr, "no inverse %d mod %d\n", x, m); exit(3); }
    v %= m; if (v < 0) v += m;
    return (int)v;
}

static int cmp_u16(const void *a, const void *b) {
    return (int)*(const uint16_t *)a - (int)*(const uint16_t *)b;
}

static int fold(int v) { v %= P; if (v < 0) v += P; return v <= P - v ? v : P - v; }

/* canonical form of a multiset T (values in Z_p \ {0}) into out (sorted). */
static void canonical_n(const uint16_t *T, int n, uint16_t *out);
static void canonical(const uint16_t *T, uint16_t *out) { canonical_n(T, K, out); }
static void canonical_n(const uint16_t *T, int n, uint16_t *out) {
    uint16_t cur[MAXK], best[MAXK];
    int have = 0;
    for (int i = 0; i < n; i++) {
        int x = T[i] % P;
        if (i > 0 && (T[i] % P) == (T[i - 1] % P)) continue; /* T need not be sorted; dup scaling harmless */
        int iv = inv_mod(x, P);
        for (int j = 0; j < n; j++) cur[j] = (uint16_t)fold((long)iv * (T[j] % P) % P);
        qsort(cur, n, sizeof(uint16_t), cmp_u16);
        int less = 0;
        if (have) {
            for (int j = 0; j < n; j++) { if (cur[j] != best[j]) { less = cur[j] < best[j]; break; } }
        }
        if (!have || less) { memcpy(best, cur, n * sizeof(uint16_t)); have = 1; }
    }
    memcpy(out, best, n * sizeof(uint16_t));
}

static int lexcmp(const uint16_t *a, const uint16_t *b) {
    for (int j = 0; j < K; j++) if (a[j] != b[j]) return a[j] < b[j] ? -1 : 1;
    return 0;
}

/* ---------------- phase 1 ---------------- */
static int TW, SW;              /* words for time bitsets (a in [0,H]) and speed bitsets (v in [0,H]) */
static u64 *G1;                 /* G1[v*TW ..] good times of speed v */
static u64 *KA;                 /* KA[a*SW ..] speeds killing time a */
static u64 *B1;                 /* B1[v*TW ..] bad (killed) times of speed v, within [1,H] */
static int USE_BOUND = 1;
static int CANON_PRUNE = 1;     /* restrict to set-canonical supports, with the pairwise second-element test */
static int V2;                  /* current second-smallest element (CANON_PRUNE mode) */
static uint16_t *MT;            /* MT[x*(H+1)+y] = min(fold(y/x), fold(x/y)) */
static u64 *CMP;                /* CMP[x*SW ..] = { y : MT[x][y] >= V2 } */
static long long small_supports = 0, noncanon_sets = 0;       /* capacity bound: prune if the r best remaining speeds cannot cover A */
static long long pruned_bound = 0;
static Store S1;
static long long nodes1 = 0, leaves_full = 0, leaves_small = 0, small_tuples = 0, noncanon = 0;
static long long improper_reps_total = 0; /* all improper normalised multisets found (before canon filter) */

static inline int bs_empty(const u64 *a, int w) { for (int i = 0; i < w; i++) if (a[i]) return 0; return 1; }

static void emit_multiset(uint16_t *T) {
    uint16_t c[MAXK], s[MAXK];
    memcpy(s, T, K * sizeof(uint16_t));
    qsort(s, K, sizeof(uint16_t), cmp_u16);
    improper_reps_total++;
    canonical(s, c);
    if (lexcmp(c, s) == 0) st_push(&S1, s); else noncanon++;
}

static int set_is_canonical(const uint16_t *U, int m) {
    uint16_t a[MAXK], c[MAXK];
    memcpy(a, U, m * sizeof(uint16_t));
    qsort(a, m, sizeof(uint16_t), cmp_u16);
    canonical_n(a, m, c);
    for (int j = 0; j < m; j++) if (a[j] != c[j]) return 0;
    return 1;
}

static void emit_plain(uint16_t *T) {
    uint16_t s2[MAXK];
    memcpy(s2, T, K * sizeof(uint16_t));
    qsort(s2, K, sizeof(uint16_t), cmp_u16);
    improper_reps_total++;
    st_push(&S1, s2);
}

/* expand support U (size m, sorted not required) into all multisets of size K with support exactly U */
static void expand_mult(uint16_t *U, int m, uint16_t *T, int pos, int idx) {
    /* T[0..m-1] = U already; fill T[m..K-1] with elements of U in nondecreasing index order */
    if (pos == K) { if (CANON_PRUNE) emit_plain(T); else emit_multiset(T); return; }
    for (int j = idx; j < m; j++) { T[pos] = U[j]; expand_mult(U, m, T, pos + 1, j); }
}

static void expand_supersets(uint16_t *W, int m, const u64 *allowed, int from) {
    /* emit all supports W u X, X subset of allowed, |W u X| <= K; elements of X chosen increasing */
    uint16_t T[MAXK];
    memcpy(T, W, m * sizeof(uint16_t));
    if (!CANON_PRUNE || set_is_canonical(W, m)) {
        if (CANON_PRUNE && m < K) small_supports++;
        expand_mult(W, m, T, m, 0);
    } else noncanon_sets++;
    if (m == K) return;
    u64 al[MAXBW];
    for (int v = from; v <= H; v++) {
        if (allowed[v >> 6] >> (v & 63) & 1) {
            W[m] = (uint16_t)v;
            if (CANON_PRUNE) {
                const u64 *c = CMP + (size_t)v * SW;
                for (int q = 0; q < SW; q++) al[q] = allowed[q] & c[q];
                expand_supersets(W, m + 1, al, v + 1);
            } else expand_supersets(W, m + 1, allowed, v + 1);
        }
    }
}

static void dfs1(uint16_t *W, int m, const u64 *A, const u64 *allowed) {
    nodes1++;
    if (bs_empty(A, TW)) {
        if (m == K) {
            leaves_full++;
            if (!CANON_PRUNE) emit_multiset(W);
            else if (set_is_canonical(W, m)) emit_plain(W);
            else noncanon_sets++;
        }
        else {
            leaves_small++;
            long long before = improper_reps_total;
            uint16_t Wc[MAXK]; memcpy(Wc, W, m * sizeof(uint16_t));
            expand_supersets(Wc, m, allowed, 2);
            small_tuples += improper_reps_total - before;
        }
        return;
    }
    if (m == K) return;
    if (USE_BOUND) {
        /* Sound pruning: any completion adds at most r = K-m further distinct speeds from 'allowed';
           together they must kill every time in A, so sum of the r largest |A & B(v)| must be >= |A|. */
        int r = K - m, na = 0, top[MAXK];
        for (int w = 0; w < TW; w++) na += __builtin_popcountll(A[w]);
        for (int i = 0; i < r; i++) top[i] = 0;
        for (int s = 0; s < SW; s++) {
            u64 x = allowed[s];
            while (x) {
                int v = s * 64 + __builtin_ctzll(x); x &= x - 1;
                const u64 *b = B1 + (size_t)v * TW;
                int c = 0;
                for (int w = 0; w < TW; w++) c += __builtin_popcountll(A[w] & b[w]);
                if (c > top[r - 1]) {
                    int i = r - 1;
                    while (i > 0 && top[i - 1] < c) { top[i] = top[i - 1]; i--; }
                    top[i] = c;
                }
            }
        }
        int sum = 0;
        for (int i = 0; i < r; i++) sum += top[i];
        if (sum < na) { pruned_bound++; return; }
    }
    /* choose surviving time with fewest available killers */
    int best = -1, bc = 1 << 30;
    u64 tmp[MAXBW];
    for (int w = 0; w < TW; w++) {
        u64 x = A[w];
        while (x) {
            int a = w * 64 + __builtin_ctzll(x); x &= x - 1;
            const u64 *ka = KA + (size_t)a * SW;
            int c = 0;
            for (int s = 0; s < SW; s++) c += __builtin_popcountll(ka[s] & allowed[s]);
            if (c < bc) { bc = c; best = a; if (c == 0) return; }
        }
    }
    u64 allow[MAXBW], A2[MAXBW];
    memcpy(allow, allowed, SW * sizeof(u64));
    const u64 *ka = KA + (size_t)best * SW;
    for (int s = 0; s < SW; s++) tmp[s] = ka[s] & allowed[s];
    for (int s = 0; s < SW; s++) {
        u64 x = tmp[s];
        while (x) {
            int v = s * 64 + __builtin_ctzll(x); x &= x - 1;
            allow[v >> 6] &= ~(1ULL << (v & 63));
            const u64 *g = G1 + (size_t)v * TW;
            for (int w = 0; w < TW; w++) A2[w] = A[w] & g[w];
            W[m] = (uint16_t)v;
            if (CANON_PRUNE) {
                u64 al2[MAXBW];
                const u64 *c = CMP + (size_t)v * SW;
                for (int q = 0; q < SW; q++) al2[q] = allow[q] & c[q];
                dfs1(W, m + 1, A2, al2);
            } else dfs1(W, m + 1, A2, allow);
        }
    }
}

static void phase1(void) {
    H = (P - 1) / 2;
    TW = (H + 64) / 64; SW = TW;
    if (TW > MAXBW) { fprintf(stderr, "p too large\n"); exit(4); }
    G1 = calloc((size_t)(H + 1) * TW, sizeof(u64));
    KA = calloc((size_t)(H + 1) * SW, sizeof(u64));
    B1 = calloc((size_t)(H + 1) * TW, sizeof(u64));
    for (int v = 1; v <= H; v++)
        for (int a = 1; a <= H; a++) {
            long r = (long)a * v % P; long d = r < P - r ? r : P - r;
            if (is_good(d, P)) G1[(size_t)v * TW + (a >> 6)] |= 1ULL << (a & 63);
            else { KA[(size_t)a * SW + (v >> 6)] |= 1ULL << (v & 63); B1[(size_t)v * TW + (a >> 6)] |= 1ULL << (a & 63); }
        }
    uint16_t W[MAXK]; W[0] = 1;
    if (!CANON_PRUNE) {
        u64 allowed[MAXBW] = {0};
        for (int v = 2; v <= H; v++) allowed[v >> 6] |= 1ULL << (v & 63);
        dfs1(W, 1, G1 + TW, allowed);
        return;
    }
    /* CANON_PRUNE: a set-canonical support U = {1 = u_1 < u_2 < ...} (distinct, in [1,H]) satisfies, for all
       distinct x, y in U, fold(y/x) >= u_2: fold(x^{-1} U) contains 1 and the fold(y/x), y != x, and is
       lexicographically >= U, so its second-smallest element is >= u_2.  Enumerate u_2 = V2 explicitly. */
    MT = malloc((size_t)(H + 1) * (H + 1) * sizeof(uint16_t));
    CMP = malloc((size_t)(H + 1) * SW * sizeof(u64));
    for (int x = 1; x <= H; x++) {
        int ix = inv_mod(x, P);
        for (int y = 1; y <= H; y++) {
            int iy = inv_mod(y, P);
            int a = fold((long)y * ix % P), b = fold((long)x * iy % P);
            MT[(size_t)x * (H + 1) + y] = (uint16_t)(a < b ? a : b);
        }
    }
    for (V2 = 2; V2 <= H; V2++) {
        memset(CMP, 0, (size_t)(H + 1) * SW * sizeof(u64));
        for (int x = 1; x <= H; x++)
            for (int y = 1; y <= H; y++)
                if (MT[(size_t)x * (H + 1) + y] >= V2) CMP[(size_t)x * SW + (y >> 6)] |= 1ULL << (y & 63);
        /* need V2 compatible with 1 */
        if (MT[(size_t)1 * (H + 1) + V2] < V2) continue;
        u64 allowed[MAXBW] = {0}, A[MAXBW];
        for (int v = V2 + 1; v <= H; v++) allowed[v >> 6] |= 1ULL << (v & 63);
        for (int q = 0; q < SW; q++) allowed[q] &= CMP[(size_t)1 * SW + q] & CMP[(size_t)V2 * SW + q];
        for (int w = 0; w < TW; w++) A[w] = G1[TW + w] & G1[(size_t)V2 * TW + w];
        W[1] = (uint16_t)V2;
        dfs1(W, 2, A, allowed);
    }
}

/* ---------------- lifting ---------------- */
static int Lcur = 1; /* current level l: tuples live in Z_{Lcur*P} */
static int lpr[8], nlpr; /* prime factors of Lcur */

static void factor_level(void) {
    int x = Lcur; nlpr = 0;
    for (int q = 2; q * q <= x; q++) if (x % q == 0) { lpr[nlpr++] = q; while (x % q == 0) x /= q; }
    if (x > 1) lpr[nlpr++] = x;
}

static int gcd_proper(const uint16_t *u) {
    for (int t = 0; t < nlpr; t++) {
        int q = lpr[t], bad = 0;
        for (int i = 0; i < K; i++) if (u[i] % q) { if (++bad > 1) break; }
        if (bad <= 1) return 1;
    }
    return 0;
}

static u64 *GL; static int LW; static long NL;
static Store *outS; static long long lift_checked;

static void lift_rec(const uint16_t *u, int c, long N0, int i, uint16_t *cur, const u64 *acc) {
    if (i == K) {
        lift_checked++;
        if (!bs_empty(acc, LW)) return;
        if (gcd_proper(cur)) return;
        st_push(outS, cur);
        return;
    }
    u64 nacc[MAXBW];
    for (int j = 0; j < c; j++) {
        long val = u[i] + j * N0;
        cur[i] = (uint16_t)val;
        const u64 *g = GL + (size_t)val * LW;
        for (int w = 0; w < LW; w++) nacc[w] = acc[w] & g[w];
        lift_rec(u, c, N0, i + 1, cur, nacc);
    }
}

static void lift(Store *in, Store *out, int c) {
    long N0 = (long)Lcur * P;
    Lcur *= c; factor_level();
    NL = (long)Lcur * P;
    if (NL > 65535) { fprintf(stderr, "level too large\n"); exit(5); }
    long half = NL / 2;
    LW = (int)((half + 64) / 64);
    if (LW > MAXBW) { fprintf(stderr, "bitset too large\n"); exit(6); }
    GL = calloc((size_t)NL * LW, sizeof(u64));
    for (long v = 0; v < NL; v++)
        for (long a = 1; a <= half; a++) {
            long r = a * v % NL; long d = r < NL - r ? r : NL - r;
            if (is_good(d, NL)) GL[(size_t)v * LW + (a >> 6)] |= 1ULL << (a & 63);
        }
    u64 all[MAXBW];
    for (int w = 0; w < LW; w++) all[w] = 0;
    for (long a = 1; a <= half; a++) all[a >> 6] |= 1ULL << (a & 63);
    outS = out; lift_checked = 0;
    uint16_t cur[MAXK];
    for (size_t t = 0; t < in->n; t++) lift_rec(in->d + t * K, c, N0, 0, cur, all);
    free(GL);
}

static int cmp_tuple(const void *a, const void *b) { return lexcmp(a, b); }

static void project(Store *in, Store *out) {
    uint16_t s[MAXK], c[MAXK];
    for (size_t t = 0; t < in->n; t++) {
        for (int j = 0; j < K; j++) s[j] = (uint16_t)(in->d[t * K + j] % P);
        canonical(s, c);
        st_push(out, c);
    }
    qsort(out->d, out->n, K * sizeof(uint16_t), cmp_tuple);
    size_t w = 0;
    for (size_t t = 0; t < out->n; t++)
        if (w == 0 || lexcmp(out->d + t * K, out->d + (w - 1) * K) != 0) {
            memmove(out->d + w * K, out->d + t * K, K * sizeof(uint16_t)); w++;
        }
    out->n = w;
    Lcur = 1; factor_level();
}

/* number of distinct classes of pi_p(S) -- invariant independent of representative choice */
static size_t class_count(Store *in, u64 *hash_out) {
    Store tmp = {0};
    int saveL = Lcur;
    project(in, &tmp);
    Lcur = saveL; factor_level();
    u64 h = 1469598103934665603ULL;
    for (size_t t = 0; t < tmp.n * K; t++) { h ^= tmp.d[t]; h *= 1099511628211ULL; }
    *hash_out = h;
    size_t n = tmp.n; free(tmp.d);
    return n;
}

static void print_tuple(FILE *f, const uint16_t *t) {
    fputc('[', f);
    for (int j = 0; j < K; j++) fprintf(f, "%s%u", j ? "," : "", t[j]);
    fputc(']', f);
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: lr_sieve K P PLAN [MUT] [USE_BOUND] [CANON_PRUNE]\n"); return 1; }
    K = atoi(argv[1]); P = atoi(argv[2]);
    const char *plan = argv[3];
    MUT = argc > 4 ? atoi(argv[4]) : 0;
    if (argc > 5) USE_BOUND = atoi(argv[5]);
    if (argc > 6) CANON_PRUNE = atoi(argv[6]);
    if (K < 2 || K > MAXK) return 1;
    for (int q = 2; q * q <= P; q++) if (P % q == 0) { fprintf(stderr, "P not prime\n"); return 1; }
    double t0 = now();
    phase1();
    double t1 = now();
    printf("{\"k\":%d,\"p\":%d,\"plan\":\"%s\",\"mut\":%d,", K, P, plan, MUT);
    printf("\"phase1\":{\"nodes\":%lld,\"leaves_full\":%lld,\"leaves_small\":%lld,\"small_tuples\":%lld,"
           "\"improper_normalised\":%lld,\"noncanonical_dropped\":%lld,\"S1_classes\":%zu,\"use_bound\":%d,\"canon_prune\":%d,\"small_supports\":%lld,\"noncanonical_sets\":%lld,\"pruned_bound\":%lld,\"seconds\":%.3f},",
           nodes1, leaves_full, leaves_small, small_tuples, improper_reps_total, noncanon, S1.n, USE_BOUND, CANON_PRUNE, small_supports, noncanon_sets, pruned_bound, t1 - t0);
    Store cur = S1; Lcur = 1; factor_level();
    { u64 h1; size_t c1 = class_count(&S1, &h1);
      printf("\"S1\":{\"tuples\":%zu,\"classes\":%zu,\"class_hash\":\"%016llx\"},", S1.n, c1, (unsigned long long)h1); }
    printf("\"steps\":[");
    char planbuf[256]; strncpy(planbuf, plan, 255); planbuf[255] = 0;
    int first = 1;
    for (char *tok = strtok(planbuf, ","); tok; tok = strtok(NULL, ",")) {
        Store nxt = {0};
        double ta = now();
        long long checked = 0;
        if (tok[0] == '/') { project(&cur, &nxt); }
        else { int c = atoi(tok); lift(&cur, &nxt, c); checked = lift_checked; }
        u64 h; size_t cls = class_count(&nxt, &h);
        printf("%s{\"op\":\"%s\",\"level\":%d,\"checked\":%lld,\"size\":%zu,\"classes_mod_p\":%zu,\"class_hash\":\"%016llx\",\"seconds\":%.3f}",
               first ? "" : ",", tok, Lcur, checked, nxt.n, cls, (unsigned long long)h, now() - ta);
        first = 0;
        free(cur.d); cur = nxt;
    }
    printf("],");
    /* final survivors as classes mod p */
    Store fin = {0}; int saveL = Lcur;
    project(&cur, &fin); Lcur = saveL;
    uint16_t id[MAXK], idc[MAXK];
    for (int j = 0; j < K; j++) id[j] = (uint16_t)(j + 1);
    canonical(id, idc);
    int only_id = 1, has_id = 0;
    for (size_t t = 0; t < fin.n; t++) { if (lexcmp(fin.d + t * K, idc) == 0) has_id = 1; else only_id = 0; }
    printf("\"final_level\":%d,\"final_size\":%zu,\"final_classes\":%zu,\"identity_class\":", saveL, cur.n, fin.n);
    print_tuple(stdout, idc);
    printf(",\"identity_survives\":%s,\"only_identity\":%s,\"survivors\":[", has_id ? "true" : "false",
           (only_id && fin.n > 0) ? "true" : "false");
    for (size_t t = 0; t < fin.n && t < 50; t++) { if (t) putchar(','); print_tuple(stdout, fin.d + t * K); }
    printf("],\"total_seconds\":%.3f}\n", now() - t0);
    return 0;
}
