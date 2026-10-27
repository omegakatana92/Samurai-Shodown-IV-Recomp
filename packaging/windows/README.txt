Samurai Shodown IV - Amakusa's Revenge
Native static recompilation for Windows x64
===========================================

This folder contains Samsho4.exe, SDL2.dll, the Visual C++ runtime DLLs and
the licences. It does NOT contain game ROMs or the Neo Geo BIOS.

Quick start
-----------
1. Put your legally obtained ROM files in the "roms" folder next to the
   executable (or anywhere else):

     samsho4.zip -> 222-p1.p1 222-p2.sp2 222-s1.s1 222-m1.m1
                    222-v1.v1 222-v2.v2 222-v3.v3
                    222-c1.c1 ... 222-c8.c8
     neogeo.zip  -> sp-s2.sp1 sfix.sfix sm1.sm1 000-lo.lo

   Unzip them: all 19 files must be directly in the same folder. See
   ROM-LAYOUT.md for sizes, CRC32 and SHA1.

2. Run Samsho4.exe. It looks for .\roms by default. For another folder:

     Samsho4.exe --rom-path "D:\NeoGeo\roms"

Controls
--------
  Arrows / left stick     move
  Z X C V / pad A B X Y   Neo Geo A B C D
  5 / Back                insert coin
  1 / Start               start
  3 / left shoulder       select
  9                       service
  F2                      test switch
  F11 or Alt+Enter        toggle fullscreen
  Esc                     quit

On MVS you must insert a coin before Start does anything. Up to two SDL
GameControllers work; the first is player 1, the second player 2.

Command line
------------
Run Samsho4.exe --help for the full list. Useful options:
  --rom-path DIR        game ROM files (default: roms)
  --bios-path DIR       BIOS files (default: the ROM path)
  --bios FILE           system ROM (default: sp-s2.sp1)
  --fullscreen          start fullscreen (F11 toggles)
  --scale N             window scale (default 3)
  --headless            no window
  --interp              interpreter only
  --verify              compare every recompiled block with Musashi

Notes
-----
* The MVS BIOS is the real sp-s2.sp1 system ROM; there is no BIOS HLE.
* The 68000 program is statically recompiled at build time from your own
  dump and runs natively; there is no 68000 interpreter in the hot path.
  Runtime-computed targets without a native entry use the bundled Musashi
  fallback. On the tested sessions native coverage measured 100%.
* Original project code is PolyForm Noncommercial 1.0.0 - free for
  noncommercial use, commercial use needs a separate licence. Upstream
  NeoGeoRecomp (MIT), Musashi (MIT), z80 (MIT), ymfm (BSD-3) and SDL2
  (zlib) keep their own licences; see LICENSES\.
* Samurai Shodown / Samurai Spirits, Neo Geo, MVS and AES are trademarks of
  SNK Corporation. This project is not affiliated with or endorsed by SNK.
