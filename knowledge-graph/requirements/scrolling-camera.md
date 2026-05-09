---
title: Scrolling Camera
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game]
strength: SHALL
---

# Scrolling Camera

Camera SHALL follow the player horizontally. Camera target SHALL be player position minus 10 tiles offset. Camera SHALL lerp toward target at 0.08 speed. Camera SHALL clamp to level bounds (0 to LVL_W-20).

|rel:portion_of| [[specs/pixel-level-spec]]
