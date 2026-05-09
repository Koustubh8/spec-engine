---
title: Incremental Sync
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [sync, performance]
strength: SHALL
---

# Incremental Sync

The sync engine SHALL support incremental sync by comparing file modification timestamps. Files whose `mtime` matches the stored `source_mtime` in the `nodes` table SHALL be skipped entirely.

A full re-sync (`force=True`) SHALL re-parse all files regardless of mtime.

On first sync (empty database), all files SHALL be parsed — this IS the full sync.

The sync SHALL detect deleted files: any node in the database whose `source_file` no longer exists on disk SHALL be deleted (along with its edges via cascade).

|rel:portion_of| [[specs/sync-engine-spec]]
|rel:has_scenario| [[scenarios/sync-only-changed-files]]
|rel:touches| [[tools/sync.py]]
