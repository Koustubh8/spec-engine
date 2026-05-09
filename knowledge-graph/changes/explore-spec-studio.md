---
title: Explore Spec Studio
kind: changes
created: 2026-05-10
updated: 2026-05-10
tags: [exploration, web-app, spec-graph, react, implemented]
status: completed
---

# Explore Spec Studio

## Raw Requirement
A web application to view, browse, and query the spec graph (markdown files with typed nodes and edges). FastAPI backend, SPA frontend, SQLAlchemy as the fast query/index layer. Markdown files remain the source of truth — SQLAlchemy is synced.

## Tech Stack (Implemented)
- **Backend**: FastAPI (uvicorn) on port 8000
- **Frontend**: React (Vite) on port 5173, react-router-dom for routing, react-markdown for rendering
- **ORM**: SQLAlchemy 2.0 (single-table inheritance for nodes, separate edges table)
- **Database**: SQLite with WAL mode + foreign keys
- **Sync**: Python script parsing YAML frontmatter + |rel:| edge syntax

## Build Learnings

### L1: `metadata` is reserved in SQLAlchemy Declarative
The column name `metadata` conflicts with `Base.metadata`. Fixed by renaming to `meta_json` with explicit column name.

### L2: SQLite edge flush race
`db.delete()` + `db.flush()` followed by `db.add()` + `db.flush()` within the same SQLite transaction didn't reliably commit the DELETE before the INSERT. Fixed using `db.execute(sa_text("DELETE ..."))` (bulk SQL) instead of ORM delete.

### L3: Edge deduplication needed
A single markdown file can have duplicate `|rel:|` lines. `parse_edges()` now deduplicates via a `seen` set before returning.

### L4: Python 3.9 doesn't support `Node | None`
PEP 604 union syntax (`int | None`, `Node | None`) requires Python 3.10+. Scrub all return type annotations using `|` union syntax.

### L5: Frontmatter `kind:` may use plural forms
Files can have `kind: concepts` (plural) in frontmatter while the directory maps to `concept` (singular). Sync now normalizes via `KIND_NORMALIZE` dict before upsert.

### L6: Edge `to_dict()` must include slugs/titles
The node detail endpoint returns edges. Using `to_dict()` (only IDs) broke the frontend edge sections. Fixed by using `to_dict_with_nodes()` which includes `from_slug`, `from_title`, `to_slug`, `to_title`.

### L7: Pagination filter resets bug
`setFilter` always reset `page=1`, even when the key WAS `page`. Fixed by guarding: `if (key !== 'page') next.set('page', '1')`.

|rel:change_for| [[specs/spec-studio-platform]]

## User Answers Ingested

### Q1: Domain?
Content/Knowledge — tools that manage and query spec graphs.

### Q2: Core idea?
A web tool to generate/manage spec graphs. The universal specification engine ambition.

### Q3: Frontend?
FastAPI backend + SPA frontend (React/Vue/Svelte).

### Q4: MVP feature?
Dashboard to view/query existing graph nodes.

### Q5: Data model?
Dual: markdown source of truth, SQLAlchemy for fast queries. Sync script bridges them.

|rel:change_for| [[specs/spec-studio-platform]]
|rel:adds| [[concepts/graph-sync-engine]]
|rel:adds| [[concepts/view-query-dashboard]]
|rel:adds| [[concepts/typed-node-schema]]
|rel:adds| [[concepts/predicate-edge-schema]]
|rel:adds| [[concepts/spa-frontend]]
|rel:adds| [[concepts/api-layer]]
|rel:adds| [[concepts/spec-graph-visualization]]
|rel:adds| [[concepts/query-engine]]
|rel:archives_to| [[specs/spec-studio-platform]]
|rel:adds| [[concepts/sqlalchemy-metadata-reserved]]
|rel:adds| [[concepts/sqlite-flush-orm-delete-insert]]
