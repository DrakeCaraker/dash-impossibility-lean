#!/usr/bin/env python3
"""
Published Ranking Reproducibility Study

For each of 5 public datasets, train 50 XGBoost models with different seeds
and measure how many distinct SHAP feature rankings appear. Demonstrates that
single-model SHAP rankings are seed-dependent artifacts, not replicable findings.

Methodology:
- 50 models per dataset, seeds 0-49
- subsample=0.8 (XGBoost recommended regularization)
- Control: subsample=1.0 (deterministic)
- Fixed test set (seed=42, 20% holdout)
- TreeSHAP global importance (mean |SHAP| over test set)

Output: results_ranking_replication.json
"""

import json
import numpy as np
from collections import Counter
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

# Datasets
from sklearn.datasets import load_breast_cancer, fetch_california_housing
from sklearn.model_selection import train_test_split

try:
    import xgboost as xgb
    import shap
except ImportError:
    print("ERROR: pip install xgboost shap")
    exit(1)

def load_datasets():
    """Load 5 public datasets."""
    datasets = {}

    # 1. Breast Cancer Wisconsin
    bc = load_breast_cancer()
    datasets['Breast Cancer'] = {
        'X': bc.data, 'y': bc.target,
        'feature_names': list(bc.feature_names),
        'n_samples': bc.data.shape[0], 'n_features': bc.data.shape[1]
    }

    # 2. California Housing
    ch = fetch_california_housing()
    datasets['California Housing'] = {
        'X': ch.data, 'y': ch.target,
        'feature_names': list(ch.feature_names),
        'n_samples': ch.data.shape[0], 'n_features': ch.data.shape[1]
    }

    # 3. Heart Disease (use sklearn's built-in if available, else simulate)
    try:
        from sklearn.datasets import fetch_openml
        hd = fetch_openml('heart-statlog', version=1, as_frame=False, parser='auto')
        datasets['Heart Disease'] = {
            'X': hd.data, 'y': (hd.target == '2').astype(int) if hd.target.dtype == object else hd.target.astype(int),
            'feature_names': list(hd.feature_names) if hasattr(hd, 'feature_names') else [f'f{i}' for i in range(hd.data.shape[1])],
            'n_samples': hd.data.shape[0], 'n_features': hd.data.shape[1]
        }
    except Exception as e:
        print(f"  Heart Disease: skipped ({e})")

    # 4. Diabetes (Pima)
    try:
        from sklearn.datasets import fetch_openml
        dm = fetch_openml('diabetes', version=1, as_frame=False, parser='auto')
        y_dm = (dm.target == 'tested_positive').astype(int) if dm.target.dtype == object else dm.target.astype(int)
        datasets['Diabetes'] = {
            'X': dm.data, 'y': y_dm,
            'feature_names': list(dm.feature_names) if hasattr(dm, 'feature_names') else [f'f{i}' for i in range(dm.data.shape[1])],
            'n_samples': dm.data.shape[0], 'n_features': dm.data.shape[1]
        }
    except Exception as e:
        print(f"  Diabetes: skipped ({e})")

    # 5. Wine Quality (regression → classification via median split)
    try:
        from sklearn.datasets import fetch_openml
        wq = fetch_openml('wine-quality-red', version=1, as_frame=False, parser='auto')
        y = (wq.target.astype(float) >= np.median(wq.target.astype(float))).astype(int)
        datasets['Wine Quality'] = {
            'X': wq.data, 'y': y,
            'feature_names': list(wq.feature_names) if hasattr(wq, 'feature_names') else [f'f{i}' for i in range(wq.data.shape[1])],
            'n_samples': wq.data.shape[0], 'n_features': wq.data.shape[1]
        }
    except Exception as e:
        print(f"  Wine Quality: skipped ({e})")

    return datasets


