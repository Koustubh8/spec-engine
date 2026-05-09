---
title: Dashboard Overview View
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [ui, react, dashboard]
strength: SHALL
---

# Dashboard Overview View

The homepage `/` SHALL display summary statistics fetched from `GET /api/stats`:

- Total node count with sparkline by kind
- Total edge count with breakdown by top predicates
- Sync status indicator with "Last synced X ago" and status color (green/red/gray)
- Quick-action cards to jump to "Browse Specs", "Browse Requirements", "Browse Concepts"
- Recent activity — last 5 synced/created nodes with timestamps

The layout SHALL follow the Dashboard As Triage pattern: overview first, then drill into detail.

|rel:portion_of| [[specs/dashboard-spec]]
