---
title: Programmatic Sprites
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game]
strength: SHALL
---

# Programmatic Sprites

All sprites SHALL be generated programmatically using raylib GenImageColor + ImageDrawPixel. No external image files SHALL be required. Sprites: player (20x28), ground (32x32), platform (32x16), enemies (18x16), coin (12x12), spike (32x32). Background SHALL be a gradient sky rendered with DrawRectangle per scanline.

|rel:portion_of| [[specs/pixel-sprite-spec]]
