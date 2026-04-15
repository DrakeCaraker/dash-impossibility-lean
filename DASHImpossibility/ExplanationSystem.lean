/-
  Abstract Explanation System.

  A general framework for explanation impossibility beyond feature attribution.
  A system S : Θ → Y is explained by E : Θ → H. The Rashomon property says
  equivalent configurations can produce incompatible explanations.

  This provides the abstract foundation for:
  - The trilemma: faithful + stable + decisive → False
  - The bilemma: for maximally incompatible H, faithful + stable → False
  - Instances: SHAP sign, feature selection, counterfactual direction
-/

set_option autoImplicit false

namespace DASHImpossibility

/-! ### Abstract Explanation System -/

/-- An explanation system with configuration space Θ, explanation space H,
    and observable space Y. -/
structure ExplanationSystem (Θ : Type) (H : Type) (Y : Type) where
  /-- The observation map: what the system produces. -/
  observe : Θ → Y
  /-- The explanation map: how we interpret a configuration. -/
  explain : Θ → H
  /-- Incompatibility relation on explanations. -/
  incompatible : H → H → Prop

/-! ### Axiom definitions -/

/-- Faithfulness: E(θ) is compatible with (not incompatible with) the system's
    native explanation. This is the WEAK definition — "consistent with" rather
    than "equal to." A faithful explanation never contradicts the model. -/
def faithful {Θ H Y : Type} (S : ExplanationSystem Θ H Y) (E : Θ → H) : Prop :=
  ∀ (θ : Θ), ¬S.incompatible (E θ) (S.explain θ)

/-- Stability: the explanation factors through the observable map.
    Equivalent configurations get the same explanation. -/
def stable {Θ H Y : Type} (S : ExplanationSystem Θ H Y) (E : Θ → H) : Prop :=
  ∀ (θ₁ θ₂ : Θ), S.observe θ₁ = S.observe θ₂ → E θ₁ = E θ₂

/-- Decisiveness: E preserves incompatibility of native explanations.
    When the system's native explanations are incompatible, E's outputs
    are also incompatible — E doesn't smooth over genuine disagreements. -/
def decisive {Θ H Y : Type} (S : ExplanationSystem Θ H Y) (E : Θ → H) : Prop :=
  ∀ (θ₁ θ₂ : Θ), S.incompatible (S.explain θ₁) (S.explain θ₂) →
    S.incompatible (E θ₁) (E θ₂)

/-! ### The Abstract Impossibility (Trilemma) -/

/-- **The Explanation Impossibility.** No explanation of a system with the
    Rashomon property can be simultaneously faithful, stable, and decisive.

    Proof structure:
    1. Rashomon gives θ₁, θ₂ with same output but incompatible explanations
    2. Decisive: incompatible(E θ₁, E θ₂)
    3. Stable: E θ₁ = E θ₂ (same observable)
    4. E θ₁ = E θ₂ but incompatible(E θ₁, E θ₂) — contradicts irreflexivity -/
theorem explanation_impossibility {Θ H Y : Type}
    (S : ExplanationSystem Θ H Y)
    (hirrefl : ∀ (h : H), ¬S.incompatible h h)
    (θ₁ θ₂ : Θ) (hobs : S.observe θ₁ = S.observe θ₂)
    (hinc : S.incompatible (S.explain θ₁) (S.explain θ₂))
    (E : Θ → H) (_hf : faithful S E) (hs : stable S E) (hd : decisive S E) :
    False := by
  have hinc_E := hd θ₁ θ₂ hinc
  have heq := hs θ₁ θ₂ hobs
  rw [heq] at hinc_E
  exact hirrefl _ hinc_E

end DASHImpossibility
