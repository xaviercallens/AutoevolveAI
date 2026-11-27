/* cb_search.c -- EG-CB68 (Proposal 5, lane W1-c).
 * Triangle-rooted restricted-growth search over linear symmetric v_3-configurations
 * that avoid Berge 4- and 8-cycles (Levi C8, C16), reimplemented from the description in
 * Tranquilli, arXiv 2608.02675 v1, Section 3.1 (no code from that paper's repository was read).
 *
 * usage: cb_search CAP ORBIT ORACLE [options]
 *   CAP     point cap (max number of introduced points)
 *   ORBIT   1 -> root block {0,4,6}; 2 -> root block {0,6,7}; 0 -> arbitrary root {0,1,2} only (no triangle assumed)
 *   ORACLE  A = DFS endpoint sets (cached per state); B = half-path joins (per pair, uncached)
 * options:
 *   -no8          disable the C8 filter (control)
 *   -no16         disable the C16 filter (control)
 *   -c6           also forbid Levi C6 (Berge triangles): girth >= 10 control
 *   -cert FILE    write the witness certificate stream to FILE
 *   -comp FILE    write every completion (block list) to FILE
 *   -split D K N  only explore subtrees whose index at depth D (number of expansions from the root
 *                 along the path, counted in preorder at that depth) is = K mod N; counters outside the
 *                 split are counted only above depth D (see README in RESULT.md)
 *   -maxsec S     abort (exit 3) after S seconds
 * Output: one JSON object on stdout.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXP 64
#define MAXB 64

typedef unsigned long long u64;

static int cap, orbit, oracleB = 0, use6 = 0, use8 = 1, use16 = 1;
static FILE *certf = NULL, *compf = NULL;
static int npts = 0, nblk = 0;
static int blk[MAXB][3];
static int ptb[MAXP][3];
static int pdeg[MAXP];
static u64 paired[MAXP];

/* counters */
static u64 c_states = 0, c_attempt = 0, c_struct = 0, c_c6 = 0, c_c8 = 0, c_c16 = 0, c_comp = 0;
static u64 c_struct_alt = 0; /* proposals that an "all old labels" enumeration would add as structural */
static u64 c_cap_block = 0;  /* fresh proposals suppressed by the cap */
static u64 depth_hist[MAXB + 1];
static u64 deepest = 0;
static u64 thash = 1469598103934665603ULL;
static int split_d = -1, split_k = 0, split_n = 1;
static u64 split_ctr[MAXB + 1];
static double maxsec = 0; static time_t t0;
static u64 tick = 0;

static void hmix(u64 x) {
    for (int i = 0; i < 8; i++) { thash ^= (x >> (8 * i)) & 0xff; thash *= 1099511628211ULL; }
}

/* ---------- Levi graph helpers ---------- */
/* vertex encoding: point x -> x ; block b -> 64 + b */

/* ---- oracle A: DFS endpoint sets ---- */
static u64 endset_acc;
static void dfsA(int v, int left, u64 vp, u64 vb) {
    if (v < 64) { /* point */
        if (left == 0) { endset_acc |= 1ULL << v; return; }
        for (int i = 0; i < pdeg[v]; i++) {
            int b = ptb[v][i];
            if (vb >> b & 1ULL) continue;
            dfsA(64 + b, left - 1, vp, vb | (1ULL << b));
        }
    } else {
        int b = v - 64;
        for (int i = 0; i < 3; i++) {
            int x = blk[b][i];
            if (vp >> x & 1ULL) continue;
            dfsA(x, left - 1, vp | (1ULL << x), vb);
        }
    }
}
static u64 endA(int x, int L) {
    endset_acc = 0;
    dfsA(x, L, 1ULL << x, 0);
    return endset_acc;
}

