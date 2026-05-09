/*
 * entity.h — Player, enemies, projectiles, boss, collision
 *
 * Requirements: player-movement, player-shooting, enemy-ai,
 *               weapon-types, boss-phases, enemy-types
 */
#ifndef ENTITY_H
#define ENTITY_H

#include "raylib.h"
#include "level.h"
#include <stdbool.h>
#include <math.h>

/* ─── Constants ──────────────────────────────────── */

#define GRAVITY 1200.0f
#define MAX_ENEMIES 20
#define MAX_PROJECTILES 64
#define MAX_POWERUPS 10

/* ─── Projectile ─────────────────────────────────── */

typedef struct {
    float x, y;
    float vx, vy;
    int damage;
    bool active;
    int life;         /* frames remaining */
    char ch;          /* visual character */
    Color color;
} Projectile;

/* ─── Player ──────────────────────────────────────── */

typedef struct {
    float x, y;           /* pixel position */
    float vx, vy;
    int hp;
    int lives;
    int score;
    int facing;           /* 1 = right, -1 = left */
    bool on_ground;
    bool alive;
    int invuln_timer;     /* flashing after hit */
    int weapon;           /* 0=default, 1=spread, 2=rapid */
    float fire_cooldown;
    float move_speed;
} Player;

void PlayerInit(Player* p) {
    /* Find 'P' spawn in level */
    int spawn_x = 1, spawn_y = 15;
    for (int y = 0; y < LVL_H; y++)
        for (int x = 0; x < LVL_W; x++)
            if (LEVEL_DATA[y][x] == 'P') { spawn_x = x; spawn_y = y; break; }

    p->x = spawn_x * CELL_SIZE + CELL_SIZE/2.0f;
    p->y = spawn_y * CELL_SIZE;
    p->vx = 0; p->vy = 0;
    p->hp = 3; p->lives = 2;
    p->facing = 1;
    p->on_ground = false;
    p->alive = true;
    p->invuln_timer = 0;
    p->weapon = 0;
    p->fire_cooldown = 0;
    p->move_speed = 200.0f;
}

/* ─── Enemy ───────────────────────────────────────── */

typedef struct {
    float x, y;
    float vx, vy;
    int hp;
    int type;         /* 0=walker, 1=shooter, 2=flyer */
    bool active;
    int fire_timer;
    float sine_phase;
    bool on_ground;
    int score_value;
    char ch;
    Color color;
} Enemy;

void EnemyInit(Enemy* e, int type, float sx, float sy) {
    e->x = sx;
    e->y = sy;
    e->vx = 0; e->vy = 0;
    e->hp = (type == 2) ? 1 : 2;
    e->type = type;
    e->active = true;
    e->fire_timer = GetRandomValue(30, 120);
    e->sine_phase = GetRandomValue(0, 628) / 100.0f;
    e->on_ground = false;
    e->score_value = (type == 2) ? 150 : (type == 1) ? 100 : 50;
    e->ch = (type == 0) ? 'g' : (type == 1) ? 's' : 'f';
    e->color = (type == 0) ? RED : (type == 1) ? PURPLE : SKYBLUE;
}

/* ─── Boss ────────────────────────────────────────── */

typedef struct {
    float x, y;
    float vx, vy;
    int hp;
    int max_hp;
    int phase;        /* 0=first, 1=second, 2=third */
    bool active;
    int attack_timer;
    bool moving_right;
    float base_y;
    int charge_timer;
    bool charging;
    float charge_vx;
} Boss;

void BossInit(Boss* b) {
    b->x = BOSS_TRIGGER_X * CELL_SIZE + CELL_SIZE;
    b->y = 5 * CELL_SIZE;
    b->vx = 0; b->vy = 0;
    b->hp = 50;
    b->max_hp = 50;
    b->phase = 0;
    b->active = true;
    b->attack_timer = 60;
    b->moving_right = true;
    b->base_y = b->y;
    b->charge_timer = 0;
    b->charging = false;
    b->charge_vx = 0;
}

