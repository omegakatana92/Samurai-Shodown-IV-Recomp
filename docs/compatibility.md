# Compatibility and verification report

Game: **Samurai Shodown IV — Amakusa's Revenge** (MVS/AES), MAME set
`samsho4`, NGH-222.

Toolkit: **NeoGeoRecomp v0.2.0**, commit
`af96b2b4b39b42b392b17bcaa6a74a5f27088202`, plus the generic fixes in
`docs/toolkit-patches.md` (`patches/0001-…` and `patches/0002-…`).

Everything below was run in this workspace. Anything not run is marked
**untested**, not assumed.

## Hardware profile

| Area | Result |
|---|---|
| 68000 program | 5 MB P ROM: 1 MB fixed + four 1 MB banks |
| Encryption / protection | none (normal PROGBK1 MVS/AES cart) |
| C ROMs | 32 MB, four odd/even pairs, no CMC decryption |
| S ROM | 128 KB fixed layer |
| M ROM | 128 KB Z80 driver |
| V ROMs | 10 MB ADPCM-A/B |
| BIOS | real `sp-s2.sp1` (MVS Asia/Europe v2), no BIOS HLE |
| Banking | standard `$2FFFF0-$2FFFFF` 1 MB window; recompiler covers bank 0 |

## ROM validation — passed

All 15 game files and the 4 required system-ROM files match MAME
`ROM_START( samsho4 )` by size, CRC32 and SHA1
(`python scripts/validate-roms.py roms`). Table in `docs/rom-layout.md`.

## Boot and hardware

| Test | Environment / run | Result |
|---|---|---|
| Interpreter boot, 3,600 frames | Windows x64, headless | **Passed**; BIOS self-test, eyecatcher, intro, HOW TO PLAY |
| Native boot, 3,600 frames | Windows x64, headless | **Passed**; 1,540,668 blocks, 68,689,480 instructions, 100.000% native, 0 uncovered |
| Native frames vs interpreter | frames 400, 600, 2400, 3599 | **Byte-identical** PNGs (SHA-256 match) |
| Windows vs Linux frames | frame 400, separate builds | **Byte-identical** PNGs (`EF9A41DD…`) |
| Windowed launch | Windows x64, SDL2 2.32 | **Passed**, exit 0, 600 frames |
| Fullscreen launch | Windows x64, `--fullscreen` | **Passed**, exit 0, 400 frames |
| Windowed + fullscreen launch | Linux AppImage under Xvfb 1280×800 + openbox | **Passed**, exit 0 |
| Aspect at 1280×800, fullscreen | X11 screen capture | content **1143×800** at x=68, aspect **1.4287** (target 320/224 = 1.4286); black pillarboxes, not stretched |
| Audio | 3,600-frame `--wav`, native | **60.81 s**, 55,555 Hz stereo, peak −2.1 dBFS, RMS −18.8 dBFS |

## Recompilation and correctness

| Metric | Result |
|---|---|
| Static discovery | 42,815 dispatch entries |
| After one profile pass (6,000 + 24,000 frames) | **42,838** entries (+23) |
| Coverage before profiling, 24,000 frames | 99.890% (446,815,292 native / 492,477 interpreted, 23 uncovered) |
| `--verify`, 24,000 frames, Windows final build | **22,255,974 blocks, 0 mismatches** |
| `--verify`, 24,000 frames, AppImage final build | **22,256,161 blocks, 0 mismatches** |
| Native instructions, 24,000 frames (both builds) | **447,307,767** — identical across platforms |
| Interpreted instructions after profiling | **0** |
| Uncovered entry points after profiling | **0** |
| Native coverage | **100.000%** of the executed instructions in these sessions |

Block counts differ slightly between the Windows and Linux builds because the
`--verify` replay groups instructions differently at block boundaries; the
instruction count, register/flag results and write sequences are identical.

The 100% figure is measured over the scripted sessions (boot, attract, menus,
and repeated matches driven by `tests/play_long.txt`). It is not a proof that
every reachable path in a 5 MB program is native; banked code in banks 1-3
would still interpret by design, and no measured execution reached them.

### Toolkit regression

The vendored, patched toolkit was built with `NEOGEORECOMP_BUILD_TESTS=ON`:

| Host | `ctest` | Conformance |
|---|---|---|
| Linux (Ubuntu 22.04, gcc 11.4, SDL 2.0.20) | 2/2 passed (gamepad test self-skips on SDL < 2.26) | **59/60**, reference interpreter 59/60 |
| Windows (clang-cl, SDL 2.32.10) | gamepad + conformance pass | **59/60**, reference interpreter 59/60 |

The one failure is Musashi's `move` test program, which uses a 68020
addressing mode that the reference 68000 interpreter fails too.

`ng_gamepad_test` (Windows, SDL 2.32 virtual pads) passes: D-pad, left stick,
A/B/X/Y → A/B/C/D, Start, Back → coin, two pads, and unplugging all map as
documented. No physical controller was tested.

