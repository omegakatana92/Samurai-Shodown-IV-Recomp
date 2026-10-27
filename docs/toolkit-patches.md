# Local changes to NeoGeoRecomp v0.2.0

The vendored toolkit is upstream **v0.2.0**, commit
`af96b2b4b39b42b392b17bcaa6a74a5f27088202`, with three patches applied, in
this order:

| Patch | Files | Purpose |
|---|---|---|
| `patches/0001-generic-runtime-and-fullscreen.patch` | `src/bus.c`, `src/exec.c`, `src/io.c`, `src/neogeo.c`, `src/ng_internal.h`, `src/platform.c`, `src/video.c`, `src/window_sdl.c`, `include/neogeorecomp/bus.h`, `docs/running.md` | watchdog, bank-aware dispatch, coverage reporting, fullscreen/aspect, sprite bounds |
| `patches/0002-toolkit-gamepad-test-portability.patch` | `tests/gamepad_test.c` | keep the gamepad test building after 0001 and on SDL < 2.26 |
| `patches/0003-window-error-reporting.patch` | `src/window_sdl.c` | report window/renderer/texture creation failures instead of running invisibly |

Patch 0001 was written for this toolkit version by the Real Bout Fatal Fury 2
port. Patches 0002 and 0003 are this port's fixes for problems visible after
0001. None of them contains a title-specific address, symbol or bypass.

To reproduce the vendored tree from scratch:

```bash
git clone --recurse-submodules https://github.com/sp00nznet/neogeorecomp
cd neogeorecomp
git checkout af96b2b4b39b42b392b17bcaa6a74a5f27088202
git apply /path/to/patches/0001-generic-runtime-and-fullscreen.patch
git apply /path/to/patches/0002-toolkit-gamepad-test-portability.patch
git apply /path/to/patches/0003-window-error-reporting.patch
```

Everything else under `neogeorecomp/` is byte-identical to upstream.

## What the patch changes

### 1. Watchdog reset

v0.2.0 decoded the watchdog ports as open bus. The real MVS resets the board
when `$300001` is not stroked for 3,244,030 master clocks (1,622,015 68000
clocks). Several SNK carts clear backup RAM at first boot and then idle until
the watchdog restarts them.

- any odd write in `$300000-$3BFFFF` strokes the watchdog;
- the frame scheduler polls the deadline and performs a board reset at the
  next scanline, preserving work RAM and backup RAM;
- the reset re-runs the BIOS and the 68000 reset vector without resetting the
  audio/video timeline.

Samurai Shodown IV boots to its attract mode and into matches with this in
place. It was not tested with the patch removed, so the project does not
claim the game *needs* it; it is included because it is the documented
behaviour of the board.

### 2. Sprite tile bounds

A C ROM whose tile count is not a power of two (48 MB / 96 MB carts) could
make the renderer index past the decoded data after the LSPC mask. The
renderer now skips tile numbers beyond the fitted tile count. Samurai
Shodown IV has 32 MB of sprites (262,144 tiles), so this path is defensive
here rather than required.

### 3. Fullscreen and aspect-correct scaling

Adds `--fullscreen`, an F11 / Alt+Enter toggle, `SDL_WINDOW_FULLSCREEN_DESKTOP`,
the scaling hint `SDL_ScaleModeNearest`, and an explicit centred destination
rectangle with a uniform 320x224 scale. The picture is pillarboxed on a 16:10
Steam Deck panel and letterboxed on 16:9, never stretched.

### 4. Bank-aware dispatch

The recompiler analyses the fixed bank and the **first megabyte** of the
banked area (`prom + 0x100000`, mapped at `$200000`). On a multi-bank cart,
the same window address holds different code depending on the bank register.
v0.2.0 dispatched a native entry for the window without checking the selected
bank, so after a bank switch it could run the wrong bank's translation.

`lookup()` now returns the interpreter whenever the window address is outside
bank 0, and `--dump-misses` ignores addresses recorded while another bank is
selected. An odd PC is also sent to the interpreter so Musashi raises the
68000 address error instead of aliasing the even address below it.

Samurai Shodown IV has four 1 MB banks, so this is a correctness fix that
matters here. On the tested sessions no executed code landed in banks 1-3
(all measured execution was bank 0 or the fixed bank), which is why native
coverage still measured 100%; the guard prevents silent corruption if play
ever reaches another bank.

### 5. Coverage reporting

`exec_report()` adds an instruction-based line:

```
[coverage] native instructions 447307769, interpreted 0, 100.000% native
```

`ng_icount` counts instructions executed by generated code and
`exec_interp_instrs` counts interpreted ones. `NG_TIMING=1` additionally
prints the simulated 68000 clocks.

## Verification of the patched toolkit

The toolkit's own conformance harness was built from this vendored tree and
run against Musashi's 68000 corpus; the result is recorded in
`docs/compatibility.md`. The patches do not touch the 68000 emitter, the
decoder or the CPU helpers, so conformance matches upstream: **59/60**, with
the reference interpreter also at 59/60. `ctest` passes 2/2 on Windows and on
Linux (the virtual-gamepad test self-skips on the SDL 2.0.20 shipped by
Ubuntu 22.04).

Upstream MIT licensing and notices are unchanged (`neogeorecomp/LICENSE`,
`neogeorecomp/NOTICE`).

## Patch 0002: gamepad test portability

Patch 0001 adds a third argument to `window_open()`, and the toolkit's own
`tests/gamepad_test.c` still called the two-argument form, so a tests-enabled
build failed to link/compile. It also uses `SDL_VirtualJoystickDesc`, which
only exists from **SDL 2.26** (Ubuntu 22.04 ships 2.0.20, and so do some
SteamOS-adjacent distributions). The test now passes the new argument and
compiles out the virtual-pad body below 2.26, reporting itself skipped. On
SDL ≥ 2.26 (the Windows build uses 2.32.10) the full mapping test still runs
and passes.

## Patch 0003: window error reporting

`window_open()` did not check `SDL_CreateWindow`, `SDL_CreateRenderer` or
`SDL_CreateTexture`. On a host where fullscreen or GL creation fails, the game
then ran with a NULL window and exited successfully without showing anything —
confusing, and it made automated window tests look green. It now:

- returns an error with `SDL_GetError()` text if the window, renderer or
  texture cannot be created;
- falls back to the software renderer when no accelerated one is available
  (useful headless/Xvfb, harmless on a Deck).

This was found while testing the AppImage under Xvfb without a window manager;
with the fix the failure is reported instead of hidden.

## Windows toolchain note

MSVC's optimizer can grow superlinearly on the giant generated dispatch
functions. The supported Windows build therefore uses **clang-cl** (MSVC ABI,
Windows SDK, MSVC runtime) driven by Ninja; `scripts/build-windows.ps1 -Msvc`
selects the Visual Studio/MSVC toolset instead. Both produce a normal native
Windows x64 executable. This is a compiler-behaviour note, not a code change.
