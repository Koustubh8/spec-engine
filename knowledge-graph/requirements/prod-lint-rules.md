---
title: Production Lint Rules
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [lint, production]
strength: SHALL
---

# Production Lint Rules

The production linter SHALL implement 12 rules covering: logging, error handling, input validation, health endpoints, CORS, timeouts, retries, config externalization, DB migrations, environment separation, monitoring, and CI.

Each rule SHALL query the spec graph (via graph.py's Graph class) to check if the relevant edges or nodes exist. If not, the rule fires with a severity level and a human-readable message.

Rules SHALL be defined as a list of dicts with: name, severity ("error"|"warning"), check function, description.

|rel:portion_of| [[specs/prod-readiness-linter]]
|rel:touches| [[tools/prod-lint.py]]
