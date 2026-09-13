# -*- coding: utf-8 -*-
"""e850_verify.py -- INDEPENDENT verifier for the Erdos 850 search.

Shares NO code with the sieve engine (e850.c).  rad(n) here is computed by
plain trial factorisation from scratch.  Used for three jobs:

  --sample FILE   re-verify the engine's (n, rad n) sample dump
  --witness "x,y" re-verify a claimed witness pair from first principles
  --selftest      known radicals, hand-checkable

Exact integers only.
"""
import sys, io, json, time

def rad_trial(n):
    """product of distinct primes dividing n, by trial division. n >= 1."""
    if n < 1:
        raise ValueError("rad undefined for n < 1")
    r = 1
    m = n
    d = 2
    while d * d <= m:
        if m % d == 0:
            r *= d
            while m % d == 0:
                m //= d
        d += 1 if d == 2 else 2
    if m > 1:
        r *= m
    return r

def selftest():
    known = {1: 1, 2: 2, 3: 3, 4: 2, 6: 6, 8: 2, 9: 3, 12: 6, 16: 2, 18: 6,
             27: 3, 30: 30, 32: 2, 36: 6, 48: 6, 49: 7, 50: 10, 64: 2, 72: 6,
             100: 10, 128: 2, 243: 3, 1024: 2, 2310: 2310, 999983: 999983}
    bad = []
    for n, r in known.items():
        got = rad_trial(n)
        if got != r:
            bad.append((n, got, r))
    print("selftest known radicals: %d checked, %d bad" % (len(known), len(bad)))
    for b in bad:
        print("  BAD", b)
    return len(bad) == 0

def verify_sample(path, k=1):
    n_ok = 0
    bad = []
    with io.open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            n = int(parts[0]); r = int(parts[1])
            got = rad_trial(n)
            if got != r:
                bad.append((n, r, got))
            else:
                n_ok += 1
    print("sample %s : %d verified, %d MISMATCH" % (path, n_ok, len(bad)))
    for b in bad[:20]:
        print("  MISMATCH n=%d engine=%d trial=%d" % b)
    return len(bad) == 0, n_ok, bad

def verify_witness(x, y, k=3):
    if x == y:
        print("REJECT: x == y")
        return False
    rows = []
    ok = True
    for i in range(k):
        a = rad_trial(x + i); b = rad_trial(y + i)
        rows.append((i, x + i, a, y + i, b, a == b))
        if a != b:
            ok = False
    for i, xi, a, yi, b, eq in rows:
        print("  i=%d  rad(%d)=%d   rad(%d)=%d   %s" % (i, xi, a, yi, b, "MATCH" if eq else "DIFFER"))
    print("WITNESS %s for x=%d y=%d k=%d" % ("CONFIRMED" if ok else "REFUTED", x, y, k))
    return ok

if __name__ == '__main__':
    args = sys.argv[1:]
    rc = 0
    if not args or '--selftest' in args:
        if not selftest():
            rc = 1
    i = 0
    while i < len(args):
        if args[i] == '--sample':
            good, n, bad = verify_sample(args[i + 1])
            if not good:
                rc = 1
            i += 2
        elif args[i] == '--witness':
            xy = args[i + 1].split(',')
            k = 3
            if i + 2 < len(args) and args[i + 2] == '--k':
                k = int(args[i + 3])
            if not verify_witness(int(xy[0]), int(xy[1]), k):
                rc = 1
            i += 2
        else:
            i += 1
    sys.exit(rc)
