---
title: Self-Improvement Loop Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [mlflow, dspy, optimization, self-improving]
---

# Self-Improvement Loop Specification

The core differentiator: every recommendation is tracked as an MLflow experiment. DSPy programs are re-optimized based on outcome feedback. The system learns which analytical approaches produce accurate recommendations.

## Loop Architecture

```
Recommendation made → MLflow run created (params: DSPy program version, input features)
    ↓
Outcome observed (N days later) → MLflow run updated with actual metric
    ↓
Weekly optimization job:
  1. Query MLflow for runs where outcome_observed = True
  2. Compute accuracy per DSPy program version × module
  3. If accuracy declined → trigger DSPy re-optimization with new few-shot examples
  4. If accuracy stable → continue; log metrics to NebulaGraph
    ↓
NebulaGraph: decision_graph nodes track every recommendation → outcome → DSPy version chain
```

## Contracts

|rel:exposes| [[concepts/get-optimization-status]]
|rel:spec_of| [[tools/self-improvement-orchestrator]]
|rel:reuses| [[concepts/DSPy]]
|rel:reuses| [[concepts/MLflow]]
|rel:contains| [[requirements/outcome-tracking]]
|rel:contains| [[requirements/dspy-optimization-schedule]]
|rel:contains| [[requirements/accuracy-monitoring]]
|rel:contains| [[requirements/fallback-to-classical]]
|rel:contains| [[requirements/nebulagraph-lineage-sync]]
