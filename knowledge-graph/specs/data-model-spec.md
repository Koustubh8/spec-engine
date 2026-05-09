---
title: Data Model Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [orm, sqlalchemy, core, data-model]
---

# Data Model Specification

SQLAlchemy ORM models for the spec graph. A single polymorphic `Node` table for all graph entities and a single `Edge` table for typed, directed relationships. Supports dual-mode: markdown files as source of truth, SQLAlchemy as fast query layer.

## Design Decisions

### Single Table Inheritance (Node) + Separate Edge Table

Two tables, not a graph database. Rationale:

- Single `nodes` table with `kind` discriminator keeps polymorphic queries simple (one query for "all nodes", one filter for "only specs")
- Single `edges` table makes graph traversal queries (`WITH RECURSIVE` CTE) straightforward in SQLite/PostgreSQL
- Avoids N join tables (one per predicate type) — 17+ predicates would mean 17+ join tables
- `properties` JSON column on both tables for extensibility
- Indexes: `(kind)` on nodes, `(from_node_id, predicate)` and `(to_node_id, predicate)` on edges for fast traversal in both directions

### Node Kinds

| Kind | Description | Required Fields | Optional Fields |
|------|-------------|-----------------|-----------------|
| `spec` | Behavior contract | title, body | tags |
| `requirement` | SHALL/MUST/SHOULD | title, body, strength | tags |
| `scenario` | Given-When-Then | title, body | tags |
| `change` | Proposed delta | title, body, status | tags |
| `design` | Technical approach | title, body | tags |
| `concept` | Domain concept | title, body | tags |
| `task` | Implementation step | title, body | tags |
| `tool` | Technology/tool | title | tags |
| `person` | Person/role | title | tags |
| `organization` | Organization | title | tags |
| `reference` | External source | title | tags |
| `project` | Project | title | tags |

### Actual Columns (from implementation)

`nodes` table: `id`, `slug`, `kind`, `title`, `body`, `meta_json` (JSON string), `tags` (JSON string), `strength`, `status`, `source_file`, `source_mtime`, `created_at`, `updated_at`

`edges` table: `id`, `from_node_id` (FK→nodes), `to_node_id` (FK→nodes), `predicate`, `properties` (JSON string), `created_at`. Unique constraint on `(from_node_id, predicate, to_node_id)`.

`sync_runs` table: `id`, `started_at`, `completed_at`, `status`, `nodes_created`, `nodes_updated`, `nodes_deleted`, `edges_created`, `edges_removed`, `warnings_count`, `errors_count`, `error_message`.

17 spec predicates + 12 universal predicates (defined in SCHEMA.md). Stored as string in the `predicate` column. No enumeration constraint — allows adding predicates without migrations.

### Sync Compatibility

Every node tracks `source_file` (path relative to KNOWLEDGE_PATH) and `source_mtime` (mtime of markdown file at last sync). This enables incremental sync: only re-parse files whose mtime changed.

|rel:spec_of| [[tools/orm-layer]]
|rel:conforms_to| [[references/SCHEMA]]
|rel:reuses| [[concepts/Fastapi Sqlite Crud]]
|rel:reuses| [[concepts/Sqlite Schema Evolution]]
|rel:contains| [[requirements/polymorphic-nodes]]
|rel:contains| [[requirements/typed-directed-edges]]
|rel:contains| [[requirements/metadata-storage]]
|rel:contains| [[requirements/graph-traversal-indexes]]
|rel:contains| [[requirements/sync-compatibility]]
|rel:contains| [[requirements/source-traceability]]
