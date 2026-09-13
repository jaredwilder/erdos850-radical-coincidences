# -*- coding: utf-8 -*-
"""drive850.py -- shard driver for the Erdos 850 exact search.

Splits [1, TOP] into SHARDS contiguous ranges and runs ./e850 on each with a
bounded worker pool.  Shards are claimed by atomic mkdir, so a SECOND driver
launched later with more workers cooperates with the first instead of
duplicating work.  Every shard writes its own survivor files and stderr log;
nothing is merged here (that is e850_collide.py's job, which does the ONE
global collision merge across all shards).

usage:
  drive850.py --top T --shards S --workers W --nmax N [--nmax2 N2]
              [--seg SEG] [--k 3] [--dir D] [--sample M] [--deadline SECS]
"""
import os, sys, io, time, subprocess, threading

def main():
    top = 10**12; shards = 64; workers = 4; nmax = 10**12; nmax2 = 10**9
    seg = 50000000; k = 3; base = '/root/peer/search850'; sample = 10000000
    deadline = 0; nice = 10
    a = sys.argv[1:]; i = 0
    while i < len(a):
        if   a[i] == '--top':      top = int(float(a[i+1])); i += 2
        elif a[i] == '--shards':   shards = int(a[i+1]); i += 2
        elif a[i] == '--workers':  workers = int(a[i+1]); i += 2
        elif a[i] == '--nmax':     nmax = int(float(a[i+1])); i += 2
        elif a[i] == '--nmax2':    nmax2 = int(float(a[i+1])); i += 2
        elif a[i] == '--seg':      seg = int(float(a[i+1])); i += 2
        elif a[i] == '--k':        k = int(a[i+1]); i += 2
        elif a[i] == '--dir':      base = a[i+1]; i += 2
        elif a[i] == '--sample':   sample = int(float(a[i+1])); i += 2
        elif a[i] == '--deadline': deadline = int(a[i+1]); i += 2
        elif a[i] == '--nice':     nice = int(a[i+1]); i += 2
        else: i += 1

    if nmax < top:
        sys.stderr.write("REFUSED: nmax (%d) < top (%d). The Difference Lemma prune "
                         "is only valid for a bound >= the scan range.\n" % (nmax, top))
        sys.exit(2)

    outd = os.path.join(base, 'out'); logd = os.path.join(base, 'logs')
    clmd = os.path.join(base, 'claims')
    for d in (outd, logd, clmd):
        os.makedirs(d, exist_ok=True)

    width = (top + shards - 1) // shards
    t0 = time.time()
    lock = threading.Lock()
    state = {'done': 0, 'skipped': 0, 'failed': 0}

    def run_shard(idx):
        lo = 1 + idx * width
        hi = min(top + 1, 1 + (idx + 1) * width)
        if lo >= hi:
            return
        tag = 'sh%04d' % idx
        donef = os.path.join(clmd, tag + '.done')
        if os.path.exists(donef):
            with lock: state['skipped'] += 1
            return
        try:
            os.mkdir(os.path.join(clmd, tag))     # atomic claim
        except FileExistsError:
            with lock: state['skipped'] += 1
            return
        cmd = [os.path.join(base, 'e850'),
               '--lo', str(lo), '--hi', str(hi), '--nmax', str(nmax),
               '--nmax2', str(nmax2), '--k', str(k), '--seg', str(seg),
               '--out',  os.path.join(outd, 'survK-%s.txt' % tag),
               '--out2', os.path.join(outd, 'surv2-%s.txt' % tag),
               '--sample', str(sample),
               '--check', os.path.join(outd, 'sample-%s.txt' % tag),
               '--question-lock',
               'oracle/ledger/question-locks/erdos850-rad-triple-witness.json']
        if nice:
            cmd = ['nice', '-n', str(nice)] + cmd
        lp = os.path.join(logd, 'seg-%s.log' % tag)
        with io.open(lp, 'w', encoding='utf-8', errors='replace') as lf:
            rc = subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=lf)
        with lock:
            if rc == 0:
                io.open(donef, 'w', encoding='utf-8').write('%d %d %.1f\n' % (lo, hi, time.time() - t0))
                state['done'] += 1
            else:
                state['failed'] += 1
            sys.stderr.write('[drive850] %s lo=%d hi=%d rc=%d done=%d skip=%d fail=%d elapsed=%.0fs\n'
                             % (tag, lo, hi, rc, state['done'], state['skipped'],
                                state['failed'], time.time() - t0))
            sys.stderr.flush()

    queue = list(range(shards))
    qlock = threading.Lock()

    def worker():
        while True:
            if deadline and time.time() - t0 > deadline:
                sys.stderr.write('[drive850] DEADLINE reached, worker stopping\n'); return
            with qlock:
                if not queue:
                    return
                idx = queue.pop(0)
            run_shard(idx)

    sys.stderr.write('[drive850] top=%d shards=%d width=%d workers=%d nmax=%d nmax2=%d seg=%d\n'
                     % (top, shards, width, workers, nmax, nmax2, seg))
    sys.stderr.flush()
    th = [threading.Thread(target=worker) for _ in range(workers)]
    for t in th: t.start()
    for t in th: t.join()
    sys.stderr.write('[drive850] POOL DONE done=%d skipped=%d failed=%d secs=%.0f\n'
                     % (state['done'], state['skipped'], state['failed'], time.time() - t0))


if __name__ == '__main__':
    main()
