---
title: Sync Compatibility Fields
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [orm, sync]
strength: SHALL
---

# Sync Compatibility Fields

Every node in the `nodes` table SHALL track its origin in the markdown file system via:

- `source_file` (string, nullable) — relative path from KNOWLEDGE_PATH root (e.g. "specs/data-model-spec.md")
- `source_mtime` (float, nullable) — file modification timestamp (os.path.getmtime) at last sync

The `(source_file, source_mtime)` pair enables incremental sync: the sync engine SHALL skip files whose mtime matches the stored value, only re-parsing changed files.

When `source_file` is NULL, the node was created directly in the database (not synced from markdown). This supports dual-mode: future write-back path.

|rel:portion_of| [[specs/data-model-spec]]
