---
title: Forecasting Spec
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [forecasting, prophet, time-series]
---

# Forecasting Spec

Time-series forecasting for demand, revenue, and inventory using Prophet.

## CRISP-DM Phases
- Business Understanding: scope defined
- Data Understanding: Bootstrap with business knowledge
- Data Preparation: pipeline transforms orders to time series
- Modeling: Prophet with yearly/weekly seasonality
- Evaluation: MAPE, track forecast vs actual drift
- Deployment: Streamlit dashboard with refresh button

## Models
1. Demand Forecast - units per product per week (4-8 week horizon)
2. Revenue Forecast - demand x average unit price (with trend)
3. Inventory Forecast - demand x materials_per_unit to restock recommendations

## Bootstrap Mode (first 8 weeks)
- User provides: expected orders/week per product, peak seasons, growth rate
- Prophet generates initial forecast from synthetic weekly averages
- As real data accumulates, each run uses more real vs synthetic

## Live Mode (8+ weeks)
- Pure data-driven Prophet on actual history
- Weekly retrain
- Track: MAPE, forecast drift, anomaly alerts

## Confidence Intervals
- 80% and 95% prediction intervals
- Anomaly: actual > 2x forecast upper bound triggers alert

|rel:portion_of| [[specs/candle-forecast-platform]]
|rel:depends_on| [[specs/data-pipeline-spec]]
