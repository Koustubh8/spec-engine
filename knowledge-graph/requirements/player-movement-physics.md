---
title: Player Movement and Physics
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game, player]
strength: SHALL
---

# Player Movement and Physics

The player SHALL move left/right with arrow keys or WASD at 250px/s. Jump SHALL be triggered by Space or W when on ground. Jump velocity SHALL be -420. Gravity SHALL be 900px/s². Player SHALL collide with solid tiles (ground, platforms) and SHALL NOT pass through walls. Player SHALL take damage from spikes (1HP, 60-frame invulnerability) and SHALL die from falling off the bottom of the level.

|rel:portion_of| [[specs/pixel-player-spec]]
