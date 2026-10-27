#!/usr/bin/env python3
"""Validate the Samurai Shodown IV (MAME set `samsho4`) ROM files.

Checks every file the runtime loads against MAME's neogeo.cpp: size, CRC32
and SHA1. The game set and the required `neogeo` system ROMs may live in one
directory or be passed as two.

Usage:
    python scripts/validate-roms.py ROM_DIR [BIOS_DIR]

Exit code 0 means every file matched; 1 means a problem was found.
No ROM data is read from or written anywhere except the paths given.
"""
import hashlib
import os
import sys
import zlib

# MAME src/mame/snk/neogeo.cpp, ROM_START( samsho4 ) and the neogeo BIOS set.
GAME = {
    "222-p1.p1":  (0x100000, "1a5cb56d", "9a0a5a1c7c5d428829f22d3d17f7033d43a51b5b"),
    "222-p2.sp2": (0x400000, "b023cd8b", "35b4cec9858225f90acdfa16ed8a3017d0d08327"),
    "222-s1.s1":  (0x020000, "8d3d3bf9", "9975ed9b458bdd14e23451d2534153f68a5e4e6c"),
    "222-m1.m1":  (0x020000, "7615bc1b", "b936f7b341f6fe0921b4c41049734684583e3596"),
    "222-v1.v1":  (0x400000, "7d6ba95f", "03cb4e0d770e0b332b07b64cacef624460b84c78"),
    "222-v2.v2":  (0x400000, "6c33bb5d", "fd5d4e08a962dd0d22c52c91bad5ec7f23cfb901"),
    "222-v3.v3":  (0x200000, "831ea8c0", "f2987b7d09bdc4311e972ce8a9ab7ca9802db4db"),
    "222-c1.c1":  (0x400000, "68f2ed95", "c0a02df012cd25bcfe341770ea861a80294148cb"),
    "222-c2.c2":  (0x400000, "a6e9aff0", "15addca49951ed53fa3c000c8d7cd327d012a620"),
    "222-c3.c3":  (0x400000, "c91b40f4", "dcda45e0336204e3e024de08edfd0a3217bc1fdd"),
    "222-c4.c4":  (0x400000, "359510a4", "b6642677ebdff7788263266402080272b8a66b15"),
    "222-c5.c5":  (0x400000, "9cfbb22d", "789c32f917d0c6e38601cd390a7bf9d803131a4a"),
    "222-c6.c6":  (0x400000, "685efc32", "db21ba1c7e3631ce0f1cb6f503ae7e0e043ff71b"),
    "222-c7.c7":  (0x400000, "d0f86f0d", "32502d71c2ab1469c492b6b382bf2bb3f85981d9"),
    "222-c8.c8":  (0x400000, "adfc50e3", "7d7ee874355b5aa75ad9c9a5c9c3df98d098d85e"),
}

BIOS = {
    "sp-s2.sp1": (0x020000, "9036d879", "4f5ed7105b7128794654ce82b51723e16e389543"),
    "sfix.sfix": (0x020000, "c2ea0cfd", "fd4a618cdcdbf849374f0a50dd8efe9dbab706c3"),
    "sm1.sm1":   (0x020000, "94416d67", "42f9d7ddd6c0931fd64226a60dc73602b2819dcf"),
    "000-lo.lo": (0x020000, "5a86cff2", "5992277debadeb64d1c1c64b0a92d9293eaf7e4a"),
}


def check(name, expected, search):
    size, crc, sha1 = expected
    for d in search:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            break
    else:
        print("MISSING   %-12s (looked in %s)" % (name, ", ".join(search)))
        return False
    data = open(p, "rb").read()
    got_crc = "%08x" % (zlib.crc32(data) & 0xFFFFFFFF)
    got_sha1 = hashlib.sha1(data).hexdigest()
    ok = len(data) == size and got_crc == crc and got_sha1 == sha1
    if ok:
        print("OK        %-12s %9d bytes  crc32 %s" % (name, len(data), got_crc))
    else:
        print("MISMATCH  %-12s size %d (want %d) crc32 %s (want %s)"
              % (name, len(data), size, got_crc, crc))
    return ok


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    game_dir = sys.argv[1]
    bios_dir = sys.argv[2] if len(sys.argv) > 2 else game_dir
    ok = True
    print("== game set samsho4 ==")
    for n, e in GAME.items():
        ok &= check(n, e, [game_dir])
    print("== system set neogeo ==")
    for n, e in BIOS.items():
        ok &= check(n, e, [bios_dir, game_dir])
    print("result:", "all files verified" if ok else "PROBLEMS FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
