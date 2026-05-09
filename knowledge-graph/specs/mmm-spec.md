---
title: Marketing Mix Modeling Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [mmm, attribution, causal, marketing]
---

# Marketing Mix Modeling Specification

Bayesian MMM for multi-channel attribution and budget optimization. Uses PyMC for Bayesian inference with adstock and saturation effects. DSPy program interprets model outputs into natural-language recommendations.

## Contract

|rel:exposes| [[concepts/post-mmm-query]]
|rel:accepts| [[concepts/mmm-query-params]]
|rel:returns| [[concepts/mmm-response]]
|rel:fails_with| [[concepts/insufficient-data]]
|rel:fails_with| [[concepts/collinear-channels]]
|rel:spec_of| [[tools/mmm-engine]]
|rel:reuses| [[concepts/Bayesian Methods]]
|rel:contains| [[requirements/bayesian-channel-attribution]]
|rel:contains| [[requirements/adstock-saturation-modeling]]
|rel:contains| [[requirements/budget-optimization]]
|rel:contains| [[requirements/roas-by-channel]]
|rel:contains| [[requirements/dspy-mmm-interpretation]]
