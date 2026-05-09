---
title: Data Ingestion Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [data, streaming, batch, marketing]
---

# Data Ingestion Specification

Streaming and batch ingestion pipeline for marketing analytics data. Handles ad platform APIs (Google Ads, Meta, LinkedIn), CRM data, and conversion tracking. Schema-on-read with JSON raw tables.

## Data Sources

| Source | Type | Latency | Fields |
|--------|------|---------|--------|
| Google Ads | Streaming API | ~15min | campaign_id, spend, impressions, clicks, conversions |
| Meta Ads | Streaming API | ~15min | campaign_id, spend, reach, frequency, conversions |
| LinkedIn Ads | Batch API | ~1hr | campaign_id, spend, impressions, clicks |
| CRM | Batch (daily) | ~24hr | customer_id, signup_date, plan, region |
| Conversion Tracking | Streaming | ~1hr | event_id, customer_id, campaign_id, revenue, timestamp |
| Google Analytics | Streaming API | ~30min | session_id, source, medium, pages, events |

## Architecture

- Raw tables: JSON columns, schema-on-read, timestamped with ingestion_ts
- Materialized views: hourly/daily aggregations for model-ready data
- Data freshness monitoring per source with alerting on staleness > 2x expected latency
- Schema drift: new fields get appended to JSON; known fields are extracted to typed columns quarterly

|rel:spec_of| [[tools/ingestion-pipeline]]
|rel:exposes| [[concepts/post-spend-event]]
|rel:exposes| [[concepts/post-conversion-event]]
|rel:exposes| [[concepts/post-customer-event]]
|rel:contains| [[requirements/streaming-ingestion]]
|rel:contains| [[requirements/batch-ingestion]]
|rel:contains| [[requirements/data-freshness-monitoring]]
|rel:contains| [[requirements/schema-on-read]]
