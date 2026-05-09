---
title: Explore ASCII Side-Scrolling Shooter
kind: changes
created: 2026-05-10
updated: 2026-05-10
tags: [exploration, game, raylib, ascii, shooter]
status: exploring
---

# Explore ASCII Side-Scrolling Shooter

## Raw Requirement
A Contra/Metal Slug style side-scrolling shooter rendered in ASCII characters using raylib in C. Single level with waves of enemies and one boss fight.

## User Answers

### Genre: Side-scrolling shooter
Contra/Metal Slug style. Run left/right, jump, shoot enemies. Boss fight at the end.

### Visual style: ASCII / terminal aesthetic
Characters as glyphs: `@` for player, letters for enemies (`g` goblin, `s` snake), `#` for walls, `.` for floor. No sprites or assets needed.

### Scope: Single level
One scrolling arena with enemy waves + one boss fight. Not procedural — designed level.

## Tech Stack
- **Language**: C99
- **Framework**: raylib (via pkg-config)
- **Build**: Makefile with gcc, -Wall -Wextra -std=c99
- **Architecture**: Header-only .h modules, linked through main.c
- **Rendering**: raylib DrawText with monospace font, character grid

|rel:change_for| [[specs/ascii-shooter-platform]]
|rel:adds| [[concepts/player-system]]
|rel:adds| [[concepts/enemy-system]]
|rel:adds| [[concepts/level-scrolling]]
|rel:adds| [[concepts/weapons-powerups]]
|rel:adds| [[concepts/boss-system]]
|rel:adds| [[concepts/hud-display]]
|rel:adds| [[concepts/game-state-machine]]
|rel:adds| [[concepts/collision-system]]
|rel:adds| [[concepts/input-handling]]
|rel:adds| [[concepts/ascii-rendering]]
