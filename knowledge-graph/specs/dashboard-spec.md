---
title: Dashboard Specification
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [ui, react, frontend]
---

# Dashboard Specification

React SPA providing a dashboard to view, browse, and query the spec graph. Dark-themed, minimal navigation, focused on data exploration.

## Views

### 1. Dashboard Overview (`/`)
- Summary stats cards (total nodes, edges, by kind)
- Quick sync status indicator
- Recent changes list
- Link to browse any kind

### 2. Node Browser (`/nodes?kind=spec`)
- Filterable table/card list grouped by kind
- Search by title
- Click to view detail

### 3. Node Detail (`/nodes/{slug}`)
- Full metadata display (frontmatter fields)
- Rendered body markdown
- Incoming edges list (this node is the target)
- Outgoing edges list (this node is the source)
- Each edge shows predicate + linked node title/kind

### 4. Graph Explorer (`/explore`)
- Input: seed node, depth, predicate filter
- Output: force-directed graph visualization (D3.js or vis-network)
- Node colors by kind, edge labels by predicate
- Click node to inspect or navigate to its detail page

### 5. Sync Panel
- Trigger sync button
- Show last sync status + summary
- Show warnings/errors if any

## Styling

Dark theme with the neo-brutalist CSS pattern from the reusable inventory. Single-column layout on mobile, two-column on desktop for detail views.

|rel:spec_of| [[tools/react-frontend]]
|rel:reuses| [[concepts/Dark Dashboard]]
|rel:reuses| [[concepts/Dashboard As Triage]]
|rel:reuses| [[concepts/Neo Brutalist Css]]
|rel:reuses| [[concepts/Modal Quick Action]]
|rel:contains| [[requirements/dashboard-overview-view]]
|rel:contains| [[requirements/node-browser-view]]
|rel:contains| [[requirements/node-detail-view]]
|rel:contains| [[requirements/graph-explorer-view]]
|rel:contains| [[requirements/sync-control-panel]]
