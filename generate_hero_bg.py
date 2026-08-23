"""Generate the hero background mosaic from a curated set of route maps.

Composites hand-picked white-on-transparent route PNGs into a single
decorative image: three size tiers scattered organically (rejection
sampling + slight rotation), each route drawn twice for a soft glow,
with baked-in edge fades so the hero text stays legible on top.
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

SRC_DIR = Path("updated_map_images")
OUT_PATH = Path("assets/hero-routes.png")

CANVAS_W, CANVAS_H = 2400, 1620

# Indices into sorted(updated_map_images/*.png) — hand-picked traces:
# no stadium ovals, favouring long meandering lines, zigzags and a few
# distinctive shapes.
FEATURE = [111, 150, 263, 303]                                   # hero-sized
MEDIUM  = [2, 63, 83, 102, 106, 113, 176, 204,                   # mid detail
           212, 230]
SMALL   = [5, 21, 30, 69, 90, 129, 145, 160]                     # faint depth
ACCENT  = [11, 16, 39, 60, 120, 148, 262, 300]                  # zigzag energy
SHAPE   = [19, 44, 78, 140, 173, 241]                            # silhouettes

TIERS = [
    # (indices, tile box px, alpha range, rotation range)
    (FEATURE, 460, (0.78, 0.88), (-6, 6)),
    (MEDIUM, 290, (0.52, 0.68), (-9, 9)),
    (ACCENT, 255, (0.50, 0.64), (-9, 9)),
    (SHAPE, 235, (0.46, 0.60), (-8, 8)),
    (SMALL, 180, (0.38, 0.52), (-10, 10)),
]

MIN_GAP = 30          # minimum spacing between tile boxes
EDGE_MARGIN = 60
FADE_START = 0.58     # vertical fade begins at this fraction of the height
FADE_END = 0.98       # fully transparent from here down
EDGE_FADE = 0.06      # horizontal fade width (fraction of width, each side)

# Elliptical "keep-clear" zone where the hero headline sits: traces are
# heavily dimmed inside it and blend back to full strength around it.
TEXT_CENTER = (0.50, 0.40)   # fractions of width / height
TEXT_RADII = (0.38, 0.32)    # ellipse radii as fractions of width / height
TEXT_MIN = 0.14              # alpha multiplier at the ellipse centre


def load_tile(path: Path, box: int, alpha_mul: float, angle: int) -> Image.Image:
    tile = Image.open(path).convert("RGBA")
    scale = box / max(tile.size)
    if scale < 1:
        tile = tile.resize(
            (max(1, round(tile.width * scale)), max(1, round(tile.height * scale))),
            Image.LANCZOS,
        )
    elif scale > 1.4:
        tile = tile.resize(
            (min(tile.width * 2, round(tile.width * scale)),
             min(tile.height * 2, round(tile.height * scale))),
            Image.LANCZOS,
        )
    if angle:
        tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    alpha = tile.getchannel("A").point(lambda v: int(v * alpha_mul))
    tile.putalpha(alpha)
    return tile


def scatter(tiles_info) -> list[tuple[Image.Image, tuple[int, int]]]:
    """Rejection-sample non-overlapping positions, largest tiles first."""
    placed = []
    rng = random.Random(7)
    dropped = 0
    for tile, gap in tiles_info:
        for _ in range(900):
            x = rng.randint(EDGE_MARGIN, CANVAS_W - EDGE_MARGIN - tile.width)
            y = rng.randint(20, CANVAS_H - 40 - tile.height)
            box = (x - gap, y - gap, x + tile.width + gap, y + tile.height + gap)
            if all(box[0] >= b[2] or box[2] <= b[0] or box[1] >= b[3] or box[3] <= b[1]
                   for b in placed):
                placed.append(box)
                yield tile, (x, y)
                break
        else:
            dropped += 1
    print(f"placed {len(tiles_info) - dropped}/{len(tiles_info)}")


def text_zone_mask(width: int, height: int) -> Image.Image:
    """Smooth elliptical multiplier that clears the headline area."""
    import numpy as np

    yy, xx = np.mgrid[0:height, 0:width].astype(float)
    dx = (xx - TEXT_CENTER[0] * width) / (TEXT_RADII[0] * width)
    dy = (yy - TEXT_CENTER[1] * height) / (TEXT_RADII[1] * height)
    d = np.hypot(dx, dy)
    # 0 at the centre -> 1 beyond the soft falloff ring
    falloff = np.clip((d - 0.55) / 0.9, 0.0, 1.0)
    values = (TEXT_MIN + (1.0 - TEXT_MIN) * falloff) * 255.0
    return Image.fromarray(values.astype("uint8"), "L")


def fade_mask(width: int, height: int) -> Image.Image:
    vertical = Image.linear_gradient("L").resize((width, height))
    lo, hi = int(FADE_START * 255), int(FADE_END * 255)

    def v_factor(v: int) -> int:
        if v <= lo:
            return 255
        if v >= hi:
            return 0
        return int(255 * (1 - (v - lo) / (hi - lo)))

    vertical = vertical.point(v_factor)

    horizontal = (
        Image.linear_gradient("L").rotate(90, expand=True).resize((width, height))
    )
    edge = int(EDGE_FADE * 255)

    def h_factor(v: int) -> int:
        if v < edge:
            return int(255 * v / edge)
        if v > 255 - edge:
            return int(255 * (255 - v) / edge)
        return 255

    horizontal = horizontal.point(h_factor)
    return ImageChops.multiply(vertical, horizontal)


def main() -> None:
    files = sorted(SRC_DIR.glob("*.png"))
    rng = random.Random(11)

    tiles_info = []
    for indices, box, (a_lo, a_hi), (r_lo, r_hi) in TIERS:
        for idx in indices:
            angle = rng.randint(r_lo, r_hi) if r_lo or r_hi else 0
            tile = load_tile(files[idx], box, rng.uniform(a_lo, a_hi), angle)
            tiles_info.append((tile, MIN_GAP))

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

    # Soft glow pass underneath, then the sharp pass on top.
    glow = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    for tile, pos in scatter(tiles_info):
        soft = tile.filter(ImageFilter.GaussianBlur(7)).point(lambda v: min(255, int(v * 1.3)))
        glow.alpha_composite(soft, pos)
        canvas.alpha_composite(tile, pos)

    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(2)))
    combined = ImageChops.multiply(
        fade_mask(CANVAS_W, CANVAS_H), text_zone_mask(CANVAS_W, CANVAS_H)
    )
    canvas.putalpha(ImageChops.multiply(canvas.getchannel("A"), combined))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT_PATH, optimize=True)
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
