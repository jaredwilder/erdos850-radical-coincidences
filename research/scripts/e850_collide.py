# -*- coding: utf-8 -*-
"""e850_collide.py -- merge the survivor sets emitted by e850.c, detect
radical-tuple collisions on BOTH the k-term search stream and the 2-term
calibration stream, and write the master receipt.

A survivor row is "n r0 r1 ... r{j-1} L" with ri = rad(n+i) and
L = lcm(r0..r{j-1}) = rad(n(n+1)...(n+j-1)).

By the DIFFERENCE LEMMA every member of every witness pair with both members
<= NMAX is a survivor, so a collision search restricted to survivors is EXACT
and COMPLETE for the bound NMAX.

Cross-checks here are an independent code path from the C engine:
  * L recomputed from the radicals with math.gcd and compared to the engine's
  * L <= NMAX re-asserted for every row
  * ri | (n+i) re-asserted for every row
  * segment coverage of [1, NMAX] checked for gaps
  * CALIBRATION: the 2-term collision list must be non-empty and must contain
    the known family x = 2^m - 2, y = x(x+2)

usage: e850_collide.py --nmax N --k K --surv "glob" [--surv2 "glob"]
                       --seg-logs "glob" --out RECEIPT.json [--tag T] [--qlock P]
"""
import sys, io, os, json, glob, time, hashlib
from math import gcd


def lcm(a, b):
    return a // gcd(a, b) * b


