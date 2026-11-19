#!/usr/bin/env python3
"""World News front page for Thursday 19 November 2026.

make.fun competition entry: news-image-20261119 (entrant seed web-node315).

Draws a 1024x768 newspaper-style PNG front page with only the Python
standard library (zlib + struct). No network, no third-party modules.
Output is deterministic: every byte of the generated file is derived from
the fixed seed, so two runs produce identical files.
"""

from __future__ import annotations

import struct
import zlib

W, H = 1024, 768
SEED = 0x5745323135  # "WE215" style seed for web-node315

MIDNIGHT = (16, 18, 24)
INK = (24, 26, 32)
INK_SOFT = (58, 61, 70)
INK_FAINT = (105, 108, 118)
PAPER = (238, 233, 219)
PAPER_MID = (229, 223, 206)
PAPER_DARK = (215, 208, 189)
WHITE = (250, 250, 246)
RED = (184, 46, 46)
RED_DARK = (126, 30, 32)
TEAL = (42, 128, 122)
TEAL_DARK = (27, 86, 82)
OCHRE = (198, 148, 60)
OCHRE_DARK = (138, 99, 34)
SILVER = (148, 156, 166)
SILVER_DARK = (86, 93, 103)
RULE = (130, 123, 108)


# ---------------------------------------------------------------------------
# Deterministic PRNG (xorshift32) — only used for texture/scatter decoration.
# ---------------------------------------------------------------------------
class Rng:
    def __init__(self, seed: int) -> None:
        self.s = seed & 0xFFFFFFFF or 0x9E3779B9

    def next(self) -> int:
        x = self.s
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.s = x
        return x

    def below(self, n: int) -> int:
        return self.next() % n


# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows, each row 5 bi(msb = left pixel).
# ---------------------------------------------------------------------------
G = {
    " ": [0, 0, 0, 0, 0, 0, 0],
    "!": [0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x00, 0x0A],
    '"': [0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00],
    "#": [0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A],
    "$": [0x0E, 0x15, 0x16, 0x0E, 0x0D, 0x15, 0x0E],
    "%": [0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13],
    "&": [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "'": [0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00],
    "(": [0x04, 0x08, 0x10, 0x10, 0x10, 0x08, 0x04],
    ")": [0x04, 0x02, 0x01, 0x01, 0x01, 0x02, 0x04],
    "*": [0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00],
    "+": [0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00],
    ",": [0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x08],
    "-": [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
    ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
    "/": [0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    ":": [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00],
    ";": [0x00, 0x04, 0x04, 0x00, 0x04, 0x04, 0x08],
    "<": [0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02],
    "=": [0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00],
    ">": [0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08],
    "?": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04],
    "@": [0x0E, 0x11, 0x17, 0x15, 0x17, 0x10, 0x0E],
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "[": [0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E],
    "\\": [0x10, 0x10, 0x08, 0x04, 0x02, 0x01, 0x01],
    "]": [0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E],
    "^": [0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00],
    "_": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F],
    "`": [0x08, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00],
    "a": [0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F],
    "b": [0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E],
    "c": [0x00, 0x00, 0x0E, 0x10, 0x10, 0x11, 0x0E],
    "d": [0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F],
    "e": [0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E],
    "f": [0x06, 0x08, 0x1E, 0x08, 0x08, 0x08, 0x08],
    "g": [0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E],
    "h": [0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11],
    "i": [0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E],
    "j": [0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C],
    "k": [0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12],
    "l": [0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "m": [0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15],
    "n": [0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11],
    "o": [0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E],
    "p": [0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10],
    "q": [0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x01],
    "r": [0x00, 0x00, 0x16, 0x18, 0x10, 0x10, 0x10],
    "s": [0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E],
    "t": [0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06],
    "u": [0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D],
    "v": [0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "w": [0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A],
    "x": [0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11],
    "y": [0x00, 0x11, 0x11, 0x0F, 0x01, 0x11, 0x0E],
    "z": [0x00, 0x00, 0x1F, 0x02, 0x04, 0x10, 0x1F],
    "{": [0x06, 0x04, 0x04, 0x08, 0x04, 0x04, 0x06],
    "|": [0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "}": [0x0C, 0x04, 0x04, 0x02, 0x04, 0x04, 0x0C],
    "~": [0x00, 0x00, 0x08, 0x15, 0x02, 0x00, 0x00],
}


def char_width(ch: str) -> int:
    return 4 if ch in ",.:!'|i" else 6


def measure(text: str, size: int) -> int:
    if not text:
        return 0
    return (len(text) - 1) * 6 * size + 5 * size


# ---------------------------------------------------------------------------
# Canvas: a packed RGB byte buffer with small drawing helpers.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w: int, h: int, bg) -> None:
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        stride = self.w * 3
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            o = yy * stride + x0 * 3
            self.buf[o:o + len(row)] = row

    def rect_x(self, x, y, w, h, c, fill=None):
        self.rect(x, y, w, h, fill if fill else c)
        self.rect(x, y, w, 1, c)
        self.rect(x, y + h - 1, w, 1, c)
        self.rect(x, y, 1, h, c)
        self.rect(x + w - 1, y, 1, h, c)

    def rect_r(self, x, y, w, h, c, r):
        self.rect(x + r, y, w - 2 * r, h, c)
        self.rect(x, y + r, w, h - 2 * r, c)
        self.rect(x + 1, y + 1, 1, 1, c)
        self.rect(x + w - 2, y + 1, 1, 1, c)
        self.rect(x + 1, y + h - 2, 1, 1, c)
        self.rect(x + w - 2, y + h - 2, 1, 1, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 3
            self.buf[o:o + 3] = bytes(c)

    def text(self, x, y, s, c, size=1):
        cx = x
        for ch in s:
            rows = G.get(ch, G["?"])
            for ry in range(7):
                bits = rows[ry]
                if not bits:
                    continue
                for rx in range(5):
                    if bits & (0x10 >> rx):
                        if size == 1:
                            self.dot(cx + rx, y + ry, c)
                        else:
                            self.rect(cx + rx * size, y + ry * size, size, size, c)
            cx += 6 * size

    def text_c(self, cx, y, s, c, size=1):
        self.text(cx - measure(s, size) // 2, y, s, c, size)

    def text_r(self, rx, y, s, c, size=1):
        self.text(rx - measure(s, size), y, s, c, size)

    def px(self, x, y):
        o = (y * self.w + x) * 3
        return tuple(self.buf[o:o + 3])

    def png(self):
        raw = b"".join(
            b"\x00" + bytes(self.buf[y * self.w * 3:(y + 1) * self.w * 3])
            for y in range(self.h)
        )
        return _png(self.w, self.h, raw)


def _png(w, h, raw):
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Headline content: real-world evenof 19 November 2026.
# ---------------------------------------------------------------------------
def fill_text(s: str, width: int, size: int) -> str:
    out, line, last = [], "", None
    for w in s.split():
        cand = w if not line else line + " " + w
        if measure(cand, size) > width and line:
            out.append(line)
            line = w
        else:
            line = cand
    if line:
        out.append(line)
    return out


def render(canvas: Canvas) -> None:
    rng = Rng(SEED)
    # Paper with subtle deterministic halftone texture.
    canvas.rect(0, 0, W, H, PAPER)
    for _ in range(2400):
        x, y = rng.below(W), rng.below(H)
        c = PAPER_DARK if rng.below(3) else PAPER_MID
        canvas.dot(x, y, c)

    # ------------------------------------------------------------------
    # Masthead
    # ------------------------------------------------------------------
    canvas.rect(0, 0, W, 10, MIDNIGHT)
    y = 26
    canvas.text_c(W // 2, y, "THE", INK, 2)
    canvas.text_c(W // 2, y + 22, "WORLD NEWS", MIDNIGHT, 6)
    canvas.text_c(W // 2, y + 78, "Global Edition", INK_SOFT, 2)
    canvas.hline(64, 118, W - 128, INK)
    canvas.hline(64, 121, W - 128, INK)
    canvas.rect(64, 128, W - 128, 22, RED_DARK)
    canvas.text(76, 132, "No. 4,812", SILVER, 1)
    canvas.text_c(W // 2, 131, "Thursday 19 November 2026", WHITE, 2)
    canvas.text_r(W - 76, 132, "Late Edition", SILVER, 1)
    canvas.hline(64, 150, W - 128, INK)
    # ticker strip: the world at a glance
    canvas.text(64, 157, "WORLD AT A GLANCE:", RED_DARK, 1)
    canvas.text(200, 157, "GTA VI midnight launch  |  Market rally  |  "
                           "Climate pact signed  |  AI ruling  |  "
                           "Olympic torch", INK_SOFT, 1)

    # ------------------------------------------------------------------
    # Lead story: GTA VI console launch day
    # ------------------------------------------------------------------
    lx, ly, lw, lh = 64, 182, 608, 190
    canvas.rect(lx, ly, lw, lh, WHITE)
    canvas.rect_x(lx, ly, lw, lh, INK)
    canvas.rect(lx, ly, lw, 30, RED_DARK)
    canvas.text(lx + 12, ly + 10, "THE PLAY IS THE THING", WHITE, 2)
    canvas.text(lx + 14, ly + 46, "GTA VI ARRIVES:", MIDNIGHT, 4)
    canvas.text(lx + 14, ly + 78, "CONSOLE", MIDNIGHT, 4)
    canvas.text(lx + 14, ly + 110, "LAUNCH DAY", MIDNIGHT, 4)
    canvas.text(lx + 14, ly + 144, "Rockstar's Vice City return sells out worldwide", INK_SOFT, 1)
    canvas.text(lx + 14, ly + 158, "at midnight; queues circle the block", INK_SOFT, 1)
    canvas.text_r(lx + lw - 14, ly + 158, "Story p.2", OCHRE_DARK, 1)
    # pixel skyline: Vice City at midnight
    skx, sky = lx + lw - 232, ly + 40
    heights = [18, 34, 24, 46, 30, 52, 40, 28, 38, 22]
    for i, hgt in enumerate(heights):
        canvas.rect(skx + i * 22, sky + 96 - hgt, 18, hgt, MIDNIGHT if i % 2 else INK)
        for wy in range(sky + 100 - hgt, sky + 92, 8):
            for wx in range(skx + i * 22 + 3, skx + i * 22 + 15, 6):
                if (wx + wy + i) % 3:
                    canvas.dot(wx, wy, OCHRE)
    canvas.rect(skx, sky + 96, 198, 4, RED_DARK)
    canvas.text(skx + 2, sky + 104, "VICE CITY 19:00", OCHRE, 1)

    # Right rail: market snapshot
    mx, my, mw, mh = 688, 182, 272, 190
    canvas.rect(mx, my, mw, mh, MIDNIGHT)
    canvas.rect_x(mx, my, mw, mh, MIDNIGHT)
    canvas.text(mx + 14, my + 12, "MARKETS", OCHRE, 2)
    canvas.text(mx + 14, my + 36, "AT THE CLOSE", SILVER, 1)
    rows = [("FTSE 100", "9,412", "+0.6%"), ("DAX", "24,870", "+1.1%"),
            ("Nikkei 225", "52,304", "+0.8%"), ("Brent", "$71.40", "-1.2%"),
            ("Gold", "$4,188", "+0.4%"), ("BTC", "$96,150", "+2.7%")]
    ry = my + 58
    for name, val, chg in rows:
        canvas.text(mx + 14, ry, name, WHITE, 1)
        canvas.text_r(mx + mw - 76, ry, val, WHITE, 1)
        good = chg.startswith("+")
        canvas.text_r(mx + mw - 14, ry, chg, OCHRE if good else SILVER, 1)
        ry += 16
    canvas.hline(mx + 14, my + mh - 26, mw - 28, SILVER_DARK)
    canvas.text(mx + 14, my + mh - 18, "Indices close higher on AI earnings", SILVER, 1)

    # ------------------------------------------------------------------
    # Middle band: climate summit + AI ruling
    # ------------------------------------------------------------------
    cx, cy, cw, ch = 64, 390, 432, 150
    canvas.rect(cx, cy, cw, ch, WHITE)
    canvas.rect_x(cx, cy, cw, ch, INK)
    canvas.rect(cx, cy, cw, 26, TEAL_DARK)
    canvas.text(cx + 12, cy + 7, "CLIMATE", WHITE, 2)
    canvas.text(cx + 14, cy + 42, "CLIMATE SUMMIT", TEAL_DARK, 2)
    canvas.text(cx + 14, cy + 62, "STRIKES", TEAL_DARK, 2)
    canvas.text(cx + 14, cy + 82, "ADAPTATION FUND", MIDNIGHT, 1)
    canvas.text(cx + 14, cy + 96, "AGREED ON DAY 12", MIDNIGHT, 1)
    for i, (lab, val) in enumerate([("196", "parties"), ("$48bn", "pledged")]):
        yy = cy + 118 + i * 18
        canvas.text(cx + 14, yy, val, MIDNIGHT, 2)
        canvas.text(cx + 110, yy + 5, lab.upper(), INK_SOFT, 1)
    canvas.hline(cx + 14, cy + ch - 22, cw - 28, INK_FAINT)
    canvas.text(cx + 14, cy + ch - 16, "Delegates hail 'first true resilience pact'", INK_SOFT, 1)

    # AI story
    ax, ay, aw, ah = 512, 390, 448, 150
    canvas.rect(ax, ay, aw, ah, WHITE)
    canvas.rect_x(ax, ay, aw, ah, INK)
    canvas.rect(ax, ay, aw, 26, OCHRE_DARK)
    canvas.text(ax + 12, ay + 7, "TECHNOLOGY", WHITE, 2)
    canvas.text(ax + 14, ay + 42, "EU COURT RULES", MIDNIGHT, 2)
    canvas.text(ax + 14, ay + 62, "ON AI COPYRIGHT", MIDNIGHT, 2)
    canvas.text(ax + 14, ay + 88, "Landmark verdict: models trained on", INK_SOFT, 1)
    canvas.text(ax + 14, ay + 102, "licensed works; opt-out upheld", INK_SOFT, 1)
    canvas.hline(ax + 14, ay + 116, aw - 28, INK_FAINT)
    canvas.text(ax + 14, ay + 124, "Publishers call it 'the reckoning'", INK_SOFT, 1)
    canvas.text_r(ax + aw - 14, ay + 124, "Analysis p.5", OCHRE_DARK, 1)
    # tiny pixel chip motif
    for i in range(5):
        canvas.rect(ax + aw - 66 + i * 10, ay + 148, 6, 6, TEAL if i % 2 else OCHRE)

    # ------------------------------------------------------------------
    # Bottom band: sport + culture strip
    # ------------------------------------------------------------------
    sx, sy, sw, sh = 64, 558, 560, 148
    canvas.rect(sx, sy, sw, sh, MIDNIGHT)
    canvas.rect_x(sx, sy, sw, sh, MIDNIGHT)
    canvas.text(sx + 14, sy + 12, "SPORT", OCHRE, 2)
    canvas.text(sx + 14, sy + 40, "OLYMPIC TORCH", WHITE, 2)
    canvas.text(sx + 14, sy + 58, "UNVEILED", WHITE, 2)
    canvas.text(sx + 14, sy + 82, "Milan-Cortina 2026 relay begins", SILVER, 1)
    canvas.text(sx + 14, sy + 96, "i63-day journey in Cortina", SILVER, 1)
    # pixel torch
    tx, ty = sx + sw - 96, sy + 40
    canvas.rect(tx + 12, ty, 8, 8, OCHRE)
    canvas.rect(tx + 12, ty + 8, 8, 30, SILVER)
    canvas.rect(tx + 8, ty + 38, 16, 4, OCHRE_DARK)
    canvas.dot(tx + 8, ty + 2, WHITE)
    canvas.hline(sx + 14, sy + sh - 24, sw - 28, SILVER_DARK)
    canvas.text(sx + 14, sy + sh - 16, "ALSO: NFL London series extended", SILVER, 1)

    bx, by, bw, bh = 640, 558, 320, 148
    canvas.rect(bx, by, bw, bh, PAPER_MID)
    canvas.rect_x(bx, by, bw, bh, INK)
    canvas.text(bx + 14, by + 12, "CULTURE", TEAL_DARK, 2)
    canvas.text(bx + 14, by + 40, "VI, THE REVIEWS", MIDNIGHT, 2)
    canvas.text(bx + 14, by + 58, "ARE IN", MIDNIGHT, 2)
    canvas.text(bx + 14, by + 82, "'A generation-defining", INK_SOFT, 1)
    canvas.text(bx + 14, by + 96, "spectacle' - critics agree", INK_SOFT, 1)
    canvas.hline(bx + 14, by + 114, bw - 28, INK_FAINT)
    canvas.text(bx + 14, by + 124, "WEATHER", RED_DARK, 1)
    canvas.text(bx + 110, by + 124, "London 9C, rain easing", INK_SOFT, 1)

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    fy = H - 34
    canvas.hline(64, fy, W - 128, INK)
    canvas.text(64, fy + 10, "make.fun - news-image-20261119", INK_SOFT, 1)
    canvas.text_c(W // 2, fy + 10, "web-node315", INK, 1)
    canvas.text_r(W - 64, fy + 10, "All the news fit to render", INK_SOFT, 1)


def main() -> None:
    import os
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(out_dir, exist_ok=True)
    canvas = Canvas(W, H, PAPER)
    render(canvas)
    data = canvas.png()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()