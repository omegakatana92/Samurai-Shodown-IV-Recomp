#!/usr/bin/env python3
"""Draw an original 256x256 icon for the Samurai Shodown IV recompilation.

No SNK artwork is used: a dark gradient, a diagonal red band, and "SS4"
block letters drawn from a tiny bitmap font.
"""
import os
import struct
import zlib

W = H = 256
px = bytearray(W * H * 3)


def put(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = r
        px[i + 1] = g
        px[i + 2] = b


# dark blue-black background with a subtle vertical gradient
for y in range(H):
    for x in range(W):
        put(x, y, 10 + y // 28, 8 + y // 40, 14 + y // 14)

# diagonal crimson band
for y in range(H):
    for x in range(W):
        if 40 <= (x + y) % 256 <= 74:
            put(x, y, 198, 32, 36)

# panel behind the letters
for y in range(78, 186):
    for x in range(22, 234):
        put(x, y, 10, 10, 14)

FONT = {
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
}
text = "SS4"
scale = 14
tw = (len(text) * 6 - 1) * scale
tx = (W - tw) // 2
ty = (H - 7 * scale) // 2
for ci, ch in enumerate(text):
    for gy, row in enumerate(FONT[ch]):
        for gx, bit in enumerate(row):
            if bit == '1':
                for yy in range(scale):
                    for xx in range(scale):
                        put(tx + (ci * 6 + gx) * scale + xx, ty + gy * scale + yy, 246, 240, 226)

# white roundel accent with a red ring
cx, cy, rad = 208, 206, 24
for y in range(cy - rad, cy + rad + 1):
    for x in range(cx - rad, cx + rad + 1):
        d = (x - cx) ** 2 + (y - cy) ** 2
        if d <= rad * rad:
            if d > (rad - 5) ** 2:
                put(x, y, 198, 32, 36)
            elif d > (rad - 10) ** 2:
                put(x, y, 246, 240, 226)
            else:
                put(x, y, 198, 32, 36)

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += px[y * W * 3:(y + 1) * W * 3]


def chunk(t, d):
    return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xFFFFFFFF)


out = b'\x89PNG\r\n\x1a\n'
out += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
out += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
out += chunk(b'IEND', b'')
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samsho4.png")
with open(path, 'wb') as f:
    f.write(out)
print(path)
