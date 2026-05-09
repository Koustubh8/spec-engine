---
title: Explore Pixel Platformer
kind: changes
created: 2026-05-10
updated: 2026-05-10
tags: [exploration, game, raylib, pixel-art, platformer]
status: completed
---

# Explore Pixel Platformer

## Raw Requirement
A side-scrolling pixel art platformer built with raylib in C. All sprites generated programmatically — no external image assets. Player runs, jumps, collects coins, stomps enemies, avoids spikes, reaches a flag at the end.

## Journey

### Phase 1: ASCII Shooter (failed)
First attempt was an ASCII side-scrolling shooter (Contra-style). Rendered characters as text glyphs via DrawText. Result: ASCII UX didn't work visually — font rendering didn't align well to a grid, characters were unreadable at game scale. Abandoned after compilation.

### Phase 2: Pixel Art Platformer (success)
Switched to generated pixel art sprites using raylib's Image/Texture functions. All sprites created pixel-by-pixel in code:
- Player: 20x28 character with blue vest, skin head, boots
- Ground tile: 32x32 dirt + grass
- Platform tile: 32x16 brown brick
- Enemies: 18x16 red (walker) and purple (hopper) creatures
- Coins: 12x12 gold circles with shine
- Spikes: triangular red hazards
- Background: gradient sky with cloud dots

### Tech Stack
- **Language**: C99
- **Framework**: raylib 5.5
- **Build**: Makefile with pkg-config, -Wall -Wextra -std=c99
- **Architecture**: Single-file main.c (732 lines), no external assets
- **Sprite generation**: raylib GenImageColor + ImageDrawPixel + LoadTextureFromImage

### Build Learnings

**L1: ASCII rendering doesn't work for games at this scale**
DrawText with system fonts produces inconsistent character spacing and sizes. For a 24px grid, characters were misaligned and hard to read. Pixel art textures (generated programmatically) produce much better results.

**L2: raylib UpdateCamera conflicts with custom function**
raylib 5.5 exports `UpdateCamera(Camera*, int mode)` — naming a custom function `UpdateCamera` causes a symbol conflict. Fixed by renaming to `GameUpdateCamera`.

**L3: C99 designated initializers with raylib structs**
`Camera2D cam = { .zoom = 1.0f }` doesn't compile with Apple clang + -std=c99. Use explicit field assignment.

**L4: Sprite generation is fast and asset-free**
`GenImageColor()` + `ImageDrawPixel()` loops produce usable pixel art textures at runtime. ~100 lines of pixel data generates all sprites. No asset pipeline needed.

|rel:change_for| [[specs/pixel-platformer-platform]]
|rel:adds| [[concepts/pixel-art-sprite-generation]]
|rel:adds| [[concepts/platformer-physics]]
|rel:adds| [[concepts/enemy-ai-patrol]]
|rel:adds| [[concepts/particle-effects]]
|rel:adds| [[concepts/scrolling-camera]]
