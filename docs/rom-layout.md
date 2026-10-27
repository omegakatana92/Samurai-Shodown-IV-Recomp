# ROM layout — MAME set `samsho4` (NGH-222)

Validated against MAME's `src/mame/snk/neogeo.cpp`, `ROM_START( samsho4 )`.
All 15 game files and the 4 required system-ROM files were checked by size,
CRC32 and SHA1 with `python scripts/validate-roms.py roms`; every one matched.

## Game set

| File | Size | CRC32 | MAME load | Role |
|---|---:|---|---|---|
| `222-p1.p1` | 1,048,576 | `1a5cb56d` | `ROM_LOAD16_WORD_SWAP` @ 0x000000 | 68000 program, fixed bank |
| `222-p2.sp2` | 4,194,304 | `b023cd8b` | `ROM_LOAD16_WORD_SWAP` @ 0x100000 | 68000 program, banked area |
| `222-s1.s1` | 131,072 | `8d3d3bf9` | `NEO_SFIX_128K` | fixed-layer graphics |
| `222-m1.m1` | 131,072 | `7615bc1b` | `NEO_BIOS_AUDIO_128K` | Z80 sound driver |
| `222-v1.v1` | 4,194,304 | `7d6ba95f` | `ROM_LOAD` @ 0x000000 | ADPCM-A samples |
| `222-v2.v2` | 4,194,304 | `6c33bb5d` | `ROM_LOAD` @ 0x400000 | ADPCM-A samples |
| `222-v3.v3` | 2,097,152 | `831ea8c0` | `ROM_LOAD` @ 0x800000 | ADPCM-A samples |
| `222-c1.c1` | 4,194,304 | `68f2ed95` | `ROM_LOAD16_BYTE` @ 0x0000000 | sprite planes 0,1 |
| `222-c2.c2` | 4,194,304 | `a6e9aff0` | `ROM_LOAD16_BYTE` @ 0x0000001 | sprite planes 2,3 |
| `222-c3.c3` | 4,194,304 | `c91b40f4` | `ROM_LOAD16_BYTE` @ 0x0800000 | sprite planes 0,1 |
| `222-c4.c4` | 4,194,304 | `359510a4` | `ROM_LOAD16_BYTE` @ 0x0800001 | sprite planes 2,3 |
| `222-c5.c5` | 4,194,304 | `9cfbb22d` | `ROM_LOAD16_BYTE` @ 0x1000000 | sprite planes 0,1 |
| `222-c6.c6` | 4,194,304 | `685efc32` | `ROM_LOAD16_BYTE` @ 0x1000001 | sprite planes 2,3 |
| `222-c7.c7` | 4,194,304 | `d0f86f0d` | `ROM_LOAD16_BYTE` @ 0x1800000 | sprite planes 0,1 |
| `222-c8.c8` | 4,194,304 | `adfc50e3` | `ROM_LOAD16_BYTE` @ 0x1800001 | sprite planes 2,3 |

Totals: 5 MB program (1 MB fixed + 4 MB banked), 32 MB sprite data,
10 MB ADPCM-A, 128 KB fixed layer, 128 KB Z80 program.

## System set (`neogeo.zip`)

| File | Size | CRC32 | Role |
|---|---:|---|---|
| `sp-s2.sp1` | 131,072 | `9036d879` | MVS Asia/Europe v2 BIOS (default `--bios`) |
| `sfix.sfix` | 131,072 | `c2ea0cfd` | BIOS fixed-layer graphics |
| `sm1.sm1` | 131,072 | `94416d67` | BIOS Z80 sound driver |
| `000-lo.lo` | 131,072 | `5a86cff2` | sprite shrink table |

## How the dump maps into `ng_game_t`

* **P ROM.** Both files are stored 16-bit word-swapped, so `swap = 1`. After
  the swap the fixed bank carries `NEO-GEO` at `$100`; the cartridge header
  entry points at `$122` (`jmp`), `$128`, `$12E` and `$134` are what the BIOS
  calls. `prom_size = 0x500000`: the first 1 MB is the fixed bank at
  `$000000-$0FFFFF`, the remaining 4 MB are four 1 MB banks behind the
  `$200000` window, selected through `$2FFFF0-$2FFFFF`.
* **C ROMs.** MAME loads them as four `ROM_LOAD16_BYTE` pairs, 8 MB per pair
  at `0x0000000`, `0x0800000`, `0x1000000`, `0x1800000`. The runtime's
  `crom_pairs` interleaves each pair byte-for-byte into the same 32 MB
  layout, which the per-scanline sprite renderer indexes directly.
* **V ROMs.** Concatenated in MAME order into one 10 MB ADPCM-A space; the
  YM2610's ADPCM-A address map selects within it.
* **S ROM / M1.** Single 128 KB files, copied as-is.

## Hardware profile

| Item | Result |
|---|---|
| Board | standard MVS/AES PROGBK1 cart, normal (non-`PROT`) board |
| Encryption | none |
| Protection / daughterboard | none (no CMC42/CMC50, no `sfight2k`-style protection) |
| Banking | 4 × 1 MB window at `$200000`; bank-select byte at `$2FFFFF` |
| Raster / IRQ | standard LSPC, IRQ1 (VBlank) and IRQ2 (timer) |
| Sound | standard M1 driver + YM2610 (SSG, FM, ADPCM-A/B) |

The 222-p2 bank contains code; only bank 0 can run as recompiled native code,
because a native routine is tied to the bytes of one bank. The generic
bank-aware dispatcher in `docs/toolkit-patches.md` (§4) interprets the other
banks instead of running the wrong bank's translation. For this title the
profile pass reached 100% native on the tested sessions, so no measured
execution landed in banks 1-3.
