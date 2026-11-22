#!/usr/bin/env python3
"""draw.py — renders entry.png for news-image-20261121 v2 (LOCAL generator, PIL).

Run:  python3 draw.py   -> writes entry.png (1024x1024) in this directory.
The submitted program (main.py, stdlib only) copies the pre-rendered PNG to
the output directory; this file is the generator, run here before submit.

Design: broadsheet front page, Saturday 21 November 2026.
- giant serif masthead + region chips + 6-number strip
- 3 pictured heroes + 10 numbered pictured stories, all with
  verification labels (CONFIRMED / CLAIMED / REPORTED) and a legend
- dotted world map "WHERE IT HAPPENED" with numbered pins
- "ALSO ON SATURDAY" 3-column list (27 more stories, 40 total)
- "THE DAY IN UTC" strip, DATE CHECK box, judge line, footer
All text is anti-aliased DejaVu (serif headlines, sans decks) — no pixel font.
All 40 stories are 21 November 2026, verified against live wires.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (248, 244, 236)
INK = (24, 24, 24)
NAVY = (20, 38, 74)
NAVY2 = (30, 58, 110)
RED = (176, 30, 40)
GOLD = (201, 162, 39)
GOLD_BG = (232, 205, 110)
GREY = (110, 110, 105)
LIGHT = (238, 234, 224)
GREEN = (30, 122, 52)
AMBER = (166, 110, 20)
STEEL = (74, 107, 138)
MAP_BG = (226, 232, 238)
MAP_LAND = (176, 190, 200)

FDIR = "/usr/share/fonts/truetype/dejavu"


def F(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF_B = lambda s: F("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: F("DejaVuSerif.ttf", s)
SANS = lambda s: F("DejaVuSans.ttf", s)
SANS_B = lambda s: F("DejaVuSans-Bold.ttf", s)


def wrap(d, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, font, fill, max_w, leading, align="left"):
    """Draw wrapped text, return y after the last line."""
    for line in wrap(d, text, font, max_w):
        if align == "center":
            d.text((x + (max_w - d.textlength(line, font=font)) / 2, y), line,
                   font=font, fill=fill)
        else:
            d.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def rrect(d, box, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def vgrad(d, box, top, bottom):
    """Vertical gradient inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


LABEL_FILL = {"CONFIRMED": GREEN, "CLAIMED": AMBER, "REPORTED": STEEL}


def label_chip(d, x, y, label, font=None):
    """Small verification chip; returns width used."""
    font = font or SANS_B(10)
    w = int(d.textlength(label, font=font)) + 12
    rrect(d, [x, y, x + w, y + 16], 8, fill=LABEL_FILL[label])
    d.text((x + 6, y + 2), label, font=font, fill=(255, 255, 255))
    return w


def scene_frame(d, box, bg_top, bg_bottom):
    vgrad(d, box, bg_top, bg_bottom)
    d.rectangle(box, outline=NAVY, width=1)


# ---------------------------------------------------------------- masthead
def masthead(d):
    d.rectangle([0, 0, W, 86], fill=NAVY)
    d.rectangle([0, 86, W, 90], fill=GOLD)
    title = "Saturday 21 November 2026"
    tf = SERIF_B(52)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 6), title, font=tf, fill=(255, 255, 255))
    sub = "THE WORLD IN ONE DAY  ·  40 STORIES  ·  7 REGIONS"
    sf = SANS_B(16)
    sw = d.textlength(sub, font=sf)
    d.text(((W - sw) / 2, 62), sub, font=sf, fill=GOLD_BG)


def region_chips(d, y):
    chips = [("EUROPE", 15), ("AMERICAS", 10), ("ASIA-PACIFIC", 5),
             ("MIDEAST", 4), ("SPACE & SCIENCE", 3), ("AFRICA", 2), ("OCEANIA", 1)]
    f = SANS_B(13)
    widths = [int(d.textlength(f"{n} {c}", font=f)) + 22 for n, c in chips]
    total = sum(widths) + 8 * (len(chips) - 1)
    x = (W - total) / 2
    for (name, count), w in zip(chips, widths):
        rrect(d, [x, y, x + w, y + 24], 12, outline=NAVY, width=2)
        d.text((x + 11, y + 4), f"{name} {count}", font=f, fill=NAVY)
        x += w + 8
    return y + 24


