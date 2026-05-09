---
title: Error-Tolerant Parsing
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [sync, robustness]
strength: SHALL
---

# Error-Tolerant Parsing

The sync engine SHALL NOT crash or abort on a single malformed file. Per-file error handling:

- Malformed YAML frontmatter → log warning with filename + error, skip the file, continue with next
- Missing `kind:` field → infer from parent directory name (e.g. file in specs/ → "spec")
- Missing `title:` field → auto-generate from filename slug (replace-hyphens-with-spaces-title-case)
- Broken edge target (slug has no matching node in DB) → create placeholder node with `kind: reference` and `title: "<slug>"`, emit warning
- Circular edge (node references itself) → skip the edge, log warning

After sync completes, the sync_run record SHALL include a `warnings` count and `errors` count so the dashboard can flag issues.

|rel:portion_of| [[specs/sync-engine-spec]]
