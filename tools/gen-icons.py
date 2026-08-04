#!/usr/bin/env python3
"""Vygeneruje PNG ikony aplikácie (bez externých knižníc).

Použitie:  python3 tools/gen-icons.py
Vytvorí:   assets/icons/icon-180.png, assets/icons/icon-512.png
"""
import math
import os
import struct
import zlib

BG = (11, 107, 203)
FG = (255, 255, 255)
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")


def coverage(px, py, shapes, samples=3):
    """Podiel plochy pixela pokrytej tvarom – jednoduchý antialiasing."""
    hits = 0
    step = 1.0 / (samples + 1)
    for i in range(1, samples + 1):
        for j in range(1, samples + 1):
            x = px + i * step
            y = py + j * step
            if any(s(x, y) for s in shapes):
                hits += 1
    return hits / float(samples * samples)


def build(size):
    c = size / 2.0
    r_out = size * 0.293
    ring = size * 0.066
    hub = size * 0.102
    spoke = size * 0.066

    def in_ring(x, y):
        d = math.hypot(x - c, y - c)
        return abs(d - r_out) <= ring / 2.0

    def in_hub(x, y):
        return math.hypot(x - c, y - c) <= hub

    def segment(angle_deg):
        """Lúč z náboja k vencu pod daným uhlom."""
        a = math.radians(angle_deg)
        x1, y1 = c + hub * math.cos(a), c + hub * math.sin(a)
        x2, y2 = c + (r_out - ring / 2.0) * math.cos(a), c + (r_out - ring / 2.0) * math.sin(a)

        def f(x, y):
            dx, dy = x2 - x1, y2 - y1
            t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
            t = max(0.0, min(1.0, t))
            return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy)) <= spoke / 2.0
        return f

    shapes = [in_ring, in_hub, segment(-90), segment(30), segment(150)]

    rows = []
    for y in range(size):
        row = bytearray([0])  # filter typu 0
        for x in range(size):
            a = coverage(x, y, shapes)
            for ch in range(3):
                row.append(int(round(BG[ch] * (1 - a) + FG[ch] * a)))
        rows.append(bytes(row))
    return b"".join(rows)


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, size):
    raw = build(size)
    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", header)
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    print("zapísané: %s (%dx%d, %d B)" % (path, size, size, len(png)))


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    write_png(os.path.join(OUT_DIR, "icon-180.png"), 180)
    write_png(os.path.join(OUT_DIR, "icon-512.png"), 512)
