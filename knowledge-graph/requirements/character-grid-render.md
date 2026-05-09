---
title: Character Grid Rendering
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game, rendering]
strength: SHALL
---

# Character Grid Rendering

The world SHALL be rendered as a grid of ASCII characters. Each cell is ~20x20 pixels. Characters: `@` player, `#` wall, `.` air, enemy letters, `-` bullets. Use raylib DrawText with monospace font. Camera offset determines which grid cells are visible.

|rel:portion_of| [[specs/ascii-rendering-spec]]
