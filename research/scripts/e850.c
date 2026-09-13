/* e850.c  --  Erdos 850 exact witness search engine.
 *
 * Problem: does there exist x != y in N with rad(x)=rad(y), rad(x+1)=rad(y+1),
 * rad(x+2)=rad(y+2)?  rad(n) = product of the distinct primes dividing n.
 *
 * DIFFERENCE LEMMA (proved; see report).  Let k >= 1.  If rad(x+i) = rad(y+i)
 * for i = 0..k-1 and x < y, put L_k(n) = rad( n(n+1)...(n+k-1) )
 *                                      = lcm( rad n, ..., rad(n+k-1) ).
 * Every prime p | L_k(x) divides some x+i, hence p | rad(x+i) = rad(y+i) |
 * y+i, hence p | (y+i)-(x+i) = y-x.  L_k(x) is squarefree, so L_k(x) | y-x.
 * Also L_k(y) = L_k(x) (same prime sets).  With 1 <= x < y <= N this gives
 *      L_k(x) = L_k(y) <= y - x <= N - 1 < N.
 * So BOTH endpoints of any witness pair lie in the survivor set
 *      S_k(N) = { n : 1 <= n <= N, L_k(n) <= N }.
 * The search is: sieve L_k(n) exactly for every n <= N, keep S_k(N) (tiny),
 * then look for two survivors with the identical radical k-tuple.  EXACT and
 * COMPLETE -- no witness with both members <= N can escape it.
 *
 * This program is the sieve half.  In one pass it emits TWO streams:
 *   --out    the k-term survivors   (k = --k, default 3)  : the actual search
 *   --out2   the 2-term survivors                          : the CALIBRATION
 * The 2-term problem has known non-empty answers (the family x = 2^m - 2,
 * y = x(x+2)), so the 2-term count per segment is the live proof that the
 * pipeline is not silently returning zero.
 *
 * Exact unsigned 64-bit integer arithmetic only.  No floating point.
 * Every product is guarded so that no overflow can occur.
 *
 * usage:
 *   e850 --lo LO --hi HI --nmax N [--k 3] [--seg S]
 *        [--out FILE] [--out2 FILE] [--sample M --check FILE]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned long long u64;

static u64 gcd_u64(u64 a, u64 b) { while (b) { u64 t = a % b; a = b; b = t; } return a; }

/* saturating lcm: lcm(a,b) if <= cap, else cap+1 (sentinel).
   a,b >= 1.  No overflow: t*b is formed only after checking t <= cap/b. */
static u64 lcm_sat(u64 a, u64 b, u64 cap)
{
    u64 g = gcd_u64(a, b);
    u64 t = a / g;                 /* exact */
    if (t > cap / b) return cap + 1;
    return t * b;                  /* <= cap */
}

