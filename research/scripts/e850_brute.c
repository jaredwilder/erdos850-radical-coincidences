/* e850_brute.c -- INDEPENDENT no-prune cross-check for the Erdos 850 search.
 *
 * Uses NO part of the Difference Lemma.  It builds rad(n) for every n <= N with
 * a plain in-memory radical sieve, sorts ALL n by the full k-tuple
 * (rad n, rad(n+1), ..., rad(n+k-1)), and reports every adjacent duplicate.
 * This is the brute force the prune is supposed to be equivalent to; running it
 * at a scale well past the previous frontier is what proves the prune did not
 * silently drop a witness.
 *
 * Memory: 2 x 4 bytes x N  (u32 rad + u32 index).  N = 1e8 -> ~1.6 GB peak.
 * Exact integers only.  rad(n) <= n < 2^32 for N < 2^32.
 *
 * usage: e850_brute --n N [--k 3]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned int u32;
typedef unsigned long long u64;

static u32 *R;      /* R[n] = rad(n) */
static int  KK;

static int cmp(const void *a, const void *b)
{
    u32 x = *(const u32 *)a, y = *(const u32 *)b;
    for (int j = 0; j < KK; j++) {
        u32 p = R[x + j], q = R[y + j];
        if (p != q) return p < q ? -1 : 1;
    }
    return x < y ? -1 : (x > y ? 1 : 0);
}

int main(int argc, char **argv)
{
    u64 N = 100000000ULL; KK = 3;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--n") && i + 1 < argc) N = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--k") && i + 1 < argc) KK = atoi(argv[++i]);
    }
    u64 M = N + (u64)KK;                 /* need rad up to N+K-1 */
    time_t t0 = time(0);

    R = (u32 *)malloc(sizeof(u32) * (size_t)(M + 1));
    u32 *S = (u32 *)malloc(sizeof(u32) * (size_t)(M + 1));   /* smooth part */
    if (!R || !S) { fprintf(stderr, "oom\n"); return 4; }
    for (u64 i = 0; i <= M; i++) { R[i] = 1; S[i] = 1; }

    for (u64 p = 2; p <= M; p++) {
        if (R[p] != 1) continue;         /* p composite: already touched by a smaller prime */
        for (u64 m = p; m <= M; m += p) { R[m] *= (u32)p; S[m] *= (u32)p; }
        u64 pe = p;
        while (pe <= M / p) {
            pe *= p;
            for (u64 m = pe; m <= M; m += pe) S[m] *= (u32)p;
        }
    }
    for (u64 i = 2; i <= M; i++) { u32 left = (u32)(i / S[i]); if (left > 1) R[i] *= left; }
    free(S);
    fprintf(stderr, "[brute] radical sieve to %llu done %llds\n", M, (long long)(time(0) - t0));

    u64 cnt = N;                          /* n = 1 .. N */
    u32 *idx = (u32 *)malloc(sizeof(u32) * (size_t)cnt);
    if (!idx) { fprintf(stderr, "oom idx\n"); return 4; }
    for (u64 i = 0; i < cnt; i++) idx[i] = (u32)(i + 1);
    qsort(idx, (size_t)cnt, sizeof(u32), cmp);
    fprintf(stderr, "[brute] sort done %llds\n", (long long)(time(0) - t0));

    u64 coll = 0;
    for (u64 i = 1; i < cnt; i++) {
        int same = 1;
        for (int j = 0; j < KK; j++) if (R[idx[i - 1] + j] != R[idx[i] + j]) { same = 0; break; }
        if (same) {
            coll++;
            if (coll <= 60) {
                fprintf(stdout, "COLLISION x=%u y=%u rads=", idx[i - 1] < idx[i] ? idx[i - 1] : idx[i],
                        idx[i - 1] < idx[i] ? idx[i] : idx[i - 1]);
                for (int j = 0; j < KK; j++) fprintf(stdout, " %u", R[idx[i] + j]);
                fprintf(stdout, "\n");
            }
        }
    }
    fprintf(stdout, "[brute] N=%llu k=%d NO_PRUNE collisions=%llu secs=%lld\n",
            N, KK, coll, (long long)(time(0) - t0));
    fflush(stdout);
    return 0;
}
