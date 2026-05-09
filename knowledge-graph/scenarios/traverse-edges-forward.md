---
title: Traverse Edges Forward
kind: scenario
created: 2026-05-10
updated: 2026-05-10
tags: [happy-path, graph]
---

# Traverse Edges Forward

**GIVEN** a spec node S with slug "auth-spec"
**AND** requirement node R with slug "user-auth"
**AND** an edge (S → R) with predicate "contains"
**WHEN** I query `SELECT to_node_id FROM edges WHERE from_node_id = S.id AND predicate = 'contains'`
**THEN** the result includes R.id
**AND** the `idx_edges_from_predicate` index is used (verify via EXPLAIN QUERY PLAN)

|rel:scenario_for| [[requirements/typed-directed-edges]]
