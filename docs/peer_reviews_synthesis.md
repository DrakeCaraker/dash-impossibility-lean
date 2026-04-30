# Peer Review Synthesis — All 9 Reviews

---

## R1_XAI_Adversarial

Now I have a comprehensive understanding of the paper. Here is my review.

---

## Reviewer 1: Structured Review

### Summary (2-3 sentences)

This paper proves that no attribution ranking (at any model level) can simultaneously be faithful, stable, and complete when the Rashomon property holds. The authors formalize the result in Lean 4, instantiate it for GBDTs, Lasso, neural nets, and activation patching, propose orbit averaging (DASH) as the resolution, and validate predictions on synthetic data, public datasets, and TinyStories transformers. The theorem itself is a 4-line proof from definitions; the bulk of the contribution is the surrounding framework (design space, bilemma, diagnostics) and the empirical program.

### Strengths

1. **Unifying framing across attribution levels.** Applying the same impossibility to input-level (SHAP) and component-level (activation patching) attribution is genuinely novel. The TinyStories experiments showing full $S_4$ realized across seeds are striking and, to my knowledge, the first systematic demonstration of this phenomenon in circuit analysis.

2. **The empirical program is thorough and well-designed.** 14/14 pre-registered predictions confirmed at two scales. The GPT-2 boundary condition (fine-tuning does not create Rashomon diversity, so instability vanishes) is an excellent falsifiability test. The ranking lottery experiment (24 distinct top-3 rankings from 50 seeds on Breast Cancer) is a compelling demonstration.

3. **The nonparametric diagnostic is practical and clean.** The 7-line minority fraction predictor achieving Spearman 0.95+ is a genuinely useful tool. Its superiority over the Gaussian formula is well-demonstrated.

4. **The Lean formalization is serious engineering.** 357 theorems, 6 axioms, 0 sorry, 58 files. The axiom stratification (core impossibility: 0 axioms; full system: 6) is well-documented and adds genuine credibility. The fact that formalization caught 3 logical errors is an honest and valuable disclosure.

5. **The design space theorem provides constructive guidance.** Showing exactly two achievable families and proving DASH is Pareto-optimal on the $\mathcal{B}$ branch goes beyond a bare impossibility.

6. **The bilemma strengthens the result for binary problems.** Showing that F+S alone is impossible (without needing completeness) for binary $H$ is a non-trivial tightening.

### Weaknesses

1. **CRITICAL: The core theorem may be trivially obvious.** The proof is: "Rashomon gives two models with opposite orderings; a stable+faithful+complete ranking must pick one ordering; it contradicts the other model." This is essentially restating the definition of the Rashomon property as an impossibility. The intellectual content is the *observation* that faithfulness+stability+completeness is the right decomposition to make the Rashomon property's consequences crisp---but the theorem itself has no surprising technical step. The authors should directly address this: is the contribution the theorem, or the framework? If the framework, the paper's emphasis on "Attribution Impossibility" as the headline result is potentially misleading. **What to do:** Add a paragraph in Section 2 explicitly acknowledging the proof's simplicity and arguing why the decomposition into F/S/C is non-trivial (e.g., other decompositions don't yield clean impossibilities, or practitioners were not aware of this consequence). Compare to Arrow's theorem, which also has a short proof but a non-obvious decomposition.

2. **CRITICAL: Relationship to Bilodeau et al. 2024 is underspecified in the main text.** The main paper gives one sentence: "completeness + linearity cannot coexist (different axis: method properties, not cross-model stability)." This is insufficient for NeurIPS reviewers who know that paper. The claim of orthogonality is only substantiated in the definitive monograph version (with the $\rho=0$ / nonlinear method example), not in the submitted main text. A reviewer could reasonably conclude this is a weaker version of Bilodeau's result, applied to a specific setting. **What to do:** Add 2-3 sentences in Section 5 (Related Work) making the orthogonality explicit: (a) Bilodeau requires linearity of the attribution method; yours does not. (b) Yours requires the Rashomon property (collinearity); Bilodeau's does not. (c) Give the concrete example: uncorrelated features + linear SHAP satisfies Bilodeau but not yours; nonlinear method + correlated features satisfies yours but not Bilodeau's.

3. **MAJOR: The Rashomon property is assumed, not proved for real models.** The paper says it is "inevitable" for stochastic symmetric algorithms (Rashomon Inevitability Theorem, Lean-verified), but this is in the supplement and the conditions for it are not stated in the main text. For the theorem to have practical force, the reader needs to know: under what conditions does the Rashomon property *actually hold*? The empirical prevalence (68% of 77 datasets) is evidence but not a proof. **What to do:** State the Rashomon Inevitability conditions briefly in Section 2 (even one sentence: "The Rashomon property holds for any stochastic learning algorithm whose training distribution is invariant under permutation of symmetric features; see supplement for the Lean-verified proof"). Without this, the impossibility is conditional on an assumption the reader cannot evaluate.

4. **MAJOR: "Attribution" is stretched to cover activation patching.** Definition 1 defines an attribution system as $(\Theta, \varphi_j, \succ)$. Calling activation patching importance $\varphi_j$ an "attribution" is defensible but non-standard. The Shapley axiomatics community (Sundararajan, Lundberg) uses "attribution" for input-level importance satisfying specific axioms (efficiency, symmetry, etc.). Activation patching satisfies none of these. The paper should acknowledge this terminological choice and defend it. **What to do:** Add a remark after Definition 1 noting that "attribution system" is used in the abstract sense of any importance measurement, and that the Shapley-axiomatic sense is a special case. This prevents readers from assuming the theorem applies only to SHAP-like methods, and also prevents the objection that the theorem is vacuous for methods that don't satisfy the axioms.

5. **MAJOR: The Design Space Theorem's Family $\mathcal{A}$ characterization is imprecise.** The theorem says $U = 1/2$ for Family $\mathcal{A}$. This seems to assume a uniform prior over models in the Rashomon set (or equal probability of each ordering). Is this stated? If $U = 1/2$ requires a symmetry assumption on the model distribution, it should be explicit. **What to do:** State the distributional assumption under which $U = 1/2$ holds (presumably: the training distribution is symmetric over interchangeable features).

6. **MAJOR: The $1/(1-\rho^2)$ ratio is for an idealized GBDT model, but the empirical fit uses a correction $\alpha \approx 2/\pi$.** The paper presents the theoretical ratio $1/(1-\rho^2)$ as a headline result but then immediately notes it needs correction for real trees. The uncorrected formula is thus never empirically validated. The Lean formalization proves the uncorrected version. There is a gap between what is proved and what is validated. **What to do:** Be explicit that the Lean-verified $1/(1-\rho^2)$ is for infinite-depth trees with $\alpha=1$, and that the finite-depth correction $\alpha \approx 2/\pi$ is empirical (not proved).

7. **MINOR: The clinical decision reversal framing is rhetorically loaded.** "45% of applicants receive a different most important feature category" sounds alarming, but the paper does not verify that this actually changes any actionable decision. The models all make the same prediction; only the explanation differs. Whether this matters depends on regulatory context. The EU AI Act reference is speculative. **What to do:** Temper the claim slightly: note that explanations differ, not decisions, and that the regulatory significance depends on jurisdiction and use case.

8. **MINOR: The paper claims "first formally verified impossibility in XAI."** This is a strong priority claim. Arrow's theorem has been formalized in Isabelle/HOL (cited). If one considers social choice theory as adjacent to decision-making explanation, this claim needs qualification. **What to do:** Add "to our knowledge" or specify "first in machine learning explainability."

9. **MINOR: The 68% prevalence figure.** The paper states 68% of 77 datasets exhibit instability. What is the threshold for "instability"? Is it any flip > 0? A flip rate > some threshold? This number is meaningless without a definition. The Wilson CI is given but the operationalization is not. **What to do:** Define the instability criterion used for the prevalence count.

10. **MINOR: Table 3 (clinical decision reversal).** The deterministic control for XGBoost shows 0% reversal, but Random Forest shows 35% even in deterministic mode. This is because RF is inherently stochastic (bootstrap). This asymmetry deserves a sentence of explanation.

### Questions for Authors

1. What is the minimal non-trivial instantiation of the Rashomon property? You define it abstractly, but does it hold for linear regression with collinear features? If yes, can you prove it (not just assert it)? If no, what is the boundary?

2. The bilemma says F+S is impossible for binary $H$. But any practitioner would say: "I don't need stability; I want the explanation for *this* model." How do you respond to the position that stability is not a desirable property---that a model-specific explanation is the right one?

3. For the component-level experiments: you use weight zeroing and mean ablation. Have you tried activation patching in the sense of Conmy et al. (2023) or path patching? These are the standard methods in the mechanistic interpretability community. Weight zeroing is a relatively crude proxy.

4. The DASH resolution requires $M=25$ models. For large-scale models (GPT-scale), this is impractical. The paper mentions GPT-2 fine-tuning as a boundary condition. But fine-tuning is not the use case where instability is most concerning---pre-training is. Can you comment on the practical feasibility of orbit averaging for frontier models?

5. The paper conflates two senses of "symmetry": DGP symmetry (features have the same true coefficient) and architectural symmetry (heads within a layer are interchangeable by construction). These are very different. DGP symmetry is about the world; architectural symmetry is about the model. Is the impossibility really "the same" at both levels, or are these two different theorems sharing a syntactic form?

