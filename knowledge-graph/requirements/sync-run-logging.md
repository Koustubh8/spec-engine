---
title: Sync Run Logging
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [sync, audit]
strength: SHOULD
---

# Sync Run Logging

The sync engine SHOULD record each sync operation in the `sync_runs` table with:

- `started_at` and `completed_at` timestamps
- `status`: "completed" or "failed"
- Counts: `nodes_created`, `nodes_updated`, `nodes_deleted`, `edges_created`, `edges_removed`
- `error_message` if failed
- `warnings_count` and `errors_count` for parsing issues

The most recent sync_run SHALL be queryable from the dashboard API for the "Last synced" status indicator.

|rel:portion_of| [[specs/sync-engine-spec]]