int main(int argc, char **argv)
{
    u64 LO = 1, HI = 0, NMAX = 0, NMAX2 = 0, SEG = 50000000ULL, SAMPLE = 0;
    int K = 3;
    const char *outpath = NULL, *out2path = NULL, *chkpath = NULL, *qlock = NULL;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--lo") && i + 1 < argc)          LO = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--hi") && i + 1 < argc)     HI = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--nmax") && i + 1 < argc)   NMAX = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--nmax2") && i + 1 < argc)  NMAX2 = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--seg") && i + 1 < argc)    SEG = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--k") && i + 1 < argc)      K = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--sample") && i + 1 < argc) SAMPLE = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--out") && i + 1 < argc)    outpath = argv[++i];
        else if (!strcmp(argv[i], "--out2") && i + 1 < argc)   out2path = argv[++i];
        else if (!strcmp(argv[i], "--check") && i + 1 < argc)  chkpath = argv[++i];
        else if (!strcmp(argv[i], "--question-lock") && i + 1 < argc) qlock = argv[++i];
        else { fprintf(stderr, "bad arg: %s\n", argv[i]); return 2; }
    }
    if (NMAX2 == 0) NMAX2 = NMAX;
    if (HI == 0 || NMAX == 0 || K < 2 || K > 8 || LO < 1) {
        fprintf(stderr, "usage: e850 --lo LO --hi HI --nmax N [--k 3] [--seg S] [--out F] [--out2 F]\n");
        return 2;
    }

    FILE *out = outpath ? fopen(outpath, "w") : stdout;
    if (!out) { perror("out"); return 3; }
    FILE *out2 = out2path ? fopen(out2path, "w") : NULL;
    FILE *chk = chkpath ? fopen(chkpath, "w") : NULL;

    /* ---- base primes up to sqrt(largest value we factor) ---- */
    u64 maxval = HI + (u64)K - 2;
    u64 root = 0; while ((root + 1) * (root + 1) <= maxval) root++;
    unsigned char *comp = (unsigned char *)calloc((size_t)root + 1, 1);
    if (!comp) { fprintf(stderr, "oom base\n"); return 4; }
    for (u64 p = 2; p * p <= root; p++) if (!comp[p]) for (u64 q = p * p; q <= root; q += p) comp[q] = 1;
    u64 npr = 0; for (u64 p = 2; p <= root; p++) if (!comp[p]) npr++;
    u64 *pr = (u64 *)malloc(sizeof(u64) * (size_t)(npr ? npr : 1));
    if (!pr) { fprintf(stderr, "oom pr\n"); return 4; }
    { u64 j = 0; for (u64 p = 2; p <= root; p++) if (!comp[p]) pr[j++] = p; }
    free(comp);
    fprintf(stderr, "[e850] question-lock: %s\n", qlock ? qlock : "(none)");
    fprintf(stderr, "[e850] base primes up to %llu : %llu  (maxval=%llu)\n", root, npr, maxval);

    size_t W = (size_t)SEG + (size_t)K - 1;
    u64 *rad = (u64 *)malloc(sizeof(u64) * W);
    u64 *sm  = (u64 *)malloc(sizeof(u64) * W);   /* smooth part: prod p^v_p(n), p <= root */
    if (!rad || !sm) { fprintf(stderr, "oom seg\n"); return 4; }

    u64 scanned = 0, survK = 0, surv2 = 0, nseg = 0;
    time_t t0 = time(0);

    for (u64 s = LO; s < HI; s += SEG) {
        u64 e = s + SEG; if (e > HI) e = HI;
        size_t w = (size_t)(e - s) + (size_t)K - 1;
        for (size_t i = 0; i < w; i++) { rad[i] = 1; sm[i] = 1; }

        u64 top = s + (u64)w - 1;
        for (u64 pi = 0; pi < npr; pi++) {
            u64 p = pr[pi];
            if (p > top) break;
            u64 st = ((s + p - 1) / p) * p;
            if (st <= top) {
                for (size_t i = (size_t)(st - s); i < w; i += (size_t)p) { rad[i] *= p; sm[i] *= p; }
            }
            u64 pe = p;
            while (pe <= top / p) {
                pe *= p;
                u64 st2 = ((s + pe - 1) / pe) * pe;
                if (st2 > top) break;
                for (size_t i = (size_t)(st2 - s); i < w; i += (size_t)pe) sm[i] *= p;
            }
        }
        /* n / smooth_part is 1 or a single prime > root (n <= maxval, root = floor sqrt maxval) */
        for (size_t i = 0; i < w; i++) {
            u64 left = (s + (u64)i) / sm[i];
            if (left > 1) rad[i] *= left;
        }

        u64 cap = (NMAX > NMAX2) ? NMAX : NMAX2;
        u64 segK = 0, seg2 = 0;
        for (size_t i = 0; i + (size_t)K <= w; i++) {
            u64 n = s + (u64)i;
            u64 L2 = lcm_sat(rad[i], rad[i + 1], cap);
            if (L2 > cap) continue;   /* L_K >= L_2 >= L_2, so nothing is skipped */
            if (out2 && n <= NMAX2 && L2 <= NMAX2) {
                fprintf(out2, "%llu %llu %llu %llu\n", n, rad[i], rad[i + 1], L2);
                seg2++;
            }
            if (L2 <= NMAX && n <= NMAX) {
                u64 L = L2;
                int ok = 1;
                for (int j = 2; j < K; j++) {
                    L = lcm_sat(L, rad[i + j], NMAX);
                    if (L > NMAX) { ok = 0; break; }
                }
                if (ok) {
                    fprintf(out, "%llu", n);
                    for (int j = 0; j < K; j++) fprintf(out, " %llu", rad[i + j]);
                    fprintf(out, " %llu\n", L);
                    segK++;
                }
            }
        }
        if (chk && SAMPLE) {
            for (size_t i = 0; i + (size_t)K <= w; i += (size_t)SAMPLE)
                fprintf(chk, "%llu %llu\n", s + (u64)i, rad[i]);
        }

        scanned += (e - s); survK += segK; surv2 += seg2; nseg++;
        fprintf(stderr, "[e850] SEG %llu..%llu scanned=%llu survK=%llu surv2=%llu elapsed=%llds\n",
                s, e, e - s, segK, seg2, (long long)(time(0) - t0));
        fflush(stderr); fflush(out); if (out2) fflush(out2);
    }

    fprintf(stderr, "[e850] DONE lo=%llu hi=%llu k=%d nmax=%llu nmax2=%llu scanned=%llu survK=%llu surv2=%llu segs=%llu secs=%lld\n",
            LO, HI, K, NMAX, NMAX2, scanned, survK, surv2, nseg, (long long)(time(0) - t0));
    if (out != stdout) fclose(out);
    if (out2) fclose(out2);
    if (chk) fclose(chk);
    free(rad); free(sm); free(pr);
    return 0;
}
