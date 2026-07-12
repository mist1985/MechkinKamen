#!/usr/bin/env python3
"""Generates the Android launcher icons and the Play listing icon.

The art is pixel-authored here and upscaled with NEAREST so it keeps the same
blocky, nearest-filtered look as the game itself. Palette is the game's own
(--ink/--bone/--blood/--brass from the stylesheet).

Run: python3 scripts/make-icons.py
"""

from PIL import Image, ImageDraw
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "android/app/src/main/res"
PLAY = ROOT / "play"

# Game palette
INK = (28, 20, 13)
BLOOD = (143, 43, 31)
BRASS = (192, 138, 62)
BONE = (232, 220, 196)

BG = (110, 33, 24)          # deep blood-red sky behind the crag
STONE_L = (159, 160, 168)   # lit faces
STONE_M = (124, 124, 130)   # body
STONE_D = (74, 74, 82)      # shadowed faces

PAL = {
    ".": None,          # transparent
    "L": STONE_L,
    "S": STONE_M,
    "D": STONE_D,
    "P": BRASS,         # flagpole
    "R": BLOOD,         # banner
    "F": BONE,          # banner highlight
}

# 24x24. The crag of Mechkin Kamen with the Republic's banner on the summit.
ART = [
    "........................",
    "........................",
    "...........P............",
    "...........PRRRF........",
    "...........PRRRF........",
    "...........PRR..........",
    "...........P............",
    "..........LLL...........",
    ".........LLSSD..........",
    "........LLSSSSD.........",
    ".......LLSSSSSDD........",
    "......LLSSSSSSSDD.......",
    ".....LLSSSSSSSSSDD......",
    "....LLSSSSSSSSSSSDD.....",
    "...LLSSSSSSSSSSSSSDD....",
    "..LLSSSSSSSSSSSSSSSDD...",
    "..LSSSSSSSSSSSSSSSSSD...",
    ".LLSSSSSSSSSSSSSSSSSDD..",
    ".LSSSSSSSSSSSSSSSSSSSD..",
    ".LSSSSSSSSSSSSSSSSSSSD..",
    ".DDDDDDDDDDDDDDDDDDDDD..",
    "........................",
    "........................",
    "........................",
]


def render(size=24):
    """The crag on a transparent field, at 1px-per-cell."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(ART):
        for x, ch in enumerate(row):
            c = PAL.get(ch)
            if c:
                px[x, y] = (*c, 255)
    return img


def scale(img, n):
    return img.resize((n, n), Image.NEAREST)


def on_background(fg, n, radius=None):
    """Composite the crag over the sky colour. radius=None -> square."""
    out = Image.new("RGBA", (n, n), (*BG, 255))
    if radius is not None:
        mask = Image.new("L", (n, n), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
        out.putalpha(mask)
    out.alpha_composite(scale(fg, n))
    if radius is not None:
        # Re-apply the circular mask so the art cannot spill past the edge.
        mask = Image.new("L", (n, n), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
        out.putalpha(mask)
    return out


def adaptive_foreground(fg, n):
    """Adaptive icons crop to a circle, so the art must sit inside the safe
    zone — roughly the middle 66%. Anything outside can be shaved off."""
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    inner = int(n * 0.66)
    out.alpha_composite(scale(fg, inner), ((n - inner) // 2, (n - inner) // 2))
    return out


DENSITIES = {           # launcher px, adaptive-foreground px
    "mdpi": (48, 108),
    "hdpi": (72, 162),
    "xhdpi": (96, 216),
    "xxhdpi": (144, 324),
    "xxxhdpi": (192, 432),
}

art = render()

for d, (launcher, fg_size) in DENSITIES.items():
    out = RES / f"mipmap-{d}"
    out.mkdir(parents=True, exist_ok=True)
    on_background(art, launcher).save(out / "ic_launcher.png")
    on_background(art, launcher, radius=1).save(out / "ic_launcher_round.png")
    adaptive_foreground(art, fg_size).save(out / "ic_launcher_foreground.png")
    print(f"  mipmap-{d}: {launcher}px + {fg_size}px foreground")

# Adaptive background is a flat colour resource, not a bitmap.
(RES / "values").mkdir(parents=True, exist_ok=True)
(RES / "values/ic_launcher_background.xml").write_text(
    '<?xml version="1.0" encoding="utf-8"?>\n'
    "<resources>\n"
    f'    <color name="ic_launcher_background">#{BG[0]:02X}{BG[1]:02X}{BG[2]:02X}</color>\n'
    "</resources>\n"
)

# Play Console requires a 512x512 32-bit PNG for the store listing.
PLAY.mkdir(parents=True, exist_ok=True)
on_background(art, 512).convert("RGB").save(PLAY / "play-icon-512.png")
print("  play/play-icon-512.png")

# Feature graphic: 1024x500, shown at the top of the store page.
feat = Image.new("RGBA", (1024, 500), (*BG, 255))
for y in range(500):  # vertical wash toward ink at the base
    t = y / 499
    row = tuple(int(BG[i] * (1 - t) + INK[i] * t) for i in range(3))
    ImageDraw.Draw(feat).line([(0, y), (1023, y)], fill=(*row, 255))
feat.alpha_composite(scale(art, 420), (60, 40))
d = ImageDraw.Draw(feat)
d.rectangle([560, 232, 980, 236], fill=(*BRASS, 255))
feat.convert("RGB").save(PLAY / "play-feature-1024x500.png")
print("  play/play-feature-1024x500.png")
print("done")
