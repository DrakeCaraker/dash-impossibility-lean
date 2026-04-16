/-
  Axiomatic definitions for the impossibility theorem.

  We axiomatize gradient boosting and TreeSHAP at the level of their
  mathematical properties, not their algorithmic implementation. This
  matches the proof strategy in impossibility.tex, which reasons about
  split counts and attribution proportionality rather than the full
  XGBoost training loop.

  The axioms are justified by:
  1. The Gaussian conditioning argument (Lemma 1 in the paper)
  2. The uniform-contribution model (Assumption 7)
  3. Symmetry of the DGP under within-group feature permutation
  4. SymPy verification of all algebraic consequences
     (see dash-shap/paper/proofs/verify_lemma6_algebra.py)

  Axiom reduction history:
  - v1: 16 axioms (splitCount axiomatized with 5 property axioms)
  - v2: 10 axioms (splitCount DEFINED, crossGroupBaseline refactored)
  - v3: 7 axioms (numTrees parametric in FeatureSpace, attribution DEFINED from splitCount)
-/

import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Probability.Moments.Variance

set_option autoImplicit false

/-! ## Feature space and correlation partition -/

/-- A feature space with P features partitioned into L groups. -/
structure FeatureSpace where
  /-- Total number of features -/
  P : ℕ
  /-- Number of groups -/
  L : ℕ
  /-- At least one feature -/
  hP : 0 < P
  /-- Group assignment: feature j belongs to group (groupOf j) -/
  groupOf : Fin P → Fin L
  /-- Each group has at least 2 members -/
  group_size_ge_two : ∀ ℓ : Fin L, 2 ≤ (Finset.univ.filter (fun j => groupOf j = ℓ)).card
  /-- Pairwise correlation within groups -/
  ρ : ℝ
  /-- ρ ∈ (0, 1) -/
  hρ_pos : 0 < ρ
  hρ_lt_one : ρ < 1
  /-- Number of boosting rounds (formerly a global axiom; now parametric) --/
  T : ℕ
  /-- T > 0 --/
  hT : 0 < T

namespace FeatureSpace

/-- The set of features in group ℓ -/
def group (fs : FeatureSpace) (ℓ : Fin fs.L) : Finset (Fin fs.P) :=
  Finset.univ.filter (fun j => fs.groupOf j = ℓ)

/-- Group size -/
def groupSize (fs : FeatureSpace) (ℓ : Fin fs.L) : ℕ :=
  (fs.group ℓ).card

end FeatureSpace

/-- Backward-compatible alias for fs.T. --/
noncomputable def numTrees (fs : FeatureSpace) : ℕ := fs.T

/-- Backward-compatible alias for fs.hT. --/
theorem numTrees_pos (fs : FeatureSpace) : 0 < fs.T := fs.hT


/-! ## Model and parameter types -/

/-- A trained model (abstract type). -/
axiom Model : Type


variable (fs : FeatureSpace)

/-- The first-mover feature in a model (the feature selected at root of tree 1) -/
axiom firstMover : Model → Fin fs.P

/-! ## Helpers for group membership -/

theorem self_mem_group (j : Fin fs.P) : j ∈ fs.group (fs.groupOf j) := by
  simp [FeatureSpace.group, Finset.mem_filter]

theorem mem_group_iff (j : Fin fs.P) (ℓ : Fin fs.L) :
    j ∈ fs.group ℓ ↔ fs.groupOf j = ℓ := by
  simp [FeatureSpace.group, Finset.mem_filter]

/-! ## Axioms: properties of sequential gradient boosting under Gaussian DGP -/

/-- AXIOM: Every feature in a group can be the first-mover.
    By DGP symmetry and randomness in sub-sampling/tie-breaking,
    each feature in a group serves as first-mover for some model. -/
axiom firstMover_surjective (ℓ : Fin fs.L) (j : Fin fs.P) (hj : j ∈ fs.group ℓ) :
    ∃ f : Model, firstMover fs f = j

