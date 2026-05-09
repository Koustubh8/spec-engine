---
title: Graph Traversal Endpoint
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [api, endpoint, graph]
---

# POST /api/query/traverse

BFS/DFS traversal starting from a seed node. Returns all nodes reachable within N hops, optionally filtered by predicate type.

Request: `{"seed": "spec-studio-platform", "depth": 3, "predicates": ["contains", "spec_of"], "direction": "forward"}`

Response: `{"nodes": [...], "edges": [...], "paths": {"seed → ...": N}}`

Supports `direction: "forward"` (outgoing edges), `"reverse"` (incoming), or `"both"`.

|rel:exposed_by| [[specs/api-layer-spec]]
|rel:accepts| [[concepts/traverse-request]]
|rel:returns| [[concepts/subgraph-response]]
