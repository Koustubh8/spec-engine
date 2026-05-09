---
title: Graph Path Finding Endpoint
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [api, endpoint, graph]
---

# POST /api/query/path

Finds the shortest path between two nodes in the graph. Uses BFS. Returns the chain of nodes and edges connecting them.

Request: `{"from": "spec-studio-platform", "to": "polymorphic-nodes"}`

Response: `{"found": true, "path": [{"node": ..., "edge": ...}, ...], "hops": 2}`

Returns `{"found": false}` if no path exists within configurable max depth (default 10).

|rel:exposed_by| [[specs/api-layer-spec]]
|rel:accepts| [[concepts/path-request]]
|rel:returns| [[concepts/path-response]]
