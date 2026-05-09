---
title: Production Lint API Endpoint
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [api, lint]
strength: SHALL
---

# Production Lint API Endpoint

The spec-studio API SHALL expose `GET /api/lint/prod` that runs the production readiness linter against the currently synced database.

Response format:
```json
{
  "score": 8,
  "max_score": 12,
  "status": "warning",
  "rules": [
    {"name": "LOGGING_SPECIFIED", "passed": false, "severity": "warning", "message": "...", "suggestion": "..."},
    {"name": "ERROR_HANDLING_SPECIFIED", "passed": true, "severity": "error"}
  ]
}
```

Status field: "passed" (all passing), "warning" (some warnings), "failed" (any errors).

|rel:portion_of| [[specs/prod-readiness-linter]]
|rel:touches| [[tools/main.py]]
