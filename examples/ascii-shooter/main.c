/*
 * main.c — ASCII Side-Scrolling Shooter
 *
 * A Contra/Metal Slug style shooter rendered in ASCII characters.
 * Single level with enemy waves and a multi-phase boss fight.
 *
 * ascii-shooter-platform spec:
 *  - ascii-player-spec: player-movement, player-shooting, player-health-lives
 *  - ascii-enemy-spec: enemy-types, enemy-spawning, enemy-ai
 *  - ascii-level-spec: level-layout, camera-scrolling, terrain-collision
 *  - ascii-weapons-spec: weapon-types, powerup-drops
 *  - ascii-boss-spec: boss-phases, boss-attacks
 *  - ascii-rendering-spec: character-grid-render, hud-display, game-states
 */

#include "raylib.h"
#include <stdlib.h>
#include <time.h>

#include "render.h"
#include "level.h"
#include "entity.h"

/* ─── Main ────────────────────────────────────────── */

int main(void) {
    srand(time(NULL));

    const int sw = 800, sh = 600;
    InitWindow(sw, sh, "ASCII SHOOTER");
    SetTargetFPS(60);

    /* Game state */
    Game game;
    game.screen_w = sw;
    game.screen_h = sh;
    game.game_state = GAME_STATE_START;
    game.boss_defeated = 0;

    GameCamera cam;
    GameCameraInit(&cam, LVL_W, sw, sh);

    /* ─── Game Loop ────────────────────────────────── */
    while (!WindowShouldClose()) {
        float dt = GetFrameTime();

        /* ─── START SCREEN ─────────────────────────── */
        if (game.game_state == GAME_STATE_START) {
            if (IsKeyPressed(KEY_SPACE)) {
                /* Initialize game */
                PlayerInit(&game.player);
                game.enemy_count = 0;
                game.player_bullet_count = 0;
                game.enemy_bullet_count = 0;
                game.powerup_count = 0;
                game.wave = 0;
                game.total_spawned = 0;
                game.boss_defeated = 0;
                game.boss.active = false;
                game.game_state = GAME_STATE_PLAYING;
                SpawnWave(&game);
            }

            BeginDrawing();
            ClearBackground(BLACK);
            DrawStartScreen(sw, sh);
            EndDrawing();
            continue;
        }

        /* ─── GAME OVER ────────────────────────────── */
        if (game.game_state == GAME_STATE_GAMEOVER) {
            if (IsKeyPressed(KEY_SPACE)) game.game_state = GAME_STATE_START;

            BeginDrawing();
            ClearBackground(BLACK);
            DrawGameOverScreen(game.player.score, sw, sh);
            EndDrawing();
            continue;
        }

        /* ─── LEVEL COMPLETE ───────────────────────── */
        if (game.game_state == GAME_STATE_COMPLETE) {
            if (IsKeyPressed(KEY_SPACE)) game.game_state = GAME_STATE_START;

            BeginDrawing();
            ClearBackground(BLACK);
            DrawLevelCompleteScreen(game.player.score, sw, sh);
            EndDrawing();
            continue;
        }

        /* ─── PLAYING ──────────────────────────────── */
        float px = game.player.x;
        float py = game.player.y;

        /* Player input */
        if (IsKeyPressed(KEY_Z)) {
            PlayerShoot(&game.player, game.player_bullets, &game.player_bullet_count);
        }

        /* Update player */
        PlayerUpdate(&game.player, dt);

        /* Fire while holding Z (auto-fire) */
        if (IsKeyDown(KEY_Z)) {
            game.player.fire_cooldown--;
            if (game.player.fire_cooldown <= 0)
                PlayerShoot(&game.player, game.player_bullets, &game.player_bullet_count);
        } else {
            if (game.player.fire_cooldown > 0) game.player.fire_cooldown--;
        }

        /* Check player death */
        if (!game.player.alive) {
            game.game_state = GAME_STATE_GAMEOVER;
        }

        /* Wave management */
        int alive = 0;
        for (int i = 0; i < game.enemy_count; i++)
            if (game.enemies[i].active) alive++;

        /* Check if we should trigger boss */
        bool should_spawn_boss = (game.player.x / CELL_SIZE) >= BOSS_TRIGGER_X && !game.boss.active && !game.boss_defeated;

        if (alive == 0 && !should_spawn_boss && !game.boss.active) {
            SpawnWave(&game);
        }

        if (should_spawn_boss) {
            BossInit(&game.boss);
            /* Clear remaining enemies */
            for (int i = 0; i < game.enemy_count; i++)
                game.enemies[i].active = false;
        }

        /* Update enemies */
        for (int i = 0; i < game.enemy_count; i++) {
            if (game.enemies[i].active)
                EnemyUpdate(&game.enemies[i], px, py, dt,
                           game.enemy_bullets, &game.enemy_bullet_count);
        }

        /* Update boss */
        if (game.boss.active) {
            BossUpdate(&game.boss, px, py, dt,
                      game.enemy_bullets, &game.enemy_bullet_count);
            if (!game.boss.active) {
                game.boss_defeated = 1;
                game.player.score += 1000;
                game.game_state = GAME_STATE_COMPLETE;
            }
        }

        /* Update projectiles */
        UpdateProjectiles(game.player_bullets, &game.player_bullet_count, dt);
        UpdateProjectiles(game.enemy_bullets, &game.enemy_bullet_count, dt);

        /* Collision */
        CheckCollisions(&game);

        /* Camera */
        GameCameraFollow(&cam, game.player.x, 0.08f);

        /* ─── RENDER ───────────────────────────────── */
        BeginDrawing();
        ClearBackground((Color){ 10, 10, 15, 255 });

        int start_col = (int)(cam.offset_x / CELL_SIZE);
        if (start_col < 0) start_col = 0;
        int end_col = start_col + cam.screen_cols + 2;
        if (end_col > LVL_W) end_col = LVL_W;

        /* Draw terrain */
        for (int y = 0; y < cam.screen_rows && y < LVL_H; y++) {
            for (int x = start_col; x < end_col; x++) {
                int sx = (x - start_col) * CELL_SIZE;
                int sy = y * CELL_SIZE;
                char ch = LEVEL_DATA[y][x];
                Color col;
                switch (ch) {
                    case '#': col = (Color){ 80, 80, 90, 255 }; break;
                    case '.': col = (Color){ 40, 40, 50, 255 }; break;
                    default:  col = BLACK; break;
                }
                char buf[2] = { ch, '\0' };
                DrawText(buf, sx, sy, CELL_SIZE - 4, col);
            }
        }

        /* Draw power-ups */
        for (int i = 0; i < game.powerup_count; i++) {
            Powerup* pu = &game.powerups[i];
            if (!pu->active) continue;
            int sx = (int)(pu->x - cam.offset_x);
            int sy = (int)pu->y;
            char buf[2] = { pu->ch, '\0' };
            DrawText(buf, sx, sy, CELL_SIZE - 4, pu->color);
        }

        /* Draw player */
        if (game.player.alive) {
            int flash = (game.player.invuln_timer / 5) % 2;
            if (!flash || game.player.invuln_timer == 0) {
                int sx = (int)(game.player.x - cam.offset_x);
                int sy = (int)game.player.y;
                DrawText("@", sx, sy, CELL_SIZE, GREEN);
            }
        }

        /* Draw enemies */
        for (int i = 0; i < game.enemy_count; i++) {
            Enemy* e = &game.enemies[i];
            if (!e->active) continue;
            int sx = (int)(e->x - cam.offset_x);
            int sy = (int)e->y;
            char buf[2] = { e->ch, '\0' };
            DrawText(buf, sx, sy, CELL_SIZE, e->color);
        }

        /* Draw player bullets */
        for (int i = 0; i < game.player_bullet_count; i++) {
            Projectile* b = &game.player_bullets[i];
            if (!b->active) continue;
            int sx = (int)(b->x - cam.offset_x);
            int sy = (int)b->y;
            char buf[2] = { b->ch, '\0' };
            DrawText(buf, sx, sy, CELL_SIZE - 8, b->color);
        }

        /* Draw enemy bullets */
        for (int i = 0; i < game.enemy_bullet_count; i++) {
            Projectile* b = &game.enemy_bullets[i];
            if (!b->active) continue;
            int sx = (int)(b->x - cam.offset_x);
            int sy = (int)b->y;
            char buf[2] = { b->ch, '\0' };
            DrawText(buf, sx, sy, CELL_SIZE - 8, b->color);
        }

        /* Draw boss */
        if (game.boss.active) {
            int sx = (int)(game.boss.x - cam.offset_x);
            int sy = (int)game.boss.y;
            Color boss_colors[] = { RED, ORANGE, PINK };
            DrawText("B", sx, sy, CELL_SIZE + 8, boss_colors[game.boss.phase]);

            /* Boss HP bar */
            float hp_ratio = (float)game.boss.hp / game.boss.max_hp;
            DrawRectangle(sx, sy - 12, 60, 6, DARKGRAY);
            DrawRectangle(sx, sy - 12, (int)(60 * hp_ratio), 6, RED);
        }

        /* HUD */
        char weapon_names[][10] = { "DEFAULT", "SPREAD", "RAPID" };
        int wave_display = game.wave + (game.boss.active ? 1 : 0);
        DrawHUD(game.player.hp, game.player.lives, game.player.score,
                weapon_names[game.player.weapon], wave_display, sw, sh);

        EndDrawing();
    }

    CloseWindow();
    return 0;
}
