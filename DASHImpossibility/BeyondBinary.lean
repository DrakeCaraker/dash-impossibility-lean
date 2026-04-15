/-
  Beyond Binary Attribution: Graded Explanations and Coverage Conflict.

  The bilemma (Bilemma.lean) shows binary explanation spaces are the hardest
  case. This file explores what happens with richer explanation spaces:

  1. ConcreteML: a fully constructive binary ML instance (zero axioms)
  2. GradedAttribution: a 3-element space (positive/weak_positive/negative)
     where the F+D-compatible set is non-singleton — more design freedom
  3. fdCompatibleAt: exact pointwise condition for F+D explanations
  4. hasCoverageConflict: diagnostic for whether the bilemma applies
  5. coverageConflict_implies_no_neutral: coverage conflict blocks DASH

  Practical message: enrich binary questions to graded questions.

  Ported from ostrowski-impossibility/Core/GeneralTheory.lean.
-/
import DASHImpossibility.Bilemma

set_option autoImplicit false

namespace DASHImpossibility

/-! ### 1. Constructive ML instance (zero axioms) -/

/-- A fully constructive binary ML explanation system.
    Two models (Bool) that agree on predictions but disagree on the sign
    of a feature's attribution.
    - observe: both produce the same output (Unit)
    - explain: model true → positive (true), model false → negative (false)
    - incompatible: positive ≠ negative

    Zero axioms, zero unproved goals. The bilemma holds by computation. -/
def concreteMLSystem : ExplanationSystem Bool Bool Unit where
  observe := fun _ => ()
  explain := fun b => b
  incompatible := fun b₁ b₂ => b₁ ≠ b₂

/-- The concrete ML system is maximally incompatible. -/
theorem concreteML_maxIncompat :
    ∀ (b₁ b₂ : Bool), ¬concreteMLSystem.incompatible b₁ b₂ → b₁ = b₂ := by
  intro b₁ b₂ h
  simp [concreteMLSystem] at h
  exact h

/-- Irreflexivity for the concrete ML system. -/
theorem concreteML_irrefl (b : Bool) :
    ¬concreteMLSystem.incompatible b b :=
  fun h => h rfl

/-- **Constructive ML bilemma.** Faithful + stable is impossible for the
    concrete ML system. Zero axioms, zero unproved goals. -/
theorem concreteML_bilemma
    (E : Bool → Bool) (hf : faithful concreteMLSystem E)
    (hs : stable concreteMLSystem E) : False :=
  bilemma_of_compatible_eq concreteMLSystem
    concreteML_irrefl
    concreteML_maxIncompat
    true false rfl (by intro h; exact absurd h (by decide))
    E hf hs

/-! ### 2. Graded attribution (ThreeH example) -/

/-- A 3-element explanation space modeling graded attribution:
    - positive: feature clearly contributes positively
    - weakPositive: feature weakly contributes positively
    - negative: feature contributes negatively
    positive and weakPositive are compatible (same direction);
    both are incompatible with negative. -/
inductive GradedAttribution where
  | positive : GradedAttribution
  | weakPositive : GradedAttribution
  | negative : GradedAttribution
  deriving DecidableEq

/-- Incompatibility for graded attributions: positive/weakPositive are
    compatible with each other but both incompatible with negative. -/
def GradedAttribution.incomp : GradedAttribution → GradedAttribution → Prop
  | .positive, .negative => True
  | .negative, .positive => True
  | .weakPositive, .negative => True
  | .negative, .weakPositive => True
  | _, _ => False

/-- Irreflexivity. -/
theorem GradedAttribution.incomp_irrefl (h : GradedAttribution) :
    ¬GradedAttribution.incomp h h := by
  cases h <;> simp [GradedAttribution.incomp]

/-- This system is NOT maximally incompatible: positive and weakPositive
    are compatible. -/
theorem graded_not_maxIncompat :
    ¬(∀ (h₁ h₂ : GradedAttribution), ¬GradedAttribution.incomp h₁ h₂ → h₁ = h₂) := by
  intro hmax
  have := hmax .positive .weakPositive (by simp [GradedAttribution.incomp])
  cases this

/-- positive and weakPositive have the same incompatibility profile. -/
theorem graded_equiv_profile :
    ∀ (h : GradedAttribution),
      GradedAttribution.incomp .positive h ↔ GradedAttribution.incomp .weakPositive h := by
  intro h
  cases h <;> simp [GradedAttribution.incomp]

