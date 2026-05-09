---
title: HUD Display
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game, rendering]
strength: SHALL
---

# HUD Display

The HUD SHALL display in fixed screen space (not scrolling): health bar (hearts or HP text), lives count, score, active weapon name, wave number. HUD SHALL be drawn after EndMode2D() so it doesn't scroll with the camera.

|rel:portion_of| [[specs/ascii-rendering-spec]]