/* ─── Power-up ────────────────────────────────────── */

typedef struct {
    float x, y;
    int type;         /* 0=spread, 1=rapid */
    bool active;
    char ch;
    Color color;
} Powerup;

/* ─── Global game state ──────────────────────────── */

#define MAX_BULLETS 100
#define GAME_STATE_START 0
#define GAME_STATE_PLAYING 1
#define GAME_STATE_GAMEOVER 2
#define GAME_STATE_COMPLETE 3

typedef struct {
    Player player;
    Enemy enemies[MAX_ENEMIES];
    int enemy_count;
    Projectile player_bullets[MAX_BULLETS];
    int player_bullet_count;
    Projectile enemy_bullets[MAX_BULLETS];
    int enemy_bullet_count;
    Boss boss;
    Powerup powerups[MAX_POWERUPS];
    int powerup_count;
    int wave;
    int total_spawned;
    int wave_enemies_alive;
    int boss_defeated;
    int game_state;
    int screen_w, screen_h;
    float dt;
} Game;

/* ─── Player Logic ───────────────────────────────── */

void PlayerUpdate(Player* p, float dt) {
    if (!p->alive) return;

    /* Horizontal input */
    p->vx = 0;
    if (IsKeyDown(KEY_LEFT))  { p->vx = -p->move_speed; p->facing = -1; }
    if (IsKeyDown(KEY_RIGHT)) { p->vx = p->move_speed; p->facing = 1; }

    /* Jump */
    if (IsKeyPressed(KEY_X) && p->on_ground) {
        p->vy = -450.0f;
        p->on_ground = false;
    }

    /* Gravity */
    p->vy += GRAVITY * dt;
    if (p->vy > 800) p->vy = 800;

    /* Apply velocity */
    p->x += p->vx * dt;
    p->y += p->vy * dt;

    /* Grid collision */
    int gx = (int)(p->x / CELL_SIZE);
    int gy = (int)(p->y / CELL_SIZE);
    p->on_ground = false;

    /* Floor collision */
    if (p->vy >= 0) {
        int floor_y = gy + 1;
        if (IsFloor(gx, floor_y)) {
            p->y = floor_y * CELL_SIZE - 1;
            p->vy = 0;
            p->on_ground = true;
        }
    }

    /* Wall collision left/right */
    if (IsSolid(gx, gy) || IsSolid(gx, gy + 1)) {
        if (p->vx > 0) p->x = gx * CELL_SIZE;
        else p->x = (gx + 1) * CELL_SIZE;
    }

    /* Death pit */
    if (IsDeathPit(gy)) {
        p->alive = false;
    }

    /* Invulnerability timer */
    if (p->invuln_timer > 0) p->invuln_timer--;
}

void PlayerShoot(Player* p, Projectile* bullets, int* count) {
    if (!p->alive) return;
    if (p->fire_cooldown > 0) return;
    if (*count >= MAX_BULLETS - 5) return;

    float bx = p->x + (p->facing * CELL_SIZE / 2);
    float by = p->y - CELL_SIZE / 2;

    if (p->weapon == 0) {
        /* Default: single shot */
        Projectile* b = &bullets[*count]; (*count)++;
        b->x = bx; b->y = by;
        b->vx = 400 * p->facing; b->vy = 0;
        b->damage = 1; b->active = true; b->life = 120;
        b->ch = '-'; b->color = YELLOW;
        p->fire_cooldown = 12;
    } else if (p->weapon == 1) {
        /* Spread: 3 shots in a fan */
        for (int i = -1; i <= 1; i++) {
            Projectile* b = &bullets[*count]; (*count)++;
            b->x = bx; b->y = by + i * 6;
            b->vx = 350 * p->facing; b->vy = i * 80;
            b->damage = 1; b->active = true; b->life = 90;
            b->ch = '*'; b->color = ORANGE;
        }
        p->fire_cooldown = 18;
    } else if (p->weapon == 2) {
        /* Rapid: fast, low damage */
        Projectile* b = &bullets[*count]; (*count)++;
        b->x = bx; b->y = by;
        b->vx = 500 * p->facing; b->vy = 0;
        b->damage = 1; b->active = true; b->life = 60;
        b->ch = '.'; b->color = SKYBLUE;
        p->fire_cooldown = 5;
    }
}

