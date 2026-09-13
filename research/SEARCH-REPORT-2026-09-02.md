# Erdos 850 - exact segmented witness search

**NO WITNESS FOUND.** Nothing that satisfies rad(x)=rad(y), rad(x+1)=rad(y+1), rad(x+2)=rad(y+2)
with x != y exists below the frontier reached. Every positive statement below is an exhaustion
*inside a stated bound* and is COMPUTATION evidence, never a closure of the negative branch. Only
a verified witness closes anything.

**Ground gained.** The prior frontier was max(x,y) <= 30,000,000 (`MINE\probe850b.log`, brute
force, 21.8 s). This run replaces the brute force with an exact prune that is a *proved
implication*, and extends the frontier from 3 x 10^7 to **4.646 x 10^11** - a factor of 15,488 - in 1h46m of
box time, using 4 nice-10 cores for the first 84 minutes and 24 for the last 22.

Receipts: `oracle\evidence\msl-machine\campaigns\erdos850-search-2026-09-02\`
Scripts: same directory (`scripts/`), also in MINE. Remote dir `/root/peer/search850/`.
Question lock: `oracle/ledger/question-locks/erdos850-rad-triple-witness.json`, passed on every
launch command and copied beside the remote receipts as `QUESTION-LOCK.json`.

---

## 1. The design, and why it is not a sort-merge over 10^12 signatures

Naively the search stores a triple signature (rad n, rad(n+1), rad(n+2)) for every n <= N and
sorts. At N = 10^12 that is 32 TB of records. It is not the right shape.

### THE DIFFERENCE LEMMA (the whole search rests on this)

> Let k >= 1 and put **L_k(n) = rad( n(n+1)...(n+k-1) ) = lcm( rad n, ..., rad(n+k-1) )**.
> Suppose rad(x+i) = rad(y+i) for i = 0..k-1 with x < y. Then
>
>   **L_k(x) = L_k(y),  and  L_k(x) divides y - x.**

*Proof.* Let p be a prime dividing L_k(x). Then p divides x+i for some i in 0..k-1, so
p | rad(x+i) = rad(y+i) | y+i. Hence p | (y+i) - (x+i) = y - x. L_k(x) is squarefree (it is a
radical) and every one of its primes divides y - x, so L_k(x) | y - x. The prime set of
y(y+1)...(y+k-1) is the union of the prime sets of the rad(y+i) = rad(x+i), which is the prime
set of x(x+1)...(x+k-1); hence L_k(y) = L_k(x). ∎

**Consequence used as the prune.** If additionally 1 <= x < y <= N then
0 < y - x <= N - 1, and L_k(x) | y - x forces

>   **L_k(x) = L_k(y) <= N - 1 < N.**

So BOTH endpoints of any witness pair lie in the survivor set
**S_k(N) = { n : 1 <= n <= N, L_k(n) <= N }**.

This is exact and it is a proved implication, not a heuristic. Nothing is thrown away: a witness
that fails the test cannot exist.

**Why it collapses the problem.** L_3(n) = rad(n(n+1)(n+2)) is typically of size n^3 divided by a
small powerful part, so the survivor condition L_3(n) <= N is a violent filter above n ~ N^{1/3}.
Measured: over [1, 4.65 x 10^11] scanned with prune bound 10^12, the 3-term survivor set has
**32,751 members and every one of them is below 4.71 x 10^7**. The search therefore does no large
sort at all - it sieves L_3 exactly and collides a set small enough to hold in a few megabytes.

### The pipeline

| stage | tool | what it does |
|---|---|---|
| 1 | `e850.c` (clang -O3) | segmented radical sieve; emits every n with L_3(n) <= NMAX, and separately every n with L_2(n) <= NMAX2 |
| 2 | `drive850.py` | shards [1, TOP], atomic-mkdir claims so a second pool can join later |
| 3 | `e850_collide.py` | ONE global sort-merge of all survivors from all shards; collision detection; cross-checks; master receipt |
| 4 | `e850_verify.py` | INDEPENDENT re-verification (trial factorisation, no sieve, no shared code) |
| 5 | `Erdos850Witness.lean` | the kernel arm |

**Radical sieve, per segment [s, e).** rad[] starts at 1 and sm[] (the smooth part) starts at 1.
For each prime p <= sqrt(max value in the window): at multiples of p do `rad *= p` and `sm *= p`;
at multiples of p^2, p^3, ... do `sm *= p` again. Then `left = n / sm[n]` is either 1 or a single
prime greater than sqrt(n) (because every prime up to sqrt(max) has been divided out and
n <= max), and `rad *= left`. Two u64 arrays of SEG entries; SEG = 5 x 10^7, so **800 MB per
worker, flat, independent of N.** No floating point anywhere. `lcm` saturates at the cap: `t*b` is
formed only after checking `t <= cap/b`, so no product can overflow.

---

## 2. Receipt semantics - which claim was actually earned

**The collision structure is GLOBAL.** Every survivor signature from every segment of every shard
enters ONE sorted structure in `e850_collide.py`. Pairs that straddle segment or shard boundaries
ARE found. The per-segment counts in the receipt's `segments` table are **candidate counts only**
and are never a collision check; the weaker per-segment claim ("no pair inside this segment") is
not made anywhere.

Because the survivor set is the complete candidate set (Difference Lemma), the global merge over
survivors is equivalent to a global merge over all n <= N. So the claim earned is the strong one:

> **no witness pair (x, y) with max(x, y) <= frontier_N.**

The receipt carries `collision_scope: GLOBAL_ACROSS_ALL_SEGMENTS`, the frontier, the prune bound,
the coverage-gap list, and `EXHAUSTIVE_AND_COMPLETE` which is true only when coverage of
[1, frontier] is gapless AND all cross-checks pass AND the known-answer gate matched.

**Frontier is the CONTIGUOUS cover, not the count of finished shards.** `e850_frontier.py` walks
the segment logs and returns the largest F with [1, F] covered with no hole. Shards finished above
a hole do real work but do not raise the claim.

---

## 3. Known-answer control - the searcher must find what is already known

A 3-term search that returns zero is indistinguishable from a broken one. The control is the
**2-term relaxation** (rad x = rad y and rad(x+1) = rad(y+1), x != y), which has a known
non-empty answer set, run through the *same code path* with k = 2.

**Control result, bound 3,000,000: 10 pairs, and the pruned searcher and the naive no-prune
searcher agree on all 10, exactly.**

| x | y | rad x = rad y | rad(x+1) = rad(y+1) | on family y = x(x+2), x = 2^m - 2 |
|---|---|---|---|---|
| 2 | 8 | 2 | 3 | yes (m=2) |
| 6 | 48 | 6 | 7 | yes (m=3) |
| 14 | 224 | 14 | 15 | yes (m=4) |
| 30 | 960 | 30 | 31 | yes (m=5) |
| **75** | **1215** | **15** | **38** | **NO** |
| 62 | 3968 | 62 | 21 | yes (m=6) |
| 126 | 16128 | 42 | 127 | yes (m=7) |
| 254 | 65024 | 254 | 255 | yes (m=8) |
| 510 | 261120 | 510 | 511 | yes (m=9) |
| 1022 | 1046528 | 1022 | 1023 | yes (m=10) |

- Pruned pipeline (`e850.c` + `e850_collide.py`): 10 pairs.
- Naive dict search, no prune, SPF sieve over all n <= 3e6 (`e850_naive.py`): 10 pairs, identical.
- Every pair re-verified from first principles by `e850_verify.py` (trial factorisation, separate
  code path): 10/10 `WITNESS CONFIRMED`.
- The 3-term naive control over the same range: 0 pairs, agreeing with the pruned search.
- Radical sieve spot-check: a deterministic sample of engine-computed rad(n) values re-derived by
  trial division, 150/150 exact, 0 mismatches.

### Third implementation, no prune at all, at 3.3x the previous frontier

`e850_brute.c` is a separate program that uses **no part of the Difference Lemma**. It builds
rad(n) for every n with an in-memory radical sieve, sorts ALL n by the full triple, and reports
every adjacent duplicate. It is the brute force the prune claims to be equivalent to.

| run | result | time |
|---|---|---|
| `e850_brute --n 3000000 --k 2` | **10 collisions**, the exact list above, (75, 1215) included | 0 s |
| `e850_brute --n 3000000 --k 3` | 0 collisions | 0 s |
| `e850_brute --n 100000000 --k 3` | **0 collisions, NO_PRUNE** | 23 s |

The last row matters: an unpruned exhaustive sort over all 10^8 triples agrees with the pruned
pipeline, at **3.3x the previous 3 x 10^7 brute-force frontier**. Three independent
implementations (pruned C sieve, naive Python dict, unpruned C sort) agree on every number.

This exact set is now a **hard gate** in `e850_collide.py` (`known_answer_gate_below_3e6`): the
2-term collisions below 3e6 must equal these 10 pairs exactly - missing pairs fail the run, and
extra pairs are surfaced as `unexpected_new_findings` rather than silently absorbed.

### The "one family" claim is FALSE, and it matters

An independent scan reported that the 10 solutions "form ONE family, y = x(x+2) with x = 2^k - 2".
Nine of them do. **(75, 1215) does not**: 75 = 3 . 5^2 and 1215 = 3^5 . 5 both have radical 15;
76 = 2^2 . 19 and 1216 = 2^6 . 19 both have radical 38; and 75 . 77 = 5775, not 1215. It is
kernel-checked below.

This is load-bearing. Had the 2-term solution set really been that single family, the family-death
proof in section 4 would have closed the whole negative branch of Erdos 850 - because a 3-term
witness is in particular a 2-term solution. It does not, because off-family 2-term solutions
exist. **No structural prune is used anywhere in this search.** The only prune is the Difference
Lemma. Exhaustive means exhaustive.

---

## 4. The family-death proof (true, but NOT a prune)

**Claim.** For the family x = 2^m - 2, y = x(x+2) with m >= 2, the third coincidence is impossible.

*Proof.* Here x + 2 = 2^m, so rad(x+2) = 2. And
y + 2 = x(x+2) + 2 = x^2 + 2x + 2 = (x+1)^2 + 1 = (2^m - 1)^2 + 1.
The third condition rad(y+2) = rad(x+2) = 2 holds iff y+2 is a power of two. Now t = 2^m - 1 is
odd, so t^2 ≡ 1 (mod 8) and y + 2 = t^2 + 1 ≡ 2 (mod 8). The powers of two modulo 8 are
1, 2, 4, 0, 0, ... - the value 2 occurs only for 2^1 = 2. So y + 2 = 2, i.e. y = 0, contradicting
y = x(x+2) >= 8 for m >= 2. ∎

Kernel-checked, three theorems, no `sorry`, no `native_decide`:

| theorem | statement | axioms |
|---|---|---|
| `odd_sq_succ_mod_eight` | t odd → (t*t + 1) % 8 = 2 | `[propext, Quot.sound]` |
| `odd_sq_succ_not_pow_two` | t odd, t >= 3 → t*t + 1 is not a power of two | `[propext, Classical.choice, Quot.sound]` |
| `family_never_extends` | m >= 2 → (2^m - 1)^2 + 1 is not a power of two | `[propext, Classical.choice, Quot.sound]` |

**What this does NOT license.** It says no witness lies ON that family. Off-family 2-term
solutions exist ((75, 1215)), so it prunes nothing globally and is used for nothing except as an
honest structural fact. It was not applied to the search.

---

## 5. The Lean arm works - proved on the known answer

`decide` cannot close `Nat.primeFactors 2 = Nat.primeFactors 8` in the kernel: `Nat.primeFactorsList`
is well-founded recursion and reduction gets stuck at
`(Nat.primeFactorsList 2).dedup.isPerm (Nat.primeFactorsList 8).dedup`. The route that works is
structural - rewrite each numeral as a product of prime powers and apply `Nat.primeFactors_pow`,
`Nat.primeFactors_mul`, `Nat.Prime.primeFactors`.

Rather than ship an uninstantiated placeholder, the Lean arm is proved on the 2-term known answer,
in exactly the canonical shape of the target statement:

```
theorem two_term_witness :
    ∃ x y : ℕ, x ≠ y ∧ x.primeFactors = y.primeFactors
      ∧ (x + 1).primeFactors = (y + 1).primeFactors
