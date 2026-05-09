---
title: Node Browser View
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [ui, react]
strength: SHALL
---

# Node Browser View

The `/nodes` page SHALL display nodes in a filterable, paginated list. Features:

- Kind tabs or dropdown (Specs, Requirements, Scenarios, Changes, Concepts, All)
- Search input filtering by title (API call with `?search=`)
- Pagination controls (prev/next, page number, page size selector)
- Each row/card shows: title, kind badge, tag chips, snippet of body text (first 100 chars)
- Click row/card → navigate to `/nodes/{slug}` detail

Empty state: "No nodes found" with suggestion to trigger a sync. Loading state: skeleton cards.

|rel:portion_of| [[specs/dashboard-spec]]
