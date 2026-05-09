---
title: Create Spec Node and List All
kind: scenario
created: 2026-05-10
updated: 2026-05-10
tags: [happy-path, orm]
---

# Create Spec Node and List All

**GIVEN** an empty nodes table
**WHEN** I insert a node with kind="spec", slug="auth-spec", title="Auth Specification", body="# Auth"
**THEN** the nodes table has 1 row
**AND** querying `SELECT * FROM nodes WHERE kind='spec'` returns 1 row
**AND** the slug "auth-spec" uniquely identifies the node

|rel:scenario_for| [[requirements/polymorphic-nodes]]
