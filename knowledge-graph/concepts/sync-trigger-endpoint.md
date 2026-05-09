---
title: POST /api/sync — Trigger Sync
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [api, endpoint, sync]
---

# POST /api/sync — Trigger Sync

Triggers a markdown → database sync. Optional force flag for full re-sync.

Request: `{"force": false}`

Response: `{"status": "completed", "summary": {"nodes_created": 15, "nodes_updated": 0, "nodes_deleted": 0, "edges_created": 23, "edges_removed": 0, "warnings": 0, "errors": 0, "duration_ms": 342}}`

Returns immediately after sync completes (sync is synchronous). For large graphs (>1000 files), consider async with polling.

|rel:exposed_by| [[specs/api-layer-spec]]
|rel:accepts| [[concepts/sync-request]]
|rel:returns| [[concepts/sync-response]]
