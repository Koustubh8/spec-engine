---
title: Streaming Data Velocity and Drift
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [constraint, streaming, data]
---

# Streaming Data Velocity and Drift

Marketing data arrives at variable velocity: ad platform APIs are near-real-time, CRM data is daily batch, and conversion tracking has 24-72 hour attribution windows.

Constraints:
- Late-arriving data (conversions attributed days after click) means real-time dashboards are always provisional
- Schema drift: ad platforms add/rename fields without notice. The ingestion layer must survive field changes without crashing
- Data quality: ad platform APIs have deduplication gaps, dedup keys change, and spend/revenue reconciliation never quite balances
- Rate limits: Google Ads / Meta APIs throttle at different rates; the system must retry with exponential backoff
- Regulatory: cookie deprecation, consent mode, and data retention policies mean data availability changes over time

**Mitigation**: Schema-on-read with JSON-typed raw tables. Separate ingestion (raw) from transformation (model-ready). Monitor data freshness per source with alerting on staleness.
|rel:constrains| [[concepts/streaming-data-ingestion]]
