---
title: Candle Forecast Reuses
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [reuse, platform-modules]
---

# Candle Forecast Reuses

This project leverages the following reusable platform modules:
- Data Pipeline Orchestrator (template for order->timeseries ETL)
- State Machine Engine (order status: received -> confirmed -> shipped)
- Reporting & Export Framework (dashboard views + CSV export)
- Notification Hub (future: alert when forecast drift exceeds threshold)
- Config Management (product catalog as config, env vars for paths)

|rel:reuses| [[concepts/data-pipeline-orchestrator]]
|rel:reuses| [[concepts/state-machine-engine]]
|rel:reuses| [[concepts/reporting-export-framework]]
|rel:reuses| [[concepts/config-management]]
