# -*- coding: utf-8 -*-
"""e850_naive.py -- NAIVE control search (no prune) for the k-fold radical
coincidence problem.  This is the KNOWN-ANSWER CONTROL: for k=1 and k=2 the
answer set is non-empty and small, so a searcher that cannot reproduce it is
broken.

Method: smallest-prime-factor sieve over [1,B], rad by SPF walk, dict of the
full k-tuple -> smallest n.  Every pair (x,y) with x<y<=B and matching tuple
is reported.  O(B) memory -- keep B small (<= a few million).

usage: e850_naive.py --bound B --k K [--out FILE] [--maxpairs M]
"""
import sys, io, json, time

def main():
    B = 1000000
    K = 2
    out = None
    maxpairs = 200
    a = sys.argv[1:]
    i = 0
    while i < len(a):
        if a[i] == '--bound': B = int(a[i + 1]); i += 2
        elif a[i] == '--k': K = int(a[i + 1]); i += 2
        elif a[i] == '--out': out = a[i + 1]; i += 2
        elif a[i] == '--maxpairs': maxpairs = int(a[i + 1]); i += 2
        else: i += 1

    t0 = time.time()
    M = B + K
    spf = list(range(M + 1))
    p = 2
    while p * p <= M:
        if spf[p] == p:
            for q in range(p * p, M + 1, p):
                if spf[q] == q:
                    spf[q] = p
        p += 1
    rad = [1] * (M + 1)
    for n in range(2, M + 1):
        m = n; r = 1
        while m > 1:
            q = spf[m]
            r *= q
            while m % q == 0:
                m //= q
        rad[n] = r
    sys.stderr.write("naive: sieve done B=%d k=%d %.1fs\n" % (B, K, time.time() - t0))

    seen = {}
    pairs = []
    for n in range(1, B + 1):
        key = tuple(rad[n + j] for j in range(K))
        if key in seen:
            pairs.append((seen[key], n, key))
        else:
            seen[key] = n
    res = {
        "tool": "e850_naive.py",
        "mode": "NAIVE_NO_PRUNE_CONTROL",
        "bound": B, "k": K,
        "pair_count": len(pairs),
        "first_pairs": [[x, y, list(kk)] for x, y, kk in pairs[:maxpairs]],
        "min_pair": ([pairs[0][0], pairs[0][1], list(pairs[0][2])] if pairs else None),
        "secs": round(time.time() - t0, 2),
    }
    txt = json.dumps(res, indent=1)
    print(txt)
    if out:
        with io.open(out, 'w', encoding='utf-8', errors='replace') as f:
            f.write(txt)

if __name__ == '__main__':
    main()
