---
title: Pixel Platformer Platform
kind: spec
created: 2026-05-10
updated: 2026-05-10
tags: [game, raylib, pixel-art, platformer]
---

# Pixel Platformer Platform

A side-scrolling pixel art platformer built with raylib in C. All sprites generated programmatically. The player navigates a scrolling level collecting coins, stomping enemies, avoiding spikes, and reaching a flag at the end.

## Sub-Specs

| Spec | System | Purpose |
|------|--------|---------|
| Player Spec | Player System | Movement, jumping, health, collision |
| Level Spec | Level System | Tile-based level, scrolling camera, spawn points |
| Sprite Spec | Sprite Generation | Programmatic pixel art textures |
| Enemy Spec | Enemy System | Walker AI, hopper AI, stomp mechanics |
| Pickup Spec | Coins & Powerups | Collectibles, score tracking |

|rel:spec_of| [[tools/pixel-platformer]]
|rel:contains| [[specs/pixel-player-spec]]
|rel:contains| [[specs/pixel-level-spec]]
|rel:contains| [[specs/pixel-sprite-spec]]
|rel:contains| [[specs/pixel-enemy-spec]]
|rel:contains| [[specs/pixel-pickup-spec]]
