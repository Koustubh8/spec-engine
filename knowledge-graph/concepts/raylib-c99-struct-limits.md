---
title: Raylib C99 Struct Limits
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [constraint, game]
---

# Raylib C99 Struct Limits

Apple clang with -std=c99 doesn't support designated initializers on raylib structs. Use explicit field assignment: cam.zoom = 1.0f; not Camera2D cam = { .zoom = 1.0f };
