---
title: Schema On Read
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [data]
strength: SHALL
---

# Schema On Read

The system SHALL use schema-on-read for raw ingestion tables. Raw data SHALL be stored as JSON blobs with ingestion_ts. Materialized views SHALL extract known fields to typed columns for model consumption.

|rel:portion_of| [[specs/data-ingestion-spec]]
