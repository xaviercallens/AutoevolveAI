/*
 * Independent checker 2 (C, integer arithmetic) for shifted lonely runner
 * certificates.  Different criterion from checker 1 (no sweep, no global
 * common denominator):
 *
 *   The union of finitely many open arcs of length < 1 on R/Z is the whole
 *   circle  <=>  every right endpoint of every arc lies strictly inside some
 *   (other) arc.   (A component of the union that is not the whole circle has
 *   a right boundary point, which is the right endpoint of one of the arcs and
 *   is not covered.)
 *
 * Arc of runner i, loop k:  { t : || a_i/D + v_i t || < p/q }.
 * Right endpoint: e = (k*D*q - a_i*q + p*D) / (v_i*D*q),  k = 0..v_i-1.
 * Runner j at time e:  x = a_j/D + v_j e = X / Q  with
 *    Q = v_i*D*q,   X = a_j*v_i*q + v_j*(k*D*q - a_i*q + p*D).
 * Strictly inside arc of j  <=>  q * min(X mod Q, Q - X mod Q) < p * Q.
 * All products are done in __int128 with explicit overflow guards.
 *
 * Input: the certificate JSON; this program extracts the integer fields
 * "n", "D", "delta_num", "delta_den" and the arrays "v", "a" by its own
 * minimal scanner.  Output: one line "COVERED" or "NOT_COVERED ..." and exit
 * status 0 (covered), 1 (not covered), 2 (malformed input).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

typedef __int128 i128;
#define MAXN 4096

static char buf[1 << 22];

static const char *find_key(const char *key) {
    char pat[64];
    snprintf(pat, sizeof pat, "\"%s\"", key);
    const char *p = strstr(buf, pat);
    if (!p) return NULL;
    p += strlen(pat);
    while (*p && (isspace((unsigned char)*p) || *p == ':')) p++;
    return p;
}

static int read_int(const char *key, long long *out) {
    const char *p = find_key(key);
    if (!p) return 0;
    if (*p == '"') p++;
    char *end;
    *out = strtoll(p, &end, 10);
    return end != p;
}

static int read_array(const char *key, long long *arr, int maxn) {
    const char *p = find_key(key);
    if (!p || *p != '[') return -1;
    p++;
    int cnt = 0;
    for (;;) {
        while (*p && (isspace((unsigned char)*p) || *p == ',')) p++;
        if (*p == ']') break;
        if (*p == '"') p++;
        char *end;
        long long x = strtoll(p, &end, 10);
        if (end == p || cnt >= maxn) return -1;
        arr[cnt++] = x;
        p = end;
        if (*p == '"') p++;
    }
    return cnt;
}

static long long V[MAXN], A[MAXN];

static i128 mod_pos(i128 x, i128 m) {
    i128 r = x % m;
    if (r < 0) r += m;
    return r;
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "usage: check_cover cert.json\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("open"); return 2; }
    size_t len = fread(buf, 1, sizeof buf - 1, f);
    fclose(f);
    buf[len] = 0;
    long long n, D, p, q;
    if (!read_int("n", &n) || !read_int("D", &D) || !read_int("delta_num", &p) || !read_int("delta_den", &q)) {
        printf("MALFORMED header\n"); return 2;
    }
    int nv = read_array("v", V, MAXN), na = read_array("a", A, MAXN);
    if (nv != n || na != n || n < 1) { printf("MALFORMED arrays nv=%d na=%d n=%lld\n", nv, na, n); return 2; }
    if (D <= 0 || p <= 0 || q <= 0 || 2 * p >= q) { printf("MALFORMED D/delta\n"); return 2; }
    for (int i = 0; i < n; i++) {
        if (V[i] <= 0 || V[i] > 1000000) { printf("MALFORMED velocity\n"); return 2; }
        for (int j = 0; j < i; j++) if (V[i] == V[j]) { printf("MALFORMED repeated velocity %lld\n", V[i]); return 2; }
        if (A[i] < 0 || A[i] >= D) { A[i] = (long long)mod_pos(A[i], D); }
    }
    /* overflow guard: |X| <= D*v_i*q + v_j*(v_i*D*q + D*q + p*D) < 4*vmax^2*D*q ; require < 2^120 */
    long long vmax = 0;
    for (int i = 0; i < n; i++) if (V[i] > vmax) vmax = V[i];
    long double bound = 4.0L * vmax * vmax * (long double)D * (long double)q * (long double)(p + 1);
    if (bound > 1.0e35L) { printf("MALFORMED magnitude too large\n"); return 2; }

    long long checked = 0;
    for (int i = 0; i < n; i++) {
        i128 Q = (i128)V[i] * D * q;
        for (long long k = 0; k < V[i]; k++) {
            i128 num_e = (i128)k * D * q - (i128)A[i] * q + (i128)p * D; /* e = num_e / Q */
            int inside = 0;
            for (int j = 0; j < n && !inside; j++) {
                if (j == i) continue; /* own arc: endpoint is on the boundary, never strictly inside */
                i128 X = (i128)A[j] * V[i] * q + (i128)V[j] * num_e;
                i128 r = mod_pos(X, Q);
                i128 d = r < Q - r ? r : Q - r;
                if ((i128)q * d < (i128)p * Q) inside = 1;
            }
            checked++;
            if (!inside) {
                printf("NOT_COVERED right endpoint of runner index %d (v=%lld) loop k=%lld is uncovered\n", i, V[i], k);
                return 1;
            }
        }
    }
    printf("COVERED n=%lld endpoints_checked=%lld\n", n, checked);
    return 0;
}
