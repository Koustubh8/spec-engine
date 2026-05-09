---
title: Graph Traversal Indexes
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [orm, performance, sqlalchemy]
strength: SHALL
---

# Graph Traversal Indexes

The system SHALL create database indexes specifically designed for bidirectional graph traversal:

- `idx_edges_from_predicate` on `edges(from_node_id, predicate)` — forward traversal: "find all nodes this node connects to via predicate P"
- `idx_edges_to_predicate` on `edges(to_node_id, predicate)` — reverse traversal: "find all nodes that connect TO this node via predicate P"
- `idx_nodes_kind` on `nodes(kind)` — fast kind-based filtering
- `idx_nodes_slug` on `nodes(slug)` — unique lookup by slug
- `idx_nodes_tags` — GIN index on `tags` JSON column (PostgreSQL) or functional index (SQLite)

These indexes SHALL be defined alongside the table definitions via SQLAlchemy `Index()` constructs, not raw SQL migrations.

|rel:portion_of| [[specs/data-model-spec]]
|rel:guarantees| [[concepts/sub-second-graph-traversal]]
|rel:touches| [[tools/models.py]]
