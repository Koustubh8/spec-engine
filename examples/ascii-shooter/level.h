/*
 * level.h — Level data, terrain definitions, collision
 *
 * Requirement: level-layout [SHALL]
 * Requirement: terrain-collision [SHALL]
 * Constraint: single-designed-level
 */
#ifndef LEVEL_H
#define LEVEL_H

#include <stdbool.h>

#define LVL_H 20
#define LVL_W 200

/* Level defined as a 2D char array.
 * ' ' = air, '#' = wall, '.' = floor, 'P' = player spawn */
static const char LEVEL_DATA[LVL_H][LVL_W] = {
    /* 0-9     1-9     2-9     3-9     4-9     5-9     6-9     7-9     8-9     9-9     10-9    11-9    12-9    13-9    14-9    15-9    16-9    17-9    18-9    19-9 */
    {"                                                                                              "},
    {"                                                                                              "},
    {"                                                                                              "},
    {"                                                                                              "},
    {"                                  ############                                                "},
    {"                                                                              #####           "},
    {"                                                          ####                                "},
    {"                ########                                                        ###    ##     "},
    {"                                                              ##                         #    "},
    {"     ######                                                       #####              ##      "},
    {"                         #####                                          ####                "},
    {"                                                      ##                              #      "},
    {"           ###                              ###                      ###              ##     "},
    {"                                                      ##                      ######         "},
    {"                         #                                                    ##             "},
    {"   P..........#####..........................####.......................####..........####...P"},
    {"############.......#######......#########..............########......................########"},
    {"########################################################################################################"},
    {"########################################################################################################"},
    {"########################################################################################################"},
};

/* Spawn points for enemies: (col, row, type)
 * type: 0=walker, 1=shooter, 2=flyer */
typedef struct { int x, y, type; } SpawnPoint;

#define NUM_SPAWNS 30
static const SpawnPoint SPAWNS[NUM_SPAWNS] = {
    {25, 14, 0}, {30, 14, 0}, {35, 10, 2},
    {42, 14, 1}, {48, 14, 0}, {50, 14, 0},
    {55, 8,  2}, {58, 14, 1}, {62, 14, 0},
    {68, 14, 0}, {72, 6,  2}, {75, 14, 1},
    {78, 14, 0}, {82, 10, 2}, {85, 14, 0},
    {90, 14, 1}, {92, 14, 0}, {95, 8,  2},
    {100, 14, 0}, {105, 14, 1}, {108, 14, 0},
    {112, 6, 2}, {115, 14, 0}, {120, 14, 1},
    {125, 14, 0}, {130, 10, 2}, {135, 14, 1},
    {140, 14, 0}, {145, 14, 0}, {150, 14, 1},
};

/* Boss fight triggered after column 170 */
#define BOSS_TRIGGER_X 170

/* Grid queries */
static inline bool IsSolid(int x, int y) {
    if (x < 0 || x >= LVL_W || y < 0 || y >= LVL_H) return true;
    return LEVEL_DATA[y][x] == '#';
}

static inline bool IsFloor(int x, int y) {
    if (x < 0 || x >= LVL_W || y >= LVL_H) return false;
    if (y < 0) return true;  /* top of screen = can jump through */
    return LEVEL_DATA[y][x] == '.' || LEVEL_DATA[y][x] == '#';
}

static inline bool IsDeathPit(int y) {
    return y >= LVL_H;  /* fell off bottom */
}

#endif
