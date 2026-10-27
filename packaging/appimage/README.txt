Samurai Shodown IV - Amakusa's Revenge
Steam Deck / Linux x86_64 AppImage
==================================

Samsho4-SteamDeck-x86_64.AppImage is a native static recompilation of the
Neo Geo game. The 68000 program runs as recompiled C; it is not an emulator
wrapper. No game ROMs or Neo Geo BIOS are inside the AppImage.

Quick start
-----------
1. Make the AppImage executable and put your ROM files beside it:

     chmod +x Samsho4-SteamDeck-x86_64.AppImage
     mkdir -p roms
     # unzip your legally obtained MAME sets into ./roms:
     #   samsho4.zip -> 222-p1.p1 ... 222-c8.c8, 222-s1.s1, 222-m1.m1,
     #                  222-v1.v1 222-v2.v2 222-v3.v3
     #   neogeo.zip  -> sp-s2.sp1 sfix.sfix sm1.sm1 000-lo.lo
     ./Samsho4-SteamDeck-x86_64.AppImage

   The launcher looks for `roms/` next to the AppImage, then in the usual
   EmulationStation folders (~/Emulation/roms/arcade, .../neogeo, ~/roms).
   To point at another folder:

     ./Samsho4-SteamDeck-x86_64.AppImage --rom-path /path/to/roms

2. On a Steam Deck: copy the AppImage and the roms folder to the Deck
   (for example ~/Games/Samsho4/), then add the AppImage in Steam
   ("Add a Non-Steam Game"). Launch it once in Desktop Mode to confirm it
   starts, then play in Gaming Mode. The launcher asks for fullscreen by
   default; 1280x800 output is pillarboxed with the original 4:3-ish
   picture, never stretched.

Controls
--------
  D-pad / left stick      move
  A B X Y                 Neo Geo A B C D
  Start                   start
  Back / View             insert coin
  Left shoulder           select
  F11 or Alt+Enter        toggle fullscreen
  Esc                     quit

Steam Input: use the default "Gamepad" template (or any template that
presents a standard Xbox controller to the game). Steam Input exposes the
Deck's controls as a controller, which is what the game reads through SDL2.
On an MVS you must insert a coin (Back/View by default) before Start does
anything. Up to two controllers work: the first is player 1, the second
player 2.

Steam Deck notes
----------------
* Fullscreen on launch; F11 toggles.
* 1280x800 (16:10): the 320x224 picture is scaled uniformly and centred
  with black pillarboxes. It is not stretched.
* Audio goes through SDL2 to PipeWire/PulseAudio; no configuration needed.
* Frame pacing follows the MVS refresh rate (59.1856 Hz).
* The AppImage bundles SDL2 2.0.20 from the build host. It does not bundle
  glibc, libstdc++ or the graphics stack, so SteamOS supplies those.
* Built on Ubuntu 22.04 (glibc 2.35); SteamOS 3 is newer.

Command line
------------
  --rom-path DIR        game ROM files
  --bios-path DIR       BIOS files (default: the ROM path)
  --bios FILE           system ROM (default: sp-s2.sp1)
  --fullscreen          start fullscreen (F11 toggles)
  --scale N             window scale (default 3)
  --headless            no window
  --interp              interpreter only
  --verify              compare every recompiled block with Musashi

Troubleshooting
---------------
* "error: cannot open .../roms/222-p1.p1": the ROM folder is not where the
  launcher looks, or the files are still zipped. Pass --rom-path.
* No controller: run `SDL_GAMECONTROLLERCONFIG=... AppImage` or check that
  Steam Input is enabled for the game in Steam's controller settings.
* Run with --headless --frames 600 to check the ROMs without opening a
  window. The last line reports native coverage.

Licensing
---------
Original project code: PolyForm Noncommercial 1.0.0 (free for noncommercial
use; see LICENSE.txt inside the AppImage). NeoGeoRecomp is MIT, Musashi MIT,
z80 MIT, ymfm BSD-3, SDL2 zlib - all notices are in
usr/share/doc/samsho4/LICENSES. Samurai Shodown, Neo Geo, MVS and AES are
trademarks of SNK Corporation; this project is not affiliated with SNK.
