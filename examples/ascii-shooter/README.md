# ASCII Shooter — Side-Scrolling Shooter in C + raylib

A Contra/Metal Slug style side-scrolling shooter rendered in ASCII characters.

## Build & Run

```bash
cd examples/ascii-shooter
make run
```

## Controls

| Key | Action |
|-----|--------|
| ← → | Move |
| X | Jump |
| Z | Shoot |
| SPACE | Start / Restart |

## Spec Graph

The full spec is in `knowledge-graph/specs/`:

| Spec | Description |
|------|-------------|
| `ascii-player-spec` | Player movement, shooting, health, lives |
| `ascii-enemy-spec` | 3 enemy types (walker, shooter, flyer) |
| `ascii-level-spec` | Level layout, scrolling camera, terrain collision |
| `ascii-weapons-spec` | 3 weapons (default, spread, rapid) |
| `ascii-boss-spec` | 3-phase boss fight |
| `ascii-rendering-spec` | ASCII grid rendering, HUD, game states |

## Architecture

```
main.c         — game loop, state machine, render
render.h       — camera, HUD, screen drawing
level.h        — level data, collision queries
entity.h       — player, enemies, boss, projectiles, waves
```

Built following the spec-driven development methodology at [Koustubh8/spec-engine](https://github.com/Koustubh8/spec-engine).
