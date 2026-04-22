#!/usr/bin/env python3
"""
Verify PROJECT_REGISTRY.md against actual repo state.
Run: python3 paper/scripts/verify_registry.py
"""

import subprocess
import re
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../..')

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def check(name, expected, actual):
    status = "PASS" if str(expected) == str(actual) else "FAIL"
    symbol = "✓" if status == "PASS" else "✗"
    print(f"  {symbol} {name}: expected={expected}, actual={actual} [{status}]")
    return status == "PASS"

print("=" * 60)
print("PROJECT REGISTRY VERIFICATION")
print("=" * 60)

all_pass = True

# 1. Lean counts
print("\n§1 Lean Formalization")
theorems = int(run("grep -c '^theorem\\|^lemma' DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print s}'"))
axioms = int(run("grep -c '^axiom' DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print s}'"))
sorry = int(run("grep -rc 'sorry' DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print s}'"))
files = int(run("ls DASHImpossibility/*.lean | wc -l").strip())

all_pass &= check("theorems", 357, theorems)
all_pass &= check("axioms", 6, axioms)
all_pass &= check("sorry", 0, sorry)
all_pass &= check("files", 58, files)

# 2. Axiom names
print("\n§1.1 Axiom Names")
axiom_lines = run("grep '^axiom' DASHImpossibility/*.lean").split('\n')
expected_axioms = ['Model', 'firstMover', 'firstMover_surjective', 'crossGroupBaselineCore', 'proportionalityConstant', 'modelMeasure']
for name in expected_axioms:
    found = any(name in line for line in axiom_lines)
    all_pass &= check(f"axiom {name}", "present", "present" if found else "MISSING")

# 3. Paper counts match Lean
print("\n§3 Paper Counts")
for paper, path in [("NeurIPS", "paper/main.tex"), ("Supplement", "paper/supplement.tex"),
                      ("JMLR", "paper/main_jmlr.tex"), ("Monograph", "paper/main_definitive.tex")]:
    if os.path.exists(path):
        content = open(path).read()
        has_357 = "357" in content
        has_6ax = "6 axiom" in content
        all_pass &= check(f"{paper} has '357'", True, has_357)
        all_pass &= check(f"{paper} has '6 axiom'", True, has_6ax)

# 4. Retracted content absent
print("\n§2.2 Retracted Content Absent")
main_content = open("paper/main.tex").read().lower()
retracted = ["entropy bimodal", "pairwise.*audit pair", "p/2 bound", "data-only.*predict"]
for term in retracted:
    found = bool(re.search(term, main_content))
    all_pass &= check(f"retracted '{term}'", False, found)

# 5. Anonymization
print("\n§ Anonymization")
main_lines = open("paper/main.tex").readlines()
for i, line in enumerate(main_lines):
    if line.startswith('%'):
        continue
    if any(name in line.lower() for name in ['drake', 'caraker', 'github.com/drake']):
        if 'anonymized' not in line.lower():
            print(f"  ✗ DEANONYMIZATION at line {i+1}: {line.strip()}")
            all_pass = False

# 6. Key files exist
print("\n§ Key Files")
for f in ["paper/main.tex", "paper/supplement.tex", "paper/main_jmlr.tex",
          "paper/main_definitive.tex", "paper/references.bib",
          "paper/figures/design_space.pdf", "paper/figures/subsample_sensitivity.pdf",
          "paper/figures/gene_expression_pathway.pdf"]:
    exists = os.path.exists(f)
    all_pass &= check(f"exists {f}", True, exists)

# Summary
print(f"\n{'=' * 60}")
if all_pass:
    print("ALL CHECKS PASSED ✓")
else:
    print("SOME CHECKS FAILED ✗")
sys.exit(0 if all_pass else 1)
