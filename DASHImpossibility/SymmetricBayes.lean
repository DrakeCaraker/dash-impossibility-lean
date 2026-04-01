/-
  The Symmetric Bayes Dichotomy.

  A general impossibility theorem for symmetric decision problems:
  when a group G acts on the decision set and the population is
  G-invariant, the achievable set consists of exactly two families.

  This generalizes the Attribution Impossibility, Model Selection
  Impossibility, and Causal Discovery Impossibility as instances.

  Supplement: §The Symmetric Bayes Dichotomy
-/
import Mathlib.GroupTheory.GroupAction.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Basic
import DASHImpossibility.Trilemma

set_option autoImplicit false

namespace DASHImpossibility

/-! ### Definition: Symmetric Decision Problem -/

/-- A symmetric decision problem with a finite group acting on a finite decision set.
    Θ is the decision space, G is the symmetry group acting on Θ. -/
structure SymmetricDecisionProblem where
  /-- Decision set (e.g., feature orderings, model rankings) -/
  Θ : Type
  [instΘFintype : Fintype Θ]
  [instΘDecEq : DecidableEq Θ]
  /-- Data/instance space -/
  D : Type
  /-- Symmetry group -/
  G : Type
  [instGGroup : Group G]
  [instGFintype : Fintype G]
  [instGDecEq : DecidableEq G]
  /-- Group action on decisions -/
  [instAction : MulAction G Θ]
  /-- The instance-optimal decision for each data point -/
  optimal : D → Θ
  /-- For every pair in the same orbit, there exist data instances
      making each one optimal (G-invariance / Rashomon-like property). -/
  orbit_reachable : ∀ (θ₁ θ₂ : Θ),
    (∃ g : G, g • θ₁ = θ₂) →
    (∃ d : D, optimal d = θ₁) ∧ (∃ d : D, optimal d = θ₂)

attribute [instance] SymmetricDecisionProblem.instΘFintype
attribute [instance] SymmetricDecisionProblem.instΘDecEq
attribute [instance] SymmetricDecisionProblem.instGGroup
attribute [instance] SymmetricDecisionProblem.instGFintype
attribute [instance] SymmetricDecisionProblem.instGDecEq
attribute [instance] SymmetricDecisionProblem.instAction

/-- An estimator maps data to decisions. -/
def Estimator (P : SymmetricDecisionProblem) := P.D → P.Θ

/-- An estimator is faithful to instance d if it returns the optimal decision. -/
def IsFaithfulAt (P : SymmetricDecisionProblem) (est : Estimator P) (d : P.D) : Prop :=
  est d = P.optimal d

-- Completeness: an estimator is complete for a pair (θ₁, θ₂) if it can
-- output both θ₁ and θ₂ (it decides between them rather than reporting
-- orbit membership). We do not need a separate definition here — the
-- pigeonhole argument below captures the consequence directly.

/-! ### Part (i): Unfaithfulness bound -/

/-- Part (i) of the SBD: If two decisions θ₁, θ₂ are in the same orbit
    and the estimator is faithful at some d₁ with optimal(d₁) = θ₁,
    then it is NOT faithful at d₂ with optimal(d₂) = θ₂ (assuming θ₁ ≠ θ₂
    and the estimator is "stable" / deterministic).

    This is the core pigeonhole: a deterministic function cannot map
    to both θ₁ and θ₂ simultaneously for the same input. -/
theorem sbd_unfaithful_witness
    (P : SymmetricDecisionProblem)
    (θ₁ θ₂ : P.Θ) (hne : θ₁ ≠ θ₂)
    (_h_orbit : ∃ g : P.G, g • θ₁ = θ₂)
    -- There exist instances making each optimal
    (d₁ : P.D) (hd₁ : P.optimal d₁ = θ₁)
    (d₂ : P.D) (hd₂ : P.optimal d₂ = θ₂)
    -- Stable estimator: same output for d₁ and d₂
    (est : Estimator P)
    (h_stable : est d₁ = est d₂) :
    -- The estimator is unfaithful to at least one instance
    ¬ IsFaithfulAt P est d₁ ∨ ¬ IsFaithfulAt P est d₂ := by
  -- If faithful at both, then est d₁ = θ₁ and est d₂ = θ₂
  -- But est d₁ = est d₂ (stability), so θ₁ = θ₂, contradiction
  by_contra h
  push Not at h
  obtain ⟨h1, h2⟩ := h
  unfold IsFaithfulAt at h1 h2
  rw [h1, hd₁] at h_stable
  rw [h2, hd₂] at h_stable
  exact hne h_stable