/-- The graded attribution system: two models, one says positive, the other
    says negative. -/
def gradedSystem : ExplanationSystem Bool GradedAttribution Unit where
  observe := fun _ => ()
  explain := fun b => if b then .positive else .negative
  incompatible := GradedAttribution.incomp

/-! ### 3. F+D exact parameterization -/

/-- An element c is **F+D-compatible** at θ if it is compatible with
    explain(θ). This is the faithfulness condition at a single point.
    For our decisive definition (which operates on pairs of configurations),
    the F+D characterization is: E is faithful iff E(θ) is compatible with
    explain(θ) for all θ, and decisive iff incompatibility of explain-values
    implies incompatibility of E-values. -/
def fdCompatibleAt {Θ H Y : Type} (S : ExplanationSystem Θ H Y) (θ : Θ) (c : H) : Prop :=
  ¬S.incompatible c (S.explain θ)

/-- For maximally incompatible systems, compatibility forces equality:
    the only compatible element at θ is explain(θ) itself. -/
theorem maxIncompat_fdCompatible_singleton {Θ H Y : Type}
    (S : ExplanationSystem Θ H Y)
    (hmax : ∀ (h₁ h₂ : H), ¬S.incompatible h₁ h₂ → h₁ = h₂)
    (c : H) (θ : Θ) (hfd : fdCompatibleAt S θ c) :
    c = S.explain θ :=
  hmax c (S.explain θ) hfd

/-- For the graded system, BOTH positive AND weakPositive are F+D-compatible
    at true (where explain = positive). The F+D set is non-singleton. -/
theorem graded_fdCompatible_positive :
    fdCompatibleAt gradedSystem true .positive := by
  simp [fdCompatibleAt, gradedSystem, GradedAttribution.incomp]

theorem graded_fdCompatible_weakPositive :
    fdCompatibleAt gradedSystem true .weakPositive := by
  simp [fdCompatibleAt, gradedSystem, GradedAttribution.incomp]

/-- **The F+D set is non-singleton for graded attributions.**
    Both positive and weakPositive are valid F+D explanations for the
    same configuration — demonstrating more design freedom than binary. -/
theorem graded_fdSet_nontrivial :
    fdCompatibleAt gradedSystem true .positive ∧
    fdCompatibleAt gradedSystem true .weakPositive ∧
    GradedAttribution.positive ≠ GradedAttribution.weakPositive :=
  ⟨graded_fdCompatible_positive, graded_fdCompatible_weakPositive, by decide⟩

/-! ### 4. Coverage conflict diagnostic -/

/-- An explanation system has **coverage conflict** if every element of H
    is incompatible with some native explanation value. There is no "safe
    harbor" — every possible explanation clashes with something.

    Coverage conflict is the diagnostic for whether the bilemma applies:
    - Coverage conflict → no neutral element → bilemma applies
    - No coverage conflict → neutral element exists → DASH works -/
def hasCoverageConflict {Θ H Y : Type} (S : ExplanationSystem Θ H Y) : Prop :=
  ∀ (c : H), ∃ (θ : Θ), S.incompatible c (S.explain θ)

/-- A neutral element: compatible with every explain-value. -/
def hasNeutralElement {Θ H Y : Type} (S : ExplanationSystem Θ H Y) : Prop :=
  ∃ (c : H), ∀ (θ : Θ), ¬S.incompatible c (S.explain θ)

/-- Coverage conflict implies no neutral element. -/
theorem coverageConflict_implies_no_neutral {Θ H Y : Type}
    (S : ExplanationSystem Θ H Y)
    (hcc : hasCoverageConflict S) :
    ¬hasNeutralElement S := by
  intro ⟨c, hc⟩
  obtain ⟨θ, hinc⟩ := hcc c
  exact hc θ hinc

/-- A neutral element destroys coverage conflict. -/
theorem neutral_destroys_coverageConflict {Θ H Y : Type}
    (S : ExplanationSystem Θ H Y)
    (hn : hasNeutralElement S) :
    ¬hasCoverageConflict S := by
  intro hcc
  exact coverageConflict_implies_no_neutral S hcc hn

/-- The concrete ML system has coverage conflict. -/
theorem concreteML_coverageConflict :
    hasCoverageConflict concreteMLSystem := by
  intro c
  cases c
  · exact ⟨true, by simp [concreteMLSystem]⟩
  · exact ⟨false, by simp [concreteMLSystem]⟩

end DASHImpossibility
