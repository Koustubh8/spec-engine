---
title: Edge Reconciliation
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [sync, edges]
strength: SHALL
---

# Edge Reconciliation

For each synced node, the sync engine SHALL fully replace its outgoing edges:

1. Parse all `|rel:PREDICATE| [[KIND/SLUG]]` lines from the file body
2. Resolve each `KIND/SLUG` to a destination node ID (create placeholder if missing)
3. DELETE all existing edges where `from_node_id` matches this node
4. INSERT all currently-parsed edges

This replace-strategy guarantees the database always reflects the markdown file exactly. No stale edge can survive an edit that removes a line.

|rel:portion_of| [[specs/sync-engine-spec]]
|rel:constrained_by| [[concepts/sqlite-flush-orm-delete-insert]]
|rel:touches| [[tools/sync.py]]
