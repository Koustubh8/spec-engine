---
title: List Nodes via API
kind: scenario
created: 2026-05-10
updated: 2026-05-10
tags: [happy-path, api]
---

# List Nodes via API

**GIVEN** a running FastAPI server with 87 nodes in the database
**WHEN** I send `GET /api/nodes?kind=spec&page=1&page_size=10`
**THEN** I receive HTTP 200
**AND** the response body has shape `{"data": [...], "meta": {"total": N, "page": 1, "page_size": 10}}`
**AND** each item in `data` has fields: id, slug, kind, title, body_preview, tags, created_at
**AND** `meta.total` equals the count of spec-kind nodes
**AND** `data` has at most 10 items

|rel:scenario_for| [[requirements/restful-endpoints]]
