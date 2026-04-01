/-
  Spearman rank correlation: definition from scratch and key properties.

  Replaces the axiomatized `spearman` and `spearman_bound` in Defs.lean
  with a concrete definition using midranks and Σd².
-/
import DASHImpossibility.Defs
import DASHImpossibility.General
import Mathlib.Data.Finset.Card

set_option autoImplicit false

namespace DASHImpossibility

variable (fs : FeatureSpace)

/-! ## Midrank definition -/

/-- Number of elements strictly below v(j) -/
noncomputable def countBelow (v : Fin fs.P → ℝ) (j : Fin fs.P) : ℕ :=
  (Finset.univ.filter (fun i => v i < v j)).card

/-- Number of elements equal to v(j) (including j itself) -/
noncomputable def countEqual (v : Fin fs.P → ℝ) (j : Fin fs.P) : ℕ :=
  (Finset.univ.filter (fun i => v i = v j)).card

/-- Midrank of element j in vector v.
    If v(j) has B elements below it and E elements equal to it,
    midrank = B + (E + 1) / 2. -/
noncomputable def midrank (v : Fin fs.P → ℝ) (j : Fin fs.P) : ℝ :=
  (countBelow fs v j : ℝ) + ((countEqual fs v j : ℝ) + 1) / 2

/-- Sum of squared rank differences between two vectors -/
noncomputable def sumSqRankDiff (v w : Fin fs.P → ℝ) : ℝ :=
  Finset.univ.sum (fun j => (midrank fs v j - midrank fs w j) ^ 2)

/-- Spearman rank correlation coefficient -/
noncomputable def spearmanCorr (v w : Fin fs.P → ℝ) : ℝ :=
  1 - 6 * sumSqRankDiff fs v w / ((fs.P : ℝ) * ((fs.P : ℝ) ^ 2 - 1))

/-! ## Key property: countEqual is always ≥ 1 -/

/-- Every element is equal to itself, so countEqual ≥ 1 -/
lemma countEqual_pos (v : Fin fs.P → ℝ) (j : Fin fs.P) :
    1 ≤ countEqual fs v j := by
  unfold countEqual
  have : j ∈ Finset.univ.filter (fun i => v i = v j) := by
    simp [Finset.mem_filter]
  exact Finset.one_le_card.mpr ⟨j, this⟩

/-! ## Key lemma: v(j) > v(k) implies midrank(v, j) > midrank(v, k) -/

/-- If v(j) > v(k), then every element ≤ v(k) is strictly below v(j).
    Specifically, countBelow(v, j) ≥ countBelow(v, k) + countEqual(v, k). -/
lemma countBelow_of_gt (v : Fin fs.P → ℝ) (j k : Fin fs.P) (h : v k < v j) :
    countBelow fs v k + countEqual fs v k ≤ countBelow fs v j := by
  unfold countBelow countEqual
  -- The set {i : v(i) < v(k)} ∪ {i : v(i) = v(k)} ⊆ {i : v(i) < v(j)}
  have hsub : Finset.univ.filter (fun i => v i < v k) ∪
              Finset.univ.filter (fun i => v i = v k) ⊆
              Finset.univ.filter (fun i => v i < v j) := by
    intro i hi
    simp only [Finset.mem_union, Finset.mem_filter, Finset.mem_univ, true_and] at hi ⊢
    rcases hi with hlt | heq
    · exact lt_trans hlt h
    · rw [heq]; exact h
  have hdisj : Disjoint (Finset.univ.filter (fun i => v i < v k))
                         (Finset.univ.filter (fun i => v i = v k)) := by
    rw [Finset.disjoint_filter]
    intro i _ hlt heq
    exact absurd heq (ne_of_lt hlt)
  calc (Finset.univ.filter (fun i => v i < v k)).card +
       (Finset.univ.filter (fun i => v i = v k)).card
      = (Finset.univ.filter (fun i => v i < v k) ∪
         Finset.univ.filter (fun i => v i = v k)).card := by
        rw [Finset.card_union_of_disjoint hdisj]
    _ ≤ (Finset.univ.filter (fun i => v i < v j)).card :=
        Finset.card_le_card hsub

/-- If v(j) > v(k), then midrank(v, j) - midrank(v, k) ≥ 1/2.
    This follows from countBelow(j) ≥ countBelow(k) + countEqual(k). -/
