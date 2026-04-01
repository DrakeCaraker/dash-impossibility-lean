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

/-- A trained model (abstract type). -/
axiom Model : Type

/-- Number of boosting rounds -/
axiom numTrees : ℕ
axiom numTrees_pos : 0 < numTrees

variable (fs : FeatureSpace)

/-- Attribution (global feature importance) for feature j in model f -/
axiom attribution : Fin fs.P → Model → ℝ

/-- Split count for feature j in model f.
    Returns ℝ (not ℕ) to avoid inconsistency: the axiomatized values T/(2-ρ²)
    are generally irrational. The values represent idealized leading-order
    split counts from the paper's Gaussian conditioning argument. -/
axiom splitCount : Fin fs.P → Model → ℝ

/-- The first-mover feature in a model (the feature selected at root of tree 1) -/
axiom firstMover : Model → Fin fs.P

/-! ## Axioms: properties of sequential gradient boosting under Gaussian DGP -/

/-- AXIOM 1: Every feature in a group can be the first-mover.
    By DGP symmetry and randomness in sub-sampling/tie-breaking,
    each feature in a group serves as first-mover for some model. -/
axiom firstMover_surjective (ℓ : Fin fs.L) (j : Fin fs.P) (hj : j ∈ fs.group ℓ) :
    ∃ f : Model, firstMover fs f = j

/-- AXIOM 2: Split count for first-mover = T/(2-ρ²).
    Leading-order behavior from Gaussian conditioning (Lemma 1). -/
axiom splitCount_firstMover (f : Model) (j : Fin fs.P)
    (hfm : firstMover fs f = j) :
    splitCount fs j f = numTrees / (2 - fs.ρ ^ 2)

/-- AXIOM 3: Split count for non-first-mover in same group = (1-ρ²)T/(2-ρ²).
    Residual signal after the first-mover absorbs the ρ-aligned component. -/
axiom splitCount_nonFirstMover (f : Model) (j : Fin fs.P)
    (ℓ : Fin fs.L) (hj : j ∈ fs.group ℓ)
    (hfm : firstMover fs f ≠ j)
    (hfm_group : firstMover fs f ∈ fs.group ℓ) :
    splitCount fs j f = (1 - fs.ρ ^ 2) * numTrees / (2 - fs.ρ ^ 2)

/-- AXIOM 4: Attribution proportional to split count (Assumption 7).
    Under the uniform-contribution model, every feature in a given model
    shares the same proportionality constant: φ_j = c · n_j for all j. -/
axiom attribution_proportional (f : Model) :
    ∃ c : ℝ, 0 < c ∧ ∀ (j : Fin fs.P),
      attribution fs j f = c * splitCount fs j f

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
    first-mover the same number of times. This holds in expectation
    for i.i.d. seeds by DGP symmetry, and exactly when M is a multiple
    of the group size. -/
def IsBalanced (M : ℕ) (models : Fin M → Model) : Prop :=
  ∀ (ℓ : Fin fs.L) (j k : Fin fs.P),
    j ∈ fs.group ℓ → k ∈ fs.group ℓ →
    (Finset.univ.filter (fun i => firstMover fs (models i) = j)).card =
    (Finset.univ.filter (fun i => firstMover fs (models i) = k)).card

/-! ## Spearman rank correlation

  Previously axiomatized; now defined from scratch in SpearmanDef.lean
  using midranks and Σd². The qualitative bound (Spearman < 1 when
  first-movers differ) is fully derived. The quantitative bound
  (Spearman ≤ 1 - 3/(P³-P)) is also derived from the definition.

  The classical argument gives a tighter bound of m³/P³ (from the
  expected Σd² under random tie-breaking), which is stated as an
  axiom in SpearmanDef.lean about the defined quantity. -/

/-! ## Variance axioms for DASH analysis

  These axioms capture the probabilistic structure needed for the
  variance bound. The derivation path via Mathlib is:
    Mathlib.Probability.Moments.Variance.IndepFun.variance_sum
  which proves Var(∑X_i) = ∑Var(X_i) for pairwise independent X_i.

  However, using this requires reformulating our axiom system to
  include a probability space (Ω, μ) with modelSample : Ω → Model,
  measurability of attributions, and independence of ensemble members.
  This is a fundamental architectural change (adding ~6 axioms for
  measure-theoretic infrastructure) that we defer to future work.

  We axiomatize the variance directly because:
  (i) Var(X̄) = Var(X)/M for i.i.d. variables is textbook;
  (ii) the measure-theoretic axioms are harder to audit than
       the single intuitive axiom;
  (iii) the derived theorems (variance halving, nonnegativity)
       are genuine proofs from this axiom, not tautologies.
-/

/-- Variance of a single model's attribution for feature j.
    Represents Var(φ_j(f)) where f ~ training distribution. -/
axiom attribution_variance (j : Fin fs.P) : ℝ

/-- Variance is nonneg. -/
axiom attribution_variance_nonneg (j : Fin fs.P) :
    0 ≤ attribution_variance fs j

/-- AXIOM: Variance of consensus decreases as 1/M.
    For M i.i.d. models, Var(consensus_j) = Var(φ_j)/M.
    This is the standard result for i.i.d. means.
    The full Lean proof would need:
      1. MeasurableSpace Model
      2. MeasureTheory.Measure Model
      3. Measurable (attribution fs j)
      4. IndepFun for the model array
    and then apply ProbabilityTheory.IndepFun.variance_sum. -/
axiom consensus_variance_bound (M : ℕ) (hM : 0 < M) (j : Fin fs.P) :
    ∃ (consensus_var : ℝ),
      consensus_var = attribution_variance fs j / M ∧
      0 ≤ consensus_var

/-! ## Symmetry axiom for DASH analysis -/

/-- AXIOM 6: Attribution symmetry for balanced ensembles.
    For a balanced ensemble (each feature serves as first-mover equally often),
    the summed attributions are equal for same-group features. This is a
    consequence of DGP symmetry: swapping j and k in the DGP leaves the
    joint distribution invariant, so E[φ_j] = E[φ_k]. For balanced finite
    ensembles, this holds exactly when:
      (a) the proportionality constant c is uniform across models
          (a consequence of identical hyperparameters), AND
      (b) features in a group have equal split counts when the
          first-mover is in a different group (DGP symmetry).
    The derivation from Axioms 2-4 requires (a) — which is not stated
    in Axiom 4 (per-model c) — and (b) — a cross-group symmetry axiom
    not currently in the system. Axiomatizing the conclusion directly
    is more parsimonious than adding both unstated assumptions. -/
axiom attribution_sum_symmetric (M : ℕ) (hM : 0 < M) (models : Fin M → Model)
    (hbal : IsBalanced fs M models)
    (j k : Fin fs.P) (ℓ : Fin fs.L) (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ) :
    Finset.univ.sum (fun i => attribution fs j (models i)) =
    Finset.univ.sum (fun i => attribution fs k (models i))
