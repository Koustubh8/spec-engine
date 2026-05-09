---
title: Sync Engine Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [sync, markdown, core]
---

# Sync Engine Specification

Reads markdown files from KNOWLEDGE_PATH, parses YAML frontmatter and `|rel:|` edges, and reconciles them into the SQLAlchemy database. Supports incremental sync (only re-parse changed files), full rebuild, and error reporting.

## Algorithm

```
1. Walk KNOWLEDGE_PATH, collecting all .md files (skip: queries/, scripts/, templates/)
2. For each file:
   a. Compare source_mtime with stored value
   b. If unchanged, skip (incremental)
   c. If changed or new:
      - Parse YAML frontmatter → node fields
      - Parse body for |rel:PREDICATE| [[KIND/SLUG]] edges
      - Upsert node in DB
      - Upsert edges (delete stale, insert new)
3. Detect deleted files (in DB but not on disk) → delete nodes + cascade edges
4. Write sync_run summary
```

## Edge Re-parsing Strategy

The tricky part: editing a node's markdown file may add/remove/modify its `|rel:|` edges. The sync engine SHALL:

1. Collect all edges found in the parsed file
2. Delete all existing edges where `from_node_id` matches this node (for all predicates)
3. Insert all currently-parsed edges
4. This is a full replace per node — simpler and safer than diffing

## Error Handling

- Malformed YAML → log error, skip file, continue
- Broken edge target (slug doesn't resolve to existing node) → create placeholder node with kind "reference", emit warning
- Missing required frontmatter fields → infer sensible defaults (title from filename, kind from directory)

|rel:spec_of| [[tools/sync-script]]
|rel:contains| [[requirements/incremental-sync]]
|rel:contains| [[requirements/edge-reconciliation]]
|rel:contains| [[requirements/error-tolerant-parsing]]
|rel:contains| [[requirements/sync-run-logging]]
