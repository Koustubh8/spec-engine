---
title: ASCII Side-Scrolling Shooter Platform
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [game, raylib, ascii, shooter]
---

# ASCII Side-Scrolling Shooter Platform

A Contra/Metal Slug style side-scrolling shooter rendered in ASCII characters using raylib in C. Single scrolling level with waves of enemies and a multi-phase boss fight.

## Game Overview

| Aspect | Design |
|--------|--------|
| Genre | Side-scrolling shooter (run-n-gun) |
| View | Side-view, camera follows player horizontally |
| Aesthetic | ASCII characters (`@` player, letter enemies, `#` walls) |
| Scope | 1 designed level, enemy waves + boss |
| Rendering | raylib DrawText with monospace font on character grid |
| Input | Arrow keys + Z (shoot) + X (jump) + Space (start/restart) |

## Sub-Specs

| Spec | System | Purpose |
|------|--------|---------|
| Player Spec | Player System | Movement, shooting, health, lives |
| Enemy Spec | Enemy System | Enemy types, AI, spawning, death |
| Level Spec | Level Design | Scrolling layout, terrain, enemy placements |
| Weapons Spec | Weapons & Power-ups | Weapon types, ammo, drops |
| Boss Spec | Boss System | Boss AI, phases, attack patterns |
| Rendering Spec | ASCII Rendering | Character grid, camera, HUD |

|rel:spec_of| [[tools/ascii-shooter-game]]
|rel:reuses| [[concepts/Game State Machine]]
|rel:contains| [[specs/ascii-player-spec]]
|rel:contains| [[specs/ascii-enemy-spec]]
|rel:contains| [[specs/ascii-level-spec]]
|rel:contains| [[specs/ascii-weapons-spec]]
|rel:contains| [[specs/ascii-boss-spec]]
|rel:contains| [[specs/ascii-rendering-spec]]
