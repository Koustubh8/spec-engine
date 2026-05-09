---
title: Causal Identification is Hard
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [constraint, causal, mmm, uplift]
---

# Causal Identification is Hard

MMM attribution and uplift modeling both require causal identification — separating correlation from causation. This is the P vs NP-adjacent problem: in the worst case, causal structure learning is NP-hard.

Practical constraints:
- MMM requires temporal alignment of channel spend (daily/weekly) with conversion events — missing data or misaligned windows produce garbage coefficients
- Uplift modeling needs randomized control/treatment assignments — observational data has selection bias that no amount of ML can fully correct
- Multi-touch attribution is fundamentally underdetermined: N touchpoints produce N! possible attribution paths, all consistent with the observed data
- Adstock effects (lagged impact of advertising) add N× more parameters to an already ill-posed problem

**Mitigation**: Use Bayesian methods (PyMC, Stan) for MMM to encode prior knowledge about channel effectiveness. Use causal forests or Meta-learners for uplift. Always surface confidence intervals, not point estimates.
|rel:constrains| [[concepts/mmm-attribution-engine]]
|rel:constrains| [[concepts/uplift-causal-engine]]