def run_ranking_study(X, y, feature_names, n_seeds=50, subsample=0.8):
    """Train n_seeds models and compute SHAP rankings."""
    # Fixed test set
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rankings_top3 = []
    rankings_top5 = []
    importances = []

    for seed in range(n_seeds):
        # Detect classification vs regression
        unique_y = len(np.unique(y_train))
        if unique_y <= 20:  # classification
            model = xgb.XGBClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.3,
                subsample=subsample, random_state=seed,
                use_label_encoder=False, eval_metric='logloss',
                verbosity=0
            )
        else:  # regression
            model = xgb.XGBRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.3,
                subsample=subsample, random_state=seed,
                verbosity=0
            )
        model.fit(X_train, y_train)

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # binary classification: class 1

        global_importance = np.mean(np.abs(shap_values), axis=0)
        importances.append(global_importance)

        ranking = np.argsort(-global_importance)
        rankings_top3.append(tuple(ranking[:3]))
        rankings_top5.append(tuple(ranking[:5]))

    importances = np.array(importances)

    # Count distinct rankings
    distinct_top3 = len(set(rankings_top3))
    distinct_top5 = len(set(rankings_top5))

    # Pairwise agreement
    n_pairs = 0
    agree_top3 = 0
    agree_top5 = 0
    for i, j in combinations(range(n_seeds), 2):
        n_pairs += 1
        if rankings_top3[i] == rankings_top3[j]:
            agree_top3 += 1
        if rankings_top5[i] == rankings_top5[j]:
            agree_top5 += 1

    # Minority fraction per feature
    signs = np.sign(np.mean(importances, axis=0))  # Not signs — importances are always positive
    # For ranking instability: compute flip rates per feature pair
    minority_fractions = []
    for f in range(importances.shape[1]):
        vals = importances[:, f]
        median_val = np.median(vals)
        above = (vals > median_val).sum()
        below = (vals <= median_val).sum()
        mf = min(above, below) / n_seeds
        minority_fractions.append(round(mf, 3))

    # Most common ranking
    top3_counter = Counter(rankings_top3)
    most_common_top3 = top3_counter.most_common(1)[0]
    top5_counter = Counter(rankings_top5)
    most_common_top5 = top5_counter.most_common(1)[0]

    # DASH consensus ranking
    mean_importance = np.mean(importances, axis=0)
    dash_ranking = np.argsort(-mean_importance)

    # Correlation matrix for identifying collinear features
    corr_matrix = np.corrcoef(X_train.T)
    max_corr_per_feature = []
    for f in range(X_train.shape[1]):
        corrs = np.abs(corr_matrix[f])
        corrs[f] = 0  # exclude self
        max_corr_per_feature.append(round(float(np.max(corrs)), 3))

    return {
        'n_seeds': n_seeds,
        'subsample': subsample,
        'distinct_top3': distinct_top3,
        'distinct_top5': distinct_top5,
        'pairwise_agreement_top3': round(agree_top3 / n_pairs, 4),
        'pairwise_agreement_top5': round(agree_top5 / n_pairs, 4),
        'most_common_top3': {
            'features': [feature_names[i] for i in most_common_top3[0]],
            'count': most_common_top3[1],
            'fraction': round(most_common_top3[1] / n_seeds, 3)
        },
        'most_common_top5': {
            'features': [feature_names[i] for i in most_common_top5[0]],
            'count': most_common_top5[1],
            'fraction': round(most_common_top5[1] / n_seeds, 3)
        },
        'dash_consensus_top5': [feature_names[i] for i in dash_ranking[:5]],
        'dash_consensus_top10': [feature_names[i] for i in dash_ranking[:10]],
        'max_correlation_per_feature': {feature_names[i]: max_corr_per_feature[i]
                                        for i in range(len(feature_names))},
    }


def main():
    print("=" * 70)
    print("PUBLISHED RANKING REPRODUCIBILITY STUDY")
    print("=" * 70)

    datasets = load_datasets()
    results = {}

    for name, data in datasets.items():
        print(f"\n{'=' * 50}")
        print(f"Dataset: {name} ({data['n_samples']} samples, {data['n_features']} features)")
        print(f"{'=' * 50}")

        # Stochastic (main experiment)
        print(f"  Running stochastic (subsample=0.8)...")
        stochastic = run_ranking_study(
            data['X'], data['y'], data['feature_names'],
            n_seeds=50, subsample=0.8
        )

        # Deterministic control
        print(f"  Running deterministic control (subsample=1.0)...")
        deterministic = run_ranking_study(
            data['X'], data['y'], data['feature_names'],
            n_seeds=50, subsample=1.0
        )

        results[name] = {
            'n_samples': data['n_samples'],
            'n_features': data['n_features'],
            'stochastic': stochastic,
            'deterministic_control': deterministic,
        }

        # Print headline
        s = stochastic
        d = deterministic
        print(f"\n  STOCHASTIC (subsample=0.8):")
        print(f"    Distinct top-3 rankings: {s['distinct_top3']}")
        print(f"    Distinct top-5 rankings: {s['distinct_top5']}")
        print(f"    Pairwise agreement (top-3): {s['pairwise_agreement_top3']:.1%}")
        print(f"    Pairwise agreement (top-5): {s['pairwise_agreement_top5']:.1%}")
        print(f"    Most common top-3: {s['most_common_top3']['features']} ({s['most_common_top3']['fraction']:.0%})")
        print(f"    DASH consensus top-5: {s['dash_consensus_top5']}")

        print(f"\n  DETERMINISTIC CONTROL (subsample=1.0):")
        print(f"    Distinct top-3 rankings: {d['distinct_top3']}")
        print(f"    Pairwise agreement (top-3): {d['pairwise_agreement_top3']:.1%}")

    # Save results
    output_path = 'results_ranking_replication.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")

    # Summary table
    print(f"\n{'=' * 70}")
    print("SUMMARY: Distinct Top-3 Rankings Across 50 Seeds")
    print(f"{'=' * 70}")
    print(f"{'Dataset':<25} {'Stochastic':>12} {'Deterministic':>14} {'Agreement':>10}")
    print("-" * 65)
    for name, r in results.items():
        s = r['stochastic']
        d = r['deterministic_control']
        print(f"{name:<25} {s['distinct_top3']:>12} {d['distinct_top3']:>14} {s['pairwise_agreement_top3']:>9.1%}")


if __name__ == '__main__':
    main()
