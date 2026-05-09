---
title: Player Movement
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game, player]
strength: SHALL
---

# Player Movement

The player SHALL move left/right using arrow keys. Jump with X key. Movement SHALL be smooth (lerp between grid cells). The player SHALL face the direction of last movement for shooting orientation. Jump SHALL have gravity and arc, not teleport.

GIVEN the player is on solid ground AND the left arrow is held WHEN update runs THEN the player moves left at movement speed.
GIVEN the player is on solid ground AND X is pressed WHEN update runs THEN the player jumps upward with jump velocity.

|rel:portion_of| [[specs/ascii-player-spec]]
