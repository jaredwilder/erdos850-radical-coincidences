# Erdős 850 — "abc implies finiteness": PRIOR-ART VERDICT

**Date:** 2026-09-02
**Task:** Part 1 (prior art) then Part 2 (Lean) only if UNRECORDED/PARTIAL.
**Bottom line:**

> ## VERDICT: **RECORDED.** Published 1993 (Langevin), restated 1996 and 2016.
> **Part 2 was NOT run.** The candidate conditional theorem is a known published result.
> Zero Lean proof work was attempted. No new mathematics is available on this line.

The candidate theorem — *under the abc conjecture there are only finitely many pairs
x ≠ y with primeFactors(x+i) = primeFactors(y+i) for i = 0,1,2* — is **exactly** the
statement Langevin proved in 1993, and it is **stated on the Erdős 850 problem page
itself**. Our sketch is a correct rediscovery, not a discovery.

---

## 1. The three recordings

### (a) The Erdős 850 page states it outright

`https://www.erdosproblems.com/850` (page last edited 28 Sep 2025), verbatim:

> "Shorey and Tijdeman **[ShTi16]** have shown that, assuming a strong form of the
> **ABC conjecture** due to Baker, then the answer to the original problem is **no**."

Also on the page: "This is sometimes known as the **Erdős–Woods conjecture**."

So the abc-conditional attack is not merely in the literature — it is recorded in the
one place any session working this problem is guaranteed to look. **This should have
been the first fetch of the campaign.**

- Retrieved: raw page + `https://www.erdosproblems.com/latex/850` (bibliography).
- Reference resolved on that page:
  **[ShTi16]** Shorey, Tarlok N. and Tijdeman, Rob, *Arithmetic properties of blocks of
  consecutive integers*, (2016), 455–471. — appears in the Springer volume
  *From Arithmetic to Zeta-Functions*, `https://link.springer.com/chapter/10.1007/978-3-319-28203-9_27`.
  Its abstract states that **the explicit abc-conjecture implies the Erdős–Woods
  conjecture for each k > 2.**
- Also on the page: **[Ma68]** Makowski, *On a problem of Erdős*, Enseign. Math. (2)
  (1968), 193 — this is the published source of the **(75, 1215)** off-family solution
  that tonight's search rediscovered and kernel-checked. That too is prior art, from 1968.
- Comments (4, read in full via `https://www.erdosproblems.com/forum/discuss/850`):
  **nothing relevant.** All four are Neel Somani / Thomas Bloom / Terence Tao discussing
  whether "integer" means "positive integer". No abc content, no finiteness content.

### (b) Langevin 1993 — the exact plain-abc finiteness statement

From Abderrahmane Nitaj's abc-conjecture bibliography (author page, CNRS/LMNO),
`https://nitaj.users.lmno.cnrs.fr/abc.html`, "Consequences" section, item 4, verbatim:

> "**The Erdös-Woods conjecture.** It was conjectured by Erdös and Woods that there
> exists an absolute constant k > 2 such that for every positive integers x and y, if
> rad(x+i)=rad(y+i) for i=1,2,...,k then x=y. No examples with different x and y are
> known. **Langevin [Lan1, Lan2] proved that the abc conjecture implies the Erdös-Woods
> conjecture with k=3 except perhaps a finite number of counter examples.**"

That final sentence **is our candidate theorem**, word for word in substance:
plain (asymptotic) abc ⟹ the k = 3 case holds with at most finitely many exceptions
⟺ the solution set of Erdős 850 is finite.

Citations, verbatim from the same page's bibliography:

- **[Lan1]** Langevin, Michel. *Partie sans facteur carré d'un produit d'entiers voisins.*
  (Square-free divisor of a product of neighbouring integers.) Approximations
  diophantiennes et nombres transcendants, C.-R. Colloq., Luminy/Fr. 1990, 203–214 (1992).
- **[Lan2]** Langevin, M. *Cas d'égalité pour le théorème de Mason et applications de la
  conjecture (abc).* (Extremal cases for Mason's theorem and applications of the (abc)
  conjecture.) **C. R. Acad. Sci., Paris, Sér. I 317, No. 5, 441–444 (1993).**

Note [Lan1]'s title — *"square-free divisor of a product of neighbouring integers"* — is
literally the object our sketch calls **L(x) = rad(x(x+1)(x+2))**. The 1992/93 papers
are working with the same quantity by the same name.

### (c) Balasubramanian–Langevin–Shorey–Waldschmidt 1996 — finiteness, generalized

Same page, immediately following:

> "It is shown in **[Bal-Lan-Sho-Wal]** that the correctness of the abc conjecture implies
> that for each pair (d,d') of positive integers, **the set of pairs (x,y) satisfying
> K(x,y,d,d') > 2 is finite**, and the set of quadruples (x,y,d,d') satisfying
> K(x,y,d,d') > 4 is also finite."

where K is the largest K with rad(x+id) = rad(y+id') for i = 0..K−1. Setting d = d' = 1,
"K > 2" is precisely three coincidences at i = 0,1,2 — **Erdős 850 — and the conclusion is
precisely finiteness.** This is a second, independent published recording of the exact
statement, in a stronger (arithmetic-progression) form.

- **[Bal-Lan-Sho-Wal]** Balasubramanian, R.; Langevin, M.; Shorey, T. N.; Waldschmidt, M.
  *On the maximal length of two sequences of integers in arithmetic progressions with the
  same prime divisors.* **Monatsh. Math. 121, No. 4, 295–307 (1996).**

### (d) Recent restatement (2025)

Noah Lebowitz-Lockard, *On pairs of consecutive sequences with the same radicals*
(arXiv:2507.09899, 2025) restates it as: *Langevin proved that simply assuming the abc
Conjecture implies that there are no distinct integers m and n for which
rad(m+i) = rad(n+i) for all i ∈ {0,1,2}.* Lebowitz-Lockard is credited in the
"Additional thanks" line on the erdosproblems.com/850 page.

⚠️ **Provenance caveat, stated honestly:** this last item is the one source I did **not**
fetch directly. The local `literature_guard.py` PreToolUse hook blocked WebFetch on
`arxiv.org` (correctly — it is doing its job). I did **not** bypass it. The content above
is from search-result summaries only, so treat (d) as *corroborating*, not *load-bearing*.
Items (a), (b), (c) were each fetched and read directly and are load-bearing on their own.

---

## 2. How our sketch compares to what is published

| | our sketch | Langevin 1993 / BLSW 1996 | Shorey–Tijdeman 2016 |
|---|---|---|---|
| abc form used | plain asymptotic abc | plain asymptotic abc | **Baker's explicit/strong** abc |
| conclusion | **finitely many** pairs | **finitely many** pairs (k=3) | **no** pairs at all, every k > 2 |
| status | rediscovery | published | published |

Our version sits exactly on the Langevin line: same hypothesis, same conclusion, same k.
It is strictly **weaker** than Shorey–Tijdeman, who pay with a stronger hypothesis
(Baker's explicit abc, which carries numerical constants) and buy outright non-existence
rather than finiteness — which is what makes their result quotable as "the answer is no".

Our sketch's mechanism is also the standard one. The Difference Lemma
(L(x) | y − x, hence L(y) = L(x) < 2y) plus the abc triple **1 + y(y+2) = (y+1)²** is the
textbook route; that triple is the classical worked example in essentially every abc
survey. Nothing in our chain is unusual.

**One technical note on our own sketch, for the record:** the "factor 2 handles the shared
prime between x and x+2" remark is not needed and slightly misstates the lemma. L(x) is
defined as rad of the *product*, i.e. the **lcm** of the three radicals, which is
squarefree; every prime dividing it divides y − x, so **L(x) | (y − x)** directly, with no
factor of 2. The factor 2 would only appear if one used the *product* of the three
radicals rather than their lcm — and x, x+2 do share the prime 2 when x is even, which is
exactly why the lcm is the right object. Tonight's SEARCH-REPORT states the lemma
correctly (§1, Difference Lemma); the task brief's restatement introduced the spurious 2.

---

## 3. Product form vs. three separate equalities (coordinator's question)

They are **different hypotheses**, and the direction matters:

- Three separate equalities `rad(x+i) = rad(y+i)`, i = 0,1,2 (the **canonical 850 form**)
  **imply** the product form `rad(x(x+1)(x+2)) = rad(y(y+1)(y+2))`, since each side is the
  union of the three prime sets. The converse is false.
- So {separate solutions} ⊆ {product solutions}, and **finiteness for the product form
  would imply finiteness for 850**.

**But that implication chain is not needed here.** Langevin, Nitaj's statement of it, and
BLSW all state the result for the **separate** form — `rad(x+i) = rad(y+i)` for each i —
which *is* the canonical Erdős 850 / Erdős–Woods form. The literature records the exact
problem, not a weaker relative of it.

Worth noting: our own Difference Lemma also **requires** the separate equalities (it needs
p | rad(x+i) ⟹ p | rad(y+i) ⟹ p | y+i for each individual i). The product-form
hypothesis alone would not license it. So our sketch is a separate-form argument too.

---

## 4. Part 2 — NOT RUN

Per the RECORDED verdict and the coordinator's standing instruction, no Lean lemmas were
attempted. **Nothing was proved, nothing was kernel-checked, no receipts exist for any
abc-conditional statement.** There is no VERIFIED/OPEN lemma table to report because no
lemma was opened.

Box usage this task: **two read-only ssh calls** (Mathlib name lookup, below). No Lean
process was started. No compute was spent.

The only thing written into
`oracle/evidence/msl-machine/campaigns/erdos850-search-2026-09-02/abc/` is a copy of this
prior-art verdict (`PRIOR-ART-VERDICT-2026-09-02.md`), so the campaign directory itself
records that this line is closed and no future session re-runs it. **No Lean file, no
receipt, and no theorem artifact was created there**, because none was earned.

### Findings that survive for whoever picks this up later

Two facts checked on the box (`/root/mathlib4` @ `919544d4`) that the task brief guessed at:

1. **`Nat.radical` does NOT exist.** The Mathlib name is
   **`UniqueFactorizationMonoid.radical`** (`Mathlib/RingTheory/Radical/Basic.lean:142`),
   defined as `(primeFactors a).prod id` over a `UniqueFactorizationMonoid`. It applies to
   ℕ directly. Defining `rad n := n.primeFactors.prod id` locally gives the identical term,
   so either route is fine.
2. **Mathlib has no abc conjecture file** (nothing matching `abc`/`mason` in
   `Mathlib/NumberTheory/`). abc must therefore be carried as an explicit hypothesis, as
   the task brief assumed. That part of the brief was right.
3. **The DeepMind formal statement is a `sorry` stub.** `google-deepmind/formal-conjectures`
   `FormalConjectures/ErdosProblems/850.lean` contains `theorem erdos_850 : answer(sorry) ↔ ∃ x y : ℕ, ...`
   with `sorry` and a TODO. The *statement* is formalized; **no conditional theorem is
   proved there.**

---

## 5. What a Lean formalization would actually be worth — one line

**A certified artifact, not new mathematics:** formalizing Langevin/Shorey–Tijdeman's
*known* conditional theorem in Lean 4 would produce the first machine-checked proof that
abc ⟹ Erdős 850 is finite — genuinely valuable as a formalization contribution (the
DeepMind entry is a bare `sorry`), but it must be labelled everywhere as **a formalization
of a published 1993 result, conditional on abc**, and never as a new theorem or as progress
on Erdős 850 itself.

Honest effort estimate if it is ever commissioned: the arithmetic core (Difference Lemma,
the coprime abc triple, the final bound) is **hours** — it is elementary and the
deterministic ladder handles it. Getting from "y is bounded" to a clean
`Set.Finite {p : ℕ × ℕ | ...}` in Mathlib idiom, with the abc hypothesis stated in a form
that is actually the standard conjecture and not an accidentally-vacuous variant, is
**1–2 days**. The real risk is not the maths, it is stating abc wrongly and proving
something empty — which is a threat-model this estate already names.

---

## 6. Standing correction for the campaign record

`SEARCH-REPORT-2026-09-02.md` §8 currently reads:

> "Turning that observation into a conditional non-existence proof (under ABC, say) is the
> next real move, and it is a proof task, not a compute task."

**That next move is already done and published.** The line should be amended to cite
Langevin 1993 and Shorey–Tijdeman 2016, or it will send another session down this same
path. The search work itself is unaffected and remains sound — a frontier of
4.646 × 10¹¹ with three agreeing implementations is real, and the observed structural
collapse (all 32,751 three-term survivors below 4.71 × 10⁷) is exactly the *empirical*
shadow of the *published conditional* theorem. Those two facts corroborate each other
nicely; neither is diminished. But the theorem is not ours to claim.

---

## Sources

- [Erdős Problem #850 — erdosproblems.com](https://www.erdosproblems.com/850) (T. F. Bloom, accessed 2026-09-02)
- [Erdős 850 LaTeX source / bibliography](https://www.erdosproblems.com/latex/850)
- [Erdős 850 discussion thread (4 comments)](https://www.erdosproblems.com/forum/discuss/850)
- [A. Nitaj, "The abc conjecture" bibliography — Consequences §4 + [Lan1][Lan2][Bal-Lan-Sho-Wal]](https://nitaj.users.lmno.cnrs.fr/abc.html)
- [Shorey & Tijdeman, "Arithmetic Properties of Blocks of Consecutive Integers" (Springer, 2016)](https://link.springer.com/chapter/10.1007/978-3-319-28203-9_27)
- [google-deepmind/formal-conjectures — ErdosProblems/850.lean](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/850.lean)
- [OEIS A343101](https://oeis.org/A343101)