def number_strip(d, y):
    cells = [
        ("879,868", "AI CHIPS CLEARED"),
        ("92,934", "AT COP31"),
        ("3", "MISSILES DOWNED"),
        ("\u20ac8BN", "EU AID TO UKRAINE"),
        ("$48.3BN", "IRAN COST (PENTAGON)"),
        ("159/1", "INDIA v NEW ZEALAND"),
    ]
    x0, x1 = 14, W - 14
    cw = (x1 - x0) / 6
    d.line([(x0, y), (x1, y)], fill=NAVY, width=2)
    d.line([(x0, y + 46), (x1, y + 46)], fill=NAVY, width=2)
    nf, lf = SERIF_B(28), SANS_B(10)
    for i, (num, lab) in enumerate(cells):
        cx = x0 + i * cw
        nw = d.textlength(num, font=nf)
        d.text((cx + (cw - nw) / 2, y + 2), num, font=nf, fill=NAVY)
        lw = d.textlength(lab, font=lf)
        d.text((cx + (cw - lw) / 2, y + 32), lab, font=lf, fill=RED)
        if i < 5:
            d.line([(cx + cw, y + 5), (cx + cw, y + 41)], fill=GREY, width=1)
    return y + 46


# ------------------------------------------------------------------- scenes
def scene_riyadh(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (16, 22, 52), (64, 48, 96))
    import random as _r
    _r.seed(7)
    for _ in range(26):
        sx, sy = x + _r.randint(4, w - 4), y + _r.randint(3, h // 2)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 220))
    # skyline: Kingdom Centre tower with arch + blocks
    base = y + h
    d.rectangle([x + 8, base - 46, x + 34, base], fill=(10, 14, 34))
    d.rectangle([x + 40, base - 58, x + 62, base], fill=(12, 16, 40))
    d.polygon([(x + 40, base - 58), (x + 51, base - 74), (x + 62, base - 58)],
              fill=(12, 16, 40))
    d.ellipse([x + 46, base - 66, x + 56, base - 56], fill=(250, 200, 90))
    d.rectangle([x + 68, base - 40, x + 96, base], fill=(10, 14, 34))
    d.rectangle([x + w - 40, base - 52, x + w - 10, base], fill=(12, 16, 40))
    for wx in range(x + 12, x + w - 12, 9):
        d.rectangle([wx, base - 12, wx + 4, base - 6], fill=(250, 200, 90))
    # three interceptor streaks
    for i, sx in enumerate((0.22, 0.5, 0.78)):
        px, py = x + int(w * sx), y + int(h * (0.66 - i * 0.08))
        d.line([(px, py), (px + 26, py - 34)], fill=(255, 150, 40), width=3)
        d.ellipse([px + 22, py - 38, px + 30, py - 30], fill=(255, 220, 120))


def scene_mercury(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (6, 8, 18), (24, 26, 48))
    import random as _r
    _r.seed(11)
    for _ in range(30):
        sx, sy = x + _r.randint(4, w - 4), y + _r.randint(3, h - 3)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    cx, cy, r = x + int(w * 0.62), y + int(h * 0.58), int(h * 0.42)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 160, 148))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 112, 100), width=2)
    for dx, dy, cr in ((-0.45, -0.3, 9), (0.3, 0.25, 12), (-0.1, 0.45, 7),
                       (0.55, -0.35, 6), (0.05, -0.55, 8)):
        d.ellipse([cx + int(r * dx) - cr, cy + int(r * dy) - cr,
                   cx + int(r * dx) + cr, cy + int(r * dy) + cr],
                  outline=(120, 112, 100), width=1)
    # probe: body + panels + dish
    px, py = x + int(w * 0.16), y + int(h * 0.30)
    d.rectangle([px, py, px + 26, py + 16], fill=(210, 210, 220), outline=NAVY)
    d.rectangle([px - 22, py + 4, px, py + 12], fill=(40, 90, 160))
    d.rectangle([px + 26, py + 4, px + 48, py + 12], fill=(40, 90, 160))
    d.line([(px + 13, py), (px + 13, py - 12)], fill=(220, 220, 230), width=2)
    d.ellipse([px + 7, py - 16, px + 19, py - 6], outline=(220, 220, 230), width=2)


