---
title: Behavioral Clustering
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [segmentation]
strength: SHALL
---

# Behavioral Clustering

The segmentation engine SHALL perform K-means clustering on behavioral features (purchase frequency, avg order value, category preference, engagement score). Optimal K SHALL be determined via elbow method + silhouette score.

|rel:portion_of| [[specs/segmentation-spec]]