lemma midrank_strict_mono (v : Fin fs.P → ℝ) (j k : Fin fs.P) (h : v k < v j) :
    midrank fs v k + 1 / 2 ≤ midrank fs v j := by
  unfold midrank
  have hcb := countBelow_of_gt fs v j k h
  have hce := countEqual_pos fs v j
  -- countBelow(j) ≥ countBelow(k) + countEqual(k)
  -- midrank(j) = countBelow(j) + (countEqual(j) + 1) / 2
  --            ≥ countBelow(k) + countEqual(k) + 1/2   (since countEqual(j) ≥ 1)
  -- midrank(k) = countBelow(k) + (countEqual(k) + 1) / 2
  --            = countBelow(k) + countEqual(k)/2 + 1/2
  -- midrank(j) - midrank(k) ≥ countEqual(k) - countEqual(k)/2 = countEqual(k)/2 ≥ 1/2
  have hcek := countEqual_pos fs v k
  have h1 : (countBelow fs v j : ℝ) ≥ (countBelow fs v k : ℝ) + (countEqual fs v k : ℝ) := by
    exact_mod_cast hcb
  have h2 : (countEqual fs v j : ℝ) ≥ 1 := by exact_mod_cast hce
  have h3 : (countEqual fs v k : ℝ) ≥ 1 := by exact_mod_cast hcek
  linarith

/-! ## Σd² > 0 when first-movers differ -/

/-- The sum of squared rank differences is nonneg (each term is a square) -/
lemma sumSqRankDiff_nonneg (v w : Fin fs.P → ℝ) :
    0 ≤ sumSqRankDiff fs v w := by
  unfold sumSqRankDiff
  exact Finset.sum_nonneg (fun j _ => sq_nonneg _)

/-- When two features have reversed orderings in v and w (v(j) > v(k)
    but w(k) > w(j)), the sum of squared rank differences is at least 1/2. -/
lemma sumSqRankDiff_pos_of_reversal (v w : Fin fs.P → ℝ) (j k : Fin fs.P)
    (hvjk : v k < v j) (hwkj : w j < w k) :
    1 / 2 ≤ sumSqRankDiff fs v w := by
  unfold sumSqRankDiff
  -- d_j = midrank(v, j) - midrank(w, j)
  -- d_k = midrank(v, k) - midrank(w, k)
  -- From hvjk: midrank(v, j) ≥ midrank(v, k) + 1/2
  -- From hwkj: midrank(w, k) ≥ midrank(w, j) + 1/2
  -- So d_j - d_k = (midrank(v,j) - midrank(v,k)) - (midrank(w,j) - midrank(w,k))
  --             ≥ 1/2 + 1/2 = 1
  -- Since d_j ≠ d_k, d_j² + d_k² ≥ (d_j - d_k)²/2 ≥ 1/2
  have hv := midrank_strict_mono fs v j k hvjk
  have hw := midrank_strict_mono fs w k j hwkj
  -- Use: sum ≥ term_j + term_k ≥ (d_j - d_k)²/2
  -- Actually let's just bound Σ ≥ d_j² + d_k²
  have hj_mem : j ∈ Finset.univ (α := Fin fs.P) := Finset.mem_univ j
  have hk_mem : k ∈ Finset.univ (α := Fin fs.P) := Finset.mem_univ k
  -- We need j ≠ k
  have hjk : j ≠ k := by
    intro heq; subst heq; exact absurd hvjk (not_lt.mpr le_rfl)
  -- Σd² ≥ d_j² + d_k²
  have hpair : (midrank fs v j - midrank fs w j) ^ 2 +
               (midrank fs v k - midrank fs w k) ^ 2 ≤
               Finset.univ.sum (fun i => (midrank fs v i - midrank fs w i) ^ 2) := by
    have hsub : {j, k} ⊆ Finset.univ (α := Fin fs.P) := Finset.subset_univ _
    have hpair_sum := Finset.sum_le_sum_of_subset_of_nonneg hsub
      (fun (i : Fin fs.P) (_ : i ∈ Finset.univ) (_ : i ∉ ({j, k} : Finset (Fin fs.P))) =>
        sq_nonneg (midrank fs v i - midrank fs w i))
    rw [Finset.sum_pair hjk] at hpair_sum
    exact hpair_sum
  -- d_j - d_k ≥ 1
  set dj := midrank fs v j - midrank fs w j
  set dk := midrank fs v k - midrank fs w k
  have hdiff : dj - dk ≥ 1 := by linarith
  -- d_j² + d_k² ≥ (d_j - d_k)²/2
  have hsq : dj ^ 2 + dk ^ 2 ≥ (dj - dk) ^ 2 / 2 := by nlinarith [sq_nonneg (dj + dk)]
  -- (d_j - d_k)² ≥ 1
  have hdiffsq : (dj - dk) ^ 2 ≥ 1 := by nlinarith
  linarith