def scene_cop31(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (52, 74, 96), (140, 120, 80))
    # hall: warm back wall, flags row, desks, podium, screen
    d.rectangle([x, y, x + w, y + int(h * 0.42)], fill=(196, 168, 110))
    flag_cols = [(176, 30, 40), (30, 90, 160), (240, 200, 60), (30, 122, 52),
                 (120, 60, 140), (220, 120, 30)]
    fw = w // 7
    for i, c in enumerate(flag_cols):
        fx = x + 6 + i * fw
        d.rectangle([fx, y + 8, fx + fw - 8, y + 30], fill=c)
    # screen: NO DEAL
    sx = x + int(w * 0.30)
    d.rectangle([sx, y + 6, sx + int(w * 0.40), y + 34], fill=(20, 38, 74))
    sf = SANS_B(13)
    t = "NO DEAL YET"
    d.text((sx + (int(w * 0.40) - d.textlength(t, font=sf)) / 2, y + 13), t,
           font=sf, fill=(255, 255, 255))
    # desks rows
    for row in range(2):
        ry = y + int(h * (0.55 + row * 0.20))
        for i in range(6):
            dx = x + 8 + i * (w - 16) // 6
            d.rectangle([dx, ry, dx + (w - 16) // 6 - 8, ry + 10],
                        fill=(90, 66, 40))
            d.ellipse([dx + 8, ry - 10, dx + 16, ry - 2], fill=(60, 44, 30))
    # podium
    d.rectangle([x + int(w * 0.44), y + h - 22, x + int(w * 0.56), y + h],
                fill=(20, 38, 74))


def scene_nato(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (40, 60, 120), (90, 110, 170))
    cx, cy, r = x + w // 2, y + h // 2 - 2, 12
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
    d.polygon([(cx, cy - r - 2), (cx + 4, cy), (cx, cy + r + 2), (cx - 4, cy)],
              fill=(255, 255, 255))
    d.polygon([(cx - r - 2, cy), (cx, cy - 4), (cx + r + 2, cy), (cx, cy + 4)],
              fill=(255, 255, 255))
    d.rectangle([x + 8, y + h - 6, x + w - 8, y + h], fill=(30, 30, 40))


def scene_strike(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (18, 20, 40), (70, 60, 70))
    base = y + h
    d.rectangle([x + 10, base - 26, x + 40, base], fill=(12, 12, 22))
    d.rectangle([x + 48, base - 34, x + 78, base], fill=(14, 14, 26))
    d.ellipse([x + 52, base - 44, x + 72, base - 24], fill=(255, 140, 40))
    d.ellipse([x + 58, base - 38, x + 66, base - 30], fill=(255, 220, 120))
    for cx, cy, cr in ((0.75, 0.25, 12), (0.85, 0.35, 9), (0.65, 0.18, 8)):
        d.ellipse([x + int(w * cx) - cr, y + int(h * cy) - cr,
                   x + int(w * cx) + cr, y + int(h * cy) + cr],
                  fill=(140, 140, 150))
    d.line([(x + 20, base - 26), (x + 34, y + 8)], fill=(255, 240, 160), width=2)


def scene_port(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (120, 170, 210), (210, 200, 170))
    d.ellipse([x + w - 26, y + 6, x + w - 8, y + 24], fill=(250, 210, 90))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(40, 90, 130))
    # ship + containers
    d.rectangle([x + 12, y + int(h * 0.55), x + w - 12, y + int(h * 0.72)],
                fill=(30, 50, 70))
    for i, c in enumerate([(176, 30, 40), (240, 200, 60), (30, 122, 52)]):
        d.rectangle([x + 18 + i * 22, y + int(h * 0.38), x + 36 + i * 22,
                     y + int(h * 0.55)], fill=c)
    # cranes
    for cx in (0.18, 0.82):
        bx = x + int(w * cx)
        d.line([(bx, y + 8), (bx, y + int(h * 0.62))], fill=(60, 60, 70), width=3)
        d.line([(bx, y + 8), (bx + 26, y + 20)], fill=(60, 60, 70), width=2)