## Gameplay

| Item | Result |
|---|---|
| BIOS warning / eyecatcher | Yes |
| Intro / story screens | Yes |
| Attract demonstration | Yes |
| HOW TO PLAY pages | Yes (observed "C-D BUTTONS COMBO SLASH") |
| Coin insertion | Yes (credit counter increments) |
| Start | Yes |
| Character select | Yes (full 4×5 grid, cursor, P1 marker) |
| Technique select (SLASH / BUST) | Yes |
| VS screen and pre-fight dialogue | Yes |
| Match: movement, A/B/C/D, hits, health bars, round timer | Yes |
| Combos / super moves / PERFECT / CONCLUSION screens | Observed during the soak |
| Match end, return to attract | Yes |
| Two-player versus | **Untested** |
| Test / service menu | **Untested** |
| Memory card | Not implemented by the toolkit |
| Audio device playback | **Untested** (WAV output verified) |
| Physical gamepad / Steam Input | **Untested** (mapping verified virtually) |

Screenshots collected during these runs are not shipped because they contain
SNK artwork.

## Windows deliverable

| Item | Result |
|---|---|
| Toolchain | clang-cl 22.1.7 (MSVC ABI, Windows SDK), Ninja, CMake 4.3.3, Release x64 |
| Build | **built**, 184 s clean, 42 generated/3 link steps |
| Package | `dist/windows/Samsho4-Windows-x64/` — exe + SDL2.dll + VC runtime + docs + licences |
| Headless smoke test | **Passed** (1,200 frames, 100.000% native) |
| Full soak, native | **Passed** (24,000 frames, 100.000% native) |
| `--verify` on the packaged exe | **Passed**, 22,256,231 blocks, 0 mismatches |
| ROMs in package | none |

## Steam Deck AppImage

| Item | Result |
|---|---|
| Build host | Windows 11 + WSL2, Ubuntu 22.04 x86_64, gcc 11.4, CMake 4.4.4, SDL2 2.0.20 |
| Output | `dist/steamdeck/Samsho4-SteamDeck-x86_64.AppImage`, 14,146,040 bytes, executable |
| Headless 24,000-frame run | **Passed**, 100.000% native, 0 uncovered |
| `--verify` on the AppImage | **Passed**, 22,255,970 blocks, 0 mismatches |
| Windowed launch (1280×800 Xvfb) | **Passed**, exit 0 |
| Fullscreen launch via AppRun | **Passed**, exit 0, window 1280×800 |
| Aspect at 1280×800 | 1143×800 content centred, aspect 1.4287, black pillarboxes |
| `ldd` | no missing libraries; glibc/libstdc++/libgcc not bundled; SDL2 bundled in `usr/lib` |
| ROMs inside AppImage | none |
| Steam Deck hardware | **Not available**: Gaming Mode, Steam Input, LCD/OLED panels **untested** |
| Built against | glibc 2.35 (Ubuntu 22.04); SteamOS 3 is newer, so the ABI floor is met |

## Known limitations

* Native coverage is 100% for the scripted sessions only; banks 1-3 interpret
  by design if execution ever reaches them.
* No Steam Deck hardware, no physical gamepad, no keyboard-by-hand test, no
  two-player or service-menu test, no listening test on a real audio device.
* The toolkit's controller layout is fixed (no remapping).
* PolyForm Noncommercial 1.0.0 does not permit commercial distribution of the
  original code.
* No ROMs or BIOS files are bundled; a legally obtained `neogeo` set is
  required.
* Samurai Shodown IV is MVS/AES only in this port; the Korean set
  (`samsho4k`) and the bootleg/hack variants are not configured.

## Deliverables

| Path | Size | SHA-256 |
|---|---:|---|
| `dist/windows/Samsho4-Windows-x64/` | folder, exe 35,264,000 bytes | `Samsho4.exe`: see `dist/SHA256SUMS.txt` |
| `dist/steamdeck/Samsho4-SteamDeck-x86_64.AppImage` | 14,146,040 bytes | `b2cbcd0f74f2f563188350ca5e34f9083364a359e91da45990a3ae537ba7671d` |

`dist/SHA256SUMS.txt` lists every file in both packages.

Hashes and sizes are for the builds produced in this workspace. Rebuilds with
other compiler versions will differ; the source, the pinned toolkit commit and
the profile entries are what make the result reproducible.

## Test log index

| Artifact | Meaning |
|---|---|
| `build-windows/build.log` | clean Windows Release build |
| `build-windows/build-profile.log` | rebuild after the profile pass |
| `build-windows/verify-final.log` | 24,000-frame `--verify` on the packaged exe |
| `build-windows/smoke.log` | 1,200-frame packaged smoke test |
| `build-windows/ng-tests-build.log` | toolkit conformance/gamepad test build |
| `dist/steamdeck/README.txt` | user instructions for the AppImage |

Logs are build artifacts and are not committed.
