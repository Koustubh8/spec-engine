---
title: Segment Drift Monitoring
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [uplift]
strength: SHALL
---

# Segment Drift Monitoring

The segmentation engine SHALL monitor segment drift over time. When a segment's centroid moves more than a configurable threshold, the system SHALL alert and suggest re-clustering.

|rel:portion_of| [[specs/segmentation-spec]]
