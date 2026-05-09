---
title: API Layer Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [api, fastapi, backend]
---

# API Layer Specification

FastAPI backend exposing REST endpoints for the React SPA to browse, filter, query, and sync the spec graph.

## Design Decisions

### URL Structure
- `/api/nodes` — node CRUD + list
- `/api/edges` — edge list + filter
- `/api/query/traverse` — graph traversal (seed + depth)
- `/api/query/path` — path finding (from → to)
- `/api/sync` — trigger markdown sync
- `/api/stats` — dashboard overview counts

### Response Format
All responses use a consistent envelope:
```json
{"data": ..., "meta": {"total": N, "page": 1, "page_size": 50}}
```

### Filtering
- `?kind=spec,requirement` — filter by node kind(s)
- `?predicate=exposes` — filter edges by predicate
- `?search=token` — full-text search on title + body
- `?tag=security` — filter by tag
- `?page=1&page_size=50` — pagination

|rel:spec_of| [[tools/fastapi-backend]]
|rel:reuses| [[concepts/Fastapi Sqlite Crud]]
|rel:deploys_to| [[concepts/localhost-dev-server]]
|rel:exposes| [[concepts/get-nodes-endpoint]]
|rel:exposes| [[concepts/get-node-detail-endpoint]]
|rel:exposes| [[concepts/get-edges-endpoint]]
|rel:exposes| [[concepts/graph-traversal-endpoint]]
|rel:exposes| [[concepts/graph-path-endpoint]]
|rel:exposes| [[concepts/sync-trigger-endpoint]]
|rel:exposes| [[concepts/stats-endpoint]]
|rel:contains| [[requirements/restful-endpoints]]
|rel:contains| [[requirements/pagination-and-filtering]]
|rel:contains| [[requirements/graph-traversal-api]]
|rel:contains| [[requirements/sync-trigger]]
|rel:contains| [[requirements/stats-summary]]
