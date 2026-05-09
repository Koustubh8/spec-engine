---
title: Terrain Collision
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game, level]
strength: SHALL
---

# Terrain Collision

Players and enemies SHALL NOT pass through `#` walls. Players SHALL stand on floor tiles (`.`) and SHALL fall if no floor beneath (gravity). Gaps in the floor SHALL be lethal (bottomless pit = instant death).

|rel:portion_of| [[specs/ascii-level-spec]]