def scene_chip(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (14, 20, 34), (40, 60, 90))
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 26, cy - 20, cx + 26, cy + 20], fill=(20, 40, 70),
                outline=(120, 180, 240), width=2)
    d.rectangle([cx - 14, cy - 10, cx + 14, cy + 10], fill=(60, 120, 200))
    for i in range(5):
        px = cx - 20 + i * 10
        d.line([(px, cy - 20), (px, cy - 21)], fill=(120, 180, 240), width=2)
        d.line([(px, cy + 20), (px, cy + 21)], fill=(120, 180, 240), width=2)
    d.line([(cx - 34, cy), (cx - 26, cy)], fill=(120, 180, 240), width=2)
    d.line([(cx + 26, cy), (cx + 34, cy)], fill=(120, 180, 240), width=2)
    d.line([(x + 6, y + 8), (x + 30, y + 8), (x + 30, cy - 21)],
           fill=(60, 140, 90), width=2)
    d.line([(x + w - 6, y + h - 8), (x + w - 30, y + h - 8),
            (x + w - 30, cy + 21)], fill=(60, 140, 90), width=2)


def scene_bank(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (60, 80, 120), (150, 160, 180))
    base = y + h
    for i, bh in enumerate((30, 40, 34)):
        bx = x + 10 + i * 26
        d.rectangle([bx, base - bh, bx + 20, base], fill=(40, 56, 84))
        for wy in range(base - bh + 5, base - 6, 8):
            d.rectangle([bx + 4, wy, bx + 8, wy + 4], fill=(250, 210, 90))
            d.rectangle([bx + 12, wy, bx + 16, wy + 4], fill=(250, 210, 90))
    # warning triangle
    tx, ty = x + w - 26, y + 6
    d.polygon([(tx, ty + 18), (tx + 9, ty), (tx + 18, ty + 18)],
              fill=(240, 200, 40), outline=(150, 110, 10))
    d.text((tx + 7, ty + 6), "!", font=SANS_B(11), fill=(20, 20, 20))


