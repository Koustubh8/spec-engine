---
title: Sync Control Panel
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [ui, sync]
strength: SHOULD
---

# Sync Control Panel

The dashboard SHOULD include a sync control panel (visible on the overview page or as a sidebar widget):

- "Sync Now" button that calls `POST /api/sync`
- Last sync status with timestamp and summary counts
- Warning/error count badge if the last sync had issues
- Optional: "Force Full Re-sync" checkbox in the sync trigger
- Loading state while sync is running (disable button, show spinner)
- Success toast on completion showing "Synced: +15 / ~0 / -0 nodes"

|rel:portion_of| [[specs/dashboard-spec]]
