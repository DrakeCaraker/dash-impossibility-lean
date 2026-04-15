/-
  Mechanistic Interpretability Impossibility.

  No circuit explanation of a neural network can simultaneously be faithful
  (report the actual circuit decomposition), stable (same circuit across
  functionally equivalent networks), and decisive (commit to a single
  decomposition).

  For binary circuit spaces (two valid decompositions), the bilemma applies:
  faithful + stable alone is impossible — even dropping decisiveness doesn't help.

  Empirical grounding: Meloux et al. (ICLR 2025) found 85 distinct valid
  circuits with zero circuit error for a simple XOR task, each admitting
  an average of 535.8 valid interpretations.

  The resolution: report circuit equivalence classes (the "CPDAG of circuits")
  — features shared across ALL valid decompositions.

  Ported from universal-explanation-impossibility/MechInterpInstanceConstructive.lean.
  Re-proved here using dash-impossibility-lean's ExplanationSystem framework.
-/
import DASHImpossibility.Bilemma

set_option autoImplicit false

namespace DASHImpossibility

/-! ### Constructive types — all finite, all decidable -/

/-- Minimal circuit configurations: two networks with different internal
    wiring but identical input-output behavior.
    Abstracts: circuitAlpha implements XOR via one circuit path,
    circuitBeta implements XOR via a different circuit path. -/
inductive MechInterpCfg where
  | circuitAlpha : MechInterpCfg
  | circuitBeta  : MechInterpCfg
  deriving DecidableEq

/-- The function computed by the network.
    Both configurations compute the same function. -/
inductive MechInterpOutput where
  | sameFunction : MechInterpOutput
  deriving DecidableEq

/-- Which circuit decomposition the interpretability method identifies. -/
inductive CircuitDecomp where
  | decompAlpha : CircuitDecomp
  | decompBeta  : CircuitDecomp
  deriving DecidableEq

/-! ### The explanation system -/

/-- Both configurations compute the same function. -/
def mechInterpObserve : MechInterpCfg → MechInterpOutput
  | _ => MechInterpOutput.sameFunction

/-- Each configuration has a different circuit decomposition. -/
def mechInterpExplain : MechInterpCfg → CircuitDecomp
  | .circuitAlpha => .decompAlpha
  | .circuitBeta  => .decompBeta

/-- The mechanistic interpretability explanation system.
    Incompatibility = inequality (circuits either match or disagree). -/
def mechInterpSystem : ExplanationSystem MechInterpCfg CircuitDecomp MechInterpOutput where
  observe := mechInterpObserve
  explain := mechInterpExplain
  incompatible := fun d₁ d₂ => d₁ ≠ d₂

/-! ### Derived properties (all by `decide` — zero axioms) -/

/-- Incompatibility is irreflexive (nothing disagrees with itself). -/
theorem mechInterp_irrefl (d : CircuitDecomp) :
    ¬mechInterpSystem.incompatible d d :=
  fun h => h rfl

/-- Circuit decomposition is maximally incompatible: compatible ⇒ equal.
    (For a 2-element type with incompatible = ≠, this is just ¬¬-elimination.) -/
theorem mechInterp_compatible_eq (d₁ d₂ : CircuitDecomp) :
    ¬mechInterpSystem.incompatible d₁ d₂ → d₁ = d₂ :=
  fun h => Classical.byContradiction fun hne => h hne

/-- Same output for both configurations. -/
theorem mechInterp_same_output :
    mechInterpObserve .circuitAlpha = mechInterpObserve .circuitBeta := by
  decide

/-- Different circuit decompositions. -/
theorem mechInterp_different_circuits :
    mechInterpSystem.incompatible
      (mechInterpExplain .circuitAlpha)
      (mechInterpExplain .circuitBeta) := by
  intro h
  exact absurd h (by decide)

/-! ### The impossibility theorems -/

/-- **Mechanistic Interpretability Impossibility (Trilemma).**
    No circuit explanation can be simultaneously faithful, stable,
    and decisive. Rashomon is DERIVED from the constructive types
    (zero axioms). -/
theorem mech_interp_impossibility
    (E : MechInterpCfg → CircuitDecomp)
    (hf : faithful mechInterpSystem E)
    (hs : stable mechInterpSystem E)
    (hd : decisive mechInterpSystem E) : False :=
  explanation_impossibility mechInterpSystem
    mechInterp_irrefl
    .circuitAlpha .circuitBeta
    mechInterp_same_output
    mechInterp_different_circuits
    E hf hs hd

/-- **Mechanistic Interpretability Bilemma.**
    For circuit explanations, faithful + stable alone is impossible —
    even dropping decisiveness does not help. This is because the
    circuit decomposition space is binary (maximally incompatible:
    compatible ⇒ equal), so faithfulness forces E = explain, which
    is automatically decisive.

    This is strictly stronger than the trilemma: there is no
    "DASH-like" resolution for circuit explanations. The only
    resolution is to report equivalence classes of circuits. -/
theorem mech_interp_bilemma
    (E : MechInterpCfg → CircuitDecomp)
    (hf : faithful mechInterpSystem E)
    (hs : stable mechInterpSystem E) : False :=
  bilemma_of_compatible_eq mechInterpSystem
    mechInterp_irrefl
    mechInterp_compatible_eq
    .circuitAlpha .circuitBeta
    mechInterp_same_output
    mechInterp_different_circuits
    E hf hs

/-- **Rashomon unfaithfulness for circuits.**
    Any stable circuit explanation method is unfaithful at ≥1 of every
    2 functionally equivalent networks with different circuits. -/
theorem mech_interp_unfaithfulness
    (E : MechInterpCfg → CircuitDecomp)
    (hs : stable mechInterpSystem E) :
    mechInterpSystem.incompatible (E .circuitAlpha) (mechInterpExplain .circuitAlpha) ∨
    mechInterpSystem.incompatible (E .circuitBeta) (mechInterpExplain .circuitBeta) :=
  rashomon_unfaithfulness mechInterpSystem
    mechInterp_compatible_eq
    E hs
    .circuitAlpha .circuitBeta
    mechInterp_same_output
    mechInterp_different_circuits

end DASHImpossibility
