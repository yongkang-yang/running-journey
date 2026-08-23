"""Generate the hero background mosaic from the exported route maps.

Composites the white-on-transparent route PNGs into a single decorative
image with baked-in edge fades, so the hero text stays legible on top.
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageChops

SRC_DIR = Path("updated_map_images")
OUT_PATH = Path("assets/hero-routes.png")

CANVAS_W, CANVAS_H = 2400, 1500
CELL = 330          # grid cell size; tiles are contained inside with breathing room
TILE_BOX = 252      # max tile dimension
JITTER = 16         # random offset so the grid feels organic
FADE_START = 0.40   # vertical fade begins at this fraction of the height
FADE_END = 0.86     # fully transparent from here down
EDGE_FADE = 0.07    # horizontal fade width (fraction of width, each side)


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
        Image.linear_gradient("L")
        .rotate(90, expand=True)
        .resize((width, height))
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
    random.seed(11)
    files = sorted(SRC_DIR.glob("*.png"))
    if not files:
        raise SystemExit(f"no route images found in {SRC_DIR}")
    random.shuffle(files)

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    cols = math.ceil(CANVAS_W / CELL)
    rows = math.ceil(CANVAS_H / CELL)

    k = 0
    for row in range(rows):
        for col in range(cols):
            path = files[k % len(files)]
            k += 1
            tile = Image.open(path).convert("RGBA")
            tile.thumbnail((TILE_BOX, TILE_BOX))
            alpha = tile.getchannel("A").point(
                lambda v: int(v * random.uniform(0.45, 0.8))
            )
            tile.putalpha(alpha)
            x = col * CELL + (CELL - tile.width) // 2 + random.randint(-JITTER, JITTER)
            y = row * CELL + (CELL - tile.height) // 2 + random.randint(-JITTER, JITTER)
            canvas.alpha_composite(tile, (max(x, 0), max(y, 0)))

    canvas.putalpha(ImageChops.multiply(canvas.getchannel("A"), fade_mask(CANVAS_W, CANVAS_H)))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT_PATH, optimize=True)
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
