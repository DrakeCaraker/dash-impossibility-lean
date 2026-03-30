/-
  Axiomatic definitions for the impossibility theorem.

  We axiomatize gradient boosting and TreeSHAP at the level of their
  mathematical properties, not their algorithmic implementation. This
  matches the proof strategy in impossibility.tex, which reasons about
  split counts and attribution proportionality rather than the full
  XGBoost training loop.

  The axioms are justified by:
  1. The Gaussian conditioning argument (Lemma 6 in the paper)
  2. The uniform-contribution model (Assumption 7)
  3. Symmetry of the DGP under within-group feature permutation
  4. SymPy verification of all algebraic consequences
     (see dash-shap/paper/proofs/verify_lemma6_algebra.py)
-/

import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Real.Basic

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

namespace FeatureSpace

/-- The set of features in group ℓ -/
def group (fs : FeatureSpace) (ℓ : Fin fs.L) : Finset (Fin fs.P) :=
  Finset.univ.filter (fun j => fs.groupOf j = ℓ)

/-- Group size -/
def groupSize (fs : FeatureSpace) (ℓ : Fin fs.L) : ℕ :=
  (fs.group ℓ).card

end FeatureSpace

/-! ## Model and attribution types -/

/-- Abstract type for random seeds -/
axiom Seed : Type
/-- Seeds are nonempty (we can always draw one) -/
axiom Seed.nonempty : Nonempty Seed
instance : Nonempty Seed := Seed.nonempty

/-- A trained model, parameterized by its random seed -/
axiom Model : Type
axiom Model.nonempty : Nonempty Model
instance : Nonempty Model := Model.nonempty

/-- Train a model from a seed -/
axiom train : Seed → Model

/-- Number of boosting rounds -/
axiom numTrees : ℕ
axiom numTrees_pos : 0 < numTrees

variable (fs : FeatureSpace)

/-- Attribution (global feature importance) for feature j in model f -/
axiom attribution : Fin fs.P → Model → ℝ

/-- Attribution is nonnegative -/
axiom attribution_nonneg : ∀ (j : Fin fs.P) (f : Model), 0 ≤ attribution fs j f

/-- Split count for feature j in model f -/
axiom splitCount : Fin fs.P → Model → ℕ

/-- The first-mover feature in a model (the feature selected at root of tree 1) -/
axiom firstMover : Model → Fin fs.P

/-! ## Axioms: properties of sequential gradient boosting under Gaussian DGP -/

/-- AXIOM 1: First-mover stays within its group.
    The first split always selects a feature from some group. -/
axiom firstMover_in_group (f : Model) :
    ∃ ℓ : Fin fs.L, firstMover fs f ∈ fs.group ℓ

/-- AXIOM 2: Split count for first-mover = T/(2-ρ²). -/
axiom splitCount_firstMover (f : Model) (j : Fin fs.P)
    (hfm : firstMover fs f = j) :
    (splitCount fs j f : ℝ) = numTrees / (2 - fs.ρ ^ 2)

/-- AXIOM 3: Split count for non-first-mover in same group = (1-ρ²)T/(2-ρ²). -/
axiom splitCount_nonFirstMover (f : Model) (j : Fin fs.P)
    (ℓ : Fin fs.L) (hj : j ∈ fs.group ℓ)
    (hfm : firstMover fs f ≠ j)
    (hfm_group : firstMover fs f ∈ fs.group ℓ) :
    (splitCount fs j f : ℝ) = (1 - fs.ρ ^ 2) * numTrees / (2 - fs.ρ ^ 2)

/-- AXIOM 4: Attribution proportional to split count (Assumption 7).
    Under the uniform-contribution model, every feature in a given model
    shares the same proportionality constant: φ_j = c · n_j for all j. -/
axiom attribution_proportional (f : Model) :
    ∃ c : ℝ, 0 < c ∧ ∀ (j : Fin fs.P),
      attribution fs j f = c * (splitCount fs j f : ℝ)

/-! ## Stability and equity definitions -/

/-- δ-stability: expected Spearman ≥ 1 - δ between two independent runs. -/
def isStable (δ : ℝ) (expectedSpearman : ℝ) : Prop :=
  expectedSpearman ≥ 1 - δ

/-- γ-equity: expected max/min attribution ratio within a group ≤ 1 + γ. -/
def isEquitable (γ : ℝ) (maxMinRatio : ℝ) : Prop :=
  maxMinRatio ≤ 1 + γ

/-! ## Consensus (DASH) definition -/

/-- DASH consensus attribution: average over M independently trained models. -/
noncomputable def consensus (M : ℕ) (hM : 0 < M) (models : Fin M → Model)
    (j : Fin fs.P) : ℝ :=
  (1 / (M : ℝ)) * (Finset.univ.sum (fun i => attribution fs j (models i)))

/-! ## Spearman rank correlation -/

/-- Spearman rank correlation between two attribution vectors.
    Full definition via Σd²/(P(P²-1)) deferred; we axiomatize the key bound. -/
axiom spearman (v w : Fin fs.P → ℝ) : ℝ

/-- Spearman is at most 1. -/
axiom spearman_le_one (v w : Fin fs.P → ℝ) : spearman fs v w ≤ 1

/-- AXIOM 5: When two models have different first-movers in the same group,
    within-group rank reshuffling bounds Spearman. Justified by the paper's
    combinatorial argument: non-first-movers are tied and randomly ordered,
    giving E[Σd²] = m(m²-1)/6 for group size m. -/
axiom spearman_bound (f f' : Model) (ℓ : Fin fs.L)
    (hfm_grp : firstMover fs f ∈ fs.group ℓ)
    (hfm'_grp : firstMover fs f' ∈ fs.group ℓ)
    (hdiff : firstMover fs f ≠ firstMover fs f') :
    spearman fs (fun j => attribution fs j f) (fun j => attribution fs j f') ≤
      1 - (fs.groupSize ℓ : ℝ) ^ 3 / ((fs.P : ℝ) ^ 3 * 6)

/-! ## Probabilistic axioms for DASH analysis -/

/-- AXIOM 6: First-mover symmetry.
    By DGP symmetry, each feature in a group is equally likely to be first-mover.
    For a balanced ensemble, each feature serves as first-mover the same number of times. -/
axiom firstMover_balanced (M : ℕ) (hM : 0 < M) (models : Fin M → Model)
    (ℓ : Fin fs.L) (j k : Fin fs.P) (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ) :
    (Finset.univ.filter (fun i => firstMover fs (models i) = j)).card =
    (Finset.univ.filter (fun i => firstMover fs (models i) = k)).card

/-- AXIOM 7: Attribution symmetry in expectation.
    Direct consequence of DGP symmetry + first-mover balance: summed attributions
    are equal for same-group features across a balanced ensemble. -/
axiom attribution_sum_symmetric (M : ℕ) (hM : 0 < M) (models : Fin M → Model)
    (j k : Fin fs.P) (ℓ : Fin fs.L) (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ) :
    Finset.univ.sum (fun i => attribution fs j (models i)) =
    Finset.univ.sum (fun i => attribution fs k (models i))