```
VERIFIED, axioms `[propext, Classical.choice, Quot.sound]`, witness (2, 8). Also
`two_term_witness_6_48` and `two_term_witness_75_1215_outside_family` (which additionally
kernel-checks `1215 ≠ 75 * (75 + 2)`, the refutation of the one-family claim).

The 3-term theorem is present but **commented out** and carries no witness numerals. There is no
witness to instantiate it with. An uninstantiated placeholder is not a result.

Command used: `cd /root/mathlib4 && export PATH=/root/.elan/bin:$PATH && lake env lean
/root/peer/search850/Erdos850Witness.lean`, with `#print axioms` appended for every theorem.
File: `kernel/Erdos850Witness.lean`.

---

## 6. Frontier and segment accounting

**FRONTIER REACHED: max(x, y) <= 464,637,500,000** (4.646 x 10^11), contiguous, gapless,
global collision semantics. **0 three-term collisions.** Prior frontier was 3 x 10^7 - this is a
**15,488x extension**. Master receipt: `receipts/MASTER-RECEIPT.json`, sha256
`3649c0856bbdd0e67bf96c66c0503ffb65dd8ab108a5ddec311db06688b914ce`.

| band | segments | numbers scanned | 3-term survivors | 2-term survivors | 3-term collisions |
|---|---|---|---|---|---|
| 1 – 9,999,999 | 1 | 50,000,000 | 32,751 | 128,083 | 0 |
| 10^7 – 10^8-1 | 1 | 50,000,000 | 0 | 853 | 0 |
| 10^8 – 10^9-1 | 18 | 900,000,000 | 0 | 1,157 | 0 |
| 10^9 – 10^10-1 | 182 | 9,012,500,000 | 0 | 0 | 0 |
| 10^10 – 10^11-1 | 1,820 | 89,993,750,000 | 0 | 0 | 0 |
| 10^11 – 4.646 x 10^11 | 7,374 | 364,631,250,000 | 0 | 0 | 0 |
| **TOTAL to frontier** | **10,904** | **464,637,500,000** | **32,751** | **130,093** | **0** |

