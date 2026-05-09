---
title: Raylib Function Name Conflicts
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [learning, raylib]
---

# Raylib Function Name Conflicts

raylib 5.5 exports UpdateCamera(Camera*, int mode). Naming any custom function UpdateCamera causes a linker/compiler conflict. Always prefix custom game functions (e.g. GameUpdateCamera) to avoid clashing with raylib's public API.
