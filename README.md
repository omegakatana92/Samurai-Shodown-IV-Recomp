# Samurai Shodown IV — Amakusa's Revenge · native recompilation

A native port of **Samurai Shodown IV: Amakusa's Revenge** (SNK, MVS/AES,
MAME set `samsho4`, NGH-222) built on
[NeoGeoRecomp](https://github.com/sp00nznet/neogeorecomp) v0.2.0.

The 68000 program is translated ahead of time into C: one C function per
routine, with the original address and disassembly above every instruction,
and runs on a model of the MVS board. It is **not** an emulator wrapper. A
Musashi interpreter stays linked as the correctness oracle and as the
fallback for addresses that have no native entry; on the measured sessions
below **nothing** executed in it.

| Deliverable | Path | State |
|---|---|---|
| Windows x64 | `dist/windows/Samsho4-Windows-x64/` | built and tested |
| Steam Deck / Linux x86_64 AppImage | `dist/steamdeck/Samsho4-SteamDeck-x86_64.AppImage` | built and tested under Xvfb 1280×800; **not** run on Deck hardware |

No game ROMs or BIOS files are included. Both builds compile the recompiled C
from *your* dump at build time; the distribution contains no ROM-derived code.

## Status at a glance

| Area | Result |
|---|---|
| ROM validation | 15 game files + 4 BIOS files match MAME by size, CRC32 and SHA1 |
| Boot | Real MVS BIOS (`sp-s2.sp1`), no BIOS HLE; eyecatcher, intro, attract |
| Recompiled entry points | **42,838** (42,815 from static discovery, +23 from one profile pass) |
| `--verify` (24,000 frames) | **22.2 M blocks, 0 mismatches** |
| Native coverage (24,000-frame soak) | **100.000%**, 0 interpreted instructions, 0 uncovered entries |
| Native vs interpreter frames | byte-identical PNGs at frames 400, 600, 2400, 3599 |
| Graphics | sprites, fix layer, palettes, raster effects, zoom — checked in play |
| Audio | Z80 driver + YM2610 synthesize to WAV: 60.8 s, 55,555 Hz, peak −2.1 dBFS |
| Windows | Release x64, windowed and fullscreen tested, SDL2 + VC runtime shipped |
| Linux AppImage | built on Ubuntu 22.04, runs headless and windowed/fullscreen |
| Steam Deck hardware | **untested** (no Deck available); see limitations |

Full measurements and the test log index: [docs/compatibility.md](docs/compatibility.md).

## Requirements

* **Windows**: Windows 10/11 x64. Build with Visual Studio 2022/2026
  ("Desktop development with C++"), CMake 3.21+, Ninja and clang-cl (or use
  `-Msvc`). The SDL2 VC development package is expected under
  `deps/sdl2/<version>/`.
* **Linux**: gcc/g++, CMake 3.21+, make/ninja, `libsdl2-dev`, `pkg-config`,
  `python3`, `wget` (for appimagetool), and `libsdl2-dev` ≥ 2.26 if you want
  the toolkit's virtual-gamepad test.
* **Your ROMs**: the MAME `samsho4` and `neogeo` sets, unzipped into one
  folder. See [docs/rom-layout.md](docs/rom-layout.md).

## Getting started — Windows

```powershell
# ROMs first: unzip both sets into .\roms
python scripts\validate-roms.py roms
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1 -RomDir .\roms -Test
.\build-windows\Samsho4.exe --rom-path .\roms
```

`scripts\build-windows.ps1` configures with clang-cl + Ninja, builds Release,
runs a headless smoke test with `-Test`, and stages
`dist\windows\Samsho4-Windows-x64\` with the executable, SDL2, the VC runtime,
README, ROM layout and all licences.

To rebuild the native table after a profile pass:

```powershell
cmake --build build-windows --target profile   # plays tests\play_long.txt, dumps misses
cmake --build build-windows                    # regenerates and recompiles
```

## Getting started — Steam Deck / Linux

```bash
mkdir -p roms   # unzip samsho4.zip and neogeo.zip here
python3 scripts/validate-roms.py roms
./packaging/appimage/build-appimage.sh ./roms
./dist/steamdeck/Samsho4-SteamDeck-x86_64.AppImage
```

The AppImage auto-detects `roms/` beside itself (and the usual EmulationStation
folders), starts fullscreen on a 1280×800 panel with a uniform scale and black
pillarboxes, and uses SDL2 for video, audio and controllers. Copy the AppImage
plus `roms/` to the Deck, add it as a non-Steam game, and launch in Gaming Mode.

## Controls

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | arrows | D-pad / left stick |
| A B C D | Z X C V | A B X Y (Xbox positions) |
| Coin | 5 (6 = P2) | Back / View |
| Start | 1 (2 = P2) | Start |
| Select | 3 | left shoulder |
| Service / test | 9 / F2 | — |
| Fullscreen | F11 or Alt+Enter | — |
| Quit | Esc | — |

Two SDL GameControllers work: first connected is player 1, second player 2.
Steam Input's default gamepad template presents the Deck as an Xbox pad, which
is exactly the layout above. On MVS you must insert a coin before Start works.

## How the recompilation works

```
222-p1.p1 + 222-p2.sp2 ──► samsho4_recomp (m68krecomp) ──► build/generated/*.c
     + sp-s2.sp1              decode, discover, emit C              │
                                                                    ▼
                    neogeorecomp runtime ◄──── Samsho4.exe/.AppImage
   dispatcher · Musashi fallback · LSPC video · palette · I/O · Z80/YM2610 · SDL2
```

* Static discovery starts from the BIOS and cartridge vectors, the four
  cartridge-header entry points (`USER`, `PLAYER_START`, `DEMO_END`,
  `COIN_SOUND`), call targets, jump tables and code pointers. It found
  42,815 dispatch entries.
* One profile pass over a 6,000-frame boot and a 24,000-frame scripted soak
  added 23 runtime-only addresses; the rebuilt table has 42,838 entries.
* Control flow is flat: calls and returns travel through a dispatcher, return
  addresses live on the emulated stack, and interrupts are real 68000
  exceptions. The C stack does not grow with 68000 call depth.
* Banked code: the cart has four 1 MB banks behind `$200000`. A native entry
  is tied to one bank's bytes, so the dispatcher interprets whenever another
  bank is selected (see `docs/toolkit-patches.md` §4). Measured execution
  stayed in the fixed bank and bank 0.

## Correctness and coverage

`--verify` replays every native block in Musashi against the same memory and
I/O values and compares registers, flags and the write sequence. On the
24,000-frame soak it checks **22.2 million blocks with 0 mismatches**, and the
run reports **100.000% native instructions** with **0 uncovered entry points**.

Frames rendered by the recompiled build are byte-identical to the interpreter's
at several points across boot and attract mode (SHA-256 match).

## Repository layout

```
samsho iv/
  CMakeLists.txt           two stages: generator, then player
  src/                     game.c (ROM layout), main.c, recomp_main.c
  neogeorecomp/            vendored toolkit v0.2.0 + patches (MIT)
  patches/                 the exact local changes, applyable to upstream
  scripts/                 Windows build/stage, Linux build, ROM validator
  packaging/               Windows README, AppImage recipe, icon, .desktop
  tests/                   scripted input (coin/start, 24,000-frame soak)
  docs/                    rom-layout, compatibility, testing, toolkit patches
  build-windows/           Windows build tree (generated C lives here)
  build-linux/             Linux build tree
  dist/windows/            Windows package
  dist/steamdeck/          AppImage + README
```

ROMs, BIOS files, generated C and entry lists are never committed
(`.gitignore`), and none of them ship in `dist/`.

## Licensing

* Original project code (ROM layout, player glue, scripts, packaging, docs):
  **PolyForm Noncommercial 1.0.0** — free for noncommercial use; commercial
  use requires a separate licence. See `LICENSE` and `LICENSE-STATUS.md`.
* Vendored NeoGeoRecomp: **MIT** © 2026 sp00nznet, with the generic fixes in
  `patches/`. Musashi **MIT**, z80 **MIT**, ymfm **BSD-3**, SDL2 **zlib**.
  All notices ship in `THIRD_PARTY_NOTICES.md` and in `LICENSES/` in each
  release.
* The PolyForm licence covers only the original code. It grants no rights in
  SNK's game data, and it does not make distribution of ROM-derived material
  lawful where it otherwise would not be. Distribute source, or a binary built
  from your own dump, only where you have the rights to do so.

## Known limitations

* **Steam Deck hardware is untested.** The AppImage was built and validated on
  Linux x86_64 (WSL2 Ubuntu 22.04) at 1280×800 under Xvfb; Gaming Mode, Steam
  Input and LCD/OLED panels were not exercised on a physical Deck.
* No physical gamepad was available. The SDL GameController mapping is covered
  by the toolkit's virtual-pad test on Windows (SDL 2.32); a real pad and
  Steam Input were not tested.
* Keyboard handlers were not exercised by a human; the scripted input path and
  the game logic behind it were.
* Two-player versus, the test/service menu and the memory-card paths were not
  tested. The toolkit does not implement memory cards.
* Audio was verified by analysing a captured WAV; playback on a real audio
  device was not listened to.
* Banks 1-3 of the cartridge would run in Musashi by design; no measured
  execution reached them, so the 100% figure is for these sessions, not a
  proof that all code is native.
* The controller layout is fixed by the toolkit; remapping is not implemented.

## Credits

Toolkit: [NeoGeoRecomp](https://github.com/sp00nznet/neogeorecomp) by
sp00nznet and contributors. Header reference: MAME's Neo Geo driver and the
NeoGeo Development Wiki (no code copied). Musashi by Karl Stenerud, z80 by
Nicolas Allemand, ymfm by Aaron Giles, SDL2 by Sam Lantinga.

Samurai Shodown / Samurai Spirits, Neo Geo, MVS and AES are trademarks of SNK
Corporation. This project is unaffiliated with and not endorsed by SNK.
