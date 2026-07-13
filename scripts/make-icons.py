#!/usr/bin/env python3
"""Generates the Android launcher icons and the Play listing assets.

The mark is an 8-bit reading of the IMRO badge the komitadji fought under —
laurel wreath, crossed rifles, grenade, skull, and the "Слобода или смрть"
banner. The original badge is 1900s historical insignia; this is an original
pixel interpretation of it, not a trace of any photograph.

Authored on a 32x32 grid and upscaled with NEAREST, so it keeps the same blocky,
nearest-filtered look as the game itself. The badge is dense with detail, and an
icon read at 48px can carry perhaps four ideas — so the lettering ("ЗА ЗАСЛУГА",
"ВМРО") is dropped and the silhouette is what survives.

Run: python3 scripts/make-icons.py
"""

import math
from PIL import Image, ImageDraw
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "android/app/src/main/res"
PLAY = ROOT / "play"

N = 32  # pixel-art grid

INK = (28, 20, 13)
BG = (58, 20, 16)          # deep oxblood, behind the badge

FIELD = (24, 30, 26)       # near-black centre of the badge
FIELD_HI = (38, 46, 38)
WREATH_L = (150, 154, 106) # laurel, lit
WREATH_D = (92, 99, 64)    # laurel, shadowed
BANNER = (176, 44, 40)     # the red ribbon
BANNER_D = (122, 28, 26)
BONE = (232, 220, 196)     # skull
BONE_D = (150, 138, 116)
WOOD = (146, 96, 52)       # rifle stock
STEEL = (168, 172, 180)    # barrel + bayonet
GREN = (112, 118, 80)      # grenade body
GREN_D = (72, 78, 52)


def badge():
    """Draw the emblem on a transparent 32x32 field.

    Order matters: wreath, then field, then rifles, then grenade, then skull,
    then the banner last so the ribbon sits over the top of the wreath the way
    it does on the real badge.
    """
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    px = img.load()

    def put(x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < N and 0 <= y < N:
            px[x, y] = (*c, 255)

    cx, cy = 16.0, 19.0
    R = 12.0        # outer edge of the laurel
    RING = 3.0      # laurel thickness

    # --- laurel ring + dark field ---
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - cx, y - cy)
            if d <= R - RING:
                put(x, y, FIELD)
            elif d <= R:
                # alternate tone around the ring so it reads as leaves, not a hoop
                a = math.atan2(y - cy, x - cx)
                leaf = int((a + math.pi) / (math.pi / 9)) % 2
                put(x, y, WREATH_L if leaf else WREATH_D)

    # --- crossed rifle and bayonet ---
    # Each arm runs corner to corner through the field: wood at the butt end,
    # steel toward the muzzle, so the X reads as two weapons rather than sticks.
    for t in range(-8, 9):
        for arm in (1, -1):
            x = cx + t * 1.0
            y = cy + t * 0.62 * arm
            c = STEEL if t > 1 else WOOD
            put(x, y, c)
            put(x, y - 1, c)
        # bayonet tip on the upper-right arm
        if t >= 7:
            put(cx + t, cy - t * 0.62 - 2, STEEL)

    # --- grenade at the centre ---
    for gy in range(-3, 5):
        for gx in range(-3, 4):
            if gx * gx + gy * gy * 0.9 <= 9.5:
                hatch = (gx + gy) % 2 == 0     # segmented, like a Mills bomb
                put(cx + gx, cy + gy, GREN if hatch else GREN_D)
    put(cx, cy - 4, GREN_D)                    # fuse
    put(cx + 1, cy - 4, GREN_D)

    # --- skull, seated at the foot of the wreath ---
    sx, sy = cx - 2, cy + 7
    for y in range(3):
        for x in range(5):
            put(sx + x, sy + y, BONE)
    put(sx + 1, sy + 1, INK)                   # eye sockets
    put(sx + 3, sy + 1, INK)
    put(sx + 2, sy + 2, BONE_D)                # nose
    for x in (0, 2, 4):                        # jaw
        put(sx + x, sy + 3, BONE)
    put(sx + 1, sy + 3, BONE_D)
    put(sx + 3, sy + 3, BONE_D)

    # --- the banner: a ribbon arcing OVER the top of the wreath ---
    # A straight bar reads as a bar. Sweeping it round the crown of the wreath,
    # the way the real badge does, is what makes it read as cloth.
    for deg in range(188, 353):
        a = math.radians(deg)
        for k in range(4):
            rr = R + 0.5 + k
            x = cx + math.cos(a) * rr
            y = cy + math.sin(a) * rr * 1.05
            put(x, y, BANNER if k < 3 else BANNER_D)
    # highlight along the crown so the ribbon has a lit edge
    for deg in range(192, 349, 2):
        a = math.radians(deg)
        put(cx + math.cos(a) * (R + 0.6), cy + math.sin(a) * (R + 0.6) * 1.05,
            (208, 68, 62))
    # swallow-tail ends, flaring out past the wreath
    for k in range(4):
        put(1 + k, 9 + k, BANNER)
        put(1 + k, 10 + k, BANNER_D)
        put(30 - k, 9 + k, BANNER)
        put(30 - k, 10 + k, BANNER_D)
    put(0, 8, BANNER_D)
    put(31, 8, BANNER_D)

    return img


