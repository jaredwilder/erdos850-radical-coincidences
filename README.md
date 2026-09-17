# Erdős #850 — Radical Coincidences

**Jared Wilder**

Search, structural lemmas, and exact controls for the problem of matching radicals at three consecutive integers.

With `rad(n)` denoting the product of the distinct prime divisors of `n`, the question is whether there exist distinct positive integers `x < y` with

```text
rad(x+i) = rad(y+i),  i = 0,1,2.
```

## Search result

The recorded large search found **no three-term pair with `max(x,y) <= 464,637,500,000`**.

The search uses contiguous global collision checks and an exact pruning rule derived from the difference lemma below. The full computation receipt is in [`research/receipts/MASTER-RECEIPT.json`](research/receipts/MASTER-RECEIPT.json).

## Difference lemma

Any matching length-`k` pair satisfies

```text
rad(x(x+1)...(x+k-1)) | (y-x).
```

This gives the main exact survivor filter used by the search.

The familiar two-term family

```text
x = 2^m - 2,
y = x(x+2)
```

never extends to a third coincidence. It is not exhaustive: `(75,1215)` is an explicit two-term pair outside that family.

## Start here

| File | Purpose |
|---|---|
| [Search report](research/SEARCH-REPORT-2026-09-02.md) | difference lemma, exact pruning, frontier, and corrections |
| [Master receipt](research/receipts/MASTER-RECEIPT.json) | large-search computation record |
| [Search code](research/scripts/) | segmented C sieve, unpruned controls, and independent verifier |
| [Lean source](research/kernel/) | two-term witnesses and the excluded power-of-two family |
| [Prior-art note](research/abc/PRIOR-ART-VERDICT-2026-09-02.md) | retired conditional abc route |

## Reproduce the controls

```sh
python verification/verify_source.py
python verification/run_controls.py
```

The control replay performs an unpruned search through 30,000, recovers all seven recorded two-term control pairs, verifies them independently by trial division, and finds no three-term pair in that range.

The larger search requires a C compiler and explicit resource settings; the research report records the production configuration.

**License:** Apache-2.0