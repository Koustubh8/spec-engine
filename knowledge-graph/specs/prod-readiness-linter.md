---
title: Production Readiness Linter
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [lint, production, quality, devops]
---

# Production Readiness Linter

Extends the existing `spec-lint.py` (14 spec-graph rules) with 12 additional rules that catch production-readiness gaps. Runs against the spec graph to flag missing contracts, configurations, and operational concerns before code is written.

## Design

A standalone Python script (`prod-lint.py`) that reads the knowledge graph via `graph.py` and runs production-readiness checks. Can also be invoked via `POST /api/lint/prod` in the spec-studio API.

## Production Readiness Rules

| # | Rule | Severity | What it catches |
|---|------|----------|-----------------|
| P1 | LOGGING_SPECIFIED | WARNING | Exposed endpoint has no logging edge |
| P2 | ERROR_HANDLING_SPECIFIED | ERROR | `fails_with` condition has no corresponding error handler node |
| P3 | INPUT_VALIDATION_SPECIFIED | WARNING | `accepts` endpoint has no Pydantic/explicit schema in spec |
| P4 | HEALTH_ENDPOINT_SPECIFIED | WARNING | No `GET /health` or `GET /readyz` endpoint exposed |
| P5 | CORS_CONFIGURED | WARNING | API spec has no `cors` or `allowed_origins` reference |
| P6 | TIMEOUT_SPECIFIED | WARNING | Long-running operation has no timeout spec |
| P7 | RETRY_SPECIFIED | WARNING | External service call has no retry strategy |
| P8 | CONFIG_EXTERNALIZED | WARNING | No `env_var` or `config` reference in design nodes |
| P9 | MIGRATION_STRATEGY | WARNING | DB-change spec has no migration tool (Alembic) reference |
| P10 | ENVIRONMENTS_DEFINED | WARNING | Spec has no `deploys_to` for staging/prod |
| P11 | MONITORING_SPECIFIED | WARNING | Service has no metrics/monitoring reference |
| P12 | CI_CONFIGURED | WARNING | Project has no CI config file or CI reference |

## Scoring

Each passing rule = 1 point. Total /12 = readiness score.

- 12/12 — Production ready
- 10-11/12 — Minor gaps
- 7-9/12 — Needs work before production
- 0-6/12 — Not production ready, DO NOT DEPLOY

## Integration with Spec Studio

The linter results display in the dashboard:

```
Production Readiness: 8/12 ⚠️
  ✅ ERROR_HANDLING_SPECIFIED
  ✅ HEALTH_ENDPOINT_SPECIFIED
  ✅ CORS_CONFIGURED
  ❌ LOGGING_SPECIFIED — Add logging to POST /api/sync
  ❌ TIMEOUT_SPECIFIED — 30s timeout needed for /api/sync
  ❌ RETRY_SPECIFIED — Sync engine calls external FS
  ❌ CONFIG_EXTERNALIZED — KNOWLEDGE_PATH is env var ✅
  ❌ MIGRATION_STRATEGY — No Alembic for schema changes
  ...
```

## Scoring

Each passing rule yields 1 point. Total /12 = readiness score.

Score bands:
- 12/12 (🟢) — Production ready
- 10-11/12 (🟡) — Minor gaps, ship with tracking
- 7-9/12 (🟠) — Needs work before production
- 0-6/12 (🔴) — Not production ready, DO NOT DEPLOY

|rel:spec_of| [[tools/prod-lint-script]]
|rel:reuses| [[concepts/Explore Before Spec]]
|rel:reuses| [[concepts/Spec Driven Workflow]]
|rel:contains| [[requirements/prod-lint-rules]]
|rel:contains| [[requirements/prod-lint-api-endpoint]]
|rel:contains| [[requirements/prod-lint-dashboard-view]]