/* ---- oracle B: half-path joins ---- */
#define MAXH 4096
typedef struct { int end; u64 vp, vb; } half_t;
static int nh;
static void dfsH(int v, int left, u64 vp, u64 vb, half_t *out) {
    if (left == 0) { out[nh].end = v; out[nh].vp = vp; out[nh].vb = vb; nh++; return; }
    if (v < 64) {
        for (int i = 0; i < pdeg[v]; i++) {
            int b = ptb[v][i];
            if (vb >> b & 1ULL) continue;
            dfsH(64 + b, left - 1, vp, vb | (1ULL << b), out);
        }
    } else {
        int b = v - 64;
        for (int i = 0; i < 3; i++) {
            int x = blk[b][i];
            if (vp >> x & 1ULL) continue;
            dfsH(x, left - 1, vp | (1ULL << x), vb, out);
        }
    }
}
static half_t HX[MAXH], HY[MAXH];
/* does a simple path of length 2h exist between distinct points x,y ? (h odd: midpoint is a block) */
static int joinB(int x, int y, int h) {
    nh = 0; dfsH(x, h, 1ULL << x, 0, HX); int nx = nh;
    nh = 0; dfsH(y, h, 1ULL << y, 0, HY); int ny = nh;
    for (int i = 0; i < nx; i++) for (int j = 0; j < ny; j++) {
        if (HX[i].end != HY[j].end) continue;
        int m = HX[i].end;
        u64 ip = HX[i].vp & HY[j].vp, ib = HX[i].vb & HY[j].vb;
        if (m < 64) { if (ip == (1ULL << m) && ib == 0) return 1; }
        else { if (ib == (1ULL << (m - 64)) && ip == 0) return 1; }
    }
    return 0;
}

/* ---- witness path (independent small DFS, used for certificates) ---- */
static int wpath[32]; static int wlen;
static int dfsW(int v, int target, int left, u64 vp, u64 vb, int pos) {
    wpath[pos] = v;
    if (left == 0) return v == target;
    if (v < 64) {
        for (int i = 0; i < pdeg[v]; i++) {
            int b = ptb[v][i];
            if (vb >> b & 1ULL) continue;
            if (dfsW(64 + b, target, left - 1, vp, vb | (1ULL << b), pos + 1)) return 1;
        }
    } else {
        int b = v - 64;
        for (int i = 0; i < 3; i++) {
            int x = blk[b][i];
            if (vp >> x & 1ULL) continue;
            if (dfsW(x, target, left - 1, vp | (1ULL << x), vb, pos + 1)) return 1;
        }
    }
    return 0;
}
static void witness(int x, int y, int L) {
    if (!dfsW(x, y, L, 1ULL << x, 0, 0)) { fprintf(stderr, "witness failure %d %d %d\n", x, y, L); exit(5); }
    wlen = L + 1;
}

/* ---- state manipulation ---- */
static void add_block(int a, int b, int c) {
    int k = nblk++;
    blk[k][0] = a; blk[k][1] = b; blk[k][2] = c;
    int t[3] = {a, b, c};
    for (int i = 0; i < 3; i++) { int x = t[i]; ptb[x][pdeg[x]++] = k; }
    paired[a] |= (1ULL << b) | (1ULL << c);
    paired[b] |= (1ULL << a) | (1ULL << c);
    paired[c] |= (1ULL << a) | (1ULL << b);
    int m = a; if (b > m) m = b; if (c > m) m = c;
    if (m + 1 > npts) npts = m + 1;
}
static void remove_block(int a, int b, int c, int old_npts) {
    nblk--;
    int t[3] = {a, b, c};
    for (int i = 0; i < 3; i++) pdeg[t[i]]--;
    paired[a] &= ~((1ULL << b) | (1ULL << c));
    paired[b] &= ~((1ULL << a) | (1ULL << c));
    paired[c] &= ~((1ULL << a) | (1ULL << b));
    npts = old_npts;
}

/* cycle test on pairs among {p,q,r} that are all already introduced (old).
 * returns 0 ok, 8 creates C8, 16 creates C16; fills witness pair. */
static u64 cacheE6[MAXP], cacheE14[MAXP]; static int cached6[MAXP], cached14[MAXP];
static int wx, wy;
static int cyc_test(int p, int q, int r, int oldn) {
    int t[3] = {p, q, r};
    int L[3] = {4, 6, 14}; int use[3] = {use6, use8, use16};
    for (int li = 0; li < 3; li++) {
        if (!use[li]) continue;
        for (int i = 0; i < 3; i++) for (int j = i + 1; j < 3; j++) {
            int x = t[i], y = t[j];
            if (x >= oldn || y >= oldn) continue;
            int hit;
            if (!oracleB) {
                if (li == 0) hit = (endA(x, 4) >> y) & 1ULL; /* C6 filter only used in controls: uncached */
                else {
                    u64 *cache = (li == 2) ? cacheE14 : cacheE6; int *cd = (li == 2) ? cached14 : cached6;
                    if (!cd[x]) { cache[x] = endA(x, L[li]); cd[x] = 1; }
                    hit = (cache[x] >> y) & 1ULL;
                }
            } else {
                hit = joinB(x, y, L[li] / 2);
            }
            if (hit) { wx = x; wy = y; return L[li] + 2; }
        }
    }
    return 0;
}