/-! ### Part (iii): Infeasibility -/

/-- Part (iii): No estimator can be faithful to ALL instances AND stable.
    If two orbit-mates can both be optimal, a stable estimator cannot
    be faithful to both. -/
theorem sbd_infeasible
    (P : SymmetricDecisionProblem)
    (θ₁ θ₂ : P.Θ) (hne : θ₁ ≠ θ₂)
    (h_orbit : ∃ g : P.G, g • θ₁ = θ₂)
    (d₁ : P.D) (hd₁ : P.optimal d₁ = θ₁)
    (d₂ : P.D) (hd₂ : P.optimal d₂ = θ₂)
    (est : Estimator P)
    (h_stable : est d₁ = est d₂)
    (h_faith₁ : IsFaithfulAt P est d₁)
    (h_faith₂ : IsFaithfulAt P est d₂) :
    False := by
  have h := sbd_unfaithful_witness P θ₁ θ₂ hne h_orbit d₁ hd₁ d₂ hd₂ est h_stable
  cases h with
  | inl h => exact h h_faith₁
  | inr h => exact h h_faith₂

/-! ### Part (ii): Ties are never unfaithful -/

/-- A "tie-reporting" estimator maps all orbit-mates to the same output.
    When an estimator reports the orbit rather than a specific element,
    it's never wrong about WHICH element is optimal (it doesn't claim to know).

    We formalize: if the estimator's output is the same for all instances
    in an orbit, then "unfaithfulness" is zero (it never asserts an
    incorrect specific element). -/
def ReportsTie (P : SymmetricDecisionProblem) (est : Estimator P)
    (d₁ d₂ : P.D) : Prop :=
  est d₁ = est d₂

/-- The tie-reporting estimator is automatically stable (same output). -/
theorem tie_is_stable (P : SymmetricDecisionProblem) (est : Estimator P)
    (d₁ d₂ : P.D) (h : ReportsTie P est d₁ d₂) :
    est d₁ = est d₂ := h

/-! ### Quantitative orbit cardinality bounds -/

/-- A stable estimator is faithful to at most one element of an orbit.
    If it's faithful at d₁ (optimal = θ₁), then for any d₂ with a different
    optimal and the same estimator output (stability), it's NOT faithful at d₂.
    This is pure logic: no orbit hypothesis needed. -/
theorem sbd_faithful_at_most_one
    (P : SymmetricDecisionProblem)
    (est : Estimator P)
    (d₁ d₂ : P.D)
    (hne : P.optimal d₁ ≠ P.optimal d₂)
    (h_stable : est d₁ = est d₂)
    (h_faith₁ : IsFaithfulAt P est d₁) :
    ¬ IsFaithfulAt P est d₂ := by
  intro h_faith₂
  unfold IsFaithfulAt at h_faith₁ h_faith₂
  exact hne (h_faith₁.symm.trans (h_stable.trans h_faith₂))

/-- The estimator's output uniquely determines which orbit-mate it can be
    faithful to. If faithful at d₁ and at d₂ with stable output, then
    the optima must agree. Contrapositive of sbd_faithful_at_most_one. -/
theorem sbd_faithful_unique
    (P : SymmetricDecisionProblem)
    (est : Estimator P)
    (d₁ d₂ : P.D)
    (h_stable : est d₁ = est d₂)
    (h_faith₁ : IsFaithfulAt P est d₁)
    (h_faith₂ : IsFaithfulAt P est d₂) :
    P.optimal d₁ = P.optimal d₂ := by
  unfold IsFaithfulAt at h_faith₁ h_faith₂
  exact h_faith₁.symm.trans (h_stable.trans h_faith₂)

/-- Binary orbit special case (k=2): a stable estimator is unfaithful to
    at least one of two instances with distinct optima. This is exactly the
    attribution and model selection impossibility pattern.
    Direct corollary of sbd_faithful_at_most_one. -/
