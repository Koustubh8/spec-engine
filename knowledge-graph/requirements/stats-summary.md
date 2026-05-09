---
title: Stats Summary Endpoint
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [api, dashboard]
strength: SHALL
---

# Stats Summary Endpoint

The API SHALL expose `GET /api/stats` returning counts for the dashboard:

- `total_nodes` — total count across all kinds
- `total_edges` — total count across all predicates
- `by_kind` — dict of `{"kind_name": count}` for all node kinds
- `top_predicates` — top 10 most-used predicates with counts
- `by_tag` — dict of `{"tag_name": count}` for the most common tags (top 20)
- `last_sync` — most recent sync_run summary or null

This endpoint SHALL be fast (sub-100ms) — implement via aggregate SQL queries, not by loading all rows.

|rel:portion_of| [[specs/api-layer-spec]]
|rel:touches| [[tools/main.py]]
