---
title: Uplift Modeling Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [uplift, causal, inference, marketing]
---

# Uplift Modeling Specification

Causal inference for campaign treatment effects. Uses Meta-learners (S-Learner, T-Learner, X-Learner) and Causal Forests for incremental lift measurement. DSPy program interprets results and recommends targeting strategies.

## Contract

|rel:exposes| [[concepts/post-uplift-query]]
|rel:accepts| [[concepts/uplift-query-params]]
|rel:returns| [[concepts/uplift-response]]
|rel:spec_of| [[tools/uplift-engine]]
|rel:reuses| [[concepts/Causal Forests]]
|rel:reuses| [[concepts/Meta-learners]]
|rel:contains| [[requirements/incremental-lift-measurement]]
|rel:contains| [[requirements/treatment-effect-scoring]]
|rel:contains| [[requirements/segment-targeting-optimization]]
|rel:contains| [[requirements/confidence-interval-reporting]]
|rel:contains| [[requirements/dspy-uplift-interpretation]]
