---
title: Streaming Ingestion
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [data]
strength: SHALL
---

# Streaming Ingestion

The system SHALL ingest streaming marketing data from Google Ads, Meta Ads, and conversion tracking APIs with sub-hour latency. Each event SHALL have an ingestion timestamp and raw JSON payload. Schema drift SHALL NOT break the pipeline — new fields append to JSON.

|rel:portion_of| [[specs/data-ingestion-spec]]