def scale(img, n):
    return img.resize((n, n), Image.NEAREST)


def on_background(fg, n, round_mask=False):
    out = Image.new("RGBA", (n, n), (*BG, 255))
    out.alpha_composite(scale(fg, n))
    if round_mask:
        mask = Image.new("L", (n, n), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
        out.putalpha(mask)
    return out


def adaptive_foreground(fg, n):
    """Adaptive icons crop to a circle; art must sit inside the middle ~66%."""
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    inner = int(n * 0.68)
    out.alpha_composite(scale(fg, inner), ((n - inner) // 2, (n - inner) // 2))
    return out


DENSITIES = {"mdpi": (48, 108), "hdpi": (72, 162), "xhdpi": (96, 216),
             "xxhdpi": (144, 324), "xxxhdpi": (192, 432)}

art = badge()

for d, (launcher, fg_size) in DENSITIES.items():
    out = RES / f"mipmap-{d}"
    out.mkdir(parents=True, exist_ok=True)
    on_background(art, launcher).save(out / "ic_launcher.png")
    on_background(art, launcher, round_mask=True).save(out / "ic_launcher_round.png")
    adaptive_foreground(art, fg_size).save(out / "ic_launcher_foreground.png")
    print(f"  mipmap-{d}: {launcher}px + {fg_size}px foreground")

(RES / "values").mkdir(parents=True, exist_ok=True)
(RES / "values/ic_launcher_background.xml").write_text(
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    f'    <color name="ic_launcher_background">#{BG[0]:02X}{BG[1]:02X}{BG[2]:02X}</color>\n'
    "</resources>\n"
)

PLAY.mkdir(parents=True, exist_ok=True)
on_background(art, 512).convert("RGB").save(PLAY / "play-icon-512.png")
print("  play/play-icon-512.png")

# Feature graphic: 1024x500 for the top of the store page.
feat = Image.new("RGBA", (1024, 500), (*BG, 255))
d = ImageDraw.Draw(feat)
for y in range(500):
    t = y / 499
    d.line([(0, y), (1023, y)], fill=(*tuple(int(BG[i] * (1 - t) + INK[i] * t) for i in range(3)), 255))
feat.alpha_composite(scale(art, 416), (72, 42))
feat.convert("RGB").save(PLAY / "play-feature-1024x500.png")
print("  play/play-feature-1024x500.png")

# A side-by-side preview at real launcher sizes, for eyeballing legibility.
prev = Image.new("RGBA", (760, 240), (32, 32, 36, 255))
x = 24
for s in (192, 96, 72, 48):
    prev.alpha_composite(on_background(art, s, round_mask=True), (x, 24))
    prev.alpha_composite(on_background(art, s), (x, 24 + 200 - s))
    x += s + 24
prev.convert("RGB").save(PLAY / "icon-preview.png")
print("  play/icon-preview.png  <- look at this one")
print("done")
