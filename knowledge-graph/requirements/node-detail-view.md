---
title: Node Detail View
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [ui, react]
strength: SHALL
---

# Node Detail View

The `/nodes/:slug` page SHALL display a single node with full detail:

- Title and kind badge at top
- All frontmatter fields displayed as a metadata panel (kind, tags, created, updated, strength, status)
- Body rendered as markdown (react-markdown or similar)
- Two edge sections:
  - **Outgoing edges** (this node → other nodes): each shows predicate badge + linked node title + kind + clickable link
  - **Incoming edges** (other nodes → this node): same format, reversed
- Edge sections group by predicate for readability

Related: if the node is a `spec`, show its requirements as a linked sub-list. If a `requirement`, show its scenarios. If a `change`, show its adds/modifies/removes.

|rel:portion_of| [[specs/dashboard-spec]]
