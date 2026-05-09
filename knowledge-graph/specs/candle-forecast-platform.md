---
title: Candle Forecast Platform
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [candle, forecasting, analytics]
---

# Candle Forecast Platform

Demand, revenue, and inventory forecasting for a DM-based candle business. Follows CRISP-DM methodology from zero data to production forecasts.

## Purpose
Predict future demand per product, project revenue, and recommend inventory restock timing. Bootstrap on business knowledge until 8+ weeks of real order data accumulate, then transition to data-driven models.

## Sub-Specs
- Order Capture Spec — instrument the DM order workflow
- Data Pipeline Spec — transform raw orders into time series
- Forecasting Spec — Prophet models for demand/revenue/inventory
- Dashboard Spec — Streamlit visualization

## Non-Goals
- Not replacing the CRM (CRM manages relationships; forecast is pure analytics)
- Not an e-commerce storefront
- Not real-time (weekly forecasts are sufficient)

|rel:spec_of| [[projects/candle-forecast-app]]
|rel:contains| [[specs/order-capture-spec]]
|rel:contains| [[specs/data-pipeline-spec]]
|rel:contains| [[specs/forecasting-spec]]
|rel:contains| [[specs/dashboard-spec]]
|rel:deploys_to| [[concepts/local-machine]]