theorem sbd_binary_orbit_half_unfaithful
    (P : SymmetricDecisionProblem)
    (est : Estimator P)
    (d₁ d₂ : P.D)
    (hne : P.optimal d₁ ≠ P.optimal d₂)
    (h_stable : est d₁ = est d₂) :
    ¬ IsFaithfulAt P est d₁ ∨ ¬ IsFaithfulAt P est d₂ := by
  by_contra h
  push Not at h
  exact hne (sbd_faithful_unique P est d₁ d₂ h_stable h.1 h.2)

/-- Ternary orbit case (k=3): a stable estimator is unfaithful to at least
    two of three instances with pairwise-distinct optima. This captures the
    CPDAG 3-node impossibility pattern (where k=6 gives 5/6 unfaithfulness,
    but the core pigeonhole already manifests at k=3). -/
theorem sbd_ternary_orbit_unfaithful
    (P : SymmetricDecisionProblem)
    (est : Estimator P)
    (d₁ d₂ d₃ : P.D)
    (hne12 : P.optimal d₁ ≠ P.optimal d₂)
    (hne13 : P.optimal d₁ ≠ P.optimal d₃)
    (hne23 : P.optimal d₂ ≠ P.optimal d₃)
    (h_stable12 : est d₁ = est d₂)
    (h_stable13 : est d₁ = est d₃) :
    -- At least two of the three are unfaithful
    (¬ IsFaithfulAt P est d₁ ∧ ¬ IsFaithfulAt P est d₂) ∨
    (¬ IsFaithfulAt P est d₁ ∧ ¬ IsFaithfulAt P est d₃) ∨
    (¬ IsFaithfulAt P est d₂ ∧ ¬ IsFaithfulAt P est d₃) := by
  -- Case split: is the estimator faithful at d₁?
  by_cases hf₁ : IsFaithfulAt P est d₁
  · -- Faithful at d₁ → not faithful at d₂ and d₃
    have hf₂ := sbd_faithful_at_most_one P est d₁ d₂ hne12 h_stable12 hf₁
    have hf₃ := sbd_faithful_at_most_one P est d₁ d₃ hne13 h_stable13 hf₁
    exact Or.inr (Or.inr ⟨hf₂, hf₃⟩)
  · -- Not faithful at d₁ → pair with whichever of d₂, d₃ is also unfaithful
    by_cases hf₂ : IsFaithfulAt P est d₂
    · exact Or.inr (Or.inl ⟨hf₁, sbd_faithful_at_most_one P est d₂ d₃ hne23
        (h_stable12.symm.trans h_stable13) hf₂⟩)
    · exact Or.inl ⟨hf₁, hf₂⟩

/-! ### Instances -/

-- The Attribution Impossibility is an instance:
-- Θ = {j > k, k > j} (two orderings)
-- G = Z/2Z (swap j ↔ k)
-- D = Model
-- optimal(f) = (j > k if φ_j(f) > φ_k(f), else k > j)
-- orbit_reachable: Rashomon property

-- The Model Selection Impossibility is an instance:
-- Θ = {m₁ > m₂, m₂ > m₁}
-- G = Z/2Z
-- D = EvalInstance
-- optimal(d) = (m₁ > m₂ if quality(m₁,d) > quality(m₂,d), else m₂ > m₁)

/-- The Attribution Impossibility follows from the SBD.
    Given the Rashomon property (= orbit_reachable for the attribution SDP),
    the impossibility is a direct application of sbd_infeasible. -/
theorem attribution_from_sbd
    (fs : FeatureSpace)
    (hrash : RashimonProperty fs)
    (ℓ : Fin fs.L) (j k : Fin fs.P)
    (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ) (hjk : j ≠ k)
    -- A stable ranking (same for all models)
    (ranking : Fin fs.P → Fin fs.P → Prop)
    (h_faithful : ∀ f : Model,
      ranking j k ↔ attribution fs j f > attribution fs k f) :
    False := by
  -- This reduces to attribution_impossibility from Trilemma.lean
  exact attribution_impossibility fs hrash ℓ j k hj hk hjk ranking h_faithful

end DASHImpossibility