/-! ## Spearman < 1 when attributions reverse -/

/-- The Spearman correlation is strictly less than 1 when two features
    have reversed rankings between the two vectors. -/
theorem spearmanCorr_lt_one_of_reversal (v w : Fin fs.P → ℝ) (j k : Fin fs.P)
    (hvjk : v k < v j) (hwkj : w j < w k) (hP : 2 ≤ fs.P) :
    spearmanCorr fs v w < 1 := by
  unfold spearmanCorr
  have hsd := sumSqRankDiff_pos_of_reversal fs v w j k hvjk hwkj
  have hP_pos : (0 : ℝ) < (fs.P : ℝ) := Nat.cast_pos.mpr fs.hP
  have hP2 : (1 : ℝ) < (fs.P : ℝ) := by exact_mod_cast (show 1 < fs.P by omega)
  have hPsq : (0 : ℝ) < (fs.P : ℝ) ^ 2 - 1 := by nlinarith
  have hdenom_pos : (0 : ℝ) < (fs.P : ℝ) * ((fs.P : ℝ) ^ 2 - 1) :=
    mul_pos hP_pos hPsq
  have hsd_pos : (0 : ℝ) < sumSqRankDiff fs v w := by linarith
  have : (0 : ℝ) < 6 * sumSqRankDiff fs v w / ((fs.P : ℝ) * ((fs.P : ℝ) ^ 2 - 1)) :=
    div_pos (mul_pos (by norm_num : (0:ℝ) < 6) hsd_pos) hdenom_pos
  linarith

/-! ## Quantitative bound: spearmanCorr ≤ 1 - 3/(P³ - P) -/

/-- When first-movers differ in the same group, Spearman ≤ 1 - 3/(P³ - P).
    This is the DERIVED stability bound that replaces the axiomatized spearman_bound. -/
