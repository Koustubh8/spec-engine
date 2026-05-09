---
title: GET /api/nodes/{slug} — Node Detail
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [api, endpoint]
---

# GET /api/nodes/{slug} — Node Detail

Returns a single node with its incoming and outgoing edges. The edges section includes the full related node data (title, kind, slug) so the frontend can render edge lists without additional requests.

|rel:exposed_by| [[specs/api-layer-spec]]
|rel:returns| [[concepts/node-detail-response]]
