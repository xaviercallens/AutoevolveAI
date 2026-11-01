/* Read graph6 (n<=16) from stdin; write graph6 lines of diameter-2-critical graphs to argv[1];
   print counts to stdout. Exact test: diameter<=2, not complete, and for every edge uv,
   G-uv has some pair at distance >2 (or disconnected). Usage: d2c_filter out.g6 */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
typedef uint16_t m_t;
static int n;
static int diam_le2(const m_t *a) {
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (!((a[i] >> j) & 1) && !(a[i] & a[j])) return 0;
    return 1;
}
int main(int argc, char **argv) {
    FILE *out = fopen(argv[1], "w");
    char line[256];
    long long seen = 0, d2c = 0;
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line);
        while (L && (line[L-1]=='\n'||line[L-1]=='\r')) line[--L] = 0;
        if (!L) continue;
        n = line[0] - 63;
        m_t a[16] = {0};
        int bit = 0, ne = 0;
        const char *p = line + 1;
        int val = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                if (bit == 0) { val = *p++ - 63; bit = 6; }
                bit--;
                if ((val >> bit) & 1) { a[i] |= 1 << j; a[j] |= 1 << i; ne++; }
            }
        seen++;
        if (ne == n*(n-1)/2) continue;           /* complete: diameter 1 */
        if (!diam_le2(a)) continue;
        int crit = 1;
        for (int u = 0; u < n && crit; u++)
            for (int v = u + 1; v < n && crit; v++)
                if ((a[u] >> v) & 1) {
                    m_t b[16]; memcpy(b, a, sizeof b);
                    b[u] &= ~(1 << v); b[v] &= ~(1 << u);
                    if (diam_le2(b)) crit = 0;
                }
        if (crit) { d2c++; fprintf(out, "%s\n", line); }
    }
    fclose(out);
    printf("seen %lld d2c %lld\n", seen, d2c);
    return 0;
}
