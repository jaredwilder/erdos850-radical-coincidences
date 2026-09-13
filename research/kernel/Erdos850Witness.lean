/-
  Erdos 850 -- witness arm.

  Canonical statement (DeepMind formal-conjectures, Erdos850.erdos_850):
    exists x y : N, x != y and x.primeFactors = y.primeFactors
                    and (x+1).primeFactors = (y+1).primeFactors
                    and (x+2).primeFactors = (y+2).primeFactors

  A single concrete witness closes the affirmative branch by kernel computation.

  This file carries:
   (A) two_term_witness -- the KNOWN-ANSWER CONTROL. The 2-term relaxation does
       have witnesses (smallest x=2, y=8; next x=6, y=48). Kernel-checking these
       proves the Lean arm of this campaign works, independently of whether the
       3-term search finds anything.
   (B) family_never_extends -- the PROVED structural fact used in the report:
       the 2-term family x = 2^m - 2, y = x(x+2) can never satisfy the third
       coincidence, because that would force (x+1)^2 + 1 to be a power of two.
   (C) three_term_witness -- COMMENTED OUT. Instantiated only from a search
       receipt. An uninstantiated placeholder is not a result.

  NOTE ON TACTICS: `decide` cannot evaluate `Nat.primeFactors` in the kernel
  (`Nat.primeFactorsList` is well-founded recursion and gets stuck).  The route
  that does work is structural: rewrite each numeral as a product of prime
  powers and use `Nat.primeFactors_pow` / `Nat.primeFactors_mul` /
  `Nat.Prime.primeFactors`.  No `native_decide`, no extra axioms.
-/
import Mathlib

namespace Erdos850Search

/-- KNOWN-ANSWER CONTROL 1: the 2-term relaxation of Erdos 850 has a witness,
    x = 2, y = 8.  rad 2 = rad 8 = 2 and rad 3 = rad 9 = 3. -/
theorem two_term_witness :
    ∃ x y : ℕ, x ≠ y ∧ x.primeFactors = y.primeFactors
      ∧ (x + 1).primeFactors = (y + 1).primeFactors := by
  refine ⟨2, 8, by norm_num, ?_, ?_⟩
  · rw [show (8 : ℕ) = 2 ^ 3 by norm_num, Nat.primeFactors_pow 2 (by norm_num)]
  · rw [show (2 + 1 : ℕ) = 3 by norm_num, show (8 + 1 : ℕ) = 3 ^ 2 by norm_num,
        Nat.primeFactors_pow 3 (by norm_num)]

/-- KNOWN-ANSWER CONTROL 2: x = 6, y = 48, one family member up. -/
theorem two_term_witness_6_48 :
    (6 : ℕ).primeFactors = (48 : ℕ).primeFactors ∧
    (7 : ℕ).primeFactors = (49 : ℕ).primeFactors := by
  refine ⟨?_, ?_⟩
  · rw [show (6 : ℕ) = 2 * 3 by norm_num, show (48 : ℕ) = 2 ^ 4 * 3 by norm_num,
        Nat.primeFactors_mul (by norm_num) (by norm_num),
        Nat.primeFactors_mul (by norm_num) (by norm_num),
        Nat.primeFactors_pow 2 (by norm_num)]
  · rw [show (49 : ℕ) = 7 ^ 2 by norm_num, Nat.primeFactors_pow 7 (by norm_num)]

/-- KNOWN-ANSWER CONTROL 3 (negative): x = 75, y = 1215 is a 2-term solution
    that is NOT in the family y = x(x+2).  It refutes the "one family" claim. -/
