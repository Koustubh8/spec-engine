---
title: Typed Directed Edges
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [orm, core, sqlalchemy, graph]
strength: SHALL
---

# Typed Directed Edges

The system SHALL implement a single `edges` SQLAlchemy table for directed, typed relationships between nodes.

Each edge SHALL have: `id` (int PK), `from_node_id` (FK → nodes.id, NOT NULL), `to_node_id` (FK → nodes.id, NOT NULL), `predicate` (string, NOT NULL — e.g. "exposes", "depends_on", "follows"), `properties` (JSON, nullable — for extra data like ternary predicate targets), `created_at` (datetime).

Cascade behavior: ON DELETE CASCADE from both FK sides — deleting a node removes all its edges.

The combined pair `(from_node_id, predicate, to_node_id)` SHALL be unique — no duplicate edges.

|rel:portion_of| [[specs/data-model-spec]]
|rel:reuses| [[concepts/Sqlite Schema Evolution]]
|rel:has_scenario| [[scenarios/traverse-edges-forward]]
|rel:touches| [[tools/models.py]]
