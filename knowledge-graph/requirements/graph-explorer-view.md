---
title: Graph Explorer View
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [ui, react, graph]
strength: SHOULD
---

# Graph Explorer View

The `/explore` page SHOULD provide an interactive force-directed graph visualization of the spec graph:

- Input panel: seed node slug (autocomplete from existing nodes), depth (1-10 slider), predicate filter (multi-select), direction (forward/reverse/both)
- Graph canvas: rendered with vis-network or D3.js force simulation
  - Node colors by kind (spec=blue, requirement=green, concept=amber, etc.)
  - Edge labels showing predicate
  - Click node → highlight its neighbors + show tooltip with title/kind
  - Right-click node → "View Detail" navigates to `/nodes/{slug}`
  - Zoom and pan controls
- Results panel: tabular list of discovered nodes and edges (sortable)

Performance: for graphs with >100 visible nodes, limit initial render and paginate the canvas.

Empty state: prompt user to enter a seed node. Loading: spinner over dimmed canvas.

|rel:portion_of| [[specs/dashboard-spec]]
