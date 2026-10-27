/*
 * game.c — the Samurai Shodown IV: Amakusa's Revenge (MAME set `samsho4`,
 * NGH-222) ROM layout, shared by the player and the generator so both load
 * the program identically.
 *
 * The layout is MAME's ROM_START( samsho4 ) in src/mame/snk/neogeo.cpp:
 *
 *   P ROM  $500000 = 1 MB fixed (222-p1.p1) + 4 MB banked (222-p2.sp2),
 *          both stored 16-bit word-swapped (ROM_LOAD16_WORD_SWAP).
 *   C ROMs 32 MB in four 8 MB odd/even pairs (ROM_LOAD16_BYTE: c1 at even
 *          bytes, c2 at odd bytes, and so on), i.e. planes 0/1 and 2/3.
 *   S ROM  222-s1.s1  (fixed layer)
 *   M1     222-m1.m1  (Z80 sound driver)
 *   V ROMs 10 MB ADPCM-A: v1, v2 (4 MB each) and v3 (2 MB), concatenated.
 *
 * The cart is a normal PROGBK1 MVS/AES board: four 1 MB banks behind the
 * $200000 window, selected through $2FFFF0-$2FFFFF. No encryption, no CMC
 * protection, no daughterboard. The fixed bank carries the "NEO-GEO"
 * signature at $100 after the word swap, which is what the loader assumes.
 */
#include "game.h"

const ng_game_t k_samsho4 = {
    .name = "samsho4",
    .title = "Samurai Shodown IV - Amakusa's Revenge",
    .prom_size = 0x500000,
    .prom = {
        /* file          file offset  dest       length    swap */
        {"222-p1.p1",  0x000000,    0x000000,  0x100000, 1},
        {"222-p2.sp2", 0x000000,    0x100000,  0x400000, 1},
    },
    .crom_size = 0x2000000,
    .crom_pairs = {
        {"222-c1.c1", "222-c2.c2"},
        {"222-c3.c3", "222-c4.c4"},
        {"222-c5.c5", "222-c6.c6"},
        {"222-c7.c7", "222-c8.c8"},
    },
    .srom = "222-s1.s1",
    .m1 = "222-m1.m1",
    .vrom = {"222-v1.v1", "222-v2.v2", "222-v3.v3"},
};