void PlayerTakeDamage(Player* p, int dmg) {
    if (p->invuln_timer > 0) return;
    p->hp -= dmg;
    p->invuln_timer = 60;
    if (p->hp <= 0) {
        p->lives--;
        if (p->lives <= 0) p->alive = false;
        else { p->hp = 3; p->invuln_timer = 120; }
    }
}

/* ─── Enemy Logic ────────────────────────────────── */

void EnemyUpdate(Enemy* e, float px, float py, float dt,
                 Projectile* bullets, int* count) {
    if (!e->active) return;

    if (e->type == 0) {
        /* Walker: moves toward player on ground */
        e->vx = (px > e->x) ? 60 : -60;
    } else if (e->type == 1) {
        /* Shooter: stands still, faces player, shoots */
        e->vx = 0;
        e->fire_timer--;
        if (e->fire_timer <= 0 && *count < MAX_BULLETS) {
            Projectile* b = &bullets[*count]; (*count)++;
            b->x = e->x; b->y = e->y - 5;
            b->vx = (px > e->x) ? 200 : -200;
            b->vy = 0;
            b->damage = 1; b->active = true; b->life = 90;
            b->ch = '-'; b->color = RED;
            e->fire_timer = GetRandomValue(60, 150);
        }
    } else if (e->type == 2) {
        /* Flyer: sine wave + drops bombs */
        e->sine_phase += 2.0f * dt;
        e->vx = (px > e->x) ? 80 : -80;
        e->vy = sinf(e->sine_phase) * 60;
        e->fire_timer--;
        if (e->fire_timer <= 0 && *count < MAX_BULLETS) {
            Projectile* b = &bullets[*count]; (*count)++;
            b->x = e->x; b->y = e->y;
            b->vx = 0; b->vy = 200;
            b->damage = 1; b->active = true; b->life = 120;
            b->ch = 'v'; b->color = RED;
            e->fire_timer = GetRandomValue(90, 180);
        }
    }

    /* Apply gravity to ground enemies */
    if (e->type != 2) {
        e->vy += GRAVITY * dt;
        e->x += e->vx * dt;
        e->y += e->vy * dt;

        int gy = (int)(e->y / CELL_SIZE);
        int gx = (int)(e->x / CELL_SIZE);
        if (e->vy >= 0 && IsFloor(gx, gy + 1)) {
            e->y = (gy + 1) * CELL_SIZE - 1;
            e->vy = 0;
        }
    } else {
        e->x += e->vx * dt;
        e->y += e->vy * dt;
        /* Clamp flyer height */
        if (e->y < 2 * CELL_SIZE) e->y = 2 * CELL_SIZE;
        if (e->y > 12 * CELL_SIZE) e->y = 12 * CELL_SIZE;
    }

    /* Off-screen deactivation (past camera) */
    if (e->x < -CELL_SIZE * 2) e->active = false;
    if (e->x > LVL_W * CELL_SIZE + CELL_SIZE * 2) e->active = false;
}

/* ─── Boss Logic ─────────────────────────────────── */

