---
title: Customer Segmentation Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [segmentation, rfm, clustering, marketing]
---

# Customer Segmentation Specification

Multi-method customer segmentation. RFM scoring, K-means clustering on behavioral features, and DSPy-optimized segment interpretation. Segments update on a configurable cadence and track drift over time.

## Contract

|rel:exposes| [[concepts/post-segment-query]]
|rel:accepts| [[concepts/segment-query-params]]
|rel:returns| [[concepts/segment-response]]
|rel:spec_of| [[tools/segmentation-engine]]
|rel:contains| [[requirements/rfm-scoring]]
|rel:contains| [[requirements/behavioral-clustering]]
|rel:contains| [[requirements/segment-drift-monitoring]]
|rel:contains| [[requirements/segment-profiles]]
|rel:contains| [[requirements/dspy-segment-interpretation]]
