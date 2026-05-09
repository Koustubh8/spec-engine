---
title: Sync Only Changed Files
kind: scenario
created: 2026-05-10
updated: 2026-05-10
tags: [happy-path, sync]
---

# Sync Only Changed Files

**GIVEN** a synced database with node for "auth-spec.md" (source_mtime = t1)
**WHEN** I run sync with force=False
**AND** auth-spec.md's mtime has NOT changed (still t1)
**THEN** the sync engine skips auth-spec.md
**AND** no UPDATE is performed on that node
**WHEN** I modify auth-spec.md (mtime advances to t2)
**AND** run sync with force=False
**THEN** the sync engine RE-PARSES auth-spec.md
**AND** the node's title/body in the DB reflects the new content
**AND** source_mtime is updated to t2

|rel:scenario_for| [[requirements/incremental-sync]]