void BossUpdate(Boss* b, float px, float py, float dt,
                Projectile* bullets, int* count) {
    if (!b->active) return;

    /* Phase detection */
    int new_phase = 0;
    if (b->hp <= b->max_hp * 0.25) new_phase = 2;
    else if (b->hp <= b->max_hp * 0.5) new_phase = 1;
    b->phase = new_phase;

    float speed = 80 + b->phase * 40;

    /* Phase 3: charge attack */
    if (b->phase >= 2) {
        b->charge_timer--;
        if (b->charging) {
            b->x += b->charge_vx * dt;
            /* Stop charging after some distance */
            if (b->charge_timer <= -30) {
                b->charging = false;
                b->charge_timer = 60;
            }
        } else {
            /* Normal movement */
            b->moving_right = (px > b->x - 50);
            b->vx = b->moving_right ? speed : -speed;
            b->x += b->vx * dt;

            /* Initiate charge if player is aligned */
            if (abs((int)(px / CELL_SIZE) - (int)(b->x / CELL_SIZE)) < 5 && b->charge_timer <= 0) {
                b->charging = true;
                b->charge_vx = (px > b->x) ? 500 : -500;
                b->charge_timer = 20;
            }
        }
    } else {
        b->moving_right = (px > b->x - 50);
        b->vx = b->moving_right ? speed : -speed;
        b->x += b->vx * dt;
    }

    /* Vertical sine float */
    b->y = b->base_y + sinf(GetTime() * (1.5f + b->phase)) * 30;

    /* Attacking */
    b->attack_timer--;
    if (b->attack_timer <= 0 && *count < MAX_BULLETS - 5) {
        if (b->phase == 0) {
            /* Single shot */
            Projectile* bl = &bullets[*count]; (*count)++;
            bl->x = b->x; bl->y = b->y;
            bl->vx = (px > b->x) ? 250 : -250; bl->vy = 0;
            bl->damage = 1; bl->active = true; bl->life = 120;
            bl->ch = 'O'; bl->color = RED;
            b->attack_timer = 40;
        } else if (b->phase == 1) {
            /* Burst of 3 */
            for (int i = -1; i <= 1; i++) {
                Projectile* bl = &bullets[*count]; (*count)++;
                bl->x = b->x; bl->y = b->y;
                bl->vx = (px > b->x) ? 250 : -250;
                bl->vy = i * 60;
                bl->damage = 1; bl->active = true; bl->life = 120;
                bl->ch = 'O'; bl->color = RED;
            }
            b->attack_timer = 30;
        } else {
            /* Spread of 5 */
            for (int i = -2; i <= 2; i++) {
                Projectile* bl = &bullets[*count]; (*count)++;
                bl->x = b->x; bl->y = b->y;
                bl->vx = (px > b->x) ? 300 : -300;
                bl->vy = i * 50;
                bl->damage = 2; bl->active = true; bl->life = 100;
                bl->ch = 'O'; bl->color = RED;
            }
            b->attack_timer = 25;
        }
    }

    /* Boss death */
    if (b->hp <= 0) b->active = false;
}

/* ─── Projectile Update ──────────────────────────── */

void UpdateProjectiles(Projectile* bullets, int* count, float dt) {
    for (int i = 0; i < *count; i++) {
        if (!bullets[i].active) continue;
        bullets[i].x += bullets[i].vx * dt;
        bullets[i].y += bullets[i].vy * dt;
        bullets[i].life--;
        if (bullets[i].life <= 0) { bullets[i].active = false; continue; }

        int gx = (int)(bullets[i].x / CELL_SIZE);
        int gy = (int)(bullets[i].y / CELL_SIZE);
        if (IsSolid(gx, gy)) bullets[i].active = false;
    }

    /* Compact array */
    int write = 0;
    for (int i = 0; i < *count; i++) {
        if (bullets[i].active) {
            if (i != write) bullets[write] = bullets[i];
            write++;
        }
    }
    *count = write;
}

/* ─── Collision Detection ────────────────────────── */

static inline bool RectsOverlap(float ax, float ay, float aw, float ah,
                                 float bx, float by, float bw, float bh) {
    return (ax < bx + bw && ax + aw > bx &&
            ay < by + bh && ay + ah > by);
}

