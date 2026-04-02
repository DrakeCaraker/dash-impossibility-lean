# Realistic Reception Assessment

Generated: 2026-04-02
Methodology: Non-adversarial, full-spectrum audience analysis

## Where This Sits in the Landscape

Most comparable to Chouldechova (2017) — a clean impossibility in an applied domain that is politically/practically salient, with the added distinction of formal verification (like Nipkow) and a companion library (like Lundberg).

The core impossibility is simpler than Arrow but less general. The formalization is more ambitious than Nipkow. The practical tools give it a Lundberg-like software path to adoption.

**Honest comparison**: The core impossibility is not as deep as Arrow or as surprising as Chouldechova. Its strength is the COMBINATION — impossibility + quantification + resolution + verification + software — which no single predecessor achieves.

## The Three Groups Who Will Care Most

1. **Practitioners** (data scientists, model validators at banks/healthcare): They get a diagnosis, a test, and a fix.
2. **Regulators** (EU AI Act, SR 11-7): Formal language for an informal concern, directly relevant to compliance.
3. **XAI theorists**: The Design Space Theorem, SBD, and conditional SHAP impossibility generate follow-on work.

## Key Findings

### Is it important?
Yes, but the importance lies in the PACKAGE (making it precise, quantifying it, proving it can't be fixed except by DASH, providing tools), not in the core impossibility alone.

### Is it surprising?
The core impossibility: no. Anyone who has retrained a model already suspected this. The Design Space Theorem (exactly two families, nothing else) IS genuinely surprising. The conditional SHAP result (switching methods doesn't help when causal effects are equal) is unexpected.

### Does the formalization matter?
For the core impossibility: no (4-line proof, anyone can check). For the full package: yes — caught 2 genuine errors, zero-sorry guarantee lets reviewers focus on axiom quality. For citation impact: negligible. Almost nobody will run `lake build`.

### Is DASH "just averaging"?
Both. The operation is simple. The contribution is proving it's optimal (Cramér-Rao), giving the tight ensemble size formula, and providing the diagnostic workflow.

### Is the SBD a real technique?
Yes, with 40% odds of being cited AS a technique within 5 years. Three genuinely distinct instances (different symmetry groups). Legitimate connection to classical invariant decision theory.

## Citation Trajectory

| Scenario | Citations (5yr) | Probability | What Determines It |
|----------|----------------|-------------|-------------------|
| Pessimistic | ~20 | 20% | No library adoption, XAI moves to LLM explanations |
| Expected | 80-150 | 60% | JMLR publication, moderate dash-shap adoption, fairness community cites |
| Optimistic | 300+ | 20% | Prominent amplification, regulatory reference, dash-shap becomes standard |

**Single most important factor**: dash-shap library adoption. Tooling drives practice more than theorems.

## The Combined Package

The combination matters significantly more than any piece alone. This is the Lundberg & Lee model — if dash-shap achieves even 5% of shap's adoption, it dwarfs citation-based impact. The README targeting 4 audiences simultaneously increases discovery surface area.

## The Honest Summary

**What this work is.** A formally verified impossibility theorem establishing that no feature ranking can be simultaneously faithful, stable, and complete when features are correlated. The core result is simple — a four-line contradiction — but embedded in substantial infrastructure: quantitative bounds, a complete design space characterization, a provably optimal resolution, a general proof technique, practical diagnostics, and 188 machine-checked Lean 4 theorems. Accompanied by a Python package and diagnostic workflow.

**Who will care.** Practitioners who use SHAP and have encountered instability. Regulators implementing the EU AI Act. XAI theorists building on the Design Space Theorem. The broader ML community will absorb the headline without reading the paper.

**What determines lasting impact.** Whether dash-shap gets integrated into the SHAP ecosystem. Whether AI regulation mandates explanation stability testing. Whether the field's attention stays on feature attribution. The theorem is permanent mathematics; whether anyone needs it depends on whether the problems remain central.