static void emit_witness_line(char tag, int q, int r, int L) {
    witness(wx, wy, L);
    fprintf(certf, "%c %d %d", tag, q, r);
    for (int i = 0; i < wlen; i++) fprintf(certf, " %d", wpath[i]);
    fputc('\n', certf);
}

static void search(int depth);

static void try_prop(int p, int q, int r, int oldn, int depth) {
    c_attempt++;
    /* structural: q,r both old and already paired with each other (p-q, p-r excluded by eligibility) */
    if (q < oldn && r < oldn && ((paired[q] >> r) & 1ULL)) {
        c_struct++; hmix(((u64)q << 16) | ((u64)r << 8) | 1);
        if (certf) fprintf(certf, "S %d %d\n", q, r);
        return;
    }
    int ct = cyc_test(p, q, r, oldn);
    if (ct == 6) { c_c6++; hmix(((u64)q << 16) | ((u64)r << 8) | 5); if (certf) emit_witness_line('6', q, r, 4); return; }
    if (ct == 8) { c_c8++; hmix(((u64)q << 16) | ((u64)r << 8) | 2); if (certf) emit_witness_line('8', q, r, 6); return; }
    if (ct == 16) { c_c16++; hmix(((u64)q << 16) | ((u64)r << 8) | 3); if (certf) emit_witness_line('G', q, r, 14); return; }
    hmix(((u64)q << 16) | ((u64)r << 8) | 4);
    /* split handling */
    int skip = 0;
    if (split_d >= 0 && depth == split_d) {
        u64 idx = split_ctr[depth]++;
        if ((int)(idx % (u64)split_n) != split_k) skip = 1;
    }
    if (certf) fprintf(certf, "E %d %d\n", q, r);
    if (skip) { if (certf) fprintf(certf, "X\n"); return; }
    int save6[MAXP], save14[MAXP];
    memcpy(save6, cached6, sizeof(int) * MAXP); memcpy(save14, cached14, sizeof(int) * MAXP);
    u64 s6[MAXP], s14[MAXP];
    memcpy(s6, cacheE6, sizeof(u64) * MAXP); memcpy(s14, cacheE14, sizeof(u64) * MAXP);
    int on = npts;
    add_block(p, q, r);
    search(depth + 1);
    remove_block(p, q, r, on);
    memcpy(cached6, save6, sizeof(int) * MAXP); memcpy(cached14, save14, sizeof(int) * MAXP);
    memcpy(cacheE6, s6, sizeof(u64) * MAXP); memcpy(cacheE14, s14, sizeof(u64) * MAXP);
    if (certf) fprintf(certf, "U\n");
}