6. You cite your own companion code (dash-shap PR #255) and a forthcoming analysis. Is this self-citation anonymous? If a reviewer can identify the authors from the companion repo, anonymity is broken.

### Missing References or Comparisons

- **Conmy et al. 2023 (ACDC)**: The standard reference for automated circuit discovery. The paper discusses activation patching but does not cite the methodological work that made it practical.
- **Wang et al. 2023 (Interpretability in the Wild)**: Showed circuit-level analysis of IOI; relevant to the claim about circuit instability.
- **Marx et al. 2024 (But Are They Right?)**: Directly addresses the question of when feature importance methods agree/disagree across models.
- **Slack et al. 2021**: On the unreliability of saliency methods---relevant to the instability narrative.
- **Ghorbani et al. 2019 (Interpretation of Neural Networks is Fragile)**: Showed that small input perturbations change attributions; related to instability but along a different axis.

### Detailed Comments (by Section)

**Section 1 (Introduction):** The opening is effective. "Train a GBDT, compute SHAP, retrain" is a clean setup. The two-level framing (input + component) is well-motivated. However, the contributions list is long (5 items) and somewhat diffuse---the reader is not sure what the *primary* contribution is. I would recommend foregrounding either the theorem or the empirical program, not both equally.

**Section 2 (Setup and Impossibility):** The definitions are clean. However, "faithful" is defined as a biconditional ($j \succ k$ iff $\varphi_j > \varphi_k$) in the Lean code but as an implication ("whenever") in the paper text. The Lean code shows both versions (strong and weak). The paper should clarify which version the main theorem uses. The Design Space Theorem is stated but not proved in the main text; given that the impossibility proof is 4 lines, there is room to sketch the design space proof or at least state its key steps.

**Section 3 (Bilemma and Diagnostics):** The bilemma is interesting. The diagnostic section is the strongest part of the paper from a practitioner perspective. The minority fraction is simple, effective, and immediately usable. The code listing is a nice touch.

**Section 4 (Resolution):** The connection to the Reynolds operator is mathematically elegant but may be lost on the NeurIPS audience. The claim that DASH is "uniquely optimal" for binary $H$ via Hunt-Stein needs a reference or a brief argument.

**Section 5 (Experiments):** Well-executed. The ranking lottery table is the strongest single exhibit. The TinyStories experiments are carefully designed with pre-registered predictions. One concern: the "24 distinct top-3 rankings" on Breast Cancer---is Breast Cancer known to have highly collinear features? If so, this is expected and less surprising. If not, it is more impressive. State the collinearity structure.

**Section 6 (Related Work):** Too compressed. The comparisons are one-sentence each. Bilodeau needs more space (see Weakness 2). The fairness trilemma comparison (Chouldechova, Kleinberg) is apt but underdeveloped---the structural analogy deserves 2-3 sentences.

**Section 7 (Discussion):** The limitations are honest. The open problems are genuinely interesting (scaling to frontier models, non-architectural symmetries). The EU AI Act claim is speculative and should be flagged as such more clearly.

### Score: 6/10

The paper addresses a real and important problem (attribution instability) with a clean theoretical framework and strong empirical validation. The Lean formalization is impressive engineering. However, the core theorem is perilously close to a restatement of the Rashomon property's definition, the comparison to Bilodeau et al. is insufficient for the main text, and several claims need tightening. The contribution is real but the balance between theorem (trivial-looking) and framework+experiments (substantial) needs better calibration in the presentation.

### Confidence: 4/5

I am familiar with the Shapley axiomatics literature, Bilodeau et al., and the mechanistic interpretability work. I am less familiar with Lean formalizations and cannot independently verify the 357-theorem claim, though the methodology appears sound.

### Best Paper Recommendation: No

The empirical program and the two-level unification are strong, but the core theorem's apparent triviality and the insufficient comparison to prior impossibility results prevent a best paper recommendation. A revised version that better addresses the "is this obvious?" question and sharpens the Bilodeau comparison could change this assessment.

---

## R2_MI_Adversarial

I now have a thorough understanding of the paper. Let me write the review.

---

## Summary (2-3 sentences)

The paper proves an impossibility theorem stating that no attribution ranking can simultaneously be faithful, stable, and complete when a "Rashomon property" holds---meaning interchangeable components can swap importance across equivalent configurations. The authors instantiate this at two levels (input-level SHAP, component-level circuit analysis), propose orbit averaging as the resolution, and validate empirically on tabular datasets and TinyStories transformers. The Lean 4 formalization (357 theorems, 0 sorry) is a genuine contribution to formal methods in ML theory.

## Strengths

1. **Clean core theorem.** The impossibility itself is elegant, genuinely zero-axiom, and machine-verified. The logical structure (Rashomon + completeness + faithfulness + stability yields contradiction) is tight and simple. This is the strongest part of the paper.

2. **Input-level experiments are thorough.** The ranking lottery experiment (24 distinct top-3 rankings from 50 seeds on Breast Cancer) is striking and reproducible. The 68%-of-77-datasets prevalence number, the clinical decision reversal on German Credit, and the cross-implementation validation (XGBoost/LightGBM/RF) are well-designed and convincing.

3. **The bilemma is a genuinely stronger result** for binary questions and has direct implications for feature selection, SHAP sign stability, and circuit membership. The tightness classification (neutral element iff F+S achievable) is mathematically clean.

4. **The minority fraction diagnostic** is simple, practical, and demonstrably superior to the Gaussian formula. The 7-line code snippet is a real contribution to practitioner tooling.

5. **Lean formalization** is a first for XAI impossibility results and sets a valuable precedent, especially the axiom stratification showing which results depend on which assumptions.

6. **The design space theorem** is well-structured and the two-family exhaustiveness is a useful conceptual contribution.

7. **Good experimental controls.** Deterministic controls (subsample=1.0) correctly produce zero instability, establishing that the effect is real and attributable to stochasticity.

## Weaknesses

1. **[CRITICAL] The "interchangeability" claim for attention heads is fundamentally wrong as stated.** The paper says (Instance 2, line 112): "heads within a layer are interchangeable by construction." This is false. Attention heads within a layer are architecturally symmetric at initialization, but after training they specialize into functionally distinct roles: induction heads, previous-token heads, duplicate-token heads, backup heads (Olsson et al. 2022, Wang et al. 2022). The architecture is symmetric; the learned functions are not. The Rashomon property as defined requires interchangeable components with swapped importance rankings. But the paper's own data shows this is trivially true only because they retrain from scratch with different seeds---the "interchangeability" is between *different training runs*, not within a single trained network. This conflates two very different things: (a) architectural symmetry of the parameter space pre-training, and (b) functional interchangeability of learned components post-training. The theorem formally requires the latter, and the paper only has the former. The authors should clearly distinguish "permutation symmetry of the loss landscape" from "interchangeability of trained components." The theorem applies, but the framing is misleading.

2. **[CRITICAL] Weight zeroing is not activation patching.** The paper repeatedly says "importance measured by activation patching (weight zeroing)" (line 302). In the MI community, activation patching (Vig et al. 2020, Meng et al. 2022) replaces activations at specific token positions with those from a reference input. Weight zeroing is a crude knockout ablation. These are fundamentally different interventions. Path patching (Goldowsky-Dill et al. 2023) traces causal effects through specific edges. Causal scrubbing (Chan et al. 2022) tests entire computational subgraphs. The paper tests weight zeroing and mean ablation (line 331), both of which are position-independent, global ablations. The impossibility may not hold for position-specific, input-dependent patching methods where the "symmetry" between heads is broken by the specific input being analyzed. The paper acknowledges this in limitations (line 354: "other patching methods may show different instability patterns") but then immediately claims "though the theorem predicts the same structure"---which is asserted without evidence. This needs either empirical validation with proper activation patching / path patching or an honest admission that the component-level results are limited to crude ablation methods.

3. **[MAJOR] TinyStories is a toy setting that does not support the safety claims.** The paper makes strong claims about AI safety (line 358: "interpretability-based safety cases that depend on identifying 'the circuit' for a behavior are subject to the same impossibility"). But the empirical evidence comes from 4-layer and 6-layer transformers on TinyStories. No serious safety case would be built on a 4-layer model. The GPT-2 experiment (line 327-328) uses fine-tuning, not training from scratch, and the authors correctly note this does not create a diverse Rashomon set. So the only setting where the impossibility is empirically confirmed at circuit level is a toy one, and the only non-toy setting (GPT-2) shows the impossibility does NOT hold. The paper spins the GPT-2 result as "confirming the boundary," but a skeptic would read it as: the impossibility is irrelevant for production models, which are pre-trained once and then fine-tuned. The safety implications paragraph (line 358) is not supported by the evidence.

4. **[MAJOR] V^G is just layer averaging with extra notation.** The paper acknowledges this (line 209: "for S_k^L this reduces to layer averaging---a familiar operation") but then argues the contribution is identifying *why* it works. However, anyone performing circuit analysis already knows that individual head importance varies across training runs and that layer-level importance is more stable. Elhage et al. (2021) discuss layer-level analysis extensively. The "richer symmetry groups" mentioned (line 209: "for richer symmetry groups...V^G extends beyond simple layer averaging") are never instantiated empirically. The V^G notation and Reynolds operator framing add mathematical elegance but essentially no new practical insight for the MI community. The random projection baseline (line 325: "random projections achieve only rho=0.30-0.41") is a straw man---nobody would use random projections as a dimensionality reduction for circuit analysis.

5. **[MAJOR] The "same theorem, same resolution" unification is misleading.** For input-level, the resolution (DASH) requires M=25 retrains at full training cost. For component-level, V^G is a free post-processing step on a single model's components. These are not "the same resolution" in any practical sense. The mathematical connection (both are Reynolds operators) is true but shallow---the Reynolds operator on different groups with different computational costs and different practical implications is a formal analogy, not a deep unification. The paper should be honest about this asymmetry rather than presenting it as a unified framework.

6. **[MAJOR] No comparison with sparse autoencoders (SAEs).** The dominant paradigm for interpreting neural network internals has shifted toward SAEs (Cunningham et al. 2023, Bricken et al. 2023, Templeton et al. 2024) which decompose activations into interpretable features that are NOT architecturally symmetric. SAE features have semantic meaning (e.g., "the Golden Gate Bridge feature") and are not subject to permutation symmetry in the same way attention heads are. If the MI community's response to head-level instability is "we don't analyze individual heads anymore, we analyze SAE features," then the component-level contribution of this paper is addressing a problem the field has already moved past. The paper needs to engage with this.

7. **[MINOR] The Rashomon Inevitability claim is too strong.** The paper states (line 95) that the Rashomon property is "inevitable for any stochastic, symmetric algorithm on interchangeable components." But modern training is NOT symmetric: learning rate warmup, layer-specific learning rates, architectural innovations (pre-norm vs post-norm), and weight initialization schemes all break the symmetry. The claim holds for idealized SGD on a perfectly symmetric loss landscape, but real training pipelines introduce many symmetry-breaking operations.

8. **[MINOR] The "pre-registered predictions" language (line 302: "We derive 7 quantitative predictions...and evaluate them before any post-hoc analysis") is unverifiable in the current paper format.** Without a timestamped pre-registration, this is just a claim.

9. **[MINOR] Missing error bars throughout.** Table 3 reports single numbers (rho=0.565, 0.540) without confidence intervals. For 10 models, pairwise Spearman has 45 pairs---what is the variance? The flip rates 0.496 and 0.489 are reported to three decimal places without uncertainty.

## Questions for Authors

1. Can you provide activation patching results (proper position-specific patching, not weight zeroing) for the TinyStories models? If the impossibility also holds for path patching, that would substantially strengthen the component-level claims. If it does not, that is important to know.

2. How does V^G interact with SAE-based analysis? If one extracts SAE features from attention head outputs, the resulting features are not architecturally symmetric. Does the impossibility still apply? If not, is the component-level theorem essentially limited to raw head/MLP analysis?

3. The GPT-2 experiment shows near-perfect stability under fine-tuning. But virtually all production interpretability work is done on pre-trained or fine-tuned models, not models trained from scratch. Can you point to a realistic scenario where someone would train multiple large models from scratch and compare circuit analyses?

4. You claim V^G extends beyond layer averaging for "richer symmetry groups." Can you provide a single concrete example where V^G produces a non-trivial (non-layer-averaging) aggregation on a real architecture?

5. The paper claims "A circuit found in one training run may not exist in a functionally equivalent run" (line 358). But the empirical evidence shows that the *layer-level* circuit structure IS stable (rho=0.98). Isn't the correct conclusion that circuits are stable at the right level of abstraction, rather than that circuit-based safety cases are unreliable?

6. What happens to the within-layer flip rate for TinyStories models trained with different hyperparameters (depth, width, learning rate) rather than just different random seeds? The current setup maximizes architectural symmetry by using identical architectures.

7. The bilemma proof sketch (line 143) says "Binary H has no neutral element: every value contradicts the other. Faithful forces E(theta) = explain(theta), making E decisive." Can you spell out why faithfulness forces exact equality here rather than approximate agreement?

## Missing References or Comparisons

- **Olsson et al. 2022** ("In-context Learning and Induction Heads"): directly relevant to head specialization, undermines the "interchangeable by construction" claim.
- **Cunningham et al. 2023, Bricken et al. 2023, Templeton et al. 2024**: SAEs as the dominant alternative to head-level circuit analysis. Critical omission.
- **Conmy et al. 2023** (ACDC): automated circuit discovery that uses path patching, not weight zeroing. The paper should compare.
- **Goldowsky-Dill et al. 2023** (Localizing Model Behavior with Path Patching): the standard method for edge-level circuit analysis.
- **Geiger et al. 2024** (Causal Abstraction): a framework for identifying circuits at different levels of abstraction, directly relevant to the orbit averaging idea.
- **Zhong et al. 2024** (The Clock and the Pizza): shows that independently trained models can learn the same algorithm in different representations, supporting the Rashomon claim but at a deeper level than the paper acknowledges.
- **Ainsworth et al. 2023** (Git Re-Basin): shows that independently trained networks can be permutation-aligned to reveal shared structure---a competing resolution to the same problem V^G addresses.

## Detailed Comments

### Section 2 - Instance 2 (lines 111-113)
The claim "heads within a layer are interchangeable by construction" needs heavy qualification. They are interchangeable in the sense that the architecture treats them symmetrically (concatenation is order-invariant up to the output projection matrix). But after training, head 0 in layer 0 might be an induction head while head 3 is a previous-token head. The paper's own Table 3 shows that *between-model* importance rankings are unstable (rho=0.54), but this is a statement about the loss landscape and SGD dynamics, not about the components themselves being interchangeable in any functional sense. The paper should say: "the loss landscape has S_k^L symmetry, so different minima can have permuted head assignments" rather than "heads are interchangeable by construction."

### Section 3 - Component diagnostic (lines 188-189)
The V^G description says it "averages activation patching scores within orbits (heads in the same layer)." This is clear and correct, but the paper oversells the novelty. The diagnostic value is identifying which comparisons are stable (between-layer, head-vs-MLP) vs. unstable (within-layer head ordering). This is useful but not surprising to anyone who has done circuit analysis.

### Section 4 - V^G empirical results (lines 321-328)
The results are clean and the predictions are confirmed. However:
- "All 4 heads in layer 0 appear as most important across 10 seeds" (line 323) --- this is a sample of 10. With 4 heads and uniform probability, you'd expect to see all 4 appear as "most important" in 10 draws with probability ~0.91 (multinomial). This is not remarkable; it would be remarkable if they did NOT all appear.
- Cohen's d of 5.4-11.9 (line 314) for what comparison? This is never defined. Between what groups? Raw vs. G-invariant? Within-layer vs. between-layer variance?
- The GPT-2 result (rho=0.993) is the most important number in the table for MI practitioners, and it says: for the models you actually care about, the problem doesn't exist. The paper buries this implication.

### Section 5 - Discussion (lines 349-364)
The broader implications paragraph (line 357-358) makes strong claims about regulatory compliance (EU AI Act) and AI safety that go well beyond what the toy-scale experiments support. The input-level claims about proxy discrimination and clinical decision reversal are well-supported. The component-level safety claims are not.

The open problems paragraph (line 363-364) mentions "scaling to frontier models (GPT-4 scale)" and "non-architectural symmetries (learned representations)" as future work. These are exactly the settings where the contribution would be significant. As it stands, the paper proves the theorem works where the symmetry is obvious (small models trained from scratch) and does not work where it matters (large pre-trained models).

### Section 5b - Method robustness (line 331)
The cross-method result (mean ablation vs. weight zeroing: per-model rho~0.5-0.6 but V^G rho~0.97-0.99) is actually interesting---it shows that *different ablation methods* disagree on raw importance but agree on orbit-averaged importance. This is framed as "another instance of the impossibility" but it is also evidence that V^G is robust to method choice, which strengthens the V^G contribution. This deserves more attention than one sentence.

## Score: 5

The paper has a clean, machine-verified impossibility theorem with strong input-level experiments. The component-level extension, which is the main novelty claim, is undermined by: (a) a misleading "interchangeability" framing, (b) crude ablation methods only, (c) toy-scale experiments, (d) the GPT-2 result suggesting the problem vanishes at scale, (e) no engagement with SAEs, and (f) V^G being layer averaging in practice. The input-level contribution alone (impossibility + DASH + diagnostics) would be a solid paper but is not novel enough for NeurIPS without the circuit-level extension. The circuit-level extension as presented does not meet the bar for the MI community.

## Confidence: 4

I am confident in my assessment of the MI claims. I have less expertise in the Lean formalization and the formal methods contribution, which I may be undervaluing. The input-level experiments are outside my primary area but appear sound.

## Best Paper Recommendation: No

---

## R4_MLTheory_Enthusiastic

I have now read the full main text and the critical supplement sections. Here is my review.

---

## Reviewer 4 — Structured Review

### Summary (2-3 sentences)

This paper proves that no attribution ranking (at any model level) can simultaneously be faithful, stable, and complete when the Rashomon property holds --- an "Arrow's theorem for explainability." The core impossibility is trivially correct once stated; the paper's real contributions are the Design Space characterization (exactly two achievable families), the bilemma for binary explanation spaces, the orbit-averaging resolution (DASH / $G$-invariant projection), and unusually thorough empirical validation at both input-level (SHAP) and component-level (activation patching on TinyStories). The Lean 4 formalization (357 theorems, 0 sorry) sets a new standard for rigor in XAI theory.

### Strengths (numbered, specific)

1. **The abstraction level is exactly right.** The core impossibility (Theorem 1) requires zero model-specific axioms --- only the Rashomon property. This is genuinely the right level of generality: Arrow's theorem does not assume utility functions are quadratic, and this theorem does not assume models are trees. The separation between "the impossibility holds at Level 0" and "quantitative bounds require model-specific axioms at Levels 2-3" is clean and well-executed.

2. **The two-level validation is compelling.** Testing the same impossibility theorem at input-level (SHAP on tabular data) and component-level (activation patching on transformers) with a unified resolution (orbit averaging as the Reynolds operator on different groups) is strong structural evidence. The TinyStories experiment showing full $S_4$ symmetry realized across 10 seeds is a beautiful empirical confirmation. The GPT-2 fine-tuning boundary condition (Rashomon diversity absent $\Rightarrow$ instability vanishes) is exactly the kind of falsification test that builds confidence.

3. **The Design Space Theorem (Theorem 2) is the most substantive contribution.** Going from "these three properties are incompatible" to "the achievable set has exactly two families, parameterized by a single axis ($M$)" is a significant upgrade over a bare impossibility. The Pareto optimality of DASH within Family $\mathcal{B}$ is properly proved via Cramer-Rao.

4. **The bilemma is a genuine strengthening, not a corollary.** For binary $H$ (SHAP sign, circuit membership, feature selection), faithful + stable alone is impossible without needing completeness. The tightness dichotomy ($F+S$ achievable iff $H$ has a neutral element) is clean and has real practical implications: it tells practitioners *when* orbit averaging helps and when they must enrich the explanation space.

5. **The $M_{\min}$ formula is derived, not assumed.** The ensemble size lower bound (Proposition in supplement S22) matches the Cramer-Rao bound, making it tight. The practitioner formula $M_{\min} = \lceil 2.71 \cdot \sigma_{jk}^2 / \Delta_{jk}^2 \rceil$ is directly useful.

6. **The Lean formalization is not cosmetic.** 357 theorems from 6 axioms with explicit stratification (core impossibility: 0 axioms, GBDT: 3, DASH equity: 5, full system: 6) demonstrates genuine logical hygiene. The claim that formalization caught 2 logical inconsistencies and 1 type mismatch is credible and valuable.

7. **The nonparametric minority-fraction diagnostic** achieving Spearman 0.92-0.98 vs. 0.46-0.89 for the Gaussian formula is a practical contribution with immediate value. The 7-line implementation lowers the barrier to adoption.

8. **The ranking lottery experiment** (Table 1: 24 distinct top-3 rankings from 50 seeds on Breast Cancer) is devastating and immediately communicable. This is the kind of result that changes practice.

### Weaknesses (numbered, with severity)

1. **MAJOR: The Design Space exhaustiveness (Step 3) has a significant scope restriction that is underemphasized in the main text.** The supplement proof (line 2976-2983) explicitly restricts to "any method $A$ that computes a deterministic ranking from per-model attributions" and explicitly excludes "methods producing probabilistic rankings, confidence intervals, or set-valued outputs" and "methods that pool training data." The main text (Theorem 2) states "exactly two families" without this qualification. This is not wrong --- the theorem is correctly stated for its domain --- but the rhetoric ("No third family exists") could mislead readers into thinking the result covers all conceivable approaches. The scope restriction should be stated in the main text theorem statement.

2. **MAJOR: The Hunt-Stein reference is applied loosely.** The classical Hunt-Stein theorem (Lehmann & Romano, Theorem 9.3.3) requires a compact group acting on the parameter space and applies to equivariant estimators under specific loss functions. In `neurips_universal_part2.tex` (line 18-21), the paper states the result for "a finite group $G$ acting on the parameter space." Finite groups are compact, so the compactness condition is fine. However, the theorem requires additional regularity conditions (the group action must be measurable, the risk function must be invariant, etc.). The paper does not verify these. For the specific case at hand (finite permutation group $S_m$, sample mean as estimator), the result is correct --- the Pitman estimator under a finite group is just the orbit average --- but citing Hunt-Stein for this is using a sledgehammer. The optimality of DASH is more directly established by the Cramer-Rao / Rao-Blackwell argument (which the supplement does provide). I recommend either verifying the Hunt-Stein conditions explicitly or downgrading the claim to the Rao-Blackwell argument, which is self-contained and sufficient.

3. **MAJOR: The Rashomon Inevitability Theorem (Theorem S5, supplement line 606) requires stronger conditions than "just symmetry."** The proof chain goes: (i) non-degeneracy (Theorem S4): requires *continuous* dependence of the training algorithm on the random seed and finite samples; (ii) algorithmic symmetry: the algorithm applied to within-group-permuted data produces the permuted model *in distribution*; (iii) the conclusion is that both orderings have probability exactly 1/2. The main text (line 95) says the theorem holds for "any stochastic, symmetric algorithm on interchangeable components," which is accurate, but "stochastic, symmetric" is doing real work here. Deterministic algorithms with tie-breaking rules (e.g., always prefer the lower-indexed feature) break the symmetry condition. The main text should note that the inevitability requires algorithmic symmetry, not just feature-level symmetry.

4. **MINOR: The "collapsed tightness" terminology (main text line 149) is introduced without definition.** The paper says the bilemma has "collapsed tightness --- structurally more severe than the fairness impossibility." This concept is not defined in the main text, is not in the supplement (I searched), and has no precedent I know of in social choice or impossibility theory. The Lean file `BeyondBinary.lean` proves `tightness_dichotomy` but does not use the term "collapsed." If this is a new concept, it needs a definition. If it is informal shorthand for "the relaxation that resolves the trilemma (dropping completeness) does not resolve the bilemma because binary spaces cannot have ties," then say that directly.

5. **MINOR: The connection between the attribution impossibility and Arrow's theorem is implicit but never made precise.** The paper gestures at the analogy (fairness trilemmas cited, social choice formalization cited) but does not state: "The attribution impossibility is/is not a formal instance of Arrow's theorem under some encoding." Given the Lean formalization, this is a missed opportunity. If the attribution impossibility can be formally reduced to Arrow (or shown to be independent), that would significantly clarify its position in the landscape.

6. **MINOR: The $\alpha \approx 2/\pi$ correction factor for finite-depth trees** (main text line 350, Figure 1a) is presented as a limitation but also used to claim $R^2 = 0.89$. Is this correction factor derived or fitted? If fitted, what is the confidence interval on $\alpha$? If derived, where is the derivation? The supplement should clarify.

7. **MINOR: The component-level validation, while impressive, uses only weight zeroing and mean ablation.** The paper acknowledges this (line 354) but the component-level impossibility is stated for "any" attribution method at any granularity. Path patching and causal scrubbing have different sensitivity profiles. One more patching method would strengthen the universality claim.

### Questions for Authors (numbered)

1. **Design Space Scope.** The supplement explicitly excludes probabilistic rankings, confidence intervals, set-valued outputs, and data-pooling methods from the exhaustiveness proof. Could a "Family C" exist in this excluded space? For instance, a method that outputs a posterior distribution over rankings is neither deterministic-complete nor tie-based. Does the impossibility still bite?

2. **Hunt-Stein vs. Rao-Blackwell.** You cite Hunt-Stein for DASH optimality but the supplement proves optimality via Cramer-Rao + Rao-Blackwell, which is stronger and self-contained. Is the Hunt-Stein reference essential for any claim, or is it a convenience citation for the connection to equivariant estimation?

3. **Rashomon Inevitability and exchangeability.** Theorem S5 requires algorithmic symmetry. Many real training pipelines have asymmetries (feature ordering in data files, initialization schemes that depend on feature index). How robust is the inevitability to approximate symmetry? Is there a quantitative version: if the algorithm is $\varepsilon$-symmetric, does the Rashomon property hold with probability $\geq 1/2 - \varepsilon$?

4. **Collapsed tightness.** Is this a formal concept you are introducing, or informal shorthand? If the former, please define it. If the latter, consider removing the term or replacing it with a direct description.

5. **SBD generality.** The supplement (line 3661) candidly states: "A general theorem proving that $G$-invariance of the decision problem always yields a two-family decomposition --- with explicit conditions on the group action and tight bounds --- is the natural next step." Does this mean the SBD as stated (Theorem S49) is not yet fully general? The three instances (binary transpositions, permutation groups, CPDAG automorphisms) are suggestive but do not constitute a proof of generality.

6. **The 68% prevalence figure.** You report 68% of 77 datasets show instability. What is the threshold for "instability"? Is this a binary call (any within-group flip > 0?) or a quantitative threshold? The Wilson CI is stated but the decision rule is not.

7. **Why absolute SHAP values?** DASH averages $|\varphi_j(f_i)|$ (Definition in supplement line 27 of the part 2 file). Why absolute values rather than signed values? For signed SHAP, the group average would be zero for symmetric features (by the exact symmetry argument), which is not useful. Is this the reason, and if so, is it discussed?

### Missing References or Comparisons

- **Marx et al. (2023), "But Are Explanations Faithful?"** --- directly relevant to the faithfulness axis.
- **Watson et al. (2024)** on explanation multiplicity under Rashomon sets --- the closest existing work to the Design Space characterization.
- **Hase et al. (2021), "Out-of-Distribution Explanation"** --- related to stability under distribution shift (different axis but relevant).
- **Conmy et al. (2023), "Towards Automated Circuit Discovery"** --- the primary automated circuit discovery method; relevant baseline for component-level claims.
- **The connection to Breiman's original "two cultures" (2001)** is cited but the specific model-class-agnostic nature of the impossibility could be connected to Breiman's point about the multiplicity of good models more explicitly.

### Detailed Comments (by section)

**Section 2 (Setup and Impossibility).** The proof of Theorem 1 is five lines and trivially correct. This is appropriate --- the power is in the abstraction, not the proof complexity. The instantiation paragraphs (input-level, component-level) are well-chosen. The one-sentence Design Space Theorem statement in the main text is too compressed; the $(S, U, C)$ triple notation is introduced without enough context for a reader encountering it for the first time.

**Section 3 (Bilemma and Diagnostics).** The bilemma proof could be slightly expanded --- "binary $H$ has no neutral element: every value contradicts the other" is correct but terse. The minority fraction diagnostic is excellent. Table 1 (comparison with Gaussian formula) would benefit from a third dataset that is not synthetic.

**Section 4 (Resolution).** The unified orbit-averaging framing (Reynolds operator on different groups) is elegant. The DASH workflow (Screen $\to$ Minority fraction $\to$ Z-test $\to$ DASH consensus) is practical and well-staged. The claim that $V^G$ "extends beyond simple layer averaging" for richer symmetry groups is intriguing but not demonstrated --- this is an open direction, not a result.

**Section 5 (Experiments).** The ranking lottery (Table 2) is the paper's most memorable result. The TinyStories validation (Table 3) is thorough: 14/14 predictions confirmed, with the GPT-2 boundary condition providing falsifiability. The clinical decision reversal (Table 4: 45% of applicants) is the strongest applied motivation. The method robustness paragraph (mean ablation vs. weight zeroing) is important and well-placed.

**Section 6 (Related Work).** Comprehensive and fair. The positioning against Bilodeau et al. (2024) is precise. The connection to Chouldechova (2017) and Kleinberg et al. (2017) fairness trilemmas is apt.

**Section 7 (Discussion).** The EU AI Act argument is provocative and well-grounded. The open problems (scaling to frontier models, non-architectural symmetries) are genuine.

### Score: 7

Strong paper with a clean theoretical contribution, unusually thorough validation, and genuine practical value. The core impossibility is simple (which is a virtue), and the Design Space Theorem provides real structural insight beyond a bare impossibility. The two-level (input + component) unification is novel and well-executed. The main weaknesses are rhetorical overstatement of the Design Space exhaustiveness scope, loose application of Hunt-Stein, and the undefined "collapsed tightness" concept. None of these are fatal; all are fixable in revision. The Lean formalization is a genuine contribution to the field's standards of rigor.

### Confidence: 4

I am confident in my assessment of the theoretical claims, the Lean formalization methodology, and the connection to invariant decision theory. I am less confident in evaluating the TinyStories experimental details (I have not reproduced them) and the EU AI Act legal analysis.

### Best Paper Recommendation: No

The paper is strong and should be accepted, but the core impossibility is too simple (in the sense of proof complexity) for a best paper award. The Design Space Theorem and the two-level unification are the deepest contributions; if the SBD were fully general (not just three instances), or if the Hunt-Stein application were made rigorous, the case would be stronger. The empirical work is excellent but not methodologically novel. A strong accept, not a best paper.

---

## R5_Fairness_Neutral

Now I have a thorough understanding of the paper. Here is my structured review.

---

## Reviewer 5: ML Fairness, Algorithmic Accountability, and Regulation

### Summary (2-3 sentences)

The paper proves that no attribution ranking can simultaneously be faithful, stable, and complete when the Rashomon property holds, and extends this impossibility to binary attribution questions (the "bilemma") and to component-level circuit attribution. It provides empirical validation on credit scoring, public benchmark datasets, and TinyStories transformers, then proposes orbit averaging (DASH) as a Pareto-optimal resolution. The paper makes explicit claims about regulatory implications for fairness auditing under the EU AI Act and ECOA.

### Strengths

1. **The fairness audit impossibility theorem (Supplement Theorem S-fairness) is genuinely novel and important.** The observation that a SHAP-based proxy audit on collinear features has coin-flip reliability is a real contribution to the algorithmic accountability literature. This deserves more prominence, not less.

2. **The paper correctly identifies the structural analogy to Chouldechova (2017) and Kleinberg et al. (2017)** and positions itself as the explainability analogue. The observation that the bilemma has "collapsed tightness" (no relaxation axis available, unlike the fairness trilemma where base rates provide a degree of freedom) is a sharp and well-articulated distinction.

3. **The scope conditions are well-stated.** The fairness audit impossibility explicitly limits itself to cases where conditions (F1)-(F2) hold, and the supplement notes that when the protected feature has unique predictive power, a single-model audit correctly identifies proxy reliance. This is responsible scoping.

4. **The DASH resolution is constructive and practical.** Unlike many impossibility results that stop at the negative conclusion, the paper provides a concrete, implementable remedy (ensemble auditing) with explicit ensemble size formulas. The workflow (Screen -> Z-test -> DASH) is actionable.

5. **The Lean formalization of the fairness audit impossibility** (FairnessAudit.lean) adds credibility. The intersectional compounding result ((1/2)^K) is also formalized.

6. **The "regulatory response for ties" paragraph in the supplement** (line 2577) is exactly the right framing: it anticipates how a practitioner would explain ties to a regulator, which is rare in theoretical papers.

### Weaknesses

1. **MAJOR: The "clinical decision reversal" framing is misleading.** The 45% number comes from German Credit, which is a credit scoring dataset. "Clinical" means medical in standard usage. The paper uses "clinical" to mean something like "consequential" or "decision-relevant," but this is non-standard and potentially confusing. Table 3 is titled "Clinical decision reversal on German Credit" -- this is a category error. The word "clinical" appears in Contribution 4 of the Introduction (line 78) without qualification. This framing risks overstating the stakes by importing medical connotations into a financial context. **Fix: replace "clinical" with "consequential" or "decision" throughout.**

2. **MAJOR: The 1/2 coin-flip claim for fairness audits is precise but narrowly scoped, and the paper does not adequately address aggregation.** The 1/2 result holds for a single feature pair (j,k) where conditions (F1)-(F2) are met. In practice, fairness auditors do not examine a single pair in isolation -- they look at aggregate SHAP importance profiles, partial dependence plots, and multiple features simultaneously. An auditor observing that zip code, neighborhood, and school district are ALL highly ranked (three proxies for race) would not be fooled by one pair flipping. The paper acknowledges scope (supplement line 4143) but the main text (line 357) presents the 1/2 without this caveat. The intersectional compounding to (1/2)^K actually argues the opposite direction from what the authors intend: if K proxies are independently coin-flipping, it is extremely unlikely that ALL of them simultaneously appear important, which would itself be a diagnostic signal. The argument needs more care about what "audit flags proxy" means in practice.

3. **MAJOR: The EU AI Act citation is a legal claim presented as legal analysis, without legal expertise.** Line 357 states the theorem "constitutes a 'known and foreseeable circumstance' under EU AI Act Art. 13(3)(b)(ii)." The supplement (line 4134-4136) hedges slightly with "We argue" and "in our reading," which is better but still problematic. Art. 13(3)(b)(ii) concerns transparency obligations for high-risk AI systems, and whether attribution instability qualifies as a "circumstance which may lead to risks to health, safety or fundamental rights" is a legal determination, not a mathematical one. The paper should either (a) cite legal scholarship supporting this interpretation, (b) explicitly note this is a technical observation that legal scholars should evaluate, or (c) remove the specific article citation and state the point in more general terms. As written, it is a legal conclusion by non-lawyers presented with the authority of a mathematical proof.

4. **MINOR: German Credit is a problematic dataset.** It is from 1994, has known issues with feature encoding, and is not representative of modern credit scoring. Using it does not fatally weaken the paper -- the result is demonstrated on other datasets too (Taiwan Credit, synthetic credit, 77 benchmark datasets) -- but leading with German Credit as the canonical example invites criticism. The paper would be stronger leading with the Taiwan Credit dataset (30,000 samples, genuine high collinearity at rho=0.95) or the synthetic credit data. The ethics checklist (line 382) notes "German Credit dataset is publicly available" but does not engage with the well-documented criticisms of using this dataset for fairness research.

5. **MINOR: The ECOA reference (supplement line 2609) is unsupported.** ECOA adverse action notices require stating the "principal reasons" for denial. The paper implies DASH provides a more defensible basis for these reasons, but does not cite the relevant regulation (Regulation B, 12 CFR 1002.9) or any legal commentary on what "principal reasons" means in the context of ensemble models. This is another instance of the paper making regulatory claims without adequate legal grounding.

6. **MINOR: Does DASH actually help fairness, or does it mask the problem?** The paper demonstrates that DASH stabilizes attributions. But for fairness purposes, the question is not whether the ranking is stable but whether the model actually relies on the protected proxy. If the true causal effect of zip code on the prediction is positive, averaging over 25 models does not change that causal fact -- it only changes whether the SHAP ranking reports it. DASH could stabilize the ranking in a way that hides genuine proxy reliance (by averaging it with noise from collinear features). The paper does not address this tension. The supplement's "Scope" paragraph (line 4143) partially addresses when the impossibility applies, but does not address whether DASH-resolved attributions are causally meaningful.

### Questions for Authors

1. Can you replace "clinical decision reversal" with "consequential decision reversal" or "explanation reversal"? The current framing is misleading for a credit scoring application.

2. The (1/2)^K intersectional compounding: does this assume the K proxy pairs are mutually independent in their attribution instability? In practice, proxies for the same protected attribute (zip code, neighborhood, school district) are themselves highly correlated, so their instabilities would be correlated too. Does the result survive this dependence?

3. Have you consulted with legal scholars on the EU AI Act interpretation? If not, would you be willing to reframe as "we conjecture that this may constitute..." rather than "we argue that..."?

4. For the fairness audit impossibility: what happens when the auditor uses conditional SHAP (conditioning on other features) rather than marginal SHAP? The paper has ConditionalImpossibility.lean -- does the fairness audit result extend to conditional SHAP, or does conditioning break the symmetry?

5. The DASH resolution stabilizes rankings, but does it preserve the causal interpretation of attributions? If the true causal graph has zip code -> default but not income -> default, does DASH correctly report this, or does averaging wash out the asymmetry?

### Missing References or Comparisons

- **Barocas & Selbst (2016), "Big Data's Disparate Impact"**: foundational reference on proxy discrimination that should be cited in the fairness audit section.
- **Raji et al. (2020), "Closing the AI Accountability Gap"**: directly relevant to the auditing claims.
- **Selbst & Barocas (2018), "The Intuitive Appeal of Explainable Machines"**: addresses the gap between technical explanations and legal requirements.
- **Regulation B (12 CFR 1002.9)**: if citing ECOA, cite the implementing regulation.
- **Slack et al. (2020), "Fooling LIME and SHAP"**: related work on SHAP reliability for fairness.
- **Chen et al. (2023)** or similar on the known problems with German Credit as a benchmark.
- **Hooker et al. (2021)** on issues with feature importance methods in the presence of correlation.

### Detailed Comments

**On the 1/2 coin-flip claim (Killer Question 1):** The 1/2 is mathematically precise for the specific scenario: a single pair (j,k) satisfying (F1)-(F2), evaluated by comparing phi_j to phi_k. The result is correct but the framing in the main text (line 357) is too strong. "Single-model SHAP audits for proxy discrimination conclude 'proxy reliance' with probability exactly 1/2 for collinear features" -- this is true for the pairwise ranking, but an audit is more than a pairwise ranking. A sophisticated auditor would examine (a) multiple feature pairs, (b) SHAP dependence plots, (c) partial dependence, (d) counterfactual analysis. The paper's result is an important warning about one specific audit methodology (rank-based SHAP importance), not a blanket indictment of all SHAP-based auditing. The main text should qualify this.

**On the EU AI Act (Killer Question 2):** The citation of Art. 13(3)(b)(ii) is the right general area, but the paper is making a legal interpretive claim. "Known and foreseeable circumstance" has not been interpreted by courts or regulatory guidance in the context of attribution instability. The supplement hedges with "We argue" and "in our reading," which is acceptable academic practice but should also appear in the main text. As written, the main text reads as a definitive legal conclusion.

**On German Credit (Killer Question 3):** Using German Credit weakens the paper slightly in the fairness community, where this dataset has been criticized. However, the paper uses it as one of several datasets, and the primary empirical contribution is the ranking lottery across 77 datasets. The German Credit result is illustrative, not load-bearing. Recommendation: keep it but add a sentence acknowledging its limitations and emphasizing that the result replicates on Taiwan Credit (which it does, per supplement).

**On "clinical" (Killer Question 4):** "Clinical" is the wrong word. Full stop. This is a credit scoring application. The paper should use "consequential" or "actionable." The current framing risks appearing to inflate the stakes by importing medical gravity into a financial context.

**On DASH and fairness (Killer Question 5):** This is the deepest concern. DASH stabilizes the attribution ranking, but stabilization is not the same as causal correctness. If zip code and income are collinear (rho=0.7) and both contribute to the prediction, DASH will report them as tied. This is mathematically honest (the data cannot distinguish their contributions), but it does not answer the regulatory question ("does the model rely on a protected proxy?"). The paper should acknowledge that DASH answers the attribution question, not the causal question, and that resolving the causal question requires causal modeling (e.g., counterfactual fairness a la Kusner et al. 2017), not just ensemble averaging.

**Would the regulatory claims survive scrutiny from a law review or policy journal?** Partially. The mathematical result (coin-flip reliability of pairwise SHAP audits) is solid and would be accepted. The specific EU AI Act citation would be flagged as legally unsupported -- a law review would require engagement with the regulatory text, legislative history, and relevant guidance documents. The ECOA reference would need citation to Regulation B and engagement with the "principal reasons" case law. The paper is strongest when it identifies the mathematical problem and weakest when it ventures into specific legal interpretations.

### Score: 6/10

The core theoretical contribution is strong and the fairness audit impossibility is genuinely novel. However, the "clinical" misnomer, the unqualified regulatory claims, and the lack of engagement with whether DASH resolves the causal question (versus just the attribution question) prevent a higher score. These are fixable issues.

### Confidence: 4/5

I am confident in the fairness/regulatory assessment. I defer to other reviewers on the Lean formalization and the component-level circuit analysis, which are outside my primary expertise.

### Best Paper Recommendation: No

The paper has best-paper-level ambition and scope, but the regulatory/fairness framing needs tightening before it reaches that level. The core impossibility theorem and the two-level (input + circuit) unification are impressive; the policy claims need more disciplined scoping.

---

## R9_AISafety_CrossDomain

I have now read the full paper. Let me produce the structured review.

---

## Reviewer 9: AI Safety / Interpretability Cross-Domain Review

### Summary (2-3 sentences)

The paper proves that no attribution ranking (input-level or component-level) can simultaneously be faithful, stable, and complete when the Rashomon property holds, and formalizes this in Lean 4. It extends the impossibility to circuit-level interpretability, showing that activation patching importance is unstable across independently trained networks (Spearman 0.54), and proposes orbit averaging (the G-invariant projection) as the resolution, lifting agreement to 0.98. This is a clean, general impossibility result with direct implications for interpretability-based safety cases.

### Strengths

1. **Genuine cross-level unification.** The same theorem covers SHAP, activation patching, and in principle any attribution system. The Reynolds operator framing (orbit averaging over different symmetry groups at different granularities) is elegant and makes the connection between DASH and V^G mathematically precise rather than merely analogical.

2. **Strong empirical design for the component-level experiments.** 7 pre-registered predictions per scale, all confirmed, with two architectural scales and a GPT-2 boundary condition. The boundary condition (fine-tuning destroys Rashomon diversity, instability vanishes) is exactly the kind of falsification test that makes the theory credible. This is better experimental methodology than most interpretability papers.

3. **The bilemma is the most safety-relevant result.** For binary questions — "is this head part of the circuit?" — faithful + stable is impossible without completeness. This is strictly stronger than the trilemma and directly attacks the foundation of circuit-based safety cases that classify components as in/out of a circuit.

4. **Cohen's d of 5.4-11.9 quantifies what was previously anecdotal.** Chughtai et al. (2023) showed networks learn different representations; this paper proves the instability is mathematically inevitable and gives effect sizes. The split-half reliability being high (0.991) while between-model agreement is low (0.565) is a particularly clean demonstration that the instability is structural, not measurement noise.

5. **Machine verification catches real errors.** The claim that the formalization caught 2 logical inconsistencies and 1 type mismatch that survived informal review is meaningful. The axiom stratification (core impossibility: 0 axioms) makes the theorem's strength transparent.

6. **The random projection control is convincing.** V^G ranks at the 100th percentile vs. random projections to the same dimensionality — this rules out the objection that "any dimensionality reduction would help."

### Weaknesses

1. **MAJOR: The symmetry group S_k^L is too coarse for safety-relevant circuits.** The paper's G-invariant projection treats all heads within a layer as interchangeable. But the circuits that matter for safety (induction heads, IOI circuit, name mover heads) are defined by cross-layer composition: head 9.1 composes with head 10.0 in specific ways. V^G collapses all heads within a layer to a single importance score, destroying precisely the cross-layer compositional structure that mechanistic interpretability aims to find. The paper acknowledges this obliquely ("extending to non-architectural symmetries" in Open Problems) but does not adequately address whether V^G is useful for the safety use cases it claims to affect. The resolution may solve the impossibility while destroying the information safety researchers actually need.

2. **MAJOR: The impossibility targets the wrong threat model for safety.** Safety cases based on interpretability do not typically require finding THE unique circuit. They require finding ANY circuit that verifies a property — e.g., "there exists no deception circuit" or "the model's behavior on this input is explained by these components." The impossibility shows that different training runs produce different circuit importance rankings, but if all equivalent models contain a functionally equivalent circuit (just with permuted heads), the safety guarantee transfers. The paper does not distinguish between "which specific head implements function F" (unstable, but irrelevant to safety) and "does function F exist in the model" (potentially stable, and what safety cares about). This is a fundamental gap in the safety argument.

3. **MAJOR: SAE features are not addressed.** Sparse autoencoder features (Bricken et al. 2023, Templeton et al. 2024) decompose activations into interpretable directions that are not tied to the architectural symmetry group S_k^L. SAE features are learned, not architectural, and the decomposition is into monosemantic features, not into heads/MLPs. The impossibility theorem applies to any attribution system, but the specific Rashomon property for SAE features is unclear: do independently trained SAEs on the same model produce the same features? (Empirically, largely yes — see Bricken et al.'s reproducibility analysis.) If SAE-based attribution escapes the Rashomon property because the decomposition is post-hoc on a fixed model, this is a significant escape hatch that the paper should acknowledge.

4. **MINOR: TinyStories is not a safety-relevant domain.** The component-level experiments use a benign text generation task where "which head matters" is not safety-critical. Safety-relevant behaviors (deception, power-seeking, sycophancy) may have circuits with very different structure — potentially more specialized and less symmetric. The paper's generalization from TinyStories to safety claims is a significant inferential leap. The GPT-2 experiment partially addresses scale but not behavioral complexity.

5. **MINOR: The EU AI Act regulatory argument (line 357) is too strong for this venue.** Claiming that explanation instability constitutes a "known and foreseeable circumstance" under Art. 13(3)(b)(ii) is a legal interpretation that requires legal analysis, not a mathematical consequence of the theorem. This overreach weakens the paper's credibility in the safety discussion.

6. **MINOR: The paper conflates "identifying the circuit" with "attributing importance to components."** Mechanistic interpretability's goal is to understand computation (what algorithm does the model implement), not to rank component importance. The impossibility applies to importance rankings, but the algorithms discovered by circuits work (composition, induction, backup behavior) may be stable across seeds even if the importance ordering of the components implementing them is not. This distinction is not made.

### Questions for Authors

1. Does the impossibility apply when the safety question is existential ("does a deception circuit exist?") rather than comparative ("which component is most important")? The theorem requires a ranking — does it say anything about detection?

2. If I train 10 networks and find that all 10 contain an induction head (just in different positions within the layer), doesn't this STRENGTHEN rather than weaken the safety case? The function is robust to training randomness. How do you reconcile this with your claim that "interpretability-based safety cases are subject to the same impossibility"?

3. SAE features decompose a fixed model's activations into interpretable directions. Since the model is fixed, there is no Rashomon set over models. Does the impossibility apply to SAE-based circuit analysis? If not, does this make SAEs the preferred tool for safety cases?

4. The V^G projection maps all heads within a layer to the same importance score. Can you identify cross-layer circuits (e.g., head A in layer 3 composes with head B in layer 7) after applying V^G? If not, what does V^G actually tell a safety researcher?

5. Cohen's d of 5.4-11.9: is this evidence that single-network circuit analysis is unreliable (bad for safety) or that instability is easy to detect (good for safety diagnostics)? Both readings seem valid.

6. The GPT-2 fine-tuning result shows Rashomon diversity vanishes. Most frontier models are fine-tuned (RLHF, instruction tuning). Does this mean the impossibility is less relevant for deployed safety-critical models?

7. Have you measured whether the FUNCTION computed by the "most important head" is stable across seeds, even if which head computes it is not? This is the key question for safety.

### Missing References or Comparisons

- **Bricken et al. (2023), "Towards Monosemanticity"** — SAE decomposition as a potential escape from architectural symmetry. This is a glaring omission given the safety framing.
- **Templeton et al. (2024), "Scaling Monosemanticity"** — scaling SAEs to Claude, demonstrating safety-relevant features.
- **Conmy et al. (2023), "Towards Automated Circuit Discovery"** — ACDC framework; relevant to whether automated circuit discovery is subject to the impossibility.
- **Marks et al. (2024), "Sparse Feature Circuits"** — circuits defined over SAE features, not architectural components. Directly relevant to the escape hatch question.
- **Geiger et al. (2024), "Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations"** — causal abstraction as an alternative to importance ranking; may escape the impossibility entirely.
- **Casper et al. (2023), "Open Problems and Fundamental Limitations of RLHF"** — discusses limitations of interpretability for safety; natural companion.
- **ARC's work on formal verification** (Christiano 2022) — the paper claims implications for formal verification of AI systems but does not engage with the actual formal verification literature.

### Detailed Comments

**Discussion broader implications (lines 356-358).** The claim that "interpretability-based safety cases that depend on identifying 'the circuit' for a behavior are subject to the same impossibility" is the paper's most consequential statement and also its weakest. The impossibility proves that importance RANKINGS are unstable. But safety cases built on circuits (e.g., Olah et al.'s "Zoom In" agenda) do not depend on rankings — they depend on understanding the ALGORITHM implemented by a circuit. The algorithm {induction head in position 2,3 composes with output head in position 5,1} may be stable across seeds even if the importance ordering of heads within layer 2 is not. The paper needs to clearly distinguish between:
- (a) "Which component is most important?" (subject to the impossibility)
- (b) "What algorithm does the model implement?" (potentially not subject to the impossibility)
- (c) "Does a dangerous capability exist?" (existential, not comparative)

The paper proves (a) is impossible but claims implications for (b) and (c) without proof. This is the central gap from a safety perspective.

**Component-level experiments (Section 4.2).** The experiments are well-designed but answer the wrong question for safety. They show that activation patching importance rankings are unstable — this is expected and confirmed by the theory. What a safety researcher wants to know is: do the 10 TinyStories networks implement the same algorithm? If you trace a specific computation (e.g., "predict the next word given the subject") through the network, is the circuit functionally equivalent across seeds even if the head indices differ? The paper does not investigate functional equivalence, only importance ranking equivalence. Adding even a preliminary analysis of functional stability (e.g., do the same attention patterns emerge across seeds, just in different head positions?) would substantially strengthen the safety argument.

**V^G as resolution.** V^G is mathematically elegant but operationally limited for safety. It tells you "layer 2 is more important than layer 3" but not "head 2.1 implements induction and composes with head 5.3." For safety cases that require understanding specific mechanisms, V^G provides the wrong level of granularity. The paper should be explicit that V^G resolves the impossibility by coarsening the question, and that this coarsening may be acceptable for some safety applications (e.g., "is layer 5 safety-relevant?") but not others (e.g., "does this model contain a deception circuit?").

That said, the paper's insight that the instability is concentrated WITHIN orbits while BETWEEN-orbit structure is stable is genuinely useful for safety. It tells safety researchers: trust comparisons between layers and between heads-vs-MLPs; do not trust comparisons between heads within the same layer. This is actionable guidance even if V^G itself is too coarse.

**The bilemma's implications for safety.** The bilemma (Theorem 3) is under-discussed relative to its importance for safety. Binary circuit membership ("is this head part of the safety-relevant circuit?") is subject to the bilemma: faithful + stable is impossible. This means any method that classifies components as "in the circuit" or "not in the circuit" will either be unfaithful or unstable. This is a genuine problem for safety cases that depend on enumerating circuit components. The paper should develop this implication more fully.

### Score: 6

The core theoretical contribution (the impossibility at arbitrary granularity) is clean and well-verified. The input-level experiments are strong. The component-level experiments are well-designed but answer the wrong question for the safety implications claimed. The safety argument has a fundamental gap: it conflates importance ranking instability with algorithmic identification instability. The omission of SAE-based interpretability as a potential escape hatch is a significant weakness given the safety framing. The paper would benefit from either (a) strengthening the safety argument by showing that functional equivalence is also unstable, or (b) weakening the safety claims to what the theorem actually proves.

### Confidence: 4

I am familiar with the mechanistic interpretability literature, the formal verification agenda, and SAE-based safety research. I am less confident in evaluating the Lean formalization and the input-level SHAP experiments, which are outside my primary expertise. My assessment of the safety implications is based on detailed knowledge of how interpretability is actually used in safety cases.

### Best Paper Recommendation: No

The paper is strong but the safety argument does not clear the bar for best paper. A best paper in this space would need to either prove that algorithmic identification (not just importance ranking) is subject to the impossibility, or demonstrate the impossibility on safety-relevant behaviors in frontier-scale models. The current paper proves a clean theorem and validates it on importance rankings in small models — significant but not transformative for the safety field.

---

**Bottom line for AI safety researchers:** This paper should make you more careful about circuit importance rankings from single training runs, but it should NOT make you abandon interpretability-based safety cases. The impossibility applies to "which component is most important" — a question that was always fragile. It does not (yet) apply to "what algorithm does the model implement" or "does a dangerous capability exist." The actionable takeaway is: trust between-layer and head-vs-MLP comparisons; do not trust within-layer head rankings from a single network. If you are building safety cases on SAE features rather than architectural components, the relevance of this impossibility to your work remains an open question that the paper does not address.

---

## R3_FormalMethods_Neutral

---

## Summary

This paper proves that no attribution ranking can simultaneously be faithful, stable, and complete when the Rashomon property holds, and extends this to a bilemma (faithful + stable is impossible for binary questions). The core result is formalized in Lean 4 (357 theorems, 6 axioms, 0 sorry) and validated empirically at both input-level (SHAP on GBDTs) and component-level (activation patching on transformers). The formalization is structurally clean, with the core impossibility genuinely depending on zero domain-specific axioms when stated in the abstract `ExplanationSystem` framework, though the domain-specific version in `Trilemma.lean` references the `Model` axiom in its type signature.

## Strengths

1. **The core impossibility is genuinely trivial in the best sense.** The proof of `explanation_impossibility` in `ExplanationSystem.lean` is 4 tactic lines: substitute stability, get contradictory incompatibility, apply irreflexivity. This is the hallmark of a clean formalization -- the theorem statement does the work, the proof is mechanical. The Arrow analogy is apt and well-executed.

2. **Honest axiom stratification.** The paper carefully separates what depends on what: core impossibility (0 domain axioms), GBDT instance (3-4), DASH resolution (6). The `GBDTSetup` structure in `Setup.lean` bundles all axioms into a single parametric structure, demonstrating that the global axioms are a convenience, not a necessity. This is good formalization practice.

3. **Two levels of formalization of the same theorem.** The abstract `ExplanationSystem` version is fully parametric (zero axioms of any kind beyond Lean's kernel). The concrete `attribution_impossibility` in `Trilemma.lean` instantiates it for feature attribution. Both versions are present and their relationship is clear. This addresses the formalization gap concern directly.

4. **The bilemma is a genuine strengthening.** The proof that for binary H, faithful + stable alone is impossible (no completeness needed) is clean and follows from the observation that binary types have no neutral element. The `MechInterp.lean` instantiation using constructive inductive types (`MechInterpCfg`, `CircuitDecomp`) with `decide`-closed proofs is a good demonstration.

5. **Practical impact is substantial.** The 24 distinct top-3 rankings across 50 seeds on Breast Cancer, 45% clinical decision reversal on German Credit, and the component-level TinyStories validation are compelling. The 7-line nonparametric diagnostic is a genuine contribution to practitioners.

6. **The component-level extension is original.** Applying the same impossibility to mechanistic interpretability (circuit attribution) and showing the same resolution (orbit averaging / $G$-invariant projection) is a natural but non-obvious extension. The GPT-2 boundary condition (fine-tuning eliminates Rashomon diversity, eliminating instability) is a good falsification test.

7. **Clean Lean hygiene.** `autoImplicit false` throughout, zero `sorry`, all axioms documented with justification. The axiom reduction history (16 -> 10 -> 7 -> 6) in `Defs.lean` is transparent.

## Weaknesses

1. **MAJOR: The "zero axiom dependencies" claim is misleading as stated in the paper.** The theorem `attribution_impossibility` in `Trilemma.lean` uses `Model` (axiom) and `attribution` (which depends on `proportionalityConstant`, an axiom) in its *statement*. Lean's `#print axioms attribution_impossibility` will list these. What the authors mean is that the *abstract* version `explanation_impossibility` in `ExplanationSystem.lean` has zero domain axioms. The paper conflates these two levels. Line 103 of the paper says "Lean: `attribution_impossibility`, zero axioms" -- this is the concrete version, not the abstract one. Recommendation: cite `explanation_impossibility` as the zero-axiom version, and note that `attribution_impossibility` depends on `Model` (type declaration axiom) but no behavioral axioms.

2. **MAJOR: The faithfulness definition in `attribution_impossibility` is a biconditional, not the paper's Definition 1.** The Lean statement has `ranking j k <-> attribution fs j f > attribution fs k f`, meaning the ranking holds *if and only if* the attribution is higher. But Definition 1 in the paper says faithfulness is the *implication*: $j \succ k$ *whenever* $\varphi_j > \varphi_k$. The biconditional is strictly stronger -- it also requires $j \succ k \Rightarrow \varphi_j > \varphi_k$, which means the ranking must *exactly* reflect every model's ordering. The `attribution_impossibility_weak` version fixes this with implication-only faithfulness but requires antisymmetry as an additional hypothesis. The paper does not discuss this discrepancy. This is a formalization gap: the main theorem proved in Lean is slightly different from what the paper states informally.

3. **MAJOR: The theorem count is inflated.** 169 of 357 theorems/lemmas (47%) have fewer than 3 tactic lines or are term-mode proofs. Many are definitional unwrapping (e.g., `splitCount_firstMover` is just `unfold splitCount; simp [hfm]`). The paper says "139 require multi-line proofs of >= 5 tactic lines," which means 218 are under 5 lines. Reporting "357 theorems" without qualification gives a misleading impression of proof depth. The honest metric is something like "~140 non-trivial theorems" or "357 lemmas and theorems, of which ~140 require multi-step reasoning."

4. **MINOR: `crossGroupBaselineCore` is suspicious as an axiom.** It declares a function `Fin fs.L -> Fin fs.L -> R` with no constraints whatsoever. It could return anything -- negative numbers, infinity (well, not literally, but arbitrary reals). It is used in the `splitCount` definition for cross-group features but has no axiomatized properties. This means theorems about cross-group behavior are essentially vacuous unless something constrains this function. The axiom is consistent (any constant function satisfies it), so it cannot introduce inconsistency, but it does mean some theorems about cross-group stability are trivially true by construction rather than meaningfully proved.

5. **MINOR: `proportionalityConstant` as axiom is an unusual choice.** Declaring `{c : R // 0 < c}` as an axiom means there exists a fixed but arbitrary positive real. This is consistent (take `c = 1`), but it introduces a global constant that all models share. If different models could have different proportionality constants, the impossibility would need to be restated. The paper's Assumption 7 (uniform-contribution model) justifies this, but the axiom bakes in a modeling assumption that might not hold for all GBDT implementations.

6. **MINOR: No comparison with other formalization efforts in XAI.** The claim "first formally verified impossibility in XAI" is stated without evidence of a literature search. This is hard to verify or falsify. The comparison with Nipkow's Arrow formalization and Zhang's statistical learning formalization is appropriate, but the absence of any XAI formalization is asserted rather than demonstrated.

7. **MINOR: The `Model : Type` axiom.** Declaring `Model` as an axiom rather than a type parameter means all theorems that mention `Model` are about a single fixed type. The `GBDTSetup` structure fixes this by making `ModelType` a parameter, but most theorems in the codebase use the global `Model` axiom. This is a style issue, not a correctness issue, but it means the formalization is less reusable than it could be.

## Questions for Authors

1. **The biconditional vs. implication gap.** The main theorem `attribution_impossibility` uses a biconditional faithfulness assumption (`ranking j k <-> ...`). This is strictly stronger than Definition 1 in the paper. Why not present `attribution_impossibility_weak` as the main result, since it matches the paper's definition? The biconditional version essentially assumes the ranking is *determined by* each model's attributions, which is a much stronger assumption than "faithfully reflects."

2. **What does `#print axioms attribution_impossibility` actually output?** The paper claims zero axioms, but the theorem references `Model` and `attribution` (which depends on `proportionalityConstant`). Can you provide the actual output? If it lists `Model` and `proportionalityConstant`, the "zero axiom" claim needs qualification. The truly zero-axiom version is `explanation_impossibility`, which should be cited instead.

3. **Could `firstMover_surjective` be weakened?** The axiom says every feature in a group can be the first-mover in *some* model. This is a strong assumption -- it requires the model class to be rich enough. For very regularized models (e.g., with strong L1 penalties), some features might never be selected as first-mover. How sensitive is the impossibility to this axiom? (The qualitative version in `Qualitative.lean` takes it as a hypothesis, which is cleaner.)

4. **The 6 axioms are all in `Defs.lean`.** Is the system consistent? Specifically, can you construct a model (in the Lean sense -- an inhabitant of `Model` with `firstMover`, `crossGroupBaselineCore`, etc.) that satisfies all 6 axioms simultaneously? The `GBDTSetup` structure suggests yes, but has this been checked with a concrete instantiation?

5. **Why formalize in Lean 4 rather than Isabelle/HOL?** Nipkow's Arrow formalization is in Isabelle. Was there a principled reason for Lean 4, or was it author preference? The Mathlib dependency (for variance, measure theory) is a practical advantage, but the paper doesn't discuss this choice.

6. **The "357 theorems" metric.** How many of these are backward-compatibility wrappers (e.g., `attribution_proportional` wrapping `proportionality_global`)? How many are "the same theorem restated for a different interface" (e.g., `attribution_impossibility` vs. `attribution_impossibility_bundled` vs. `explanation_impossibility`)? A de-duplicated count would be more informative.

## Missing References or Comparisons

- **Wiedijk (2006), "The Seventeen Provers of the World"** -- for context on formalization methodology and what counts as "verified."
- **Affeldt et al. (2020), "Measure theory in Coq"** -- for comparison of measure-theoretic formalization approaches.
- **The Lean 4 Mathlib community standards** for axiom usage and formalization quality. The paper should note whether the formalization follows Mathlib conventions (it mostly does, except for the global axiom pattern).
- **Bilodeau et al. (2024)** is cited but the comparison is thin. Their impossibility is about *method* properties (completeness + linearity), while this paper's is about *cross-model* stability. The paper should explain why these are complementary rather than competing results.
- **Slack et al. (2020), "Fooling LIME and SHAP"** -- adversarial instability of explanations, a different axis of the same problem.

## Detailed Comments

### Axiom count and justification

The 6 axioms break down as:
- **2 type/function declarations** (`Model : Type`, `firstMover : Model -> Fin fs.P`): These are infrastructure. Declaring `Model` as an axiom rather than a parameter is a style choice that doesn't affect soundness.
- **1 behavioral axiom** (`firstMover_surjective`): The key substantive assumption. It says the model class is rich enough that any feature can dominate. This is reasonable for GBDT with random subsampling but not universal.
- **1 structural constant** (`crossGroupBaselineCore`): Unconstrained function. Its existence is trivially consistent. Its role is to define cross-group split counts, but without constraints, theorems about cross-group behavior are definitional truths.
- **1 proportionality constant** (`proportionalityConstant`): A positive real, bundled with its positivity proof. Consistent (take c=1). Used to define `attribution` from `splitCount`.
- **1 measure** (`modelMeasure`): For variance calculations. Consistent (take the zero measure, though this would make variance trivially zero).

The axiom set is consistent -- one can construct a trivial model satisfying everything. The `firstMover_surjective` axiom is the only one with real mathematical content. The system is honest about this.

### Proof depth

The core impossibility is shallow: 4 tactic lines for `explanation_impossibility`, 4 for `attribution_impossibility`. This is appropriate -- the theorem IS shallow. The depth comes from the quantitative bounds (ratio divergence, DASH convergence, Spearman bounds), which are in the Level 3-5 files. The design space theorem and the ensemble bound involve more complex reasoning.

The paper's claim of "139 multi-line proofs" is roughly consistent with my analysis (188 proofs with >= 3 tactic lines by my count, 169 with < 3). The discrepancy depends on counting methodology (5-line threshold vs. 3-line threshold).

### Does the Lean verification add real confidence?

**Yes, but not where the paper emphasizes.** The core impossibility is simple enough that a paper proof suffices -- no one would doubt it. The real value of the formalization is:

1. **Axiom discipline.** The formalization forces explicit declaration of every assumption. The reduction from 16 to 6 axioms (documented in `Defs.lean`) is a genuine contribution -- it reveals which assumptions are independent and which are derivable.

2. **The quantitative bounds.** Proofs like `ratio_tendsto_atTop` (that the attribution ratio diverges as rho -> 1) involve enough algebra that Lean verification adds confidence. The paper mentions the formalization "caught 2 logical inconsistencies and 1 type mismatch."

3. **The design space exhaustiveness.** The claim that exactly two families exist is the kind of combinatorial argument where formal verification genuinely helps.

4. **Instance correctness.** The bilemma instances (SHAP sign, feature status, circuit decomposition) are all closed by `decide` or constructive proofs. This confirms the abstract theorem applies to the concrete cases.

The formalization does NOT verify the empirical claims, the connection between the Lean axioms and real GBDT behavior, or the correctness of the experimental code. This is appropriate and the paper does not overclaim here.

### The formalization gap

There is a small but real formalization gap:

- **Definition mismatch.** The paper's Definition 1 (faithfulness as implication) does not match the main Lean theorem (faithfulness as biconditional). The `_weak` version fixes this but is not the version cited in the paper.
- **Stability encoding.** The paper says stability means the ranking "does not depend on theta." The Lean version in `Trilemma.lean` encodes this by quantifying faithfulness over ALL models f -- the ranking must be a biconditional with every model's attributions. This is actually a conjunction of faithfulness + stability + completeness, not just faithfulness. The abstract `ExplanationSystem` version separates these correctly.
- **The Rashomon property.** The Lean version quantifies over features in the same group. The paper states it for "interchangeable components." These match for the feature-attribution instance but the universality claim requires the abstract version.

## Score: 7/10

The paper presents a clean impossibility result with genuine practical implications, verified in Lean 4 with honest axiom accounting. The component-level extension to mechanistic interpretability is original and well-validated. The formalization is substantive, not ceremonial. However, the paper overclaims on the "zero axiom" characterization, inflates the theorem count, and has a formalization gap between the paper's definitions and the main Lean theorem. The core result, while true and useful, is mathematically simple -- the contribution is in the breadth of application (input-level + component-level), the quantitative bounds, the diagnostic, and the formalization discipline, not in the depth of the impossibility itself.

## Confidence: 4/5

I have read the Lean code directly, verified the axiom count, checked the proof structure, and identified specific formalization gaps. I am confident in the technical assessment. My uncertainty is about whether the component-level empirical validation (TinyStories) is as strong as claimed -- I have not examined the experimental code, and the 14/14 prediction pass rate on a system designed to confirm the theory could reflect post-hoc selection of predictions.

## Best Paper Recommendation: No

The result is solid and the paper is well-written, but the core impossibility is too simple to be a best paper. The value is in the packaging (impossibility + quantitative bounds + diagnostic + formalization + two-level application), which is excellent for a strong accept but not best-paper territory. A best paper would need either a deeper impossibility (one that is surprising or counterintuitive, not a direct consequence of Rashomon + trichotomy) or a more transformative practical impact.

---

## R7_SocialChoice_CrossDomain

Now I have a thorough understanding of the paper and the formalization. Here is my review.

---

## Summary (2-3 sentences)

The paper proves that no attribution ranking can simultaneously be faithful (reflecting model attributions), stable (model-independent), and complete (deciding all feature pairs) when the Rashomon property holds -- i.e., when equivalent models disagree on feature orderings. The authors extend this to a "bilemma" for binary attribution questions, characterize a two-family design space of achievable methods, and validate predictions at both input-level (SHAP) and component-level (circuit interpretability) attribution. The formalization in Lean 4 (357 theorems, 0 sorry) provides machine-verified guarantees and the paper positions orbit averaging (DASH) as the Pareto-optimal resolution.

## Strengths (numbered, specific)

1. **Correct structural analogy to Arrow.** The paper genuinely captures the same pattern: three desirable properties are jointly incompatible when a diversity condition holds. The Rashomon property plays the role of unrestricted domain, faithfulness maps to Pareto/unanimity, stability maps to IIA, and completeness is completeness. The resolution (relax completeness to partial orders / ties) mirrors the move from total orders to quasi-orders in social choice. This is not a superficial analogy.

2. **The bilemma is a genuine and novel contribution to impossibility theory.** The result that for binary hypothesis spaces, faithfulness + stability alone is impossible (without needing completeness) has no direct analogue I know of in social choice. It runs opposite to Gibbard-Satterthwaite, where binary alternatives make things easier (majority rule works). The observation that the absence of a neutral element collapses the three-property impossibility into a two-property one is structurally interesting and could transfer to other domains.

3. **The "collapsed tightness" concept is original.** In social choice, we discuss "tightness" of impossibility theorems (whether removing any axiom makes the rest satisfiable). The bilemma's collapsed tightness -- where a two-axiom subset is already unsatisfiable in certain domains -- is a useful taxonomic concept. I am not aware of a standard name for this in social choice, though there are analogues: e.g., for strict preferences with no indifference, certain weaker impossibilities become stronger. The paper names and formalizes this clearly.

4. **The Design Space Theorem has structural content.** It is not merely "faithful or ties." The exhaustiveness result (Lean: `family_a_or_family_b`) establishes that complete + faithful implies the existence of a witnessing model for unfaithfulness -- this is an existential quantifier with content. The characterization of Family B with convergence rates ($S = 1 - O(1/M)$) and the invocation of Hunt-Stein optimality gives it depth beyond a trivial dichotomy. The social choice analogue would be characterizing the set of achievable social welfare functions when IIA is relaxed; Sen's value restriction and Black's single-peakedness provide domain restrictions that restore possibility. Here, Family B (orbit averaging) is the domain restriction analogue: it restricts the ranking to orbits where Rashomon does not bite.

5. **Machine verification is valuable and sets a standard.** The Nipkow 2009 formalization of Arrow in Isabelle/HOL took approximately 2,000 lines for a much deeper proof. This formalization covers a broader territory (357 theorems across 58 files) for a shallower core theorem but with extensive quantitative extensions. The zero-axiom core impossibility is genuinely impressive -- it means the result follows from pure logic plus the Rashomon hypothesis.

6. **Two-level validation (input + component) is convincing.** The same theorem, validated at feature-level (SHAP) and circuit-level (activation patching), demonstrates genuine generality. The GPT-2 boundary condition (no Rashomon diversity => no instability) is a strong falsifiability test.

7. **Practical diagnostic.** The 7-line minority fraction predictor achieving Spearman 0.92-0.98 is a useful practical contribution independent of the theory.

## Weaknesses (numbered, with severity)

1. **MAJOR: The core proof is trivially shallow compared to Arrow.** The `attribution_impossibility` proof is 4 lines in LaTeX and 4 tactics in Lean. Arrow's theorem requires constructing a dictator through a sequence of pivotal voter arguments (the ultrafilter lemma, essentially). The comparison in the Lean header comment ("Analogue of Arrow's impossibility theorem") risks overselling. The proof structure is: assume Rashomon, instantiate to get two witnesses, apply faithfulness twice, derive contradiction by stability. This is a straightforward application of the pigeonhole principle / intermediate value theorem pattern. The paper should be more explicit that the analogy is *structural* (same incompatibility pattern) rather than *proof-theoretic* (the proofs have comparable depth). The depth of this work lies in the extensions (bilemma, design space, quantitative bounds), not in the core theorem.

2. **MAJOR: The Rashomon property is assumed, not derived from primitives.** In Arrow's theorem, unrestricted domain is a transparency condition -- it just says all preference profiles are admissible. The Rashomon property is a much stronger empirical condition (there exist models in the hypothesis class that reverse attributions). The paper claims it is "inevitable" for stochastic symmetric algorithms (supplement), but this inevitability result itself requires assumptions about the algorithm class. The analogy to unrestricted domain is imperfect: unrestricted domain is a meta-axiom about the input space, while Rashomon is an empirical property of the model class that may or may not hold. The paper acknowledges this ("the 68% prevalence figure... may not generalize") but the theoretical framing sometimes suggests universality that the empirical evidence doesn't fully support.

3. **MAJOR: The Design Space Theorem's "exactly two families" is less deep than claimed.** In social choice, when you relax IIA, you get a rich landscape: Borda count, Kemeny-Young, approval voting, etc. When this paper relaxes completeness, the only option presented is orbit averaging. But there are other partial-order constructions: e.g., rank features only when all models in a sample agree (unanimous partial order), or rank features when a supermajority agrees (qualified majority partial order). These would be Family B variants with different convergence properties. The paper treats Family B as monolithic ("orbit averaging") when it should acknowledge a richer sub-landscape. The claim of "exactly two" relies on a binary distinction (complete or not) rather than characterizing the space of partial orders.

4. **MINOR: The connection to mechanism design is unexplored.** The DASH resolution (average over an ensemble) is analogous to "average scoring rules" in mechanism design. The strategyproofness literature has deep results about when averaging resolves impossibilities (e.g., the VCG mechanism averages over bidder valuations). The paper could strengthen its cross-domain positioning by connecting to this literature.

5. **MINOR: The "zero axiom" framing is slightly misleading.** The core impossibility has zero *behavioral* axioms but relies on the `Model` and `attribution` type declarations, which are themselves axioms in Lean. The paper is careful about this distinction in the supplement but the main text's "zero axiom dependencies" phrasing could mislead readers unfamiliar with formal verification.

6. **MINOR: Limited engagement with the social choice formalization literature.** Beyond Nipkow 2009, there is Wiedijk 2007 (Arrow in Mizar), Grandi and Endriss 2013 (computational social choice formalizations), and recent Lean 4 formalizations of voting theory. The related work section mentions Nipkow but not the broader landscape.

## Questions for Authors (numbered)

1. The core impossibility follows from a very general pattern: if a binary relation must respect two contradictory constraints (faithfulness at theta vs. faithfulness at theta'), it cannot be total. This pattern appears in many contexts beyond attribution. Do you view the contribution as the *pattern* or the *instantiation*? If the pattern, what distinguishes it from the general observation that "you can't have a total order on a set with contradictory partial-order constraints"?

2. The bilemma shows F+S is impossible for binary H. For ternary H (e.g., positive/zero/negative), is F+S achievable? If so, what is the threshold |H| at which the bilemma ceases to apply? Is there a Gibbard-Satterthwaite-like characterization where |H| >= 3 restores possibility?

3. The Rashomon Inevitability Theorem (supplement) -- does it require the interchangeability to be exact, or does it hold for approximate interchangeability? If approximate, what is the quantitative relationship between the degree of interchangeability and the strength of the Rashomon property?

4. Could you formalize the Design Space Theorem's Family B sub-landscape? Specifically: for qualified majority partial orders (rank j > k only when fraction >= q of models agree), what is the achievable (stability, unfaithfulness, completeness) triple as a function of q? This would give the Design Space result the richness of social choice domain-restriction characterizations.

5. The Hunt-Stein optimality of DASH -- this requires a group-theoretic invariance structure. What is the precise group? Is it the symmetric group on models ($S_M$), or something richer? And does the Hunt-Stein result apply to the *ranking* problem or only to the *point estimation* problem for attribution values?

## Structural Comparison with Arrow's Theorem

The comparison is **structurally valid but proof-theoretically asymmetric**. Here is the precise mapping:

| Arrow's Theorem | Attribution Impossibility |
|----------------|--------------------------|
| Alternatives (>=3) | Features (>=2 interchangeable) |
| Voters | Models in Rashomon set |
| Social welfare function | Attribution ranking |
| Unrestricted domain | Rashomon property |
| Independence of Irrelevant Alternatives | Faithfulness (rank reflects attributions) |
| Pareto / Unanimity | (subsumed by faithfulness) |
| Non-dictatorship | Stability (no single model dictates) |
| Completeness | Completeness |
| Resolution: relax transitivity/completeness | Resolution: relax completeness (ties) |

The structural parallel is genuine. Both are trilemmas where three desirable properties of an aggregation (social welfare function / attribution ranking) are jointly incompatible when a diversity condition holds on the inputs (voter preferences / model attributions).

However, the comparison has important asymmetries:

1. **Proof depth.** Arrow's proof requires showing that any SWF satisfying IIA + Pareto must be dictatorial -- this involves constructing the dictator through a sequence of pivotal-voter arguments (or equivalently, showing that the decisive coalitions form an ultrafilter). The attribution impossibility is a direct 4-line contradiction. The structural depth of Arrow lies in the *construction*, not the *contradiction*. This paper's depth lies elsewhere: in the bilemma, the design space, and the quantitative bounds.

2. **The Rashomon property is stronger than unrestricted domain.** Unrestricted domain says "all profiles are possible." Rashomon says "there exist profiles that specifically reverse the ranking of specific pairs." Rashomon is an *existential* condition on the model class, not a *universal* condition on the input space. This makes the impossibility easier to prove but harder to verify empirically (you need to find the witnesses).

3. **The bilemma has no Arrow analogue.** For Arrow, reducing to 2 alternatives makes everything trivial (majority rule satisfies all axioms). For attribution, reducing to binary H makes the impossibility *stronger*. This is a genuine structural novelty.

4. **The design space is less rich than the social choice landscape.** Arrow spawned decades of characterization results (possibility domains, Arrovian vs. non-Arrovian aggregation rules, probabilistic social choice). The design space here is a binary dichotomy (complete+unfaithful vs. ties+stable). This is partly because the attribution setting has less combinatorial structure than voting (no transitivity requirement, no independence condition across pairs).

**Verdict on the Rashomon property as a social choice concept.** The Rashomon property is closest to a *diversity condition* in social choice -- specifically, it resembles the *free triple* condition used in proving Arrow's theorem (for any three alternatives, there exist voters ranking them in any order). The key difference is that Rashomon is pairwise (for each pair, there exist models reversing the order) while the free triple condition involves triples. The pairwise nature is why the proof is simpler.

## Score: 6/10

The paper makes a genuine contribution to impossibility theory: the bilemma, collapsed tightness, and the two-level validation are novel. The core impossibility, while correct and well-formalized, is straightforward. The paper's value is primarily in (a) identifying that this pattern governs attribution at all model levels, (b) the bilemma's structural novelty, (c) the empirical validation architecture, and (d) the Lean formalization as a standard-setting exercise. It falls short of a top paper because the core theorem lacks the depth of the impossibilities it compares itself to, and the design space characterization is coarser than the social choice analogues it invokes.

## Confidence: 4/5

I am very confident in my assessment of the structural relationship to Arrow's theorem and the social choice literature. I am slightly less confident in evaluating the empirical contribution (component-level validation) as it falls outside my core expertise.

## Best Paper Recommendation: No

The paper is solid and makes a real contribution, but the core theorem is not deep enough for best-paper consideration at a top venue. The bilemma and the two-level validation architecture are the strongest novel elements. If the Design Space Theorem were developed to the richness of social-choice domain-restriction results (characterizing the full sub-landscape of Family B), the case would be stronger.

---

## R10_GroupTheory_CrossDomain

I have now read the full paper. Let me formulate my review.

---

## Review: "The Attribution Impossibility: No Importance Ranking Is Faithful, Stable, and Complete Under Symmetry"

**Reviewer 10 — Representation theory / Invariant theory**

---

## Summary

The paper proves that no attribution ranking (at input or component level) can simultaneously be faithful, stable, and complete when a Rashomon property holds, and that for binary attribution questions the situation is strictly worse (the "bilemma"). It proposes orbit averaging ("DASH" for input features, G-invariant projection for circuits) as the resolution, frames this as the Reynolds operator on the relevant symmetry group, and validates predictions on tabular data and TinyStories transformers. The Lean 4 formalization is extensive (357 theorems, 0 sorry).

## Strengths

1. **The core impossibility is clean and general.** Theorem 1 requires zero model-specific axioms -- only the Rashomon property. The proof is four lines. This is the kind of result that, once stated, seems obvious in retrospect, which is a mark of a good theorem.

2. **The bilemma is a genuine strengthening.** Dropping completeness for binary H and still getting impossibility is a meaningful structural observation. The tightness classification (F+S achievable iff H has a neutral element) is a nice characterization.

3. **The two-level empirical program is well-executed.** The input-level experiments (24 distinct top-3 rankings, 45% clinical reversal) and the component-level experiments (TinyStories, GPT-2 boundary) are complementary and mutually reinforcing. The 14/14 pre-registered predictions passing is strong evidence for the theory.

4. **The design space theorem provides decision-theoretic structure.** Showing exactly two achievable families and that the ideal point is infeasible gives practitioners a clear mental model.

5. **The Lean formalization is substantial and apparently rigorous.** 357 theorems from 6 axioms with 0 sorry across 58 files is impressive engineering, and the axiom stratification (core impossibility at 0 axioms) is the right way to organize such a formalization.

6. **The nonparametric flip predictor is practical and elegant.** Seven lines of code, Spearman 0.92-0.98, outperforming the parametric alternative by 2x. This alone is a useful contribution.

7. **The GPT-2 boundary condition is a proper falsifiability test.** Showing that fine-tuning (which does not create Rashomon diversity) yields near-zero instability confirms that the theory is not vacuously true.

## Weaknesses

1. **MAJOR: The Reynolds operator framing is mathematically imprecise and adds less than claimed.** The paper says "Both are the Reynolds operator on different symmetry groups" (Section 4). But the Reynolds operator is a specific construction: for a group G acting on a vector space V, it is $R_G(v) = \frac{1}{|G|}\sum_{g \in G} g \cdot v$, projecting onto V^G. The paper uses $R_G[\varphi]_j = \frac{1}{|G_j|}\sum_{g \in G_j} \varphi_{g(j)}$, which is orbit averaging on the orbit of j -- this is indeed a special case of the Reynolds operator restricted to each orbit, but the notation $G_j$ (stabilizer? orbit?) is undefined and the connection is stated without verification that the group action is well-defined on the attribution space.

   More seriously, for DASH: the group is $S_M$ acting on M models. But DASH averages $|\text{SHAP}|$ values across models -- it does not permute model indices in the importance vector. The Reynolds operator on $S_M$ acting on $\mathbb{R}^M$ by coordinate permutation projects onto the constant vector (the mean). DASH computes the mean of attributions. Calling the mean "the Reynolds operator" is technically correct but conveys no additional information -- it is like calling the arithmetic mean "the trace of the identity representation divided by the dimension." The invariant-theoretic language does not predict anything that "take the mean" does not.

2. **MAJOR: The Hunt-Stein optimality claim is under-specified.** The paper states "By the Hunt-Stein theorem, DASH is the best equivariant estimator" (Section 4). The Hunt-Stein theorem requires: (a) a group G acting on the parameter space and sample space, (b) an invariant loss function, (c) G amenable (finite groups satisfy this trivially). But the paper never specifies: what is the parameter being estimated? What is the loss function? What is the equivariance constraint? Without these, the claim is not a theorem application but a slogan. For a finite group, the conclusion (average over the group) is immediate from the symmetry of the loss, and does not require Hunt-Stein at all -- it follows from Jensen's inequality for any convex loss.

3. **MINOR: The claim about "richer symmetry groups" is hand-waving.** Section 4 states: "For richer symmetry groups (e.g., weight permutation symmetries), V^G extends beyond simple layer averaging." This is asserted without any example, computation, or even a sketch. Weight permutation symmetries in MLPs (the neuron permutation group) are well-studied in the loss landscape literature. The Reynolds operator for this group would average over all neuron permutations within a layer -- this is again just layer averaging of neuron-level importance. The paper does not provide any example where the G-invariant projection yields something non-obvious.

4. **MINOR: The orbit structure discussion could be sharper.** The paper says "Both sacrifice completeness (report ties for interchangeable components) to gain stability." In invariant-theoretic terms, the projection onto V^G collapses orbits to points -- you lose the information about which orbit representative you observe. This is the correct explanation for why completeness is sacrificed, and the paper should state it explicitly rather than treating it as an empirical observation. The dimension count is: for G = S_k^L acting on kL components, V^G has dimension L (one coordinate per orbit). The paper does not give this dimension, which would make the information loss concrete.

5. **MINOR: The "Pareto-optimal" claim is imprecise.** Theorem 2 says DASH is Pareto-optimal "among unbiased aggregations on the B branch." This is a weak claim -- the comparison class is narrow. The paper should clarify whether there exist biased estimators that dominate DASH in some regime (the James-Stein phenomenon for dimension >= 3 comes to mind, though the equivariance constraint may rule it out).

## Questions for Authors

1. In what precise sense is DASH "the Reynolds operator on S_M"? The Reynolds operator for S_M acting on R^M by coordinate permutation maps any vector to its mean. DASH computes means of attributions across models. Is there any content to this identification beyond "DASH takes means"?

2. Can you provide a single concrete example where the G-invariant projection for a symmetry group G produces an output that is not "average within obvious architectural units"? For instance, if G includes both head permutations and layer permutations, what does V^G look like?

3. For the Hunt-Stein claim: what exactly is the parameter space, the loss function, and the equivariance constraint? Can you write down the Hunt-Stein theorem statement as it applies to your setting?

4. The dimension of V^G for G = S_k^L is L (one invariant per orbit = per layer). Can you confirm this? If so, the projection from kL dimensions to L dimensions represents a specific, quantifiable information loss. Does the residual (the non-invariant part) have any interpretable structure, or is it pure noise under the Rashomon property?

5. The paper mentions Molien's theorem nowhere, despite it being the standard tool for computing dim(V^G) for finite groups. Is there a reason? For G = S_k acting on R^k, Molien gives dim(V^G) = 1 (as expected). For G = S_k^L acting on R^{kL}, it gives dim(V^G) = L. These are trivial applications, but stating them would make the invariant-theoretic framework more than notational.

6. The bilemma's connection to invariant theory: the statement "F+S is achievable iff H has a neutral element" is reminiscent of the fixed-point theorem for group actions (a finite group acting on a finite set has a fixed point iff the number of orbits equals the number of fixed points mod |G|). Is there a formal connection, or is this a coincidence of language?

## Mathematical Assessment of the Orbit Averaging Claims

The group-theoretic framing is **technically correct but largely decorative** at the level presented in this paper. Here is my detailed assessment:

**What is correct:**
- The Reynolds operator for a finite group G acting on a vector space V does project onto V^G.
- For G = S_k^L acting on R^{kL} by permuting heads within layers, V^G is indeed the L-dimensional subspace of vectors constant within each layer. The projection is layer averaging.
- DASH does compute means, and the mean is the image of the Reynolds operator for the symmetric group acting by coordinate permutation.
- Orbit averaging is the unique linear projection onto V^G that is G-equivariant and idempotent.

**What is missing or misleading:**
- The Reynolds operator identification adds no predictive power in the cases considered. For S_k^L, "average within layers" is obvious without any invariant theory. The framework would add value if it predicted a non-obvious aggregation for a non-obvious symmetry group -- but no such example is provided.
- The Hunt-Stein application is not properly instantiated. The parameter, loss, and equivariance constraint are not specified, making the "best equivariant estimator" claim unverifiable from the paper alone.
- The paper does not use any of the machinery of invariant theory (Molien's theorem, character theory, decomposition into isotypic components). It uses only the zeroth-order fact that averaging over G projects onto V^G. This is undergraduate linear algebra, not representation theory.
- The connection between the two levels (DASH = S_M, circuits = S_k^L) is stated as if it were deep ("The same mathematics"), but the common structure is simply "taking means over a group action," which is a single definition, not a unifying theory.

**Where the framework could genuinely add insight (but the paper does not go there):**
- Decomposing the attribution space into isotypic components under G would separate the "stable" part (trivial representation = V^G) from the "unstable" part (non-trivial representations). The variance of attributions in each isotypic component could be bounded separately. This would give a finer characterization than the binary stable/unstable dichotomy.
- For non-obvious groups (e.g., the neuron permutation group composed with scaling symmetries in ReLU networks, or the full weight-space symmetry group of a transformer including attention head permutations AND key-query rotation symmetries), the Reynolds operator would produce genuinely non-trivial projections. The paper gestures at this but provides nothing concrete.
- Molien's theorem could give the dimension of V^G for arbitrary architectural symmetry groups, yielding an "information budget" (how much of the attribution vector survives projection). This is a natural quantity the paper does not compute.

**Verdict:** The group theory is a correct but thin veneer over "take the mean." It provides useful language (orbits, invariant subspace, equivariance) but no computational or predictive content beyond what is obvious without it. The paper would be honest to say: "Orbit averaging is the natural aggregation; we note the connection to the Reynolds operator for readers familiar with invariant theory." Claiming it as a major conceptual contribution overstates the case.

## Score: 7

The core impossibility theorem is clean, general, and well-proven. The empirical program is thorough and the two-level validation is compelling. The Lean formalization is a genuine contribution. The group-theoretic framing is oversold but not wrong. The paper makes a solid contribution to the theory of explainability, even if the invariant-theory layer is thinner than advertised. The bilemma and tightness classification are nice structural results. The practical diagnostic (minority fraction) is useful. I would accept this paper with revisions to temper the invariant-theory claims.

## Confidence: 4

I am confident in my assessment of the mathematical content. I have less certainty about the empirical methodology (not my primary expertise) but the experimental design appears sound. I am very confident that the group-theoretic claims are technically correct but add less insight than the paper suggests.

## Best Paper Recommendation: No

The core result is simple (which is good) but the contribution is primarily in the synthesis -- connecting input-level and component-level attribution, the empirical program, and the formalization. The invariant-theory contribution, which might have elevated this to best-paper territory, is not developed deeply enough. A best paper in this space would need to either prove a deeper structural result (e.g., the isotypic decomposition of attribution variance) or demonstrate the Reynolds operator framework on a genuinely non-obvious symmetry group.

---

## R8_Statistics_Monograph

I now have sufficient material for the review. Here is my assessment:

---

## Summary (2-3 sentences)

The paper proves that no single-model feature ranking can simultaneously be faithful, stable, and complete under collinearity, with formal verification in Lean 4. The empirical validation spans tree ensembles (ranking lottery, prevalence survey, diagnostics), transformer circuits (TinyStories), and domain applications (gene expression, credit). The theoretical contribution is strong, but the statistical methodology in several empirical sections has gaps that weaken the evidentiary claims.

## Strengths (numbered, specific)

1. **Clean impossibility result with zero axiom dependencies.** The core theorem (attribution_impossibility) requires only the Rashomon property as hypothesis, making the result extremely general. The Lean 4 formalization with 0 sorry is a genuine contribution to reproducibility in ML theory.

2. **Config C negative control is well-designed.** Using GPT-2 fine-tuned from a shared checkpoint as a non-Rashomon boundary condition is a thoughtful falsification exercise. The theory correctly predicts reduced instability, and the fact that within-model noise exceeds between-model variation is a crisp diagnostic.

3. **Split-half reliability control.** Demonstrating that within-model measurement precision (Spearman 0.991) far exceeds between-model agreement (0.565) cleanly isolates the source of instability as model multiplicity rather than measurement noise. This is exactly the right control.

4. **Random projection null for G-invariant lift.** Showing the G-invariant projection achieves the 100th percentile among 1,000 random projections to the same dimensionality is a strong control against the concern that any low-dimensional projection would yield high correlation.

5. **Prevalence survey with explicit power analysis.** The paper honestly reports 32% power at the 10% threshold and frames 68% as a conservative lower bound. This is commendably transparent.

6. **Specificity controls (Lending Club, Wine, Heart Disease, California Housing).** Datasets where the impossibility should NOT bite are correctly identified as stable. This is crucial for establishing that the framework is not just detecting noise.

7. **Subsample sensitivity analysis.** The graduated analysis from subsample=0.80 to 1.00 is convincing: instability persists even at 0.95, and only the fully deterministic case eliminates it.

## Weaknesses (numbered, with severity)

1. **CRITICAL: The "seven pre-registered predictions" are never enumerated.** Line 1872 claims "Seven pre-registered predictions derived from the theory are evaluated per configuration; all 7/7 pass." But the paper never lists what these seven predictions are, when they were registered, or where the pre-registration is documented. "Pre-registered" has a specific meaning in the replication methodology literature (timestamped specification of hypotheses and analysis plan before data collection). Without evidence of actual pre-registration or even an enumeration of the predictions, this claim is unverifiable. This is the most misleading single sentence in the empirical sections.

2. **MAJOR: Minority fraction vs. flip rate correlation is near-tautological.** The minority fraction MF_j is defined as min(count(SHAP_j > 0), count(SHAP_j < 0)) / M. The flip rate for sign flips is essentially the same quantity -- the probability that a new model lands in the minority sign class. Reporting Spearman 0.92-0.98 between these two quantities is reporting that an empirical estimator correlates with the quantity it estimates. The paper partially acknowledges this at line 2110 ("Recall is tautologically 1.0") but then prominently reports the Spearman correlations as if they constitute a meaningful empirical finding (e.g., in the executive summary, line 146). The advantage over the Gaussian formula is real, but the comparison is between a nonparametric estimator of the target and a parametric model of the target -- the nonparametric estimator will always win when data is available.

3. **MAJOR: Cross-method correlation (rho = 0.5-0.6) lacks a null comparison.** Table in lines 1959-1969 shows weight zeroing vs. mean ablation cross-method Spearman of 0.504-0.591. The paper interprets this as "substantial disagreement." But what is the expected Spearman correlation under a null where the two methods rank components independently? For n=20 components, the expected absolute Spearman under independence is approximately 0.30 (|rho| ~ sqrt(1/n) for random rankings). For n=54, approximately 0.19. So rho = 0.50-0.59 is actually *significant positive agreement*, not disagreement. The paper should report the null expectation and frame this as "methods agree more than chance but less than perfectly" rather than "methods disagree substantially."

4. **MAJOR: No multiple testing correction across the paper.** The paper reports p-values from: Hartigan's dip test (5 datasets), permutation tests (3 configs), Z-tests (hundreds of feature pairs across 11 datasets), Mann-Whitney tests, and split-half reliability tests. There is no family-wise error rate correction or false discovery rate control. The single mention of multiplicity (line 1031, referring to Pocock/O'Brien-Fleming boundaries for a sequential design) is a caveat for a different context. For the prevalence survey alone, testing hundreds of feature pairs across 77 datasets without FDR control means some fraction of the "unstable" designations are false positives.

5. **MAJOR: Non-independence of 45 pairwise comparisons from 10 models.** The TinyStories experiment computes 45 pairwise Spearman correlations from 10 models and reports statistics (mean, CI). These 45 values share models -- correlation(model_1, model_2) and correlation(model_1, model_3) are dependent because both include model_1. The 95% CIs reported in Table 3 (e.g., [0.527, 0.603]) appear to be computed as if the 45 pairs were independent, which they are not. The effective sample size is closer to 10 (models) than 45 (pairs). The CIs are likely too narrow.

6. **MINOR: Duplicate paragraph.** Lines 3072-3074 contain the paragraph starting "Just fix the seed" duplicated verbatim (it appears at both line 3072 and line 3074). This is an editorial error.

7. **MINOR: Prevalence survey hyperparameter sensitivity.** The robustness analysis uses only 3 hyperparameter configurations on 8 datasets. With prevalence ranging 50-75% across configurations, the statement "The 68% headline is conservative" is not well-supported -- 50% (Config B) is substantially lower. The paper should acknowledge this range more carefully.

8. **MINOR: Bimodality validation on California Housing.** The dip test gives p=0.575 (not significant), and the paper calls this "borderline." But the theory predicts bimodality when collinearity is present. California Housing has real collinearity. The failure of the prediction should be discussed more carefully rather than dismissed as "weaker collinearity structure."

## Questions for Authors (numbered)

1. Where exactly are the "seven pre-registered predictions" enumerated? Were they documented with a timestamp before any TinyStories experiments were run? If not, please replace "pre-registered" with "theory-derived" or "a priori."

2. For the minority fraction predictor: what is the added value of reporting Spearman correlation between MF_j and flip rate, given that MF_j is an estimator of the flip rate? Would a calibration plot (MF_j vs. observed flip rate) with confidence bands be more informative?

3. For the cross-method comparison (Table in lines 1959-1969): what is the expected Spearman correlation under the null hypothesis that the two methods rank components independently? Is rho=0.50 significantly above this null?

4. How are the 95% CIs for pairwise Spearman correlations in Table 3 computed? Do they account for the non-independence of the 45 pairs?

5. The prevalence survey flags a dataset as "unstable" if ANY correlated pair exceeds the 10% flip threshold. With hundreds of pairs tested per high-dimensional dataset, what is the expected false positive rate per dataset? Is the 93% rate for P >= 20 partly inflated by multiple comparisons?

6. The paper claims the ranking lottery count "keeps growing" (24 at 50 seeds, 35 at 100 seeds). Is there an asymptotic analysis or species-richness estimator (e.g., Chao1) applied to estimate the true number of distinct rankings?

## Statistical Methodology Assessment

The paper's theoretical methodology is rigorous: the impossibility proof, Berry-Esseen bounds for the Z-test, and the design space theorem are sound. The diagnostic framework (Screen -> Z-test -> DASH) is well-motivated and the thresholds are principled.

The empirical methodology has several gaps:

- **Estimation vs. prediction confusion**: The minority fraction is presented as a "predictor" of flip rates, but it is an estimator of the same quantity. The high correlation is uninformative.

- **Missing null distributions**: The cross-method comparison and some correlation analyses lack null baselines, making it impossible to assess whether observed values are surprising.

- **Multiple testing**: With dozens of statistical tests across multiple datasets and configurations, the absence of any multiplicity correction is a notable gap. Individual significant p-values (e.g., dip p=0.0002) would survive Bonferroni correction, but the overall framework of reporting many uncorrected p-values weakens the statistical rigor.

- **Non-independence**: The pairwise comparison structure (45 pairs from 10 models) is not properly handled. Standard errors and CIs are likely anti-conservative.

- **Pre-registration claim**: Using "pre-registered" without evidence of actual pre-registration is a serious methodological red flag in the current replication-crisis context. The predictions may well have been derived from theory before seeing data, but the term carries a specific evidentiary standard that appears unmet.

The core claims (instability exists, it is predicted by collinearity + similar importance, DASH resolves it) are well-supported even with these issues. The concerns primarily affect the precision of quantitative claims and the strength of certain validation arguments.

## Score: 6/10

The theoretical contribution is strong (impossibility theorem, Lean formalization, design space exhaustiveness). The empirical validation demonstrates the phenomenon convincingly at a qualitative level. However, the statistical methodology issues -- particularly the pre-registration claim, the near-tautological minority fraction analysis, missing null distributions, and absent multiplicity corrections -- prevent a higher score. These are fixable in revision.

## Confidence: 4/5

I am confident in the statistical methodology assessment. The identified issues (near-tautological correlation, missing nulls, multiplicity, non-independence) are standard concerns in empirical methodology review. The one area of lower confidence is the G-invariant projection framework for TinyStories, where the group-theoretic construction may have subtleties I have not fully evaluated.

