/* g6_cycles.c -- independent cycle-length filter for graph6 input (control P2c; shares no code with cb_search.c).
 * For each graph (n <= 62) decides by plain DFS whether it has a simple cycle of length 4, 8 and 16.
 * Prints counts: total, with C4, with C8, with C16, and with none of C4/C8 ("C4C8free"), none of C4/C8/C16.
 * usage: g6_cycles < file.g6
 */
#include <stdio.h>
#include <string.h>

static int n, adjn[64], adj[64][64];
static int start, target_len, found;
static unsigned long long vis;

static void dfs(int v, int depth) {
    if (found) return;
    for (int i = 0; i < adjn[v]; i++) {
        int w = adj[v][i];
        if (w == start && depth == target_len) { found = 1; return; }
        if (w > start && !((vis >> w) & 1ULL) && depth < target_len) {
            vis |= 1ULL << w;
            dfs(w, depth + 1);
            vis &= ~(1ULL << w);
            if (found) return;
        }
    }
}
static int has_cycle(int L) {
    found = 0; target_len = L;
    for (start = 0; start < n && !found; start++) { vis = 1ULL << start; dfs(start, 1); }
    return found;
}
int main(void) {
    char s[4096];
    unsigned long long tot = 0, c4 = 0, c8 = 0, c16 = 0, f48 = 0, f4816 = 0;
    while (fgets(s, sizeof s, stdin)) {
        if (s[0] == '>') continue;
        n = s[0] - 63;
        memset(adjn, 0, sizeof adjn);
        int bit = 0, k = 1;
        for (int j = 1; j < n; j++) for (int i = 0; i < j; i++) {
            int byte = s[k + bit / 6] - 63;
            int b = (byte >> (5 - bit % 6)) & 1;
            bit++;
            if (b) { adj[i][adjn[i]++] = j; adj[j][adjn[j]++] = i; }
        }
        tot++;
        int h4 = has_cycle(4), h8 = has_cycle(8), h16 = has_cycle(16);
        c4 += h4; c8 += h8; c16 += h16;
        if (!h4 && !h8) { f48++; if (!h16) f4816++; }
    }
    printf("{\"graphs\":%llu,\"with_C4\":%llu,\"with_C8\":%llu,\"with_C16\":%llu,\"C4C8free\":%llu,\"C4C8C16free\":%llu}\n",
           tot, c4, c8, c16, f48, f4816);
    return 0;
}