static void search(int depth) {
    c_states++;
    if ((++tick & 0xffff) == 0 && maxsec > 0 && difftime(time(NULL), t0) > maxsec) {
        printf("{\"aborted\":true,\"states\":%llu}\n", c_states); exit(3);
    }
    depth_hist[nblk]++;
    if ((u64)nblk > deepest) deepest = nblk;
    /* invalidate caches: state changed */
    memset(cached6, 0, sizeof(cached6)); memset(cached14, 0, sizeof(cached14));
    int p = -1;
    for (int x = 0; x < npts; x++) if (pdeg[x] < 3) { p = x; break; }
    if (p < 0) {
        c_comp++; hmix(0xC0C0ULL);
        if (certf) fprintf(certf, "C\n");
        if (compf) {
            fprintf(compf, "%d", npts);
            for (int b = 0; b < nblk; b++) fprintf(compf, " %d,%d,%d", blk[b][0], blk[b][1], blk[b][2]);
            fputc('\n', compf);
        }
        return;
    }
    /* lex bound: lex-max block through p whose least point is p */
    int ba = -1, bb = -1;
    for (int i = 0; i < pdeg[p]; i++) {
        int b = ptb[p][i];
        if (blk[b][0] == p) {
            if (blk[b][1] > ba || (blk[b][1] == ba && blk[b][2] > bb)) { ba = blk[b][1]; bb = blk[b][2]; }
        }
    }
    int oldn = npts;
    int elig[MAXP]; int ne = 0;
    for (int x = p + 1; x < oldn; x++) {
        if (pdeg[x] < 3 && !((paired[p] >> x) & 1ULL)) elig[ne++] = x;
    }
    int f = oldn; /* next fresh label */
    /* count the alternative-convention structural proposals (all old labels > p) for diagnostics */
    for (int x = p + 1; x < oldn; x++) {
        int bad_x = !(pdeg[x] < 3 && !((paired[p] >> x) & 1ULL));
        for (int y = x + 1; y < oldn; y++) {
            int bad_y = !(pdeg[y] < 3 && !((paired[p] >> y) & 1ULL));
            if ((bad_x || bad_y) && (x > ba || (x == ba && y > bb))) c_struct_alt++;
        }
        if (bad_x && x > ba && f + 1 <= cap) c_struct_alt++;
    }
    /* proposals in lexicographic order of (q, r) */
    for (int i = 0; i < ne; i++) {
        int q = elig[i];
        for (int j = i + 1; j < ne; j++) {
            int r = elig[j];
            if (q < ba || (q == ba && r <= bb)) continue;
            try_prop(p, q, r, oldn, depth);
        }
        if (q < ba) continue; /* (q, fresh) > (ba,bb) iff q > ba, or q == ba (fresh > bb always) */
        if (f + 1 <= cap) try_prop(p, q, f, oldn, depth); else c_cap_block++;
    }
    if (f > ba) {
        if (f + 2 <= cap) try_prop(p, f, f + 1, oldn, depth); else c_cap_block++;
    }
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: cb_search CAP ORBIT ORACLE [opts]\n"); return 1; }
    cap = atoi(argv[1]); orbit = atoi(argv[2]); oracleB = (argv[3][0] == 'B');
    for (int i = 4; i < argc; i++) {
        if (!strcmp(argv[i], "-no8")) use8 = 0;
        else if (!strcmp(argv[i], "-no16")) use16 = 0;
        else if (!strcmp(argv[i], "-c6")) use6 = 1;
        else if (!strcmp(argv[i], "-cert")) { certf = fopen(argv[++i], "w"); if (!certf) return 2; }
        else if (!strcmp(argv[i], "-comp")) { compf = fopen(argv[++i], "w"); if (!compf) return 2; }
        else if (!strcmp(argv[i], "-split")) { split_d = atoi(argv[i + 1]); split_k = atoi(argv[i + 2]); split_n = atoi(argv[i + 3]); i += 3; }
        else if (!strcmp(argv[i], "-maxsec")) maxsec = atof(argv[++i]);
        else { fprintf(stderr, "bad option %s\n", argv[i]); return 1; }
    }
    if (cap > 60 || cap < 8 || (orbit < 0 || orbit > 2)) { fprintf(stderr, "bad args\n"); return 1; }
    t0 = time(NULL);
    clock_t c0 = clock();
    if (orbit == 0) add_block(0, 1, 2); /* arbitrary-root mode: no Berge triangle assumed */
    else {
        add_block(0, 1, 3); add_block(1, 2, 4); add_block(0, 2, 5);
        if (orbit == 1) add_block(0, 4, 6); else add_block(0, 6, 7);
    }
    if (certf) fprintf(certf, "R %d %d%s%s%s\n", cap, orbit, use6 ? " c6" : "", use8 ? "" : " no8", use16 ? "" : " no16");
    search(0);
    if (certf) { fprintf(certf, "END %llu %llu %llu %llu %llu %llu %llu\n", c_states, c_attempt, c_struct, c_c6, c_c8, c_c16, c_comp); fclose(certf); }
    if (compf) fclose(compf);
    double secs = (double)(clock() - c0) / CLOCKS_PER_SEC;
    printf("{\"cap\":%d,\"orbit\":%d,\"oracle\":\"%c\",\"c8_filter\":%d,\"c16_filter\":%d,"
           "\"split\":[%d,%d,%d],"
           "\"c6_filter\":%d,\"c6\":%llu,\"states\":%llu,\"attempted\":%llu,\"structural\":%llu,\"c8\":%llu,\"c16\":%llu,\"completions\":%llu,"
           "\"structural_alt_extra\":%llu,\"cap_suppressed\":%llu,\"max_blocks\":%llu,\"transcript_hash\":\"%016llx\","
           "\"cpu_seconds\":%.3f,\"depth_hist\":[",
           cap, orbit, oracleB ? 'B' : 'A', use8, use16, split_d, split_k, split_n,
           use6, c_c6, c_states, c_attempt, c_struct, c_c8, c_c16, c_comp, c_struct_alt, c_cap_block, deepest, thash, secs);
    for (int i = 0; i <= MAXB && i <= 60; i++) { if (i) printf(","); printf("%llu", depth_hist[i]); }
    printf("]}\n");
    return 0;
}
