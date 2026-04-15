/-
  The Bilemma: Strengthened Impossibility for Binary Attribution.

  For maximally incompatible explanation spaces (the only compatible pair is
  (h,h)), faithful + stable alone is impossible — strictly stronger than the
  trilemma. This applies to binary attribution questions: SHAP sign
  (positive/negative), feature selection (selected/not), counterfactual
  direction (increase/decrease).

  Results:
  - bilemma_of_compatible_eq: F+S → False for maximally incompatible H
  - rashomon_unfaithfulness: any stable method is unfaithful at ≥1 of 2 witnesses
  - all_or_nothing: every method either equals explain or is unfaithful somewhere
  - Instances: SHAPSign, FeatureStatus

  Origin: discovered in the Ostrowski impossibility project, re-proved here
  for self-containedness.
-/
import DASHImpossibility.ExplanationSystem

set_option autoImplicit false

namespace DASHImpossibility

/-! ### The Bilemma -/

/-- **The Bilemma.** For maximally incompatible explanation spaces
    (compatible ⇒ equal), faithful + stable is impossible — not just F+S+D.

    The proof: maximal incompatibility forces faithful E to equal explain
    (there's nowhere else to go). Then E = explain is decisive. So E is
    F+S+D, contradicting the trilemma.

    This is strictly stronger than the trilemma and applies to all binary
    attribution questions (SHAP sign, feature selection, counterfactual
    direction). -/
theorem bilemma_of_compatible_eq {Θ H Y : Type}
    (S : ExplanationSystem Θ H Y)
    (hirrefl : ∀ (h : H), ¬S.incompatible h h)
    (hcompat : ∀ (h₁ h₂ : H), ¬S.incompatible h₁ h₂ → h₁ = h₂)
    (θ₁ θ₂ : Θ) (hobs : S.observe θ₁ = S.observe θ₂)
    (hinc : S.incompatible (S.explain θ₁) (S.explain θ₂))
    (E : Θ → H) (hf : faithful S E) (hs : stable S E) :
    False := by
  -- From faithful + hcompat: E = explain at every θ
  have heq : ∀ (θ : Θ), E θ = S.explain θ := fun θ => hcompat _ _ (hf θ)
  -- Therefore decisive (E preserves incompatibility because E = explain)
  have hd : decisive S E := by
    intro θ₁' θ₂' hinc'
    rw [heq θ₁', heq θ₂']
    exact hinc'
  exact explanation_impossibility S hirrefl θ₁ θ₂ hobs hinc E hf hs hd

/-! ### Rashomon Unfaithfulness Bound -/

/-- **Rashomon unfaithfulness bound.** For any binary attribution question,
    any stable method is unfaithful at ≥1 of every 2 Rashomon witnesses.
    On any pair of equivalent models that disagree on the sign/selection
    of a feature, a stable method must get it wrong for at least one. -/
theorem rashomon_unfaithfulness {Θ H Y : Type}
    (S : ExplanationSystem Θ H Y)
    (hcompat : ∀ (h₁ h₂ : H), ¬S.incompatible h₁ h₂ → h₁ = h₂)
    (E : Θ → H) (hs : stable S E)
    (θ₁ θ₂ : Θ) (hobs : S.observe θ₁ = S.observe θ₂)
    (hinc : S.incompatible (S.explain θ₁) (S.explain θ₂)) :
    S.incompatible (E θ₁) (S.explain θ₁) ∨
    S.incompatible (E θ₂) (S.explain θ₂) := by
  by_cases h : S.incompatible (E θ₁) (S.explain θ₁)
  · left; exact h
  · right
    have h1 : E θ₁ = S.explain θ₁ := hcompat _ _ h
    have h2 : E θ₂ = E θ₁ := (hs θ₁ θ₂ hobs).symm
    rw [h2, h1]
    exact hinc

/-! ### All-or-Nothing Theorem -/

/-- **All-or-nothing theorem.** For binary attribution, every method either
    (1) matches the model's native attribution exactly (faithful + E = explain)
    or (2) is unfaithful at some configuration.
    There is no "approximately faithful" middle ground. -/
theorem all_or_nothing {Θ H Y : Type}
    (S : ExplanationSystem Θ H Y)
    (hcompat : ∀ (h₁ h₂ : H), ¬S.incompatible h₁ h₂ → h₁ = h₂)
    (E : Θ → H) :
    (faithful S E ∧ (∀ (θ : Θ), E θ = S.explain θ)) ∨
    (∃ (θ : Θ), S.incompatible (E θ) (S.explain θ)) := by
  by_cases hf : faithful S E
  · left; exact ⟨hf, fun θ => hcompat _ _ (hf θ)⟩
  · right
    -- ¬faithful = ¬(∀ θ, ¬incompatible (E θ) (explain θ)) = ∃ θ, incompatible (E θ) (explain θ)
    have : ¬∀ (θ : Θ), ¬S.incompatible (E θ) (S.explain θ) := hf
    exact Classical.byContradiction fun h =>
      this fun θ => fun hinc => h ⟨θ, hinc⟩

/-! ### ML Instances -/

/-- SHAP sign: positive or negative attribution. -/
inductive SHAPSign where
  | positive
  | negative
  deriving DecidableEq

/-- Incompatibility for SHAP signs: positive and negative are incompatible. -/
def SHAPSign.incomp : SHAPSign → SHAPSign → Prop
  | .positive, .negative => True
  | .negative, .positive => True
  | _, _ => False

/-- SHAP sign incompatibility is irreflexive. -/
theorem SHAPSign.incomp_irrefl (h : SHAPSign) :
    ¬SHAPSign.incomp h h := by
  cases h <;> simp [SHAPSign.incomp]

/-- SHAP sign is maximally incompatible: compatible ⇒ equal. -/
theorem SHAPSign.compatible_eq (h₁ h₂ : SHAPSign) :
    ¬SHAPSign.incomp h₁ h₂ → h₁ = h₂ := by
  cases h₁ <;> cases h₂ <;> simp [SHAPSign.incomp]

/-- Feature selection status: selected or not selected. -/
inductive FeatureStatus where
  | selected
  | notSelected
  deriving DecidableEq

/-- Incompatibility for feature selection: selected and not-selected
    are incompatible. -/
def FeatureStatus.incomp : FeatureStatus → FeatureStatus → Prop
  | .selected, .notSelected => True
  | .notSelected, .selected => True
  | _, _ => False

/-- Feature status incompatibility is irreflexive. -/
theorem FeatureStatus.incomp_irrefl (h : FeatureStatus) :
    ¬FeatureStatus.incomp h h := by
  cases h <;> simp [FeatureStatus.incomp]

/-- Feature status is maximally incompatible: compatible ⇒ equal. -/
theorem FeatureStatus.compatible_eq (h₁ h₂ : FeatureStatus) :
    ¬FeatureStatus.incomp h₁ h₂ → h₁ = h₂ := by
  cases h₁ <;> cases h₂ <;> simp [FeatureStatus.incomp]

/-! ### Instance Impossibilities -/

/-- **SHAP sign bilemma.** No method for determining a feature's attribution
    sign (positive/negative) can be simultaneously faithful and stable
    under model multiplicity. -/
theorem shap_sign_bilemma {Θ Y : Type}
    (S : ExplanationSystem Θ SHAPSign Y)
    (hS : S.incompatible = SHAPSign.incomp)
    (θ₁ θ₂ : Θ) (hobs : S.observe θ₁ = S.observe θ₂)
    (hinc : S.incompatible (S.explain θ₁) (S.explain θ₂))
    (E : Θ → SHAPSign) (hf : faithful S E) (hs : stable S E) :
    False := by
  exact bilemma_of_compatible_eq S
    (fun h => by rw [hS]; exact SHAPSign.incomp_irrefl h)
    (fun h₁ h₂ hc => SHAPSign.compatible_eq h₁ h₂ (by rwa [hS] at hc))
    θ₁ θ₂ hobs hinc E hf hs

/-- **Feature selection bilemma.** No method for determining whether a
    feature is selected can be simultaneously faithful and stable
    under model multiplicity. -/
theorem feature_selection_bilemma {Θ Y : Type}
    (S : ExplanationSystem Θ FeatureStatus Y)
    (hS : S.incompatible = FeatureStatus.incomp)
    (θ₁ θ₂ : Θ) (hobs : S.observe θ₁ = S.observe θ₂)
    (hinc : S.incompatible (S.explain θ₁) (S.explain θ₂))
    (E : Θ → FeatureStatus) (hf : faithful S E) (hs : stable S E) :
    False := by
  exact bilemma_of_compatible_eq S
    (fun h => by rw [hS]; exact FeatureStatus.incomp_irrefl h)
    (fun h₁ h₂ hc => FeatureStatus.compatible_eq h₁ h₂ (by rwa [hS] at hc))
    θ₁ θ₂ hobs hinc E hf hs

end DASHImpossibility
