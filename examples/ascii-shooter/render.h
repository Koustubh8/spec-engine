/*
 * render.h — ASCII rendering, camera, and HUD
 *
 * Requirement: character-grid-render [SHALL]
 * Requirement: hud-display [SHALL]
 */
#ifndef RENDER_H
#define RENDER_H

#include "raylib.h"
#include <stdio.h>

#define CELL_SIZE 24

/* ─── Camera ─────────────────────────────────────── */

typedef struct {
    float offset_x;    /* world offset in pixels */
    int level_w;       /* total level width in cells */
    int screen_cols;   /* how many columns fit on screen */
    int screen_rows;
} GameCamera;

void GameCameraInit(GameCamera* cam, int lvl_w, int sw, int sh) {
    cam->offset_x = 0;
    cam->level_w = lvl_w;
    cam->screen_cols = sw / CELL_SIZE + 1;
    cam->screen_rows = sh / CELL_SIZE + 1;
}

void GameCameraFollow(GameCamera* cam, float target_x, float lerp_speed) {
    float target = target_x - (cam->screen_cols * CELL_SIZE) / 2.0f;
    target = (target < 0) ? 0 : target;
    float max_x = (cam->level_w * CELL_SIZE) - (cam->screen_cols * CELL_SIZE);
    if (max_x > 0 && target > max_x) target = max_x;
    cam->offset_x += (target - cam->offset_x) * lerp_speed;
}

/* ─── HUD ────────────────────────────────────────── */

void DrawHUD(int hp, int lives, int score, const char* weapon, int wave,
             int sw, int sh) {
    char buf[128];
    int y = sh - 30;

    snprintf(buf, sizeof(buf), "HP: ");
    DrawText(buf, 10, y, 18, RED);
    for (int i = 0; i < hp; i++) DrawText("@", 70 + i * 20, y, 18, GREEN);
    for (int i = hp; i < 3; i++) DrawText("@", 70 + i * 20, y, 18, DARKGRAY);

    snprintf(buf, sizeof(buf), "LIVES: %d", lives);
    DrawText(buf, 150, y, 18, WHITE);

    snprintf(buf, sizeof(buf), "SCORE: %d", score);
    DrawText(buf, 300, y, 18, YELLOW);

    snprintf(buf, sizeof(buf), "WPN: %s", weapon);
    DrawText(buf, 480, y, 18, SKYBLUE);

    snprintf(buf, sizeof(buf), "WAVE: %d", wave);
    DrawText(buf, 630, y, 18, ORANGE);
}

/* ─── Screens ────────────────────────────────────── */

void DrawStartScreen(int sw, int sh) {
    DrawText("ASCII SHOOTER", sw/2 - 160, sh/2 - 60, 48, GREEN);
    DrawText("A Contra-style side-scrolling shooter", sw/2 - 180, sh/2, 18, GRAY);
    DrawText("ARROWS: Move   X: Jump   Z: Shoot", sw/2 - 160, sh/2 + 40, 16, LIGHTGRAY);
    DrawText("PRESS SPACE TO START", sw/2 - 120, sh/2 + 80, 18, YELLOW);
}

void DrawGameOverScreen(int score, int sw, int sh) {
    DrawRectangle(0, 0, sw, sh, (Color){ 0, 0, 0, 180 });
    DrawText("GAME OVER", sw/2 - 120, sh/2 - 40, 40, RED);
    char buf[64];
    snprintf(buf, sizeof(buf), "FINAL SCORE: %d", score);
    DrawText(buf, sw/2 - 100, sh/2 + 10, 22, YELLOW);
    DrawText("PRESS SPACE TO RESTART", sw/2 - 130, sh/2 + 50, 16, GRAY);
}

void DrawLevelCompleteScreen(int score, int sw, int sh) {
    DrawRectangle(0, 0, sw, sh, (Color){ 0, 0, 0, 180 });
    DrawText("LEVEL COMPLETE!", sw/2 - 140, sh/2 - 40, 36, GREEN);
    char buf[64];
    snprintf(buf, sizeof(buf), "SCORE: %d", score);
    DrawText(buf, sw/2 - 60, sh/2 + 10, 22, YELLOW);
    DrawText("VICTORY!", sw/2 - 60, sh/2 + 50, 20, GOLD);
    DrawText("PRESS SPACE TO PLAY AGAIN", sw/2 - 140, sh/2 + 90, 16, GRAY);
}

#endif
