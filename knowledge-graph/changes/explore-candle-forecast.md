---
title: Explore Candle Forecast
kind: change
created: 2026-05-10
updated: 2026-05-10
tags: [candle, forecasting, crisp-dm]
status: proposed
---

# Explore Candle Forecast

## Intent
Build a full-suite forecasting application for a candle business following CRISP-DM: demand prediction (units per product), revenue projection, and inventory restock recommendations.

## Context
- Zero structured data captured today
- Orders come via Instagram DM (product name + quantity + expected delivery date)
- Payment via UPI screenshot confirmation
- Ship via Dunzo/Porter
- ~20-50 orders/day, 10+ catalog items

## Sub-Problems
1. Order data capture (instrument the DM-to-ship workflow)
2. Data pipeline (aggregate raw orders → time series)
3. Forecasting models (demand, revenue, inventory)
4. Dashboard & reporting

|rel:change_for| [[specs/candle-forecast-platform]]
|rel:adds| [[concepts/order-capture-workflow]]
|rel:adds| [[concepts/forecast-data-pipeline]]
|rel:adds| [[concepts/forecast-time-series-models]]
|rel:adds| [[concepts/forecast-dashboard]]
