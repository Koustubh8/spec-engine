# Production Readiness Linter

Guides for running and extending the production readiness checks against a spec graph. The linter runs 12 rules against the spec graph database and returns a score out of 12 with per-rule pass/fail details.

## The 12 Rules

| # | Rule | Severity | What it catches |
|---|------|----------|-----------------|
| P1 | LOGGING_SPECIFIED | WARNING | Exposed endpoint has no logging framework reference |
| P2 | ERROR_HANDLING_SPECIFIED | ERROR | `fails_with` conditions with no error handler spec |
| P3 | INPUT_VALIDATION_SPECIFIED | WARNING | `accepts` endpoints with no schema/Pydantic model |
| P4 | HEALTH_ENDPOINT_SPECIFIED | WARNING | No `/health` or `/readyz` endpoint exposed |
| P5 | CORS_CONFIGURED | WARNING | API spec with no CORS / allowed-origins reference |
| P6 | TIMEOUT_SPECIFIED | WARNING | Long-running operations with no timeout spec |
| P7 | RETRY_SPECIFIED | WARNING | External dependencies with no retry strategy |
| P8 | CONFIG_EXTERNALIZED | WARNING | No env-var / config-file reference in design nodes |
| P9 | MIGRATION_STRATEGY | WARNING | DB schema changes with no migration tool (Alembic) |
| P10 | ENVIRONMENTS_DEFINED | WARNING | Only 1 or 0 `deploys_to` targets (needs staging/prod) |
| P11 | MONITORING_SPECIFIED | WARNING | No monitoring/metrics reference (Prometheus/Grafana) |
| P12 | CI_CONFIGURED | WARNING | No CI pipeline reference (GitHub Actions, etc.) |

## Score Bands

| Score | Status | Meaning |
|-------|--------|---------|
| 12/12 | 🟢 Passed | Production ready |
| 10-11/12 | 🟡 Warning | Minor gaps, ship with tracking |
| 7-9/12 | 🟠 Warning | Needs work before production |
| 0-6/12 | 🔴 Failed | NOT production ready |

## Running the Linter

```bash
# CLI (direct)
cd ~/mywork/spec-studio/backend
python3 prod_lint.py

# API
curl http://127.0.0.1:8000/api/lint/prod | jq .

# Via React dashboard
# Open http://127.0.0.1:5173/ — Production Readiness card at top
```

## Rule Implementation Pattern

Each rule is a standalone function that takes a SQLAlchemy `Session` and returns `(bool, str | None)` — `(True, None)` if passed, `(False, "message")` if failed.

Rules query the `nodes` and `edges` tables for patterns that indicate production readiness:

```python
def rule_logging_specified(db: Session):
    logging_refs = db.query(Node).filter(
        Node.kind.in_(["concept", "tool", "reference"]),
        Node.slug.ilike("%log%")
    ).count()
    if logging_refs > 0:
        return True, None
    return False, "No logging framework reference found."
```

## Adding New Rules

The `RULES` list in `prod_lint.py` is an array of dicts:

```python
RULES = [
    {
        "name": "LOGGING_SPECIFIED",
        "severity": "warning",  # "error" or "warning"
        "check": rule_logging_specified,
        "description": "Every exposed endpoint has logging",
    },
    ...
]
```

Add a new dict entry + corresponding function. Rules are stateless — they receive a fresh DB session and return `(bool, str | None)`.

## CLI Output

```
  PRODUCTION READINESS: 5/12 🔴

  ERRORS (1):
    ❌ ERROR_HANDLING_SPECIFIED — 2 `fails_with` edges exist...

  WARNINGS (6):
    ⚠️  HEALTH_ENDPOINT_SPECIFIED — No health check endpoint...

  PASSING (5):
    ✅ LOGGING_SPECIFIED
    ✅ INPUT_VALIDATION_SPECIFIED
```

## API Response

```json
{
  "score": 5,
  "max_score": 12,
  "status": "failed",
  "rules": [
    {"name": "LOGGING_SPECIFIED", "passed": true, "severity": "warning", "description": "...", "message": null},
    {"name": "ERROR_HANDLING_SPECIFIED", "passed": false, "severity": "error", "description": "...", "message": "..."}
  ]
}
```

## Integrating into a Web App

1. Add `GET /api/lint/prod` route to FastAPI that calls `run_prod_lint(db)`
2. Dashboard component fetches on mount, renders a color-coded score card with score circle
3. Failing rules show message + suggestion; passing rules collapse to a summary count
