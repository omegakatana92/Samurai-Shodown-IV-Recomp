# Building and testing

Reproduce every result in `docs/compatibility.md` from a clean folder.

## 0. ROMs

Unzip your legally obtained MAME `samsho4` and `neogeo` sets into `roms/`
(one flat folder, 19 files) and validate them:

```bash
python scripts/validate-roms.py roms
```

Expected last line: `result: all files verified`.

## 1. Windows x64

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1 -RomDir .\roms -Test
```

What it does: configures `build-windows` with Ninja + clang-cl (MSVC ABI),
builds `Samsho4.exe` in Release, runs a headless smoke test, stages
`dist\windows\Samsho4-Windows-x64\`. Add `-Msvc` for the Visual Studio
generator, `-SdlDir <...>` for an SDL2 outside `deps/sdl2`.

Build without a window (interpreter-only smoke):

```powershell
cmake -S . -B build-interp -G Ninja -DCMAKE_BUILD_TYPE=Release `
      -DCMAKE_C_COMPILER=clang-cl -DCMAKE_CXX_COMPILER=clang-cl -DSAMSHO4_ROM_DIR=
cmake --build build-interp
.\build-interp\Samsho4.exe --headless --rom-path .\roms --frames 1200
```

## 2. Linux / AppImage

```bash
./scripts/build-linux.sh ./roms                 # binary only -> build-linux/Samsho4
./packaging/appimage/build-appimage.sh ./roms   # -> dist/steamdeck/*.AppImage
```

The AppImage script builds Release, strips, collects the SDL2 it linked
against, writes `AppRun` (ROM discovery + fullscreen), the desktop entry and
icon, copies the licences, downloads `appimagetool` if needed and packs with
`--no-appstream`.

On a headless host, run the AppImage with `APPIMAGE_EXTRACT_AND_RUN=1` if
FUSE is unavailable.

## 3. Interpreter first

```bash
./build-windows/Samsho4.exe --headless --interp --rom-path ./roms --frames 3600 \
  --screenshot 600:600.png --screenshot 2400:2400.png --screenshot 3599:3599.png
```

This exercises the board model without any recompiled code. The BIOS
self-test, eyecatcher, intro and menu pages should be correct here before
looking at native execution.

## 4. Native build and frame comparison

Rebuild with `SAMSHO4_ROM_DIR` set (the scripts do this) and capture the same
frames, then compare hashes with the interpreter run:

```powershell
.\build-windows\Samsho4.exe --headless --rom-path .\roms --frames 3600 `
  --screenshot 600:n600.png --screenshot 2400:n2400.png --screenshot 3599:n3599.png
Get-FileHash 600.png,n600.png -Algorithm SHA256
```

Frames 400, 600, 2400 and 3599 were byte-identical in the delivered build.

## 5. Correctness (`--verify`)

```powershell
.\build-windows\Samsho4.exe --headless --verify --rom-path .\roms --frames 24000 `
  --input tests\play_long.txt
```

Expected:

```
[verify] 22255974 blocks checked, 0 mismatches
[exec] native blocks 22255974, interpreted instructions 0, 0 uncovered entry points
[coverage] native instructions 447307767, interpreted 0, 100.000% native
```

The block count depends on the compiler's block boundaries; the instruction
count and the "0 mismatches" do not.

## 6. Profiling (close native coverage gaps)

```powershell
cmake --build build-windows --target profile
cmake --build build-windows
```

`profile` runs a 6,000-frame boot and the 24,000-frame soak with
`--dump-misses`, merging runtime-only entry points into `build-windows/entries.txt`.
The rebuild regenerates the C with `--entries`. Before the pass the soak
reported 99.890% native and 23 uncovered entry points; after it, 100.000% and
0. Entry lists are ROM-derived and never committed.

## 7. Audio

```bash
./Samsho4 --headless --rom-path ./roms --frames 3600 --wav boot.wav
python3 - <<'PY'
import wave, struct, math
w = wave.open("boot.wav"); n = w.getnframes(); r = w.getframerate()
a = struct.unpack("<%dh" % (n * w.getnchannels()), w.readframes(n))
print(r, "Hz", n / r, "s", "peak", max(abs(x) for x in a),
      "rms", round(math.sqrt(sum(x*x for x in a)/len(a)), 1))
PY
```

Delivered build: 55,555 Hz stereo, 60.81 s, peak 25,744 (−2.1 dBFS).

## 8. Windowed and fullscreen on Linux (headless host)

```bash
Xvfb :99 -screen 0 1280x800x24 -ac &
DISPLAY=:99 openbox &
DISPLAY=:99 APPIMAGE_EXTRACT_AND_RUN=1 ./dist/steamdeck/Samsho4-SteamDeck-x86_64.AppImage \
  --rom-path ./roms --frames 2200 &
DISPLAY=:99 import -window root shot.png
```

`import` (ImageMagick) with `imagemagick` and `x11-apps` installed. Measure the
non-black bounding box: at 1280×800 the game occupies 1143×800, centred at
x=68 (aspect 1.4287), with black pillarboxes. Without a window manager SDL's
fullscreen request can fail, which is why `openbox` is started first.

## 9. Toolkit regression tests

```bash
cmake -S neogeorecomp -B /tmp/ng-tests -DCMAKE_BUILD_TYPE=Release \
      -DNEOGEORECOMP_BUILD_TESTS=ON
cmake --build /tmp/ng-tests --parallel 8
ctest --test-dir /tmp/ng-tests --output-on-failure
```

Expected: conformance 59/60 (reference interpreter 59/60), gamepad test passes
on SDL ≥ 2.26 and self-skips below it.

## 10. Steam Deck

Copy the AppImage and `roms/` to the Deck, add the AppImage as a non-Steam
game (Proton off), launch once in Desktop Mode, then play in Gaming Mode.
**This step was not performed in this workspace** — no Deck hardware was
available.

## Clean rebuild

```powershell
Remove-Item -Recurse build-windows,dist
```

```bash
rm -rf build-linux dist
```

Deleting the build tree also deletes `entries.txt` (the profile result), so
the next build starts from static discovery only. Keep the file if you want to
reproduce the 100% coverage numbers without re-profiling.
