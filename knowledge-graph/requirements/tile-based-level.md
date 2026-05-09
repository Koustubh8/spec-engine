---
title: Tile Based Level
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game]
strength: SHALL
---

# Tile Based Level

Level SHALL be a 150x20 integer grid. 0=air, 1=ground tile, 2=platform, 3=spike. Ground and platform tiles SHALL be solid for player standing. Spikes SHALL damage on contact. Level SHALL have procedurally generated platforms and pre-placed spike pits.

|rel:portion_of| [[specs/pixel-level-spec]]
