---
title: DSPy Cold Start and Feedback Latency
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [constraint, dspy, ml]
---

# DSPy Cold Start and Feedback Latency

The self-improvement loop depends on DSPy optimizing its LM programs based on outcomes. This creates a cold-start problem: before any campaigns have run, there are no outcomes to optimize against.

Constraints:
- **Cold start**: Initial DSPy programs must use zero-shot / few-shot prompts before any outcome data exists. The first N recommendations are uncalibrated
- **Feedback latency**: Campaign outcomes take days/weeks to materialize. MMM attribution needs 4-8 weeks of data for stable estimates. The improvement loop runs on a weekly schedule at best
- **Label sparsity**: Most marketing decisions don't have clean counterfactuals. "Would this customer have converted without the email?" is unanswerable for an individual
- **Optimization cost**: Each DSPy optimization run calls the LM 50-200x for prompt exploration. On a weekly cycle with 5 DSPy programs, that's significant API cost
- **Concept drift**: Consumer behavior changes seasonally. A DSPy program optimized on Q1 data may perform poorly in Q4

**Mitigation**: Bootstrap with synthetic data + historical campaign data. Run DSPy optimization on a staged schedule (weekly for high-velocity modules, monthly for slow ones). Maintain fallback classical ML models (XGBoost) that work without LM calls.
|rel:constrains| [[concepts/dspy-optimized-programs]]
|rel:constrains| [[concepts/self-improvement-loop]]
