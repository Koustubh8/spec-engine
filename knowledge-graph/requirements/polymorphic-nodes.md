---
title: Polymorphic Node Table
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [orm, core, sqlalchemy]
strength: SHALL
---

# Polymorphic Node Table

The system SHALL implement a single `nodes` SQLAlchemy table with single-table inheritance using a `kind` discriminator column supporting all 12+ node kinds (spec, requirement, scenario, change, design, concept, task, tool, person, organization, reference, project).

Each node SHALL have: `id` (int PK), `slug` (unique string, kebab-case), `kind` (string discriminator), `title` (string), `body` (text, nullable), `metadata` (JSON, nullable for frontmatter fields beyond title/kind), `tags` (JSON array of strings), `created_at` (datetime), `updated_at` (datetime).

The ORM model SHALL support polymorphic loading — querying `Node` returns all nodes, filtering by `kind` returns only that type.

|rel:portion_of| [[specs/data-model-spec]]
|rel:guarantees| [[concepts/unified-node-query]]
|rel:has_scenario| [[scenarios/create-spec-node]]
|rel:constrained_by| [[concepts/sqlalchemy-metadata-reserved]]
|rel:touches| [[tools/models.py]]