void CheckCollisions(Game* g) {
    Player* p = &g->player;
    float ps = CELL_SIZE * 0.7f;

    /* Player bullets → enemies */
    for (int i = 0; i < g->player_bullet_count; i++) {
        Projectile* b = &g->player_bullets[i];
        if (!b->active) continue;

        /* Check vs enemies */
        for (int e = 0; e < g->enemy_count; e++) {
            Enemy* en = &g->enemies[e];
            if (!en->active) continue;
            if (RectsOverlap(b->x, b->y, 8, 8, en->x, en->y, ps, ps)) {
                en->hp -= b->damage;
                b->active = false;
                if (en->hp <= 0) {
                    en->active = false;
                    p->score += en->score_value;
                    /* Drop power-up? */
                    if (GetRandomValue(0, 4) == 0 && g->powerup_count < MAX_POWERUPS) {
                        Powerup* pu = &g->powerups[g->powerup_count]; g->powerup_count++;
                        pu->x = en->x; pu->y = en->y;
                        pu->type = GetRandomValue(0, 1);
                        pu->active = true;
                        pu->ch = (pu->type == 0) ? 'S' : 'R';
                        pu->color = (pu->type == 0) ? GREEN : SKYBLUE;
                    }
                }
                break;
            }
        }

        /* Check vs boss */
        if (g->boss.active) {
            if (RectsOverlap(b->x, b->y, 8, 8, g->boss.x, g->boss.y, ps * 2, ps * 2)) {
                g->boss.hp -= b->damage;
                b->active = false;
            }
        }
    }

    /* Enemy bullets → player */
    for (int i = 0; i < g->enemy_bullet_count; i++) {
        Projectile* b = &g->enemy_bullets[i];
        if (!b->active) continue;
        if (RectsOverlap(b->x, b->y, 8, 8, p->x, p->y, ps, ps)) {
            b->active = false;
            PlayerTakeDamage(p, b->damage);
        }
    }

    /* Enemy contact → player */
    for (int e = 0; e < g->enemy_count; e++) {
        Enemy* en = &g->enemies[e];
        if (!en->active) continue;
        if (RectsOverlap(en->x, en->y, ps, ps, p->x, p->y, ps, ps)) {
            PlayerTakeDamage(p, 1);
        }
    }

    /* Boss contact → player */
    if (g->boss.active) {
        if (RectsOverlap(g->boss.x, g->boss.y, ps * 2, ps * 2, p->x, p->y, ps, ps)) {
            PlayerTakeDamage(p, 1);
        }
    }

    /* Power-up pickup */
    for (int i = 0; i < g->powerup_count; i++) {
        Powerup* pu = &g->powerups[i];
        if (!pu->active) continue;
        if (RectsOverlap(pu->x, pu->y, ps, ps, p->x, p->y, ps, ps)) {
            p->weapon = pu->type + 1;
            pu->active = false;
        }
    }
}

/* ─── Wave System ────────────────────────────────── */

void SpawnWave(Game* g) {
    g->wave++;
    int enemies_in_wave = 3 + g->wave * 2;
    if (enemies_in_wave > MAX_ENEMIES) enemies_in_wave = MAX_ENEMIES;

    g->enemy_count = 0;
    int spawned = 0;

    for (int i = 0; i < NUM_SPAWNS && spawned < enemies_in_wave; i++) {
        int spawn_idx = (g->wave * 7 + i * 3) % NUM_SPAWNS;
        const SpawnPoint* sp = &SPAWNS[spawn_idx];

        /* Only spawn enemies ahead of the player */
        if (sp->x * CELL_SIZE < g->player.x) continue;

        EnemyInit(&g->enemies[g->enemy_count], sp->type,
                  sp->x * CELL_SIZE, sp->y * CELL_SIZE);
        g->enemy_count++;
        spawned++;
    }

    g->total_spawned += spawned;
}

#endif
