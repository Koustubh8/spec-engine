---
title: Dspy Optimization Schedule
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [dspy]
strength: SHALL
---

# Dspy Optimization Schedule

The system SHALL run DSPy optimization on a configurable schedule (default: weekly). Each optimization cycle SHALL: query MLflow for completed runs with outcomes, identify underperforming DSPy programs, re-optimize with new few-shot examples, register new DSPy version in MLflow model registry.

|rel:portion_of| [[specs/self-improvement-spec]]
