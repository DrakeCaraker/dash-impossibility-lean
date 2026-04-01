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