def sha256_file(p):
    h = hashlib.sha256()
    with io.open(p, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def load_stream(pat, j, nmax):
    """returns rows [(tuple_of_radicals, n, L)], plus fault lists."""
    rows, bad_L, bad_bound, bad_div = [], [], [], []
    files = sorted(glob.glob(pat)) if pat else []
    for fp in files:
        with io.open(fp, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                v = [int(t) for t in line.split()]
                if len(v) != j + 2:
                    bad_L.append((v[0] if v else -1, 'MALFORMED_ROW', len(v)))
                    continue
                n = v[0]; rs = v[1:1 + j]; Lc = v[1 + j]
                L = 1
                for r in rs:
                    L = lcm(L, r)
                if L != Lc:
                    bad_L.append((n, Lc, L))
                if L > nmax:
                    bad_bound.append((n, L))
                for jj, r in enumerate(rs):
                    if (n + jj) % r != 0:
                        bad_div.append((n, jj, r))
                rows.append((tuple(rs), n, L))
    rows.sort()
    return files, rows, bad_L, bad_bound, bad_div


def collide(rows):
    out = []
    for i in range(1, len(rows)):
        if rows[i][0] == rows[i - 1][0]:
            out.append((rows[i - 1][1], rows[i][1], list(rows[i][0]), rows[i][2]))
    out.sort(key=lambda c: c[1])
    return out


# The COMPLETE set of 2-term solutions (rad x = rad y, rad(x+1) = rad(y+1),
# x < y) with y <= 3,000,000.  Established twice, independently: by the naive
# no-prune dict search (e850_naive.py) and by this pruned pipeline; every pair
# re-verified from first principles by e850_verify.py (trial factorisation).
# NINE lie on the family x = 2^m - 2, y = x(x+2).  (75, 1215) does NOT --
# any control that demands "all on the family" fails for the wrong reason.
KNOWN_2TERM_BELOW_3E6 = [
    (2, 8), (6, 48), (14, 224), (30, 960), (75, 1215), (62, 3968),
    (126, 16128), (254, 65024), (510, 261120), (1022, 1046528),
]
CONTROL_BOUND = 3000000


def known_family(nmax):
    """x = 2^m - 2, y = x(x+2), m >= 2 -- the known 2-term solution family."""
    fam = []
    m = 2
    while True:
        x = (1 << m) - 2
        y = x * (x + 2)
        if y > nmax:
            break
        fam.append((x, y))
        m += 1
    return fam


def main():
    nmax = 0; K = 3; survglob = None; surv2glob = None; loggl = None; out = None
    tag = "e850"; qlock = None; maxreport = 60; frontier = 0; nmax2 = 0
    a = sys.argv[1:]; i = 0
    while i < len(a):
        if a[i] == '--nmax': nmax = int(float(a[i + 1])); i += 2
        elif a[i] == '--k': K = int(a[i + 1]); i += 2
        elif a[i] == '--surv': survglob = a[i + 1]; i += 2
        elif a[i] == '--surv2': surv2glob = a[i + 1]; i += 2
        elif a[i] == '--seg-logs': loggl = a[i + 1]; i += 2
        elif a[i] == '--out': out = a[i + 1]; i += 2
        elif a[i] == '--tag': tag = a[i + 1]; i += 2
        elif a[i] == '--qlock': qlock = a[i + 1]; i += 2
        elif a[i] == '--frontier': frontier = int(float(a[i + 1])); i += 2
        elif a[i] == '--nmax2': nmax2 = int(float(a[i + 1])); i += 2
        else: i += 1

    if frontier == 0: frontier = nmax
    if nmax2 == 0: nmax2 = nmax
    if frontier > nmax:
        sys.stderr.write("REFUSED: frontier > prune bound; the prune is not valid there.\n")
        sys.exit(2)
    t0 = time.time()
    filesK, rowsK, bLK, bBK, bDK = load_stream(survglob, K, nmax)
    files2, rows2, bL2, bB2, bD2 = load_stream(surv2glob, 2, nmax) if surv2glob else ([], [], [], [], [])

    colK = collide(rowsK)
    col2 = collide(rows2)

    # --- calibration: the known 2-term family must be reproduced exactly ---
    two_bound = min(nmax2, frontier)
    fam = known_family(two_bound)
    found2 = set((c[0], c[1]) for c in col2)
    fam_missing = [p for p in fam if p not in found2]
    fam_extra = sorted(found2 - set(fam))

    # HARD known-answer gate: below 3e6 the 2-term solution set is known exactly
    # (10 pairs: 9 on the family x = 2^m - 2, plus the off-family (75, 1215)).
    ctrl_applicable = two_bound >= CONTROL_BOUND
    ctrl_expected = set(KNOWN_2TERM_BELOW_3E6)
    ctrl_found = set(p for p in found2 if p[1] <= CONTROL_BOUND)
    ctrl_missing = sorted(ctrl_expected - ctrl_found)
    ctrl_unexpected = sorted(ctrl_found - ctrl_expected)
    ctrl_ok = (not ctrl_applicable) or (not ctrl_missing and not ctrl_unexpected)

    calibration_ok = (bool(surv2glob) and len(col2) > 0
                      and len(fam_missing) == 0 and ctrl_ok and ctrl_applicable)

    # --- segment table ---
    segs = []; scanned_total = 0; cover = []
    if loggl:
        for lp in sorted(glob.glob(loggl)):
            with io.open(lp, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    if line.startswith('[e850] SEG '):
                        p = line.split()
                        lo, hi = p[2].split('..')
                        sc = int(p[3].split('=')[1])
                        sk = int(p[4].split('=')[1])
                        s2 = int(p[5].split('=')[1])
                        segs.append({"lo": int(lo), "hi": int(hi), "scanned": sc,
                                     "survivors_k": sk, "survivors_2": s2,
                                     "log": os.path.basename(lp)})
                        scanned_total += sc
                        cover.append((int(lo), int(hi)))
    cover.sort()
    # completeness is judged ONLY on [1, frontier]; work already done beyond the
    # declared frontier is real but is not part of the claim, so a hole above it
    # is not a gap in the claim.
    inrange = [(lo, min(hi, frontier + 1)) for lo, hi in cover if lo <= frontier]
    inrange.sort()
    gaps = []; want = 1
    for lo, hi in inrange:
        if lo > want:
            gaps.append([want, lo])
        want = max(want, hi)
    if want < frontier + 1:
        gaps.append([want, frontier + 1])
    scanned_in_frontier = sum(hi - lo for lo, hi in inrange)

    checks_ok = not (bLK or bBK or bDK or bL2 or bB2 or bD2)
    complete = (not gaps) and checks_ok and calibration_ok

    rec = {
        "tool": "e850_collide.py",
        "tag": tag,
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "problem": "Erdos 850: exists x != y with rad(x+i)=rad(y+i) for i=0..k-1",
        "k": K,
        "frontier_N": frontier,
        "prune_bound_nmax": nmax,
        "two_term_bound_nmax2": nmax2,
        "frontier_meaning": "no witness pair (x,y) with 1 <= x < y <= frontier_N, i.e. max(x,y) <= N",
        "collision_scope": "GLOBAL_ACROSS_ALL_SEGMENTS",
        "collision_scope_note": (
            "Every survivor signature from every segment over [1,N] enters ONE global sorted "
            "structure in this script; collisions are detected across that single merge, so "
            "pairs straddling segment boundaries ARE found. The per-segment counts in "
            "'segments' below are CANDIDATE counts only and are never a collision check. "
            "The survivor set is the complete candidate set by the Difference Lemma, so the "
            "global merge over survivors is equivalent to a global merge over all n <= N."),
        "verdict": ("WITNESS FOUND" if colK else "NO_WITNESS_TO_FRONTIER"),
        "prior_ground": {"source": "MINE/probe850b.log", "covered_max_xy": 30000000,
                         "collisions": 0,
                         "note": "prior independent brute force; this run re-covers and extends it"},
        "honesty": ("Exhaustion to N is COMPUTATION evidence of a bound, NEVER closure of the "
                    "negative branch. Only a verified witness closes anything."),
        "method": ("Difference Lemma prune: for a witness, L_k(n)=rad(n..n+k-1) divides y-x, and "
                   "L_k(x)=L_k(y); with x<y<=N this forces L_k(n) <= N-1 for BOTH endpoints. "
                   "Sieve L_k(n) exactly for every n <= N (segmented radical sieve), keep the "
                   "survivors, collide their radical tuples. Exact, complete, no heuristic."),
        "question_lock": qlock,
        "streams": {
            "k_term": {
                "files": [{"path": os.path.basename(f), "sha256": sha256_file(f),
                           "bytes": os.path.getsize(f)} for f in filesK],
                "survivor_count": len(rowsK),
                "collision_count": len(colK),
                "collisions": [{"x": c[0], "y": c[1], "radicals": c[2], "L": c[3]}
                               for c in colK[:maxreport]],
            },
            "two_term_calibration": {
                "files": [{"path": os.path.basename(f), "sha256": sha256_file(f),
                           "bytes": os.path.getsize(f)} for f in files2],
                "survivor_count": len(rows2),
                "collision_count": len(col2),
                "collisions": [{"x": c[0], "y": c[1], "radicals": c[2], "L": c[3]}
                               for c in col2[:maxreport]],
                "known_family_expected": [{"x": p[0], "y": p[1]} for p in fam],
                "known_family_missing": [{"x": p[0], "y": p[1]} for p in fam_missing],
                "outside_known_family": [{"x": p[0], "y": p[1]} for p in fam_extra[:maxreport]],
                "outside_known_family_count": len(fam_extra),
                "known_answer_gate_below_3e6": {
                    "applicable": ctrl_applicable,
                    "expected_pairs": [{"x": p[0], "y": p[1]} for p in sorted(ctrl_expected, key=lambda q: q[1])],
                    "expected_count": len(ctrl_expected),
                    "found_count": len(ctrl_found),
                    "missing": [{"x": p[0], "y": p[1]} for p in ctrl_missing],
                    "unexpected_new_findings": [{"x": p[0], "y": p[1]} for p in ctrl_unexpected],
                    "EXACT_MATCH": ctrl_ok,
                    "note": ("9 of the 10 lie on the family x = 2^m - 2, y = x(x+2); "
                             "(75, 1215) does NOT. No structural prune is used anywhere in "
                             "this search - the only prune is the Difference Lemma, a proved "
                             "implication. Exhaustive means exhaustive."),
                },
                "CALIBRATION_OK": calibration_ok,
            },
        },
        "scanned_total": scanned_total,
        "scanned_within_frontier": scanned_in_frontier,
        "coverage_gaps": gaps,
        "coverage_complete": not gaps,
        "cross_checks": {
            "L_recomputed_mismatch": len(bLK) + len(bL2),
            "L_exceeds_nmax": len(bBK) + len(bB2),
            "radical_does_not_divide": len(bDK) + len(bD2),
            "all_pass": checks_ok,
        },
        "segments": segs,
        "segment_count": len(segs),
        "EXHAUSTIVE_AND_COMPLETE": complete,
        "secs": round(time.time() - t0, 2),
    }
    txt = json.dumps(rec, indent=1)
    if out:
        with io.open(out, 'w', encoding='utf-8', errors='replace') as f:
            f.write(txt)
    print("k=%d survivors=%d collisions=%d | 2-term survivors=%d collisions=%d calib_ok=%s"
          % (K, len(rowsK), len(colK), len(rows2), len(col2), calibration_ok))
    print("scanned=%d gaps=%d crosschecks_ok=%s COMPLETE=%s"
          % (scanned_total, len(gaps), checks_ok, complete))
    for c in colK[:20]:
        print("  *** %d-TERM COLLISION x=%d y=%d radicals=%s L=%d" % (K, c[0], c[1], c[2], c[3]))
    for c in col2[:24]:
        print("  2-term x=%d y=%d radicals=%s L=%d" % (c[0], c[1], c[2], c[3]))
    print("  known-answer gate below 3e6: applicable=%s expected=%d found=%d EXACT_MATCH=%s"
          % (ctrl_applicable, len(ctrl_expected), len(ctrl_found), ctrl_ok))
    if ctrl_missing:
        print("  CONTROL FAILURE - missing known 2-term pairs:", ctrl_missing[:10])
    if ctrl_unexpected:
        print("  NEW FINDING - 2-term pairs below 3e6 not in the known set:", ctrl_unexpected[:10])
    if fam_missing:
        print("  missing known family members:", fam_missing[:10])
    if gaps[:5]:
        print("  GAPS", gaps[:5])


if __name__ == '__main__':
    main()
