---
title: Source Traceability
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [audit, sync]
strength: SHOULD
---

# Source Traceability

The system SHOULD maintain a `sync_runs` table tracking every sync operation:

- `id` (int PK)
- `started_at` (datetime, NOT NULL)
- `completed_at` (datetime, nullable)
- `status` (string — "running", "completed", "failed")
- `nodes_created` (int, default 0)
- `nodes_updated` (int, default 0)
- `nodes_deleted` (int, default 0)
- `edges_created` (int, default 0)
- `edges_removed` (int, default 0)
- `error_message` (text, nullable)

This enables the dashboard to show a sync status panel: "Last synced 2m ago — 15 nodes, 23 edges"

Should NOT block the dashboard from loading if no sync has ever run — the dashboard degrades gracefully ("Not synced yet, trigger sync from settings").

|rel:portion_of| [[specs/data-model-spec]]
