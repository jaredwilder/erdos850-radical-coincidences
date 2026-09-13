# -*- coding: utf-8 -*-
"""e850_frontier.py -- print the CONTIGUOUS scanned frontier from the engine's
segment logs.  Only a contiguous cover of [1, F] licenses a claim about F; a
scattered set of finished shards does not.  Prints F and nothing else.

usage: e850_frontier.py --seg-logs "glob"
"""
import sys, io, glob

def main():
    pat = None
    a = sys.argv[1:]; i = 0
    while i < len(a):
        if a[i] == '--seg-logs': pat = a[i + 1]; i += 2
        else: i += 1
    cover = []
    for lp in glob.glob(pat):
        with io.open(lp, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.startswith('[e850] SEG '):
                    lo, hi = line.split()[2].split('..')
                    cover.append((int(lo), int(hi)))
    cover.sort()
    want = 1
    for lo, hi in cover:
        if lo > want:
            break
        want = max(want, hi)
    print(want - 1)

if __name__ == '__main__':
    main()
