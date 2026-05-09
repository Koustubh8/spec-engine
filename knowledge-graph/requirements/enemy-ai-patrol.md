---
title: Enemy Ai Patrol
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [game]
strength: SHALL
---

# Enemy Ai Patrol

Walkers SHALL patrol horizontally at 60px/s, reversing direction at tile edges. Hoppers SHALL jump toward the player every ~30 frames with velocity -300. Both SHALL be stompable by jumping on them from above (dy < -8, player vy > 0). Stomping SHALL set player vy to -300 and spawn 8 red particles. Both enemies SHALL deal contact damage.

|rel:portion_of| [[specs/pixel-enemy-spec]]
