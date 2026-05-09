---
title: Consultant Chat Interface Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [ui, chat, react, api]
---

# Consultant Chat Interface Specification

React chat interface where the user asks marketing questions and receives analytical responses powered by the ML pipeline. Each response includes a score, confidence interval, and links to the MLflow run that produced it.

## Supported Queries
- "What's the ROAS on Instagram this month?" → MMM module
- "Which customers are at risk of churning?" → CLV module
- "Did the email campaign actually drive incremental revenue?" → Uplift module
- "Who should we target with the next promotion?" → Segmentation + Uplift
- "Which creative is winning?" → Creative Analysis
- "Where should I shift $10K of budget?" → MMM + Budget Optimization

|rel:spec_of| [[tools/consultant-frontend]]
|rel:exposes| [[concepts/post-chat-message]]
|rel:accepts| [[concepts/chat-message]]
|rel:returns| [[concepts/chat-response]]
|rel:contains| [[requirements/nlp-query-routing]]
|rel:contains| [[requirements/response-with-confidence]]
|rel:contains| [[requirements/mlflow-run-linking]]
|rel:contains| [[requirements/streaming-response-updates]]
|rel:contains| [[requirements/historical-accuracy-display]]
