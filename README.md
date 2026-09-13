# Erdős #850: radical coincidences

Can two distinct positive integers have matching prime divisors at three
consecutive positions? With `rad(n)` denoting the product of the distinct
prime divisors of `n`, the question is whether

```text
rad(x+i) = rad(y+i),  i=0,1,2,  1 <= x < y.
```

This is the focused home for Jared Wilder's search code, structural lemmas,
Lean examples, controls and research history for this problem.

## Start here

| Read | Purpose |
|---|---|
| [Search report](research/SEARCH-REPORT-2026-09-02.md) | Difference lemma, exact pruning, frontier and corrections |
| [Master receipt](research/receipts/MASTER-RECEIPT.json) | Recorded computation through 464,637,500,000 |
| [Search implementations](research/scripts/) | Segmented C sieve, unpruned controls, trial-factorization verifier |
| [Lean source and log](research/kernel/) | Two-term witnesses and the excluded power-of-two family |
| [Prior-art reconciliation](research/abc/PRIOR-ART-VERDICT-2026-09-02.md) | Why the conditional abc route was retired |

## Results and current boundary

The historical master receipt records no three-term pair with
`max(x,y) <= 464,637,500,000`, using global collision checks across a contiguous
search range. This promotion preserves that evidence; it does not rerun the
large search or claim a solution of the infinite problem.

The elementary difference lemma says that any matching length-`k` pair
satisfies `rad(x(x+1)...(x+k-1)) | y-x`. It justifies the survivor filter.
The familiar two-term family `x=2^m-2, y=x(x+2)` never extends to a third
coincidence. That family is not exhaustive: `(75,1215)` is an explicit
two-term pair outside it. The correction remains in the search report.

## Run the checks

Python 3, standard library only, from the repository root:

```sh
python verification/verify_source.py
python verification/run_controls.py
```

The second command replays the unpruned search through 30,000, finds all seven
recorded two-term control pairs, checks them independently by trial division,
and finds no three-term pair in that small range. See the
[dated replay](verification/REPLAY-2026-09-13.json).

The larger C search needs a C compiler and explicit resource settings. Remote
orchestrators retain their original machine paths; follow the report before
launching a large run. Historical Lean checks require the recorded Mathlib
environment and were not rebuilt during this promotion.

## Provenance

All 23 files under `research/` are exact copies of the public source subtree.
[The source manifest](SOURCE-MANIFEST.json) pins its commit, original paths,
Git blob IDs and SHA-256 hashes. Historical paths inside source documents are
preserved. The former [mixed repository](https://github.com/jaredwilder/erdos-computational-searches)
remains the archive; this repository is the preferred problem-level entry.

Author: Jared Wilder. Source campaign: 2026-09-02. Focused release: 2026-09-13.
License: Apache-2.0, inherited from the public source.
