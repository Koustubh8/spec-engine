---
title: Data Pipeline Spec
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [pipeline, etl, time-series]
---

# Data Pipeline Spec

Transforms raw order records into time-series data suitable for forecasting models.

## Requirements
- Weekly aggregation: orders -> daily sales per product (units, revenue)
- Handle missing data: if no orders on a day, fill with zero
- Product catalog enrichment: join raw_material_cost, wax_per_unit, etc.
- Forecast input generation: pivot to (ds, y) format for Prophet
- Inventory calculation: predicted_units x materials_per_unit
- Incremental: only process new records since last run

## Flow
1. Read orders.csv (from capture tool)
2. Aggregate: GROUP BY date, product_id -> SUM(qty), SUM(revenue)
3. Fill date gaps with zeros
4. Join product catalog for material ratios
5. Write to forecast_inputs/ as CSV

|rel:portion_of| [[specs/candle-forecast-platform]]
|rel:depends_on| [[specs/order-capture-spec]]
