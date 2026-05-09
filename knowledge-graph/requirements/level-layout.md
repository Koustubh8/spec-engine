---
title: Level Layout
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game, level]
strength: SHALL
---

# Level Layout

The level SHALL be defined as a 2D character array (char map[HEIGHT][WIDTH]). `#` for walls, `.` for floor/air, `P` for player spawn, `E` for enemy spawn points. Level SHALL be wider than the screen so scrolling is meaningful.

|rel:portion_of| [[specs/ascii-level-spec]]