theorem two_term_witness_75_1215_outside_family :
    (75 : ℕ).primeFactors = (1215 : ℕ).primeFactors ∧
    (76 : ℕ).primeFactors = (1216 : ℕ).primeFactors ∧
    (1215 : ℕ) ≠ 75 * (75 + 2) := by
  refine ⟨?_, ?_, by norm_num⟩
  · rw [show (75 : ℕ) = 3 * 5 ^ 2 by norm_num, show (1215 : ℕ) = 3 ^ 5 * 5 by norm_num,
        Nat.primeFactors_mul (by norm_num) (by norm_num),
        Nat.primeFactors_mul (by norm_num) (by norm_num),
        Nat.primeFactors_pow 5 (by norm_num), Nat.primeFactors_pow 3 (by norm_num)]
  · rw [show (76 : ℕ) = 2 ^ 2 * 19 by norm_num, show (1216 : ℕ) = 2 ^ 6 * 19 by norm_num,
        Nat.primeFactors_mul (by norm_num) (by norm_num),
        Nat.primeFactors_mul (by norm_num) (by norm_num),
        Nat.primeFactors_pow 2 (by norm_num), Nat.primeFactors_pow 2 (by norm_num)]

/-- The arithmetic core of the family-death argument: for odd t, t^2 + 1 is
    congruent to 2 mod 8, so the only power of two it can equal is 2 itself. -/
theorem odd_sq_succ_mod_eight (t : ℕ) (ht : t % 2 = 1) : (t * t + 1) % 8 = 2 := by
  have h : t % 8 = 1 ∨ t % 8 = 3 ∨ t % 8 = 5 ∨ t % 8 = 7 := by omega
  rcases h with h | h | h | h <;> rw [Nat.add_mod, Nat.mul_mod, h] <;> norm_num

/-- Hence for odd t >= 3, t^2 + 1 is never a power of two. -/
theorem odd_sq_succ_not_pow_two (t : ℕ) (ht : t % 2 = 1) (ht3 : 3 ≤ t) :
    ¬ ∃ j : ℕ, t * t + 1 = 2 ^ j := by
  rintro ⟨j, hj⟩
  have h2 : (t * t + 1) % 8 = 2 := odd_sq_succ_mod_eight t ht
  have h9 : 9 ≤ t * t := Nat.mul_le_mul ht3 ht3
  match j with
  | 0 => norm_num at hj; omega
  | 1 => norm_num at hj; omega
  | 2 => norm_num at hj; omega
  | (n + 3) =>
      have h0 : (2 : ℕ) ^ (n + 3) % 8 = 0 := by
        rw [pow_add]; simp [Nat.mul_mod]
      rw [hj] at h2; omega

/-- THE STRUCTURAL FACT.  The 2-term solution family x = 2^m - 2, y = x(x+2)
    can never satisfy the third coincidence.  There x + 2 = 2^m, so rad(x+2)=2,
    and y + 2 = (x+1)^2 + 1 = (2^m - 1)^2 + 1, which would have to be a power of
    two.  It is congruent to 2 mod 8 and exceeds 2, so it is not. -/
theorem family_never_extends (m : ℕ) (hm : 2 ≤ m) :
    ¬ ∃ j : ℕ, ((2 ^ m - 1) * (2 ^ m - 1) + 1) = 2 ^ j := by
  have h4 : 4 ≤ 2 ^ m := by
    calc (4 : ℕ) = 2 ^ 2 := by norm_num
    _ ≤ 2 ^ m := Nat.pow_le_pow_right (by norm_num) hm
  obtain ⟨c, hc⟩ : (2 : ℕ) ∣ 2 ^ m := dvd_pow_self 2 (by omega)
  exact odd_sq_succ_not_pow_two _ (by omega) (by omega)

/-  (C) THE REAL TARGET -- instantiate X, Y and their prime-power factorisations
    from the search receipt only.  No witness exists at the time of writing.

theorem three_term_witness :
    ∃ x y : ℕ, x ≠ y ∧ x.primeFactors = y.primeFactors
      ∧ (x + 1).primeFactors = (y + 1).primeFactors
      ∧ (x + 2).primeFactors = (y + 2).primeFactors := by
  refine ⟨X, Y, by norm_num, ?_, ?_, ?_⟩
  ...
-/

end Erdos850Search

#print axioms Erdos850Search.two_term_witness
#print axioms Erdos850Search.two_term_witness_6_48
#print axioms Erdos850Search.two_term_witness_75_1215_outside_family
#print axioms Erdos850Search.odd_sq_succ_mod_eight
#print axioms Erdos850Search.odd_sq_succ_not_pow_two
#print axioms Erdos850Search.family_never_extends
