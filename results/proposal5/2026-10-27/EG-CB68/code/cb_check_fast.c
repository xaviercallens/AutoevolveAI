/* cb_check_fast.c -- second streaming witness checker for EG-CB68 (C port of the rules in cb_check.py,
 * written for large streams that the Python checker cannot read in the time box).
 * It searches for nothing: it re-derives the proposal schedule (candidate list, filtered and sorted), checks every
 * structural rejection directly, checks every C6/C8/C16 witness as a simple path of length 4/6/14 in the current
 * Levi graph between two distinct introduced members of {p,q,r}, recurses into expansions, recomputes all
 * counters and compares them with the END line. Exit 0 = accepted, 1 = rejected.
 * usage: cb_check_fast [--allow-completions] < STREAM
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned long long u64;
static int cap, orbit, f6 = 0, f8 = 1, f16 = 1, allow = 0;
static int B[128][3], nb = 0, n = 0;
static int inc[64][4], ninc[64];
static u64 cnt[7]; /* states attempted structural c6 c8 c16 completions */
static char line[4096];
static long long lineno = 0;

static void die(const char *m) {
    printf("{\"accepted\":false,\"error\":\"%s\",\"line\":%lld}\n", m, lineno);
    exit(1);
}
static int rd(void) { /* returns 1 if a line was read */
    if (!fgets(line, sizeof line, stdin)) return 0;
    lineno++;
    return 1;
}
static void ins(int a, int b, int c) {
    B[nb][0] = a; B[nb][1] = b; B[nb][2] = c;
    int t[3] = {a, b, c};
    for (int i = 0; i < 3; i++) { if (ninc[t[i]] >= 3) die("degree overflow"); inc[t[i]][ninc[t[i]]++] = nb; if (t[i] + 1 > n) n = t[i] + 1; }
    nb++;
}
static void del(int a, int b, int c, int oldn) {
    nb--;
    if (B[nb][0] != a || B[nb][1] != b || B[nb][2] != c) die("internal remove");
    int t[3] = {a, b, c};
    for (int i = 0; i < 3; i++) ninc[t[i]]--;
    n = oldn;
}
static int share(int x, int y) {
    for (int i = 0; i < ninc[x]; i++) { int k = inc[x][i]; if (B[k][0] == y || B[k][1] == y || B[k][2] == y) return 1; }
    return 0;
}
static int inblk(int x, int k) { return k >= 0 && k < nb && (B[k][0] == x || B[k][1] == x || B[k][2] == x); }
static int adj(int u, int v) {
    if ((u < 64) == (v < 64)) return 0;
    if (u < 64) return inblk(u, v - 64);
    return inblk(v, u - 64);
}
typedef struct { int q, r; } pr_t;
static int cmp(const void *a, const void *b) {
    const pr_t *x = a, *y = b;
    if (x->q != y->q) return x->q - y->q;
    return x->r - y->r;
}
static void state(void);
static void state(void) {
    cnt[0]++;
    int p = -1;
    for (int x = 0; x < n; x++) if (ninc[x] < 3) { p = x; break; }
    if (p < 0) {
        if (!rd() || strcmp(line, "C\n")) die("complete state not reported as C");
        cnt[6]++;
        if (!allow) die("completion found");
        return;
    }
    int bq = -1, br = -1;
    for (int i = 0; i < ninc[p]; i++) {
        int k = inc[p][i];
        if (B[k][0] == p && (B[k][1] > bq || (B[k][1] == bq && B[k][2] > br))) { bq = B[k][1]; br = B[k][2]; }
    }
    int el[64], ne = 0;
    for (int x = p + 1; x < n; x++) if (ninc[x] < 3 && !share(p, x)) el[ne++] = x;
    pr_t c[2200]; int nc = 0;
    int f = n;
    for (int i = 0; i < ne; i++) {
        for (int j = i + 1; j < ne; j++) { c[nc].q = el[i]; c[nc].r = el[j]; nc++; }
        c[nc].q = el[i]; c[nc].r = f; nc++;
    }
    c[nc].q = f; c[nc].r = f + 1; nc++;
    pr_t d[2200]; int nd = 0;
    for (int i = 0; i < nc; i++) {
        int gt = c[i].q > bq || (c[i].q == bq && c[i].r > br);
        if (gt && c[i].r + 1 <= cap) d[nd++] = c[i];
    }
    qsort(d, nd, sizeof(pr_t), cmp);
    for (int i = 0; i < nd; i++) {
        int q = d[i].q, r = d[i].r;
        if (!rd()) die("truncated");
        cnt[1]++;
        char tag; int a1, a2, off;
        if (sscanf(line, "%c %d %d%n", &tag, &a1, &a2, &off) < 3) die("malformed");
        if (a1 != q || a2 != r) die("schedule mismatch");
        if (tag == 'S') {
            if (!(q < n && r < n && share(q, r))) die("bad structural");
            cnt[2]++;
        } else if (tag == '6' || tag == '8' || tag == 'G') {
            int L = tag == '6' ? 4 : tag == '8' ? 6 : 14;
            if ((tag == '6' && !f6) || (tag == '8' && !f8) || (tag == 'G' && !f16)) die("disabled filter");
            int path[32], np = 0, used = 0, v;
            char *s = line + off;
            while (np < 32 && sscanf(s, "%d%n", &v, &used) == 1) { path[np++] = v; s += used; }
            if (np != L + 1) die("witness length");
            for (int a = 0; a < np; a++) {
                if (path[a] < 0 || path[a] >= 128) die("witness vertex range");
                for (int b2 = a + 1; b2 < np; b2++) if (path[a] == path[b2]) die("witness not simple");
            }
            int e0 = path[0], e1 = path[L];
            int ok0 = (e0 == p || e0 == q || e0 == r), ok1 = (e1 == p || e1 == q || e1 == r);
            if (!ok0 || !ok1 || e0 == e1 || e0 >= n || e1 >= n) die("witness endpoints");
            for (int a = 0; a < L; a++) if (!adj(path[a], path[a + 1])) die("witness edge");
            cnt[tag == '6' ? 3 : tag == '8' ? 4 : 5]++;
        } else if (tag == 'E') {
            int on = n;
            ins(p, q, r);
            state();
            del(p, q, r, on);
            if (!rd() || strcmp(line, "U\n")) die("missing U");
        } else die("unexpected record");
    }
}
int main(int argc, char **argv) {
    for (int i = 1; i < argc; i++) if (!strcmp(argv[i], "--allow-completions")) allow = 1;
    if (!rd() || line[0] != 'R') die("header");
    char fl[3][16] = {"", "", ""};
    int k = sscanf(line, "R %d %d %15s %15s %15s", &cap, &orbit, fl[0], fl[1], fl[2]);
    if (k < 2) die("header");
    for (int i = 0; i < k - 2; i++) {
        if (!strcmp(fl[i], "c6")) f6 = 1; else if (!strcmp(fl[i], "no8")) f8 = 0; else if (!strcmp(fl[i], "no16")) f16 = 0; else die("flag");
    }
    if (orbit == 0) ins(0, 1, 2);
    else if (orbit == 1 || orbit == 2) { ins(0, 1, 3); ins(1, 2, 4); ins(0, 2, 5); if (orbit == 1) ins(0, 4, 6); else ins(0, 6, 7); }
    else die("orbit");
    state();
    if (!rd()) die("missing END");
    u64 cl[7];
    if (sscanf(line, "END %llu %llu %llu %llu %llu %llu %llu", &cl[0], &cl[1], &cl[2], &cl[3], &cl[4], &cl[5], &cl[6]) != 7) die("END");
    for (int i = 0; i < 7; i++) if (cl[i] != cnt[i]) die("counter mismatch");
    if (rd()) die("trailing data");
    printf("{\"accepted\":true,\"cap\":%d,\"orbit\":%d,\"states\":%llu,\"attempted\":%llu,\"structural\":%llu,\"c6\":%llu,\"c8\":%llu,\"c16\":%llu,\"completions\":%llu}\n",
           cap, orbit, cnt[0], cnt[1], cnt[2], cnt[3], cnt[4], cnt[5], cnt[6]);
    return 0;
}
