# NeurIPS Best Paper Session — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the NeurIPS paper to present input-level and component-level attribution as two manifestations of one impossibility; update the monograph with TinyStories results; vet both as adversarial reviewer.

**Architecture:** Option 3 (unified theorem + split experiments). Sections 1-4 present the impossibility, diagnostics, and resolution covering both granularities with orbit averaging as the unifying math. Section 5 splits: 5a input-level experiments, 5b component-level experiments. The monograph gets a new TinyStories section, mean ablation comparison, component-level framing, updated related work, and Code/Data Availability.

**Deliverables:** Revised `paper/main.tex`, 200-word OpenReview abstract, updated `paper/main_definitive.tex`, updated `paper/references.bib`, updated `paper/supplement.tex` theorem counters if needed.

---

## Part A: NeurIPS Paper (paper/main.tex)

### Task 1: Critical read + assessment

**Files:** Read only — `paper/main.tex`

- [ ] **Step 1:** Identify what must change for the paradigm shift to land by page 3
- [ ] **Step 2:** List all content that must compress or move to supplement
- [ ] **Step 3:** Write assessment as a text note (not saved — just communicated to user)

### Task 2: Add Chughtai 2023 to references.bib

**Files:**
- Modify: `paper/references.bib`

- [ ] **Step 1:** Add `chughtai2023toy` bib entry (Chughtai, Henighan, et al., "A Toy Model of Universality: Reverse Engineering How Networks Learn Group Operations", ICML 2023)

### Task 3: Restructure main.tex — Introduction

**Files:**
- Modify: `paper/main.tex` lines 50-76

The new introduction must deliver the paradigm shift by page 2. Hook: both levels of attribution are unstable for the same mathematical reason.

- [ ] **Step 1:** Rewrite abstract (lines 50-56) to cover both levels of attribution
- [ ] **Step 2:** Rewrite Introduction hook (lines 59-64) with dual-level framing: "Your SHAP plot depends on the seed. So does your circuit diagram."
- [ ] **Step 3:** Rewrite contributions list to include component-level results
- [ ] **Step 4:** Verify the paradigm shift lands by page 2-3

### Task 4: Restructure main.tex — Setup + Impossibility (unified)

**Files:**
- Modify: `paper/main.tex` lines 78-123

Present the theorem as applying to ANY attribution system with Rashomon. Show input-level and component-level are both instances.

- [ ] **Step 1:** Generalize Setup to define "attribution" at any granularity (input features OR internal components)
- [ ] **Step 2:** After the impossibility theorem proof, add "Instance 1: Input-level" and "Instance 2: Component-level" showing both are covered by the same theorem
- [ ] **Step 3:** Keep Design Space theorem, add note that G-invariant projection is the component-level analogue of Family B
- [ ] **Step 4:** Compress quantitative bounds paragraph (already supplement reference)

### Task 5: Restructure main.tex — Bilemma + Diagnostics (both levels)

**Files:**
- Modify: `paper/main.tex` lines 125-197

Bilemma applies to both levels. Diagnostics: coverage conflict for input-level, Noether counting / symmetry group for component-level.

- [ ] **Step 1:** Keep bilemma theorem + proof as-is (already general)
- [ ] **Step 2:** Add one sentence noting bilemma applies to circuit decomposition (binary: in-circuit or not)
- [ ] **Step 3:** After coverage conflict diagnostic, add "Component-level diagnostic" paragraph: the symmetry group $G = S_k^L$ determines which components are interchangeable; the G-invariant projection $V^G$ separates stable from unstable attribution
- [ ] **Step 4:** Compress variance budget and model-class universality paragraphs (move detail to supplement)

### Task 6: Restructure main.tex — Resolution (orbit averaging)

**Files:**
- Modify: `paper/main.tex` lines 229-249

Present DASH and G-invariant projection as the same mathematical operation: orbit averaging / Reynolds operator.

- [ ] **Step 1:** Frame resolution as "orbit averaging resolves the impossibility at both levels"
- [ ] **Step 2:** Input-level: DASH averages across the Rashomon set (existing content, tighten)
- [ ] **Step 3:** Component-level: G-invariant projection averages importance within orbits of the symmetry group; lifts agreement from ρ≈0.55 to ρ≈0.98
- [ ] **Step 4:** Note: same math (Reynolds operator), different symmetry groups

### Task 7: Restructure main.tex — Experiments §5a (input-level)

**Files:**
- Modify: `paper/main.tex` lines 251-343

Compress existing input-level experiments to ~1.5 pages. Keep: ranking lottery, clinical reversal, prevalence. Move to supplement: full gene expression, subsample sensitivity figure, cross-implementation details, published ranking replication.

- [ ] **Step 1:** Keep synthetic Gaussian + figures (already compact)
- [ ] **Step 2:** Keep ranking lottery table + key paragraph
- [ ] **Step 3:** Keep clinical reversal table + Applicant #91 narrative (compressed)
- [ ] **Step 4:** Compress gene expression to 2-3 sentences referencing universal monograph
- [ ] **Step 5:** Move subsample sensitivity figure + cross-implementation details to supplement
- [ ] **Step 6:** Keep prevalence as one paragraph

### Task 8: Add Experiments §5b (component-level attribution)

**Files:**
- Modify: `paper/main.tex` (insert after §5a)

New ~1.5 page section with TinyStories results. Data from `docs/tinystories-results-reference.json` and `docs/mean-ablation-results-reference.json`.

