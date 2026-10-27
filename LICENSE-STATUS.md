# License status

**Status: PolyForm Noncommercial 1.0.0.**

The repository owner's "polymaster" request is applied, by project convention,
as **PolyForm Noncommercial 1.0.0** — the same licence as the other
NeoGeoRecomp game repositories. The full text is in `LICENSE`.

## What the PolyForm licence covers

Only code in this repository that the project authors wrote and have the right
to license, principally:

- `src/` — the Samurai Shodown IV ROM layout and the player entry point
- `scripts/`, `packaging/` — build, packaging, icon and ROM-validation helpers
- `CMakeLists.txt` — the project's build description
- `tests/` — scripted input
- the project documentation in `docs/` and the top-level `README.md`

## What it does not cover

- `neogeorecomp/` — the upstream toolkit, **MIT**. See
  `neogeorecomp/LICENSE` and `neogeorecomp/NOTICE`.
- Musashi, z80 and ymfm — MIT / MIT / BSD-3-Clause. Verbatim texts are in
  `neogeorecomp/LICENSES/`.
- SDL2 — zlib licence. See `packaging/SDL2.txt`.
- SNK game data, the Neo Geo BIOS, and anything generated from them. **None of
  that is distributed here.**
- The local toolkit patches in `patches/` are fixes to MIT-licensed upstream
  code and remain under the upstream MIT terms.

## Distribution caution

PolyForm Noncommercial is not an open-source licence and does not permit
commercial redistribution. Do not assume that a build of this project may be
sold, bundled with commercial hardware, or distributed for a fee. ROMs, BIOS
files and code generated from them are not covered by this licence at all;
users must supply their own legally obtained dumps.

The release binaries on GitHub contain statically recompiled code produced
from the author's own dump. They grant no rights in SNK's game code and are
provided for use with ROMs the recipient is legally entitled to use.
