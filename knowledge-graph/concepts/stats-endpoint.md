---
title: GET /api/stats — Dashboard Stats
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [api, endpoint]
---

# GET /api/stats — Dashboard Stats

Returns summary statistics for the dashboard overview. Fast — no pagination, no heavy queries.

Response:
```json
{
  "total_nodes": 87,
  "total_edges": 330,
  "by_kind": {"spec": 5, "requirement": 9, "concept": 20, ...},
  "top_predicates": [{"predicate": "contains", "count": 8}, ...],
  "last_sync": {"status": "completed", "ago": "2m ago"},
  "recent_changes": 3
}
```

|rel:exposed_by| [[specs/api-layer-spec]]
|rel:returns| [[concepts/stats-response]]