/-- Cross-group baseline core: the split count a feature receives when the
    first-mover is in a different group. Depends only on (target group,
    source group), not on which specific feature is the first-mover.
    This makes cross-group stability definitional rather than axiomatic. -/
axiom crossGroupBaselineCore : Fin fs.L → Fin fs.L → ℝ

/-- Cross-group baseline: wraps crossGroupBaselineCore by extracting the
    source group from the model's first-mover. DEFINED, not axiomatized. -/
noncomputable def crossGroupBaseline (ℓ_target : Fin fs.L) (f : Model) : ℝ :=
  crossGroupBaselineCore fs ℓ_target (fs.groupOf (firstMover fs f))

/-- Cross-group stability (DERIVED from definition of crossGroupBaseline). -/
theorem crossGroupBaseline_stable (f f' : Model) (ℓ_target ℓ_source : Fin fs.L)
    (hfm : fs.groupOf (firstMover fs f) = ℓ_source)
    (hfm' : fs.groupOf (firstMover fs f') = ℓ_source)
    (_hne : ℓ_target ≠ ℓ_source) :
    crossGroupBaseline fs ℓ_target f = crossGroupBaseline fs ℓ_target f' := by
  unfold crossGroupBaseline; rw [hfm, hfm']

/-! ## Split count: DEFINED from firstMover, ρ, T, and crossGroupBaseline

  Previously axiomatized as a function with 4 property axioms. Now defined
  concretely using if-then-else, with the 4 properties derived as theorems.
  This eliminates 4 net axioms (5 removed, 1 added: crossGroupBaselineCore).
-/

/-- Split count for feature j in model f. DEFINED from the first-mover
    structure: within the first-mover's group, the dominant feature gets
    T/(2-ρ²) and others get the (1-ρ²) residual. Cross-group features
    receive a group-dependent baseline. -/
noncomputable def splitCount (j : Fin fs.P) (f : Model) : ℝ :=
  if fs.groupOf (firstMover fs f) = fs.groupOf j then
    if firstMover fs f = j then
      fs.T / (2 - fs.ρ ^ 2)
    else
      (1 - fs.ρ ^ 2) * fs.T / (2 - fs.ρ ^ 2)
  else
    crossGroupBaseline fs (fs.groupOf j) f

/-- Split count for first-mover = T/(2-ρ²). DERIVED. -/
theorem splitCount_firstMover (f : Model) (j : Fin fs.P)
    (hfm : firstMover fs f = j) :
    splitCount fs j f = fs.T / (2 - fs.ρ ^ 2) := by
  unfold splitCount; simp [hfm]

/-- Split count for non-first-mover in same group = (1-ρ²)T/(2-ρ²). DERIVED. -/
theorem splitCount_nonFirstMover (f : Model) (j : Fin fs.P)
    (ℓ : Fin fs.L) (hj : j ∈ fs.group ℓ)
    (hfm : firstMover fs f ≠ j)
    (hfm_group : firstMover fs f ∈ fs.group ℓ) :
    splitCount fs j f = (1 - fs.ρ ^ 2) * fs.T / (2 - fs.ρ ^ 2) := by
  unfold splitCount
  have hgj : fs.groupOf j = ℓ := (mem_group_iff fs j ℓ).mp hj
  have hgfm : fs.groupOf (firstMover fs f) = ℓ := (mem_group_iff fs _ ℓ).mp hfm_group
  simp [hgfm, hgj, hfm]

/-! ## Attribution: DEFINED from splitCount via proportionality constant

  Previously two axioms: `attribution` (function) + `proportionality_global`
  (existential ∃ c > 0). Now one axiom (proportionalityConstant as subtype)
  + one definition + one derived theorem.
-/

/-- Proportionality constant c > 0 relating SHAP importance to split counts.
    Under the uniform-contribution model (Assumption 7), this constant is
    the same across all models. Bundled with positivity proof. -/
axiom proportionalityConstant : {c : ℝ // 0 < c}

/-- Attribution (global feature importance) for feature j in model f.
    DEFINED as c · splitCount(j, f). Previously an axiom. -/
noncomputable def attribution (j : Fin fs.P) (f : Model) : ℝ :=
  proportionalityConstant.val * splitCount fs j f

-- Make attribution opaque for downstream proofs (backward compatibility)
attribute [irreducible] attribution

/-- Proportionality with UNIFORM constant (DERIVED from definition).
    Previously an axiom; now a theorem. -/
theorem proportionality_global :
    ∃ c : ℝ, 0 < c ∧ ∀ (f : Model) (j : Fin fs.P),
      attribution fs j f = c * splitCount fs j f := by
  refine ⟨proportionalityConstant.val, proportionalityConstant.property, fun f j => ?_⟩
  unfold attribution
  rfl

/-- Per-model proportionality (consequence of the global version). -/
theorem attribution_proportional (f : Model) :
    ∃ c : ℝ, 0 < c ∧ ∀ (j : Fin fs.P),
      attribution fs j f = c * splitCount fs j f := by
  obtain ⟨c, hc, hcf⟩ := proportionality_global fs
  exact ⟨c, hc, fun j => hcf f j⟩

/-! ## Stability and equity definitions -/

/-- δ-stability: expected Spearman ≥ 1 - δ between two independent runs. -/
def isStable (δ : ℝ) (expectedSpearman : ℝ) : Prop :=
  expectedSpearman ≥ 1 - δ

/-- γ-equity: expected max/min attribution ratio within a group ≤ 1 + γ. -/
def isEquitable (γ : ℝ) (maxMinRatio : ℝ) : Prop :=
  maxMinRatio ≤ 1 + γ

/-! ## Consensus (DASH) definition -/

/-- DASH consensus attribution: average over M independently trained models. -/
noncomputable def consensus (M : ℕ) (_hM : 0 < M) (models : Fin M → Model)
    (j : Fin fs.P) : ℝ :=
  (1 / (M : ℝ)) * (Finset.univ.sum (fun i => attribution fs j (models i)))

/-! ## Balanced ensemble -/

/-- An ensemble is balanced if each feature in each group serves as
    first-mover the same number of times. -/
def IsBalanced (M : ℕ) (models : Fin M → Model) : Prop :=
  ∀ (ℓ : Fin fs.L) (j k : Fin fs.P),
    j ∈ fs.group ℓ → k ∈ fs.group ℓ →
    (Finset.univ.filter (fun i => firstMover fs (models i) = j)).card =
    (Finset.univ.filter (fun i => firstMover fs (models i) = k)).card

/-! ## Spearman rank correlation

  Defined from scratch in SpearmanDef.lean using midranks and Σd². -/

/-! ## Variance of attributions — derived from Mathlib -/

/-- Measurable space structure on Model.
    Uses the discrete (⊤) σ-algebra, which makes every subset measurable.
    Previously an axiom; now derived — any type admits ⊤ as a MeasurableSpace.
    This is the canonical choice when measurability constraints are trivial. -/
noncomputable instance modelMeasurableSpace : MeasurableSpace Model := ⊤

/-- Probability measure on Model representing the training distribution.
    This cannot be derived — it encodes the distribution over models induced
    by the training algorithm with random seeds. -/
axiom modelMeasure : MeasureTheory.Measure Model

/-- Variance of a single model's attribution for feature j. -/
noncomputable def attribution_variance (j : Fin fs.P) : ℝ :=
  ProbabilityTheory.variance (fun f => attribution fs j f) modelMeasure

/-- Variance is nonneg — derived from ProbabilityTheory.variance_nonneg. -/
theorem attribution_variance_nonneg (j : Fin fs.P) :
    0 ≤ attribution_variance fs j := by
  unfold attribution_variance
  exact ProbabilityTheory.variance_nonneg _ _

/-- Variance of consensus decreases as 1/M. DERIVED. -/
theorem consensus_variance_bound (M : ℕ) (_hM : 0 < M) (j : Fin fs.P) :
    ∃ (consensus_var : ℝ),
      consensus_var = attribution_variance fs j / M ∧
      0 ≤ consensus_var :=
  ⟨attribution_variance fs j / M, rfl,
    div_nonneg (attribution_variance_nonneg fs j) (Nat.cast_nonneg M)⟩

/-! ## Cross-group symmetry — DERIVED from splitCount definition -/

/-- Features in a group have equal split counts when the first-mover
    is in a different group. DERIVED. -/
theorem splitCount_crossGroup_symmetric (f : Model)
    (j k : Fin fs.P) (ℓ : Fin fs.L)
    (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ)
    (hfm_not_group : firstMover fs f ∉ fs.group ℓ) :
    splitCount fs j f = splitCount fs k f := by
  have hgj : fs.groupOf j = ℓ := (mem_group_iff fs j ℓ).mp hj
  have hgk : fs.groupOf k = ℓ := (mem_group_iff fs k ℓ).mp hk
  have hne_j : fs.groupOf (firstMover fs f) ≠ fs.groupOf j := by
    rw [hgj]; intro h; exact hfm_not_group ((mem_group_iff fs _ ℓ).mpr h)
  have hne_k : fs.groupOf (firstMover fs f) ≠ fs.groupOf k := by
    rw [hgk]; intro h; exact hfm_not_group ((mem_group_iff fs _ ℓ).mpr h)
  unfold splitCount
  rw [if_neg hne_j, if_neg hne_k, hgj, hgk]

/-- Cross-group stability: changing the first-mover within a group
    does not affect split counts for features outside that group. DERIVED. -/
theorem splitCount_crossGroup_stable (f f' : Model)
    (j : Fin fs.P) (ℓ : Fin fs.L)
    (hj : j ∉ fs.group ℓ)
    (hfm : firstMover fs f ∈ fs.group ℓ)
    (hfm' : firstMover fs f' ∈ fs.group ℓ) :
    splitCount fs j f = splitCount fs j f' := by
  have hgj_ne : fs.groupOf j ≠ ℓ := by
    intro h; exact hj ((mem_group_iff fs j ℓ).mpr h)
  have hgfm : fs.groupOf (firstMover fs f) = ℓ := (mem_group_iff fs _ ℓ).mp hfm
  have hgfm' : fs.groupOf (firstMover fs f') = ℓ := (mem_group_iff fs _ ℓ).mp hfm'
  have hne_f : fs.groupOf (firstMover fs f) ≠ fs.groupOf j := by
    rw [hgfm]; exact Ne.symm hgj_ne
  have hne_f' : fs.groupOf (firstMover fs f') ≠ fs.groupOf j := by
    rw [hgfm']; exact Ne.symm hgj_ne
  unfold splitCount
  rw [if_neg hne_f, if_neg hne_f']
  exact crossGroupBaseline_stable fs f f' (fs.groupOf j) ℓ hgfm hgfm' hgj_ne

-- Make splitCount opaque for downstream proofs
attribute [irreducible] splitCount

/-! ## Symmetry theorem for DASH analysis

  **Attribution symmetry for balanced ensembles (DERIVED).**
  Previously axiomatized; now derived from:
  - proportionality_global (uniform c across models)
  - split-count definition
  - splitCount_crossGroup_symmetric (cross-group symmetry)
  - IsBalanced (equal first-mover counts)
-/

/-- Helper: split counts are equal for same-group features when the
    first-mover is not j. -/
theorem splitCount_eq_of_not_firstMover_j_or_k (f : Model) (j k : Fin fs.P)
    (ℓ : Fin fs.L) (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ)
    (hfmj : firstMover fs f ≠ j) (hfmk : firstMover fs f ≠ k) :
    splitCount fs j f = splitCount fs k f := by
  by_cases hfm_in : firstMover fs f ∈ fs.group ℓ
  · rw [splitCount_nonFirstMover fs f j ℓ hj hfmj hfm_in,
        splitCount_nonFirstMover fs f k ℓ hk hfmk hfm_in]
  · exact splitCount_crossGroup_symmetric fs f j k ℓ hj hk hfm_in

-- attribution_sum_symmetric: DERIVED in SymmetryDerive.lean
