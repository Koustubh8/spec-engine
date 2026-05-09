---
title: Dashboard Spec
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [dashboard, streamlit, visualization]
---

# Dashboard Spec

Streamlit-based dashboard showing forecasts, actuals, and inventory recommendations.

## Views
1. **Overview** - Summary cards: forecast revenue next 4 weeks, top products, inventory alerts
2. **Demand Forecast** - Line chart: historical + forecast with confidence bands per product
3. **Revenue Projection** - Bar chart: weekly revenue forecast with cumulative
4. **Inventory Planner** - Table: product, predicted units, wax needed, current stock, restock by date
5. **Model Health** - MAPE tracker, forecast vs actual comparison, data age indicator

## Bootstrap Notice
- Banner showing weeks of real data collected vs estimate-based
- Transitions to "Data-driven forecast" once 8+ weeks accumulated

|rel:portion_of| [[specs/candle-forecast-platform]]
|rel:depends_on| [[specs/forecasting-spec]]