- [ ] **Step 1:** Write section header and framing paragraph: "The same theorem at circuit level"
- [ ] **Step 2:** Add TinyStories setup: 10 models × 2 architectural scales, activation patching, 7 pre-registered predictions
- [ ] **Step 3:** Add results table (Config A/B): full ρ, G-inv ρ, within-flip, between-flip, Cohen's d
- [ ] **Step 4:** Add key findings: 14/14 predictions PASS, within-layer flip ≈ 0.50 (predicted), head-vs-MLP = 0.000, full S₄ realization
- [ ] **Step 5:** Add GPT-2 boundary condition: ρ=0.993, within-flip=0.043 (no Rashomon → no instability, theorem is falsifiable)
- [ ] **Step 6:** Add mean ablation robustness: G-inv ρ≈0.97-0.99 under both methods; cross-method ρ≈0.5-0.6 (methods disagree on raw heads, agree on V^G)
- [ ] **Step 7:** Add permutation test, random projection controls, split-half reliability

### Task 9: Restructure main.tex — Related Work + Discussion

**Files:**
- Modify: `paper/main.tex` lines 345-378

Add Fisher 2019, D'Amour 2022, Chughtai 2023. Add component-level implications to discussion.

- [ ] **Step 1:** Add Fisher 2019 (MCR/Rashomon set variable importance ranges) to related work
- [ ] **Step 2:** Add D'Amour 2022 (underspecification) — distinguish: they document instability empirically, we prove the impossibility
- [ ] **Step 3:** Add Chughtai 2023 (toy model of universality) — circuit diversity as empirical Rashomon
- [ ] **Step 4:** Update Discussion to cover component-level implications and the orbit-averaging resolution as the unifying mathematical framework
- [ ] **Step 5:** Update Lean paragraph to note component-level formalization

### Task 10: Draft 200-word OpenReview abstract

**Files:**
- Create: `paper/abstract_openreview.txt`

- [ ] **Step 1:** Write 200-word abstract covering both levels, the theorem, diagnostics, resolution, key numbers (45% reversal, 68% prevalence, ρ=0.54→0.98, 14/14 predictions, GPT-2 boundary, 357 theorems)

### Task 11: Update supplement.tex counters

**Files:**
- Modify: `paper/supplement.tex` lines 29-33

- [ ] **Step 1:** Update theorem/figure/table counters to match revised main paper numbering

### Task 12: Compilation check + number verification

**Files:** All paper files

- [ ] **Step 1:** Compile main.tex with pdflatex and check for errors
- [ ] **Step 2:** Run Lean count verification block from CLAUDE.md
- [ ] **Step 3:** Verify all numbers in the paper trace to result files or Lean theorems
- [ ] **Step 4:** Check page count ≤ 10 (excluding references and checklist)

### Task 13: /vet the NeurIPS paper

- [ ] **Step 1:** Invoke the vet skill as an adversarial NeurIPS reviewer

---

## Part B: Monograph (paper/main_definitive.tex)

### Task 14: Add TinyStories component-level attribution section to monograph

**Files:**
- Modify: `paper/main_definitive.tex` (insert after current §8.13 or MI section)

Full results with per-seed tables, all controls, all statistics from `docs/tinystories-results-reference.json`.

- [ ] **Step 1:** Write section header and experimental setup (architecture details, training, evaluation)
- [ ] **Step 2:** Write per-config results subsection with full statistics tables
- [ ] **Step 3:** Write controls subsection (split-half, random projection, permutation test)
- [ ] **Step 4:** Write GPT-2 boundary condition subsection
- [ ] **Step 5:** Write S₄ realization and full symmetry analysis

### Task 15: Add mean ablation comparison section to monograph

**Files:**
- Modify: `paper/main_definitive.tex` (insert after TinyStories section)

Data from `docs/mean-ablation-results-reference.json`.

- [ ] **Step 1:** Write method comparison: weight zeroing vs mean ablation
- [ ] **Step 2:** Write cross-method agreement analysis (per-model ρ table)
- [ ] **Step 3:** Write key finding: methods disagree on raw heads but agree on V^G — the disagreement IS an instance of the impossibility

### Task 16: Add "Component-Level Attribution" framing to monograph

**Files:**
- Modify: `paper/main_definitive.tex` (update MI section intro ~line 1774)

- [ ] **Step 1:** Add framing paragraph: activation patching = attribution at component granularity, governed by same theorem
- [ ] **Step 2:** Connect to G-invariant projection as orbit averaging (Reynolds operator)

### Task 17: Update monograph related work

**Files:**
- Modify: `paper/main_definitive.tex` lines 3337-3418

- [ ] **Step 1:** Add Fisher 2019 (model class reliance / Rashomon set ranges)
- [ ] **Step 2:** Add D'Amour 2022 (underspecification as empirical Rashomon)
- [ ] **Step 3:** Add Chughtai 2023 (circuit universality / diversity)

### Task 18: Add Code and Data Availability section to monograph

**Files:**
- Modify: `paper/main_definitive.tex` (before or after Discussion)

- [ ] **Step 1:** Add section with GitHub URLs, Lean DOI, TinyStories dataset reference, dash-shap PR #255

### Task 19: Verify monograph numbers

**Files:** `paper/main_definitive.tex`, result JSON files

- [ ] **Step 1:** Verify all TinyStories numbers match `docs/tinystories-results-reference.json`
- [ ] **Step 2:** Verify all mean ablation numbers match `docs/mean-ablation-results-reference.json`
- [ ] **Step 3:** Verify Lean counts match CLAUDE.md verification block

### Task 20: /vet the monograph

- [ ] **Step 1:** Invoke the vet skill for the monograph
