#!/usr/bin/env python3
"""Generates the Android launcher icons and the Play listing assets.

The mark is a reading of the IMRO badge the komitadži fought under — laurel
wreath, crossed rifles, grenade, skull — with the motto СЛОБОДА ИЛИ СМРТ split
across two curved ribbons. The badge is 1900s historical insignia and the motto
is a historical slogan; this is an original drawing of them, not a trace of any
photograph.

Authored at 128x128, NOT the 32x32 of the first version — text is simply
impossible on a 32 grid, and the motto is the whole point of the badge. Upscaled
with NEAREST so it keeps the blocky look of the game.

Run: python3 scripts/make-icons.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "android/app/src/main/res"
PLAY = ROOT / "play"

N = 128                       # authoring resolution

# The badge must be centred on the canvas. CY was 70 on a 128px canvas — six
# pixels low — so the whole mark sat off-centre on the launcher and the bottom
# ribbon ran to y=126 of 128, close enough to the edge for the adaptive-icon mask
# to bite into it. Both radii below are chosen so the widest part of the badge
# (the ribbons, at R_OUT + RIB_OUT) leaves a real margin inside the canvas.
CX, CY = 64, 64               # dead centre
R_OUT = 36                    # outer edge of the laurel
RIB_OUT = 15                  # how far the ribbons stand outside the laurel
# widest extent = 36 + 15 = 51 from centre -> 102px across on a 128 canvas,
# leaving 13px of margin all round.
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

BG        = (58, 20, 16)      # deep oxblood
FIELD     = (24, 30, 26)      # near-black centre of the badge
WREATH_L  = (150, 154, 106)
WREATH_D  = (92, 99, 64)
BANNER    = (176, 44, 40)
BANNER_HI = (208, 68, 62)
BANNER_D  = (122, 28, 26)
BONE      = (232, 220, 196)
INK       = (28, 20, 13)
WOOD      = (146, 96, 52)
STEEL     = (168, 172, 180)
GREN      = (112, 118, 80)
GREN_D    = (72, 78, 52)
BRASS     = (192, 138, 62)


def ribbon(img, r_in, r_out, a0, a1, flip=False):
    """A curved band swept between two angles — the ribbon the motto sits on.
    Swept round the wreath rather than laid straight across it: a straight bar
    reads as a bar, not as cloth."""
    d = ImageDraw.Draw(img)
    steps = 260
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        for k in range(r_out - r_in):
            rr = r_in + k
            x = CX + math.cos(a) * rr
            y = CY + math.sin(a) * rr
            if k == 0 or k == (r_out - r_in) - 1:
                c = BANNER_D                      # the fold along each edge
            elif k <= 1:
                c = BANNER_HI                     # a lit edge, so it has body
            else:
                c = BANNER
            d.point((x, y), fill=c)
    # swallow-tails at each end
    for end, sgn in ((a0, -1), (a1, 1)):
        a = math.radians(end)
        for k in range(-3, 4):
            rr = (r_in + r_out) / 2 + k
            x = CX + math.cos(a) * rr + sgn * 3
            y = CY + math.sin(a) * rr
            d.point((x, y), fill=BANNER_D)


def text_arc(img, text, radius, a0, a1, size, fill, flip=False):
    """Set the text ALONG the ribbon, one glyph at a time, each rotated to sit
    square on the curve. Straight text across a curved band looks pasted on."""
    font = ImageFont.truetype(FONT, size)
    n = len(text)
    for i, ch in enumerate(text):
        t = (i + 0.5) / n
        a = a0 + (a1 - a0) * t
        ar = math.radians(a)

        box = font.getbbox(ch)
        w, h = max(1, box[2] - box[0]), max(1, box[3] - box[1])
        glyph = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
        ImageDraw.Draw(glyph).text((2 - box[0], 2 - box[1]), ch, font=font, fill=fill)

        # Tangent to the arc. The bottom ribbon needs the OTHER convention, or the
        # motto comes out inverted — the glyph's "up" has to point toward the
        # centre of the circle there, not away from it.
        rot = -(a + 90) if not flip else (90 - a)
        glyph = glyph.rotate(rot, resample=Image.BICUBIC, expand=True)

        x = CX + math.cos(ar) * radius
        y = CY + math.sin(ar) * radius
        img.alpha_composite(glyph, (int(x - glyph.width / 2), int(y - glyph.height / 2)))


def badge():
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # --- laurel ring + dark field ---
    for y in range(N):
        for x in range(N):
            dist = math.hypot(x - CX, y - CY)
            if dist <= R_OUT - 9:
                img.putpixel((x, y), (*FIELD, 255))
            elif dist <= R_OUT:
                a = math.atan2(y - CY, x - CX)
                leaf = int((a + math.pi) / (math.pi / 14)) % 2
                img.putpixel((x, y), (*(WREATH_L if leaf else WREATH_D), 255))

    # --- crossed RIFLE and SWORD ---
    # They were two identical sticks before, which is just an X. On the badge they
    # are two different weapons, and they have to read as two different weapons:
    # one has a wooden stock and a barrel, the other a blade, a guard and a grip.

    def along(angle_deg, t, off=0):
        a = math.radians(angle_deg)
        ca, sa = math.cos(a), math.sin(a)
        return (CX + ca * t - sa * off, CY + sa * t + ca * off)

    # RIFLE — butt low-left, muzzle high-right
    RA = -35
    for t in range(-29, 30):
        c = WOOD if t < 0 else STEEL              # stock, then barrel
        half = 2 if t < -7 else 1                 # the butt is the thick end
        for w in range(-half, half + 1):
            d.point(along(RA, t, w), fill=c)
    for w in range(-3, 4):                        # butt-plate
        d.point(along(RA, -29, w), fill=BRASS)
    for t in range(-5, 2):                        # bolt handle, out to one side
        d.point(along(RA, t, 3), fill=STEEL)
    d.point(along(RA, 27, 2), fill=STEEL)         # front sight
    d.point(along(RA, 27, -2), fill=STEEL)

    # SWORD — grip low-right, point high-left, and it TAPERS
    SA = -145
    for t in range(-28, 31):
        if t < -19:
            c, half = (54, 40, 28), 1             # grip
        elif t < -15:
            c, half = BRASS, 1                    # ferrule
        else:
            c = STEEL
            half = 2 if t < 18 else 1             # blade narrows toward the point
        for w in range(-half, half + 1):
            d.point(along(SA, t, w), fill=c)
    for w in range(-5, 6):                        # crossguard, square to the blade
        d.point(along(SA, -14, w), fill=BRASS)
        d.point(along(SA, -13, w), fill=BRASS)
    for w in range(-2, 3):                        # pommel
        d.point(along(SA, -29, w), fill=BRASS)
    d.point(along(SA, 30, 0), fill=BONE)          # the point catching the light

    # --- grenade at the centre ---
    for gy in range(-11, 13):
        for gx in range(-10, 11):
            if gx * gx + gy * gy * 0.85 <= 100:
                hatch = ((gx // 3) + (gy // 3)) % 2 == 0
                d.point((CX + gx, CY + gy), fill=GREN if hatch else GREN_D)
    d.rectangle([CX - 2, CY - 15, CX + 2, CY - 11], fill=GREN_D)      # fuse

    # --- skull, at the foot of the wreath (pulled up to clear the smaller ring) ---
    sx, sy = CX - 6, CY + 14
    d.rectangle([sx, sy, sx + 12, sy + 8], fill=BONE)
    d.rectangle([sx + 2, sy + 2, sx + 4, sy + 4], fill=INK)          # eyes
    d.rectangle([sx + 8, sy + 2, sx + 10, sy + 4], fill=INK)
    d.rectangle([sx + 6, sy + 5, sx + 6, sy + 7], fill=(150, 138, 116))
    for k in (0, 4, 8, 12):                                          # teeth
        d.rectangle([sx + k, sy + 9, sx + k + 1, sy + 11], fill=BONE)

    # --- the two ribbons: СЛОБОДА over the top, ИЛИ СМРТ under the foot ---
    ribbon(img, R_OUT + 2, R_OUT + RIB_OUT, 197, 343)     # top arc
    ribbon(img, R_OUT + 2, R_OUT + RIB_OUT, 17, 163)      # bottom arc

    text_arc(img, "СЛОБОДА", R_OUT + 8.5, 203, 337, 10, BONE)
    text_arc(img, "ИЛИ СМРТ", R_OUT + 8.5, 163, 17, 10, BONE, flip=True)

    return img


def scale(img, n):
    """NEAREST when enlarging (keeps the blocky look); LANCZOS when shrinking,
    or the motto turns to aliased noise at launcher sizes."""
    return img.resize((n, n), Image.NEAREST if n >= N else Image.LANCZOS)


def on_background(fg, n, round_mask=False):
    out = Image.new("RGBA", (n, n), (*BG, 255))
    out.alpha_composite(scale(fg, n))
    if round_mask:
        mask = Image.new("L", (n, n), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
        out.putalpha(mask)
    return out


def adaptive_foreground(fg, n):
    """Adaptive icons crop to a circle; art must sit inside the middle ~72%."""
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    inner = int(n * 0.72)
    out.alpha_composite(scale(fg, inner), ((n - inner) // 2, (n - inner) // 2))
    return out


DENSITIES = {"mdpi": (48, 108), "hdpi": (72, 162), "xhdpi": (96, 216),
             "xxhdpi": (144, 324), "xxxhdpi": (192, 432)}

art = badge()

for dens, (launcher, fg_size) in DENSITIES.items():
    out = RES / f"mipmap-{dens}"
    out.mkdir(parents=True, exist_ok=True)
    on_background(art, launcher).save(out / "ic_launcher.png")
    on_background(art, launcher, round_mask=True).save(out / "ic_launcher_round.png")
    adaptive_foreground(art, fg_size).save(out / "ic_launcher_foreground.png")
    print(f"  mipmap-{dens}: {launcher}px + {fg_size}px foreground")

(RES / "values").mkdir(parents=True, exist_ok=True)
(RES / "values/ic_launcher_background.xml").write_text(
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    f'    <color name="ic_launcher_background">#{BG[0]:02X}{BG[1]:02X}{BG[2]:02X}</color>\n'
    "</resources>\n"
)

PLAY.mkdir(parents=True, exist_ok=True)
on_background(art, 512).convert("RGB").save(PLAY / "play-icon-512.png")
print("  play/play-icon-512.png")

feat = Image.new("RGBA", (1024, 500), (*BG, 255))
dd = ImageDraw.Draw(feat)
for y in range(500):
    t = y / 499
    dd.line([(0, y), (1023, y)],
            fill=(*tuple(int(BG[i] * (1 - t) + INK[i] * t) for i in range(3)), 255))
feat.alpha_composite(scale(art, 416), (72, 42))
feat.convert("RGB").save(PLAY / "play-feature-1024x500.png")
print("  play/play-feature-1024x500.png")

prev = Image.new("RGBA", (760, 240), (32, 32, 36, 255))
x = 24
for s in (192, 96, 72, 48):
    prev.alpha_composite(on_background(art, s, round_mask=True), (x, 24))
    prev.alpha_composite(on_background(art, s), (x, 24 + 200 - s))
    x += s + 24
prev.convert("RGB").save(PLAY / "icon-preview.png")
print("  play/icon-preview.png")
print("done")
