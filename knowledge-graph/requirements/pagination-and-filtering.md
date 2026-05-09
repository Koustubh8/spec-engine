---
title: Pagination and Filtering
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [api, performance]
strength: SHALL
---

# Pagination and Filtering

List endpoints SHALL support offset-based pagination via `?page=1&page_size=50` query parameters. Page_size SHALL default to 50, maximum 200.

Filtering SHALL support:

- `?kind=spec,requirement` — comma-separated kind filter
- `?search=token` — SQL LIKE or full-text search across title and body
- `?tag=security` — filter by tag (exact match on JSON array)
- `?predicate=exposes` — filter edges by predicate

Responses SHALL include a `meta` block with `total`, `page`, `page_size`. For large result sets, the frontend SHALL show pagination controls.

|rel:portion_of| [[specs/api-layer-spec]]