(The first two bands use one 5 x 10^7 segment each, so their survivor counts are reported at that
granularity. 2-term survivors are emitted only up to the separate 2-term bound 10^9, which is why
that column is zero above it - not an absence, a declared bound.)

Total numbers actually sieved, including shards finished above the contiguous frontier:
**539,687,500,000**. That extra work is real but is NOT part of the claim; only the gapless
prefix [1, 464,637,500,000] is.

**Cross-checks on the master receipt, all zero faults:**

| check | result |
|---|---|
| L recomputed from radicals (math.gcd) vs engine value | 0 mismatches / 162,844 rows |
| L <= prune bound re-asserted | 0 violations |
| rad(n+i) divides n+i re-asserted | 0 violations |
| coverage gaps in [1, frontier] | 0 |
| known-answer gate below 3 x 10^6 | EXACT_MATCH, 10 / 10 |
| independent trial-division re-verification of engine radicals | 200 / 200, 0 mismatches |
| `EXHAUSTIVE_AND_COMPLETE` | **true** |

**Live 2-term calibration, complete to 10^9: 14 solutions**, every one re-verified by trial
factorisation. The 4 above the control bound are (2046, 4190208), (4094, 16769024),
(8190, 67092480), (16382, 268402688) - all on the family, all `WITNESS CONFIRMED`. The signal is
alive at every scale, so a zero in the 3-term column is an absence, not a silent bug.

