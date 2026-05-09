---
title: Spec Studio Platform
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [platform, root, spec-graph]
---

# Spec Studio Platform

A web application to view, browse, and query the spec graph. FastAPI backend with SQLAlchemy ORM, React SPA frontend. Dual-mode: markdown files are source of truth, SQLAlchemy is the fast query/index layer with a sync bridge.

## Purpose

Provide a visual, queryable interface to the specification graph. Replace raw markdown file browsing with a structured dashboard — group by kind, filter, search, traverse relationships, and visualize the graph.

## Non-Goals

- Write/editing nodes from the UI (Phase 2)
- Real-time collaboration
- Authentication/authorization (local tool)
- NebulaGraph sync from the UI (separate tool)

## Sub-Specs

| Spec | Component | Purpose | Files |
|------|-----------|---------|-------|
| Data Model Spec | ORM Layer | SQLAlchemy Node + Edge tables | `backend/models.py` |
| Sync Engine Spec | Sync Script | Markdown → SQLAlchemy sync | `backend/sync.py` |
| API Layer Spec | FastAPI Backend | 7 REST endpoints on port 8000 | `backend/main.py` |
| Dashboard Spec | React Frontend | 3 SPA views on port 5173 | `frontend/src/*.jsx` |

## Running Services

```bash
# Backend (port 8000)
cd ~/mywork/spec-studio/backend && KNOWLEDGE_PATH=~/mywork/knowledge-graph uvicorn main:app

# Frontend (port 5173)
cd ~/mywork/spec-studio/frontend && npx vite --host 127.0.0.1
```

|rel:spec_of| [[tools/spec-studio]]
|rel:contains| [[specs/data-model-spec]]
|rel:contains| [[specs/sync-engine-spec]]
|rel:contains| [[specs/api-layer-spec]]
|rel:contains| [[specs/dashboard-spec]]
|rel:reuses| [[concepts/Spec Driven Workflow]]
|rel:reuses| [[concepts/Explore Before Spec]]
|rel:reuses| [[concepts/Agent Forgets Graph Updates]]
|rel:archived_from| [[changes/explore-spec-studio]]
|rel:contains| [[specs/prod-readiness-linter]]
|rel:reuses| [[concepts/explore-before-spec]]