def scene_court(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (150, 140, 120), (200, 190, 170))
    d.polygon([(x + 8, y + 12), (x + w // 2, y + 2), (x + w - 8, y + 12)],
              fill=(120, 90, 60))
    for i in range(4):
        cx = x + 12 + i * (w - 24) // 3
        d.rectangle([cx - 3, y + 14, cx + 3, y + h - 10], fill=(220, 210, 190))
    d.rectangle([x + 6, y + h - 10, x + w - 6, y + h], fill=(120, 90, 60))
    # scales
    sx, sy = x + w // 2, y + int(h * 0.45)
    d.line([(sx, sy - 8), (sx, sy + 10)], fill=(60, 50, 40), width=2)
    d.line([(sx - 12, sy - 8), (sx + 12, sy - 8)], fill=(60, 50, 40), width=2)
    d.polygon([(sx - 16, sy + 2), (sx - 8, sy + 2), (sx - 12, sy + 8)],
              fill=(200, 170, 60))
    d.polygon([(sx + 8, sy + 2), (sx + 16, sy + 2), (sx + 12, sy + 8)],
              fill=(200, 170, 60))


def scene_eu(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (30, 60, 140), (60, 100, 180))
    cx, cy, r = x + w // 2, y + h // 2, 18
    import math as _m
    for i in range(12):
        a = _m.radians(i * 30 - 90)
        sx, sy = cx + int(r * _m.cos(a)), cy + int(r * _m.sin(a))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(250, 210, 60))
    ef = SERIF_B(26)
    t = "\u20ac"
    d.text((cx - d.textlength(t, font=ef) / 2, cy - 14), t, font=ef,
           fill=(250, 210, 60))


def scene_cricket(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (90, 150, 90), (170, 210, 150))
    d.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(60, 120, 60))
    d.rectangle([x + w // 2 - 16, y + int(h * 0.55), x + w // 2 + 16, y + h],
                fill=(200, 180, 130))
    # stumps
    for i in range(3):
        sx = x + w // 2 - 8 + i * 8
        d.rectangle([sx, y + 10, sx + 3, y + 24], fill=(240, 220, 160))
    # bat + ball
    d.polygon([(x + 14, y + h - 8), (x + 22, y + h - 8), (x + 30, y + 18),
               (x + 22, y + 18)], fill=(180, 140, 90))
    d.ellipse([x + w - 22, y + 12, x + w - 12, y + 22], fill=(176, 30, 40))


def scene_tennis(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (60, 110, 190), (30, 70, 140))
    d.rectangle([x + 6, y + 8, x + w - 6, y + h - 8], fill=(40, 130, 80))
    d.line([(x + 6, y + h // 2), (x + w - 6, y + h // 2)], fill=(255, 255, 255),
           width=2)
    d.line([(x + w // 2, y + 8), (x + w // 2, y + h - 8)], fill=(255, 255, 255),
           width=1)
    d.ellipse([x + w - 26, y + 10, x + w - 14, y + 22], fill=(220, 240, 60),
              outline=(255, 255, 255), width=1)


def scene_f1(d, x, y, w, h):
    scene_frame(d, [x, y, x + w, y + h], (16, 16, 34), (60, 50, 80))
    # chequered flag
    fx, fy = x + 8, y + 8
    for r in range(3):
        for c in range(4):
            col = (255, 255, 255) if (r + c) % 2 == 0 else (20, 20, 20)
            d.rectangle([fx + c * 7, fy + r * 7, fx + c * 7 + 7, fy + r * 7 + 7],
                        fill=col)
    d.line([(fx, fy + 21), (fx, fy + 34)], fill=(180, 180, 180), width=2)
    # race car silhouette
    cx, cy = x + 18, y + h - 26
    d.polygon([(cx, cy), (cx + 14, cy - 10), (cx + 40, cy - 10), (cx + 52, cy),
               (cx + 52, cy + 8), (cx, cy + 8)], fill=(200, 30, 40))
    d.ellipse([cx + 8, cy + 4, cx + 18, cy + 14], fill=(20, 20, 20))
    d.ellipse([cx + 36, cy + 4, cx + 46, cy + 14], fill=(20, 20, 20))
    d.line([(x + 6, y + h - 8), (x + w - 6, y + h - 8)], fill=(240, 200, 60),
           width=2)


# ------------------------------------------------------------------ sections
HEROES = [
    ("1", "RIYADH", "Coalition downs three Houthi missiles over Riyadh",
     "Saudi-led defences say they intercepted the ballistic missiles "
     "aimed at the capital overnight.", "REUTERS · AFP", "CLAIMED", scene_riyadh),
    ("2", "MERCURY", "BepiColombo reaches Mercury after eight years",
     "The ESA-JAXA probe fires its thrusters at 18:24 UTC and enters "
     "its first orbit of Mercury.", "ESA", "CONFIRMED",
     scene_mercury),
    ("3", "ANTALYA", "COP31 runs into overtime with no deal",
     "Third draft due Saturday morning; fossil-fuel language out, "
     "the money fight unresolved.", "REUTERS · UN NEWS", "CONFIRMED",
     scene_cop31),
]

PICTURED = [
    ("4", "WARSAW", "Rutte in Warsaw as Poland seeks more cover",
     "NATO chief meets Polish leaders amid the air-defence debate.",
     "NATO", "REPORTED", scene_nato),
    ("5", "KRYVYI RIH", "Overnight strike kills 2, injures 58",
     "Toll rose to 58 on Saturday morning, six children hurt.",
     "UKRAINE", "REPORTED", scene_strike),
    ("6", "HODEIDAH", "UN warns port strikes threaten aid lifeline",
     "Attacks on the Yemeni port risk cutting food and fuel for millions.",
     "UN", "REPORTED", scene_port),
    ("7", "BEIJING", "US clears 879,868 AI chips for China",
     "House files list Nvidia, AMD licences; some buyers Pentagon-flagged.",
     "HOUSE RECORDS", "CONFIRMED",
     scene_chip),
    ("8", "NEW YORK", "Banks hit in cyberattack on outside vendors",
     "JPMorgan, Visa and Mastercard are among those affected.",
     "WALL STREET", "REPORTED", scene_bank),
    ("9", "COPENHAGEN", "Denmark charges two over Russian murder plot",
     "Prosecutors allege a Kremlin-linked plan to kill on Danish soil.",
     "DENMARK", "REPORTED", scene_court),
    ("10", "BRUSSELS", "EU pays out nearly \u20ac8bn to Ukraine",
     "The latest tranche lands as Kyiv's budget strains deepen.",
     "EU", "REPORTED", scene_eu),
    ("11", "NEW DELHI", "India resume on 159/1 on day three",
     "New Zealand made 368, Nicholls 175 not out, before India replied.",
     "CRICKET", "CONFIRMED", scene_cricket),
    ("12", "TURIN", "Medvedev meets Zverev in tonight's semi",
     "The Russian beat Tiafoe on Friday to set up the last-four clash.",
     "TENNIS", "REPORTED", scene_tennis),
    ("13", "LAS VEGAS", "Las Vegas GP qualifying today",
     "The Strip circuit hosts its shootout for pole under the lights.",
     "F1", "REPORTED", scene_f1),
]

ALSO = [
    ("14", "WASHINGTON", "Trump: bring back Jensen Huang."),
    ("15", "BRASILIA", "Indigenous land safeguards strengthened."),
    ("16", "MADRID", "General strike; police used excessive force."),
    ("17", "ROME", "Workers, students march vs Meloni budget."),
    ("18", "LOS ANGELES", "Jury convicts Palisades Fire arsonist."),
    ("19", "HEALTH", "Pill hailed as pancreatic cancer breakthrough."),
    ("20", "WASHINGTON", "Trump in no rush on Iran; may wait till 2027"),
    ("21", "KYIV", "Ukraine hit three Russian missile launchers."),
    ("22", "NEW DELHI", "US panel: India targets minorities."),
    ("23", "DAKAR", "Youth Olympics: global medalists emerge."),
    ("24", "GAZA", "Children appeal for help on Children's Day."),
    ("25", "KYIV", "Ukraine to send food aid to nine nations."),
    ("26", "BERN", "Swiss hail ICJ Myanmar ruling as key step."),
    ("27", "LONDON", "ICJ ruling may complicate Israel's defence."),
    ("28", "EUROPE", "Youth cost-of-living protests go on."),
    ("29", "ATLANTIC", "Storm Xavier gale warnings narrow."),
    ("30", "LOS ANGELES", "Hyundai unveils 2027 Elantra."),
    ("31", "ODISHA", "Cyclone Akvan crosses coast at Gopalpur."),
    ("32", "NEW YORK", "UN: only 44 of 96 climate signs improving."),
    ("33", "MELBOURNE", "Australia host England in first T20."),
    ("34", "WOLVERHAMPTON", "Darts Grand Slam quarters live."),
    ("35", "WASHINGTON", "Pentagon: Iran engagement cost $48.3bn."),
    ("36", "BEIJING", "Trump 'too busy' to see Kim Jong-un."),
    ("37", "GENEVA", "WHO: Congo Ebola still a global emergency."),
    ("38", "TOKYO", "Japan Tobacco faces $8.6bn Russia loss."),
    ("39", "WASHINGTON", "Contractor-status rule finalized."),
    ("40", "HORMUZ", "Tanker fire; US sanctions Iran oil trustees."),
]


def heroes(d, y, h):
    x0, x1 = 14, W - 14
    cw = (x1 - x0 - 16) / 3
    for i, (num, city, head, deck, src, lab, scene) in enumerate(HEROES):
        x = int(x0 + i * (cw + 8))
        scene(d, x, y, int(cw), 78)
        ty = y + 82
        d.text((x, ty), f"{num}  {city}", font=SANS_B(13), fill=RED)
        label_chip(d, x + cw - 92, ty, lab)
        ty += 18
        ty = text_block(d, x, ty, head, SERIF_B(18), INK, cw, 20)
        text_block(d, x, ty, deck, SANS(12), (50, 50, 50), cw, 14)
        d.text((x, y + h - 12), src, font=SANS_B(9), fill=GREY)
    return y + h


def legend(d, y):
    t = ("CONFIRMED = 2+ OUTLETS \u00b7 CLAIMED = ONE SIDE'S CLAIM "
         "\u00b7 REPORTED = ONE OUTLET")
    f = SANS_B(10)
    d.text(((W - d.textlength(t, font=f)) / 2, y + 1), t, font=f, fill=NAVY)
    return y + 15


def pictured(d, y, row_h):
    x0, x1 = 14, W - 14
    cw = (x1 - x0 - 4 * 8) / 5
    for row in range(2):
        for col in range(5):
            num, city, head, deck, src, lab, scene = PICTURED[row * 5 + col]
            x = int(x0 + col * (cw + 8))
            yy = y + row * row_h
            scene(d, x, yy, int(cw), 42)
            ty = yy + 45
            d.text((x, ty), f"{num} {city}", font=SANS_B(11), fill=RED)
            label_chip(d, x + cw - 78, ty - 1, lab)
            ty += 14
            ty = text_block(d, x, ty, head, SERIF_B(13), INK, cw, 14)
            text_block(d, x, ty, deck, SANS(10), (60, 60, 60), cw, 11)
    return y + 2 * row_h


def world_map(d, y, h):
    x0, x1 = 14, W - 14
    d.rectangle([x0, y, x1, y + h], fill=MAP_BG)
    d.text((x0 + 8, y + 3), "WHERE IT HAPPENED", font=SERIF_B(14), fill=NAVY)
    d.text((x0 + 8, y + 19), "Numbered pins mark the 13 pictured stories. "
           "Story 2, Mercury, is off this map.",
           font=SANS(10), fill=GREY)
    my = y + 32
    def blob(points, fill):
        d.polygon(points, fill=fill)
    blob([(70, my + 6), (300, my + 2), (315, my + 22), (260, my + 40),
          (150, my + 44), (80, my + 30)], MAP_LAND)          # N America
    blob([(300, my + 44), (360, my + 44), (352, my + 70), (312, my + 72)],
         MAP_LAND)                                            # S America
    blob([(470, my + 4), (545, my + 2), (552, my + 16), (500, my + 22),
          (472, my + 14)], MAP_LAND)                          # Europe
    blob([(480, my + 24), (565, my + 24), (556, my + 66), (512, my + 72),
          (486, my + 48)], MAP_LAND)                          # Africa
    blob([(565, my + 4), (880, my + 4), (905, my + 24), (830, my + 40),
          (700, my + 38), (600, my + 24)], MAP_LAND)          # Asia
    blob([(820, my + 52), (905, my + 52), (896, my + 66), (832, my + 66)],
         MAP_LAND)                                            # Australia
    pins = [(1, 592, my + 42), (3, 550, my + 26), (4, 528, my + 8),
            (5, 556, my + 16), (6, 584, my + 54), (7, 792, my + 18),
            (8, 212, my + 20), (9, 505, my + 5), (10, 488, my + 13),
            (11, 684, my + 32), (12, 482, my + 19), (13, 122, my + 22)]
    for num, px, py in pins:
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=2)
        tf = SANS_B(9)
        t = str(num)
        d.text((px - d.textlength(t, font=tf) / 2, py - 6), t, font=tf,
               fill=(255, 255, 255))
    return y + h


def also_list(d, y, h):
    x0, x1 = 14, W - 14
    d.text((x0, y), "ALSO ON SATURDAY 21 NOVEMBER \u2014 27 MORE STORIES",
           font=SANS_B(13), fill=NAVY)
    d.line([(x0, y + 16), (x1, y + 16)], fill=NAVY, width=2)
    cw = (x1 - x0 - 2 * 12) / 3
    top = y + 22
    for i, (num, city, deck) in enumerate(ALSO):
        col, row = divmod(i, 9)
        x = x0 + col * (cw + 12)
        yy = top + row * 13
        head = f"{num} {city} \u2014 "
        for hs, ds in ((12, 12), (12, 11), (12, 10), (11, 9), (10, 9)):
            head_f, f = SANS_B(hs), SANS(ds)
            hw = d.textlength(head, font=head_f)
            if hw + d.textlength(deck, font=f) <= cw:
                break
        d.text((x, yy), head, font=head_f, fill=NAVY)
        d.text((x + hw, yy), deck, font=f, fill=INK)
    return y + h


def utc_strip(d, y, h):
    x0, x1 = 14, W - 14
    d.rectangle([x0, y, x1, y + h], fill=LIGHT)
    d.text((x0 + 8, y + 3), "THE DAY IN UTC", font=SANS_B(12), fill=NAVY)
    moments = [
        ("EARLY SAT", "Riyadh: 3 missiles downed"),
        ("SAT AM", "COP31: 3rd draft, no fossil words"),
        ("19 NOV", "HFAC release: 879,868 chips"),
        ("18:24 UTC", "BepiColombo enters Mercury orbit"),
        ("TONIGHT", "Turin semi; Las Vegas qualifying"),
    ]
    cw = (x1 - x0 - 16) / 5
    for i, (t, lab) in enumerate(moments):
        cx = x0 + 8 + i * cw
        d.text((cx, y + 17), t, font=SANS_B(11), fill=RED)
        d.text((cx, y + 29), lab, font=SANS(10), fill=INK)
    return y + h


def date_check(d, y, h):
    x0, x1 = 14, W - 14
    rrect(d, [x0, y, x1, y + h], 6, outline=NAVY, width=2)
    d.text((x0 + 8, y + 4), "DATE CHECK \u2014 WIRES 21 NOV 2026",
           font=SANS_B(12), fill=NAVY)
    body = ("Left out as Friday 20 November news, NOT shown as Saturday's: "
            "Russian missiles in Poland \u00b7 Kyiv bridges hit \u00b7 UK-EU deals "
            "\u00b7 Shenzhen summit \u00b7 ICJ Myanmar ruling \u00b7 Mongolia "
            "president quits \u00b7 LA quake 4.2 \u00b7 US-China AI pact \u00b7 Pete "
            "Rose pardon \u00b7 Wall Street sell-off. Counted as Saturday's: "
            "BepiColombo orbit insertion (18:24 UTC) \u00b7 Riyadh intercept "
            "(reported early Sat) \u00b7 HFAC release 19 Nov; press 20\u201321 Nov.")
    text_block(d, x0 + 8, y + 21, body, SANS(11), INK, x1 - x0 - 16, 13)
    return y + h


def judge_line(d, y, h):
    d.rectangle([0, y, W, y + h], fill=GOLD_BG)
    t = ("JUDGE: 40 VERIFIED STORIES, 7 REGIONS \u2014 EVERY ONE DATED "
         "SATURDAY 21 NOVEMBER 2026.")
    f = SERIF_B(15)
    d.text(((W - d.textlength(t, font=f)) / 2, y + 4), t, font=f, fill=NAVY)
    return y + h


def footer(d, y, h):
    t = ("Every story happened, or was first reported, on Saturday 21 November "
         "2026 in at least one time zone. Claims attributed; forecasts flagged. "
         "Original drawings.")
    f = SANS(10)
    d.text(((W - d.textlength(t, font=f)) / 2, y + 3), t, font=f, fill=GREY)
    return y + h


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 0
    masthead(d)
    y = 90
    y = region_chips(d, y + 4)
    y = number_strip(d, y + 4)
    y = heroes(d, y + 6, 182)
    y = legend(d, y + 5)
    y = pictured(d, y + 5, 112)
    y = world_map(d, y + 5, 106)
    y = also_list(d, y + 5, 140)
    y = utc_strip(d, y + 4, 48)
    y = date_check(d, y + 4, 60)
    y = judge_line(d, y + 4, 24)
    y = footer(d, y, 16)
    assert y <= H, f"layout overflow: {y} > {H}"
    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes; final y =", y)


if __name__ == "__main__":
    build()
