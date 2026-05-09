---
title: Bayesian Channel Attribution
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [mmm]
strength: SHALL
---

# Bayesian Channel Attribution

The MMM engine SHALL use Bayesian methods (PyMC) for channel attribution. Priors SHALL encode domain knowledge about channel effectiveness. Posterior distributions SHALL be sampled (not just MAP estimates).

|rel:portion_of| [[specs/mmm-spec]]
