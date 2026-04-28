# Future Research Directions

From 9-reviewer panel (April 2026): 4 adversarial, 3 cross-domain, 2 neutral. Scores 5-7, mean 6.2. Consensus: strong accept, not best paper yet. These are the paths that would elevate it.

## Path 1: Algorithmic Identification Impossibility (R9, R2)

Prove that "what algorithm does the model implement" is also unstable across seeds, not just "which component is most important." The current theorem constrains importance rankings. Safety cases depend on algorithm identification (existential: "does a deception circuit exist?") which may be stable even when rankings are not. Showing functional instability — that the same computation is implemented by genuinely different algorithms across seeds, not just permuted heads — would make the safety implications airtight.

Key experiment: trace a specific computation (e.g., induction, next-token prediction given subject) through each of the 10 TinyStories networks. Measure whether attention patterns are functionally equivalent across seeds (just permuted) or genuinely different algorithms.

## Path 2: Frontier-Scale From-Scratch Training (R2, R9)

Train multiple GPT-2+ models from scratch on the same data and show the impossibility holds at scale. The current evidence is: toy models (4L/4H, 6L/8H) show full instability; GPT-2 fine-tuned shows no instability. The gap between these is the gap that matters. Fine-tuning doesn't create Rashomon diversity, but pre-training does — verify this empirically at ≥12 layers.

Practical blocker: training 10 GPT-2-scale models from scratch requires ~10× the compute of the current TinyStories experiments.

## Path 3: Deep Invariant Theory (R10, R7)

### 3a: Isotypic decomposition of attribution variance
Decompose the attribution space into isotypic components under G. The trivial representation = V^G (stable part). Non-trivial representations = unstable part. Bound variance in each component separately. This gives a finer characterization than the binary stable/unstable dichotomy.

### 3b: Molien's theorem for information budgets
Compute dim(V^G) for arbitrary architectural symmetry groups via Molien's theorem. For G = S_k^L: dim = L (trivial). For richer groups (neuron permutations composed with scaling symmetries in ReLU networks, key-query rotation symmetries in attention): dim(V^G) may be non-trivial. This yields an "information budget" — how much of the attribution vector survives projection.

### 3c: Non-trivial V^G example
Find a concrete architecture where the G-invariant projection produces something that is NOT "average within obvious architectural units." Candidates: weight permutation symmetries in MLPs; full weight-space symmetry group of a transformer including head permutations AND key-query rotation symmetries.

### 3d: Residual structure
Characterize the non-invariant part of the attribution vector. Under Rashomon, is it pure noise, or does it have interpretable structure (e.g., the specific permutation chosen by a given seed)?

## Path 4: General SBD Theorem (R4, R7)

Prove that G-invariance of ANY symmetric decision problem yields a two-family decomposition with explicit conditions on the group action and tight bounds. The current SBD has three instances (binary transpositions, permutation groups, CPDAG automorphisms). A general theorem — "for any finite group G acting on a decision space satisfying [conditions], the achievable set decomposes into exactly two families parameterized by the orbit structure" — would be a genuine contribution to impossibility theory and decision theory.

The supplement (line 3661) candidly identifies this as "the natural next step."

## Path 5: Family B Sub-Landscape (R7)

Characterize the full sub-landscape of partial-order methods within Family B. For qualified majority partial orders (rank j > k only when fraction ≥ q of models agree), what is the achievable (stability, unfaithfulness, completeness) triple as a function of q? DASH is the q=0.5 case (majority). Unanimous partial order is q=1.0. This would give the Design Space result the richness of social choice domain-restriction characterizations (Sen's value restriction, Black's single-peakedness).

## Path 6: SAE Escape Hatch (R2, R9)

Do independently trained SAEs on the same model produce the same features? If yes (as Bricken et al.'s reproducibility analysis suggests), SAE-based attribution may escape the Rashomon property because the decomposition is post-hoc on a fixed model — there is no Rashomon set over models. This would make SAEs the principled escape from the impossibility for component-level attribution.

If no — if SAE features are themselves unstable across training runs of the SAE — then the impossibility extends to the dominant paradigm for neural network interpretability.

Either answer is significant.

## Path 7: Additional Experiments (R2, R8)

### 7a: Path patching / causal scrubbing
Test the impossibility with position-specific, input-dependent patching methods (Conmy et al. 2023 ACDC, Goldowsky-Dill et al. 2023 path patching). These break within-layer symmetry for specific inputs. If the impossibility holds even for input-dependent methods, the result is much stronger. If not, the boundary is important to characterize.

### 7b: Git Re-Basin comparison
Ainsworth et al. 2023 show independently trained networks can be permutation-aligned to reveal shared structure. This is a competing resolution to V^G. Compare: does permutation alignment + raw importance achieve the same lift as V^G? If so, the instability is entirely explained by permutation symmetry and V^G is sufficient. If not, there's additional structure beyond permutation.

### 7c: Statistical corrections
- Multiple testing correction (FDR) across all reported p-values
- Non-independence correction for pairwise CIs from 10 models (effective N ≈ 10, not 45)
- Null baseline for cross-method ρ (expected |ρ| under independence ≈ 0.30 for n=20)
- Chao1 species-richness estimator for the ranking lottery asymptote

### 7d: Approximate Rashomon inevitability
Quantitative version: if the training algorithm is ε-symmetric (e.g., due to feature ordering, initialization schemes, learning rate warmup), does the Rashomon property hold with probability ≥ 1/2 − ε?
