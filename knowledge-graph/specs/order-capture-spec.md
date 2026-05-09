---
title: Order Capture Spec
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [candle, data-collection, cli]
---

# Order Capture Spec

A lightweight CLI tool to record each candle order as it arrives via DM. This is the data foundation for all forecasting.

## Requirements
- Record: date, product name, quantity, unit price, customer name, expected delivery date, payment status, shipped date
- Products catalog: name, category, unit price, raw material composition
- Quick entry: tab-complete product names, default today's date
- Export: CSV export for the data pipeline
- Bootstrapping: ability to backfill recent orders from memory

## Workflow
1. User receives DM -> opens CLI -> enters order
2. Customer confirms payment -> user marks payment_confirmed=true
3. User ships -> records shipped_date
4. Weekly: export CSV -> feed into data pipeline

|rel:portion_of| [[specs/candle-forecast-platform]]
|rel:depends_on| [[concepts/products-catalog]]