**The shape of the survivor set is the finding.** All 32,751 three-term survivors lie below
**47,045,880**; the largest is n = 47,045,880. From 4.7 x 10^7 to 4.6 x 10^11 - nine and a half
billion numbers of scanning - **not one further n satisfies rad(n(n+1)(n+2)) <= 10^12**. The
obstruction is not that we have not looked far enough.

**Run accounting.** Launched 14:07 UTC on 4 workers at nice 10; ramped to 24 at 15:31 UTC once the
erdos289 job's processes exited (gate condition logged in `logs/watch850.log` as
`drive289_gone` - 289 wrote no new master receipt, so the fallback condition fired and is recorded
as such); stopped at 15:53 UTC on operator order reallocating the box to the 273 hunt. All
workers confirmed terminated, 0 cores held. Segment logs are flushed per segment, so the killed
in-flight shards contribute exactly the segments they completed and nothing more.

---

## 7. Agreement with the peer's independent algorithm

A peer session ran a completely different algorithm on the same box - a triple-signature hash over
a contiguous in-memory range, no Difference Lemma, no segmentation. Its receipt
(`peer-net/erdos850-RECEIPT.json`, written by that session, not by this one) reports:

| | peer net | this search |
|---|---|---|
| algorithm | in-memory triple-signature hash | segmented radical sieve + Difference Lemma prune |
| 2-term control below 3e6 | 10 found, 0 missing, 0 unexpected | 10 found, 0 missing, 0 unexpected |
| control trusted | true | true (`EXACT_MATCH`) |
| 3-term frontier | max(x,y) <= 1,000,000,000 | max(x,y) <= 464,637,500,000 |
| witnesses | 0 | 0 |

