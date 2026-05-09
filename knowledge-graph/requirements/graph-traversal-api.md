---
title: Graph Traversal API
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [api, graph]
strength: SHALL
---

# Graph Traversal API

The API SHALL implement BFS-based graph traversal as an endpoint:

Request: `POST /api/query/traverse`
Body: `{"seed": "node-slug", "depth": 3, "predicates": ["contains"], "direction": "forward"}`

Direction options:
- `"forward"` — follow outgoing edges from seed
- `"reverse"` — follow incoming edges to seed
- `"both"` — both directions

The response SHALL return all nodes and edges discovered, plus a path summary showing how many hops each leaf is from the seed.

Graph traversal SHALL be implemented as iterative SQLAlchemy queries (batch-fetch neighbors per hop), NOT recursion, to avoid Python stack limits. Max depth SHALL be 10.

|rel:portion_of| [[specs/api-layer-spec]]
|rel:touches| [[tools/main.py]]
