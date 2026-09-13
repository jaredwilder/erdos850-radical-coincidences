#!/bin/bash
# watch850.sh -- wait until the erdos289 job has released the box, then start a
# SECOND pool of workers on the erdos850 search.  Pool A (4 workers, nice 10)
# keeps running throughout; the pools cooperate through the atomic-mkdir shard
# claims in /root/peer/search850/claims, so nothing is done twice.
#
# Gate (both must hold, logged explicitly):
#   1. no drive289 process alive
#   2. a SEARCH-RECEIPT*.json in /root/peer/search289 newer than this script's start
#      (its master receipt) -- OR condition 1 stable for 3 consecutive checks
set -u
BASE=/root/peer/search850
LOG=/root/peer/out/watch850.log
START=$(date +%s)
STAMP=/root/peer/out/.watch850.stamp
touch "$STAMP"
EXTRA_WORKERS=${1:-20}
stable=0
echo "[watch850] start $(date -u +%FT%TZ) extra_workers=$EXTRA_WORKERS" >> "$LOG"
while true; do
  n289=$(pgrep -c -f drive289 || true)
  newrec=$(find /root/peer/search289 -maxdepth 1 -name 'SEARCH-RECEIPT*.json' -newer "$STAMP" 2>/dev/null | wc -l)
  if [ "${n289:-0}" -eq 0 ]; then
    stable=$((stable+1))
  else
    stable=0
  fi
  echo "[watch850] $(date -u +%FT%TZ) drive289_procs=${n289:-0} new_master_receipt=$newrec stable=$stable" >> "$LOG"
  if [ "${n289:-0}" -eq 0 ] && { [ "$newrec" -gt 0 ] || [ "$stable" -ge 3 ]; }; then
    reason="drive289_gone"
    [ "$newrec" -gt 0 ] && reason="master_receipt_present_and_drive289_gone"
    echo "[watch850] GATE OPEN ($reason) at $(date -u +%FT%TZ) -- launching pool B with $EXTRA_WORKERS workers" >> "$LOG"
    cd "$BASE" || exit 1
    export PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1
    nohup nice -n 10 python3 drive850.py --top 1e12 --shards 256 --workers "$EXTRA_WORKERS" \
      --nmax 1e12 --nmax2 1e9 --seg 5e7 --k 3 --sample 1e7 --nice 10 --dir "$BASE" \
      --question-lock oracle/ledger/question-locks/erdos850-rad-triple-witness.json \
      >> /root/peer/out/drive850-poolB.log 2>&1 &
    echo "[watch850] pool B pid $! launched" >> "$LOG"
    exit 0
  fi
  sleep 60
done