**Two independent algorithms agree exactly on the whole overlap [1, 10^9], including the full
2-term control set with the off-family (75, 1215).** The disagreement risk that matters - one of
them silently returning zero - is closed from both sides.

---

## 8. What is open

- The negative branch of Erdos 850 is **untouched**. A bound is a bound.
- The Difference Lemma makes the cost of extending the frontier linear in N with a flat 800 MB
  per worker, so the frontier is a pure function of core-hours. There is no memory wall to hit.
- The 3-term survivor set being entirely below 4.71 x 10^7 while the scan ran to 4.65 x 10^11 is itself the
  interesting object: it says the obstruction is not "we have not looked far enough" but that
  rad(n(n+1)(n+2)) grows too fast for two members to be within N of each other. Turning that
  observation into a conditional non-existence proof (under ABC, say) is the next real move, and
  it is a proof task, not a compute task.

## CORRECTION (2026-09-02, prior-art verdict abc/PRIOR-ART-VERDICT-2026-09-02.md)

The conditional non-existence move described above was made in 1993. Langevin (C. R. Acad. Sci. Paris 317, 1993) proved that abc implies the k=3 Erdős-Woods statement up to finitely many exceptions; Balasubramanian-Langevin-Shorey-Waldschmidt (Monatsh. Math. 121, 1996) give the finiteness in the separate-equalities form that is canonical 850; and erdosproblems.com/850 itself records Shorey-Tijdeman 2016: under Baker's explicit abc the answer to 850 is NO. This search owns only the computational bound (no witness with max(x,y) <= 4.646e11) and the kernel-checked side facts; the survivor collapse below 4.71e7 is the empirical shadow of the published conditional theorem, not a claim of ours. Also: L(x) is the lcm of three squarefree radicals, so L(x) | (y-x) exactly, no factor of 2.
