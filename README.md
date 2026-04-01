# The Attribution Impossibility — Lean 4 Formalization

Lean 4 machine-checked proof of an impossibility theorem for feature attribution under collinearity. No single-model feature ranking can simultaneously be **faithful** (reflect the model's attributions), **stable** (consistent across equivalent models), and **complete** (rank all feature pairs) when features are correlated. The core theorem carries zero domain-specific axiom dependencies, verified by `#print axioms`. DASH ensemble averaging is proved to be the optimal relaxation.

Paper 3 in the [dash-shap](https://github.com/DrakeCaraker/dash-shap) research program. Targeting NeurIPS 2026.

---

## Key Results

- **Attribution Impossibility (Lean, zero domain axioms).** `attribution_impossibility` in `Trilemma.lean` — no faithful, stable, complete ranking exists under the Rashomon property. Axiom trace: only `propext`, `Classical.choice`, `Quot.sound`.
- **GBDT quantitative bounds (Lean, derived).** Attribution ratio = 1/(1-ρ²) → ∞ as ρ → 1. Proved in `Ratio.lean` from split-count axioms.
- **DASH resolution (Lean, derived).** `consensus_equity` in `Corollary.lean` — balanced ensemble averaging achieves exact ties for collinear features. Variance decreases as 1/M.
- **Design Space Theorem (Lean, derived).** `design_space_theorem` in `DesignSpace.lean` — characterizes all achievable (faithfulness, stability, completeness) triples.
- **Experimental validation.** CV = 0.35–0.66 for within-group feature rankings across XGBoost, LightGBM, CatBoost on 11 datasets. DASH reduces ranking variance by O(1/M).
- **15 Lean files, 49 declarations, 15 axioms, 0 sorry.**

---

## Repository Structure

```
dash-impossibility-lean/
├── DASHImpossibility/
│   ├── Defs.lean              # FeatureSpace, 13 axioms, stability/equity defs
│   ├── Trilemma.lean          # attribution_impossibility (zero domain axioms)
│   ├── Iterative.lean         # IterativeOptimizer abstraction
│   ├── General.lean           # GBDT instance, gbdt_impossibility
│   ├── SplitGap.lean          # split_gap_exact (pure algebra)
│   ├── Ratio.lean             # attribution_ratio = 1/(1-ρ²), ratio_tendsto_atTop
│   ├── SpearmanDef.lean       # Spearman defined from midranks, stability bounds
│   ├── Lasso.lean             # lasso_impossibility (ratio = ∞)
│   ├── NeuralNet.lean         # nn_impossibility (conditional)
│   ├── RandomForest.lean      # Contrast case (documentation only)
│   ├── SymmetryDerive.lean    # attribution_sum_symmetric (DERIVED from axioms)
│   ├── Impossibility.lean     # Equity violation + stability bound
│   ├── Corollary.lean         # DASH consensus equity, variance convergence
│   ├── DesignSpace.lean       # Design Space Theorem, strongly_faithful_impossible
│   └── Basic.lean             # Import hub
├── paper/
│   ├── main.tex               # NeurIPS 2026 paper (13 pages)
│   ├── supplement.tex         # Supplementary material (65 pages)
│   ├── references.bib         # 23 citations
│   ├── scripts/               # 26 experiment and figure scripts
│   ├── figures/               # PDF figures
│   └── results_*.json/txt     # 26 experiment results files
├── docs/
│   ├── co-author-guide.md     # Onboarding for co-authors
│   ├── verification-audit.md  # Verification checklist and risk assessment
│   └── impact-assessment.md  # Impact analysis for collaborators
├── lakefile.toml
├── lean-toolchain
└── CLAUDE.md                  # Development instructions
```

---

## Quick Start

### Build

```bash
# Install Lean 4 via elan if needed
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Clone and build
git clone https://github.com/DrakeCaraker/dash-impossibility-lean
cd dash-impossibility-lean
lake build    # ~2500 jobs, takes 10-20 min on first build
```

### Verify the core theorem has zero domain axioms

```bash
# In a Lean 4 file or by running lake lean:
#print axioms DASHImpossibility.attribution_impossibility
# Expected output: propext, Classical.choice, Quot.sound, Model, attribution
```

### Check counts

```bash
grep -c "^theorem\|^lemma" DASHImpossibility/*.lean  # should total 49
grep -c "^axiom" DASHImpossibility/*.lean             # should total 15
grep -r "sorry" DASHImpossibility/*.lean              # should be empty
```

### Run experiments

```bash
cd paper/scripts
pip install xgboost lightgbm catboost shap scikit-learn numpy pandas
python run_validation.py          # Main validation
python run_cross_implementation.py  # Cross-implementation stability
python run_dash_resolution.py     # DASH ensemble results
```

---

## Paper

- **Title:** The Attribution Impossibility: Faithful, Stable, and Complete Feature Rankings Cannot Coexist Under Collinearity
- **Authors:** Drake Caraker, Bryan Arnold, David Rhoads
- **arXiv:** [link to be added before May 4, 2026]
- **NeurIPS 2026:** abstract May 4, paper May 6
- **Companion repository:** [dash-shap](https://github.com/DrakeCaraker/dash-shap)

---

## Citation

```bibtex
@inproceedings{caraker2026attribution,
  title     = {The Attribution Impossibility: Faithful, Stable, and Complete
               Feature Rankings Cannot Coexist Under Collinearity},
  author    = {Caraker, Drake and Arnold, Bryan and Rhoads, David},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2026},
  note      = {Lean 4 formalization: \url{https://github.com/DrakeCaraker/dash-impossibility-lean}}
}
```

---

## Authors

**Drake Caraker** — conceptualization, Lean formalization, experiments
**Bryan Arnold** — [role]
**David Rhoads** — [role]

Independent researchers. Contact: [to be added]

---

## License

MIT License. See `LICENSE` for details.
