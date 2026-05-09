---
title: Data Freshness Monitoring
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [data]
strength: SHALL
---

# Data Freshness Monitoring

The system SHOULD monitor data freshness per source. If a source exceeds 2x its expected latency, an alert SHALL fire. Dashboard SHALL show last-updated timestamp per source.

|rel:portion_of| [[specs/data-ingestion-spec]]