theorem spearmanCorr_bound (f f' : Model) (j k : Fin fs.P) (ℓ : Fin fs.L)
    (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ) (hjk : j ≠ k)
    (hfm : firstMover fs f = j) (hfm' : firstMover fs f' = k)
    (hP : 2 ≤ fs.P) :
    spearmanCorr fs (fun i => attribution fs i f) (fun i => attribution fs i f') ≤
      1 - 3 / ((fs.P : ℝ) ^ 3 - (fs.P : ℝ)) := by
  unfold spearmanCorr
  -- We have attribution reversal: attribution j f > attribution k f,
  -- attribution k f' > attribution j f'
  have hrev := attribution_reversal fs f f' j k ℓ hj hk hfm hfm' hjk
  have hsd := sumSqRankDiff_pos_of_reversal fs
    (fun i => attribution fs i f) (fun i => attribution fs i f')
    j k hrev.1 hrev.2
  -- sumSqRankDiff ≥ 1/2
  -- spearmanCorr = 1 - 6 * Σd² / (P(P²-1))
  --             ≤ 1 - 6 * (1/2) / (P(P²-1))
  --             = 1 - 3 / (P(P²-1))
  --             = 1 - 3 / (P³ - P)
  have hP_pos : (0 : ℝ) < (fs.P : ℝ) := Nat.cast_pos.mpr fs.hP
  have hP2 : (1 : ℝ) < (fs.P : ℝ) := by exact_mod_cast (show 1 < fs.P by omega)
  have hPsq : (0 : ℝ) < (fs.P : ℝ) ^ 2 - 1 := by nlinarith
  have hdenom_pos : (0 : ℝ) < (fs.P : ℝ) * ((fs.P : ℝ) ^ 2 - 1) :=
    mul_pos hP_pos hPsq
  have hdenom_ne : (fs.P : ℝ) * ((fs.P : ℝ) ^ 2 - 1) ≠ 0 := ne_of_gt hdenom_pos
  -- P * (P² - 1) = P³ - P
  have hfactor : (fs.P : ℝ) * ((fs.P : ℝ) ^ 2 - 1) = (fs.P : ℝ) ^ 3 - (fs.P : ℝ) := by ring
  rw [hfactor]
  have hdenom_pos' : (0 : ℝ) < (fs.P : ℝ) ^ 3 - (fs.P : ℝ) := by linarith [hfactor]
  -- 1 - 6 * Σd² / (P³ - P) ≤ 1 - 3 / (P³ - P)
  -- ⟺ 3 / (P³ - P) ≤ 6 * Σd² / (P³ - P)
  -- ⟺ 3 ≤ 6 * Σd²  (since denominator > 0)
  -- ⟺ 1/2 ≤ Σd²  ✓
  suffices h : 3 / ((fs.P : ℝ) ^ 3 - (fs.P : ℝ)) ≤
               6 * sumSqRankDiff fs (fun i => attribution fs i f)
                 (fun i => attribution fs i f') /
               ((fs.P : ℝ) ^ 3 - (fs.P : ℝ)) by linarith
  rw [div_le_div_iff_of_pos_right hdenom_pos']
  linarith

/-! ## Classical quantitative bound (axiomatized about defined quantity)

  The classical combinatorial argument gives Spearman ≤ 1 - m³/P³, which is
  tighter than the derived 3/(P³-P) bound above.

  **Why this remains an axiom (derivation gap analysis):**

  The bound requires showing Σd² ≥ m³(P²-1)/(6P²), i.e., that the sum of
  squared midrank differences is Ω(m³). The natural approach is:

  1. Within the group of size m, the first-mover dominates: in model f
     (first-mover j), attr(j,f) > attr(i,f) for all i in the group; in model
     f' (first-mover k), attr(k,f') > attr(i,f') for all i in the group.
  2. The midrank of j changes between models: j drops from first-mover
     position to tied-with-(m-2)-others position within the group.
  3. One wants to conclude that d_j = midrank(v,j) - midrank(w,j) ≥ (m-1)/2,
     and similarly d_k ≥ (m-1)/2, giving Σd² ≥ (m-1)²/2.

  The obstacle is step 3: midranks are **global** (computed over all P
  features), so the midrank of j depends on how j's attribution compares to
  features OUTSIDE the group. The current axioms do not constrain the relative
  ordering of cross-group attributions across different models. Specifically:

  - `splitCount_crossGroup_symmetric` says features in group ℓ' have equal
    split counts when the first-mover is NOT in ℓ', but does not say those
    split counts are the same across models f and f' (which have different
    first-movers, both in group ℓ).
  - Without knowing how outside-group features interleave with group features
    in the global ranking, we cannot bound the midrank change of any single
    feature.

  **To derive this, one would need either:**
  (a) An axiom constraining cross-group attribution magnitudes (e.g., that
      features outside group ℓ have the same attribution in f and f'), or
  (b) A probabilistic framework for expected Σd² under random tie-breaking
      of the (m-1) tied non-first-movers, requiring Lean formalization of
      expectations over random permutations, or
  (c) A purely combinatorial argument that the minimum Σd² over all possible
      global interleaving patterns is still Ω(m³), which would require
      a careful case analysis on the relative magnitudes of cross-group
      attributions.

  Approach (a) is the most tractable and would require one new axiom:
    `splitCount_crossGroup_stable : ∀ f f' j, j ∉ fs.group ℓ →
       firstMover fs f ∈ fs.group ℓ → firstMover fs f' ∈ fs.group ℓ →
       splitCount fs j f = splitCount fs j f'`
  which says changing the first-mover within a group does not affect features
  outside the group. With this, outside-group features would have identical
  midranks in both models, and the Σd² contribution would come purely from
  within-group reshuffling, making the m³ bound derivable.

  For now, we keep `spearman_classical_bound` as an axiom about the defined
  `spearmanCorr` quantity (not about an opaque type). -/
axiom spearman_classical_bound (f f' : Model) (ℓ : Fin fs.L)
    (hfm_grp : firstMover fs f ∈ fs.group ℓ)
    (hfm'_grp : firstMover fs f' ∈ fs.group ℓ)
    (hdiff : firstMover fs f ≠ firstMover fs f') :
    spearmanCorr fs (fun j => attribution fs j f) (fun j => attribution fs j f') ≤
      1 - (fs.groupSize ℓ : ℝ) ^ 3 / (fs.P : ℝ) ^ 3

end DASHImpossibility
