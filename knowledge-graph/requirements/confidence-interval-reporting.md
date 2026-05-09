---
title: Confidence Interval Reporting
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [uplift]
strength: SHALL
---

# Confidence Interval Reporting

Every uplift estimate SHALL include confidence intervals. When intervals cross zero (no detectable effect), the system SHALL explicitly report 'no significant lift detected' rather than a point estimate.

|rel:portion_of| [[specs/uplift-spec]]
