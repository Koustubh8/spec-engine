---
title: Sync Trigger Endpoint
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [api, sync]
strength: SHALL
---

# Sync Trigger Endpoint

The API SHALL expose `POST /api/sync` to trigger markdown → database sync on demand.

Request: `{"force": false}` — when false (default), only changed files are re-parsed (incremental). When true, all files are re-parsed.

Response: returns immediately with sync summary including counts of created/updated/deleted nodes and edges.

Sync SHALL be synchronous (the response waits for completion). If the sync takes > 30 seconds, the response SHALL still return once complete.

|rel:portion_of| [[specs/api-layer-spec]]
|rel:touches| [[tools/main.py]]
|rel:touches| [[tools/sync.py]]
