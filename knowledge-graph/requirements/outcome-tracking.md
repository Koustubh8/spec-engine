---
title: Outcome Tracking
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [self-improvement]
strength: SHALL
---

# Outcome Tracking

Every recommendation SHALL be logged as an MLflow run with: input features, DSPy program version, predicted outcome, and timestamp. When actual outcome is observed, the MLflow run SHALL be updated with the ground truth.

|rel:portion_of| [[specs/self-improvement-spec]]
