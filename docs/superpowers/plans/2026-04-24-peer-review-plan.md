# Multi-Reviewer Peer Review Plan

## Reviewer Matrix

### Domain Specialists (6 reviewers)
| ID | Persona | Stance | Focus | Target |
|----|---------|--------|-------|--------|
| R1 | XAI/Attribution theory (knows Bilodeau, Huang, Shapley axiomatics) | Adversarial | Is the impossibility trivial? Does it add to Bilodeau 2024? | NeurIPS |
| R2 | Mechanistic interpretability (knows Elhage, Conmy, Nanda, Wang) | Adversarial | Is component-level claim well-grounded? Is V^G novel? | NeurIPS |
| R3 | Formal methods / proof assistant (knows Lean, Isabelle, Coq, mathlib) | Neutral | Are 6 axioms justified? Is the formalization meaningful or boilerplate? | Both |
| R4 | ML theory / learning theory (knows Rashomon, PAC, VC) | Enthusiastic-rigorous | Is the Design Space theorem a genuine characterization? | NeurIPS |
| R5 | Applied ML / fairness (knows Chouldechova, Kleinberg, COMPAS) | Neutral | Is the regulatory claim (EU AI Act) defensible? Clinical reversal meaningful? | NeurIPS |
| R6 | Biostatistics / genomics (knows GWAS, pathway analysis, biomarker discovery) | Neutral | Is the gene expression claim (TSPAN8/CEACAM5) correctly interpreted? | Monograph |

### Cross-Domain Reviewers (4 reviewers)
| ID | Persona | Stance | Focus | Target |
|----|---------|--------|-------|--------|
| R7 | Social choice / Arrow's theorem expert | Cross-domain | Structural analogy to Arrow. Is the trilemma genuinely new or a known pattern? | NeurIPS |
| R8 | Statistics / causal inference (knows Pearl, Spirtes, d-separation) | Cross-domain | Is "Rashomon property" well-defined? Statistical methodology sound? | Both |
| R9 | AI safety researcher (knows Anthropic's interpretability, SAEs, circuits) | Cross-domain | Does the impossibility actually constrain safety cases? Is the V^G resolution practical? | NeurIPS |
| R10 | Representation theory / group theory (knows Reynolds operator, invariant theory) | Cross-domain | Is the orbit averaging framing mathematically rigorous or hand-wavy? | NeurIPS |

### Area Chairs (2 meta-reviewers)
| ID | Persona | Stance | Focus | Target |
|----|---------|--------|-------|--------|
| AC1 | NeurIPS area chair (ML theory track) | Meta-review | Best paper potential? Scores, weaknesses, decision | NeurIPS |
| AC2 | Nature interdisciplinary area editor | Meta-review | Cross-domain significance, accessibility, monograph completeness | Monograph |

## Review Template (all reviewers)

```
## Summary (2-3 sentences)
## Strengths (numbered, specific)
## Weaknesses (numbered, specific, with severity: CRITICAL / MAJOR / MINOR)
## Questions for Authors (numbered)
## Missing References or Comparisons
## Detailed Comments (by section)
## Score: [1-10] with one-line justification
## Confidence: [1-5] (5 = expert in this exact area)
## Best Paper Recommendation: Yes/No with justification
```

## Execution Plan

### Phase 1: NeurIPS paper reviews (R1-R5, R7-R10 in parallel)
- Each reviewer reads paper/main.tex
- Each applies their persona and stance
- Output: structured review per template

### Phase 2: Monograph reviews (R3, R6, R8, AC2 in parallel)
- R3: Lean formalization section
- R6: Gene expression + TinyStories methodology
- R8: Statistical methodology throughout
- AC2: Overall assessment

### Phase 3: Area chair meta-reviews (AC1, AC2)
- AC1 synthesizes NeurIPS reviews
- AC2 synthesizes monograph reviews

### Phase 4: Triage and fix
- Sort all weaknesses by severity (CRITICAL > MAJOR > MINOR)
- Fix every CRITICAL and MAJOR issue
- Address MINOR issues where feasible within page limit
