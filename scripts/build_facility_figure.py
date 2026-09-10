#!/usr/bin/env python3
"""Rebuild the Facilities figure (assets/img/research/facility_overview.jpg).

Edit CROP below, run the script, check the result, commit. Nothing else on
the site needs to change -- the Facilities tile already points at the output
path.

    python scripts/build_facility_figure.py            # rebuild
    python scripts/build_facility_figure.py --show     # also write a preview
                                                       # with panel guides

The master is `scripts/figures/facility_overview_master.png`, a 1950x2400
lossless copy of the four-panel figure with the air compressor's model
number already painted out. Work from it rather than from the copy in the
NSF CAREER folder: that original still carries the model number, and it must
not end up in this repo, which is public.

Panel boundaries in master pixels, measured from the white gutters
(left, top, right, bottom) -- see PANELS below. Panels (b) and (c) sit side
by side in one band, split by the gutter at x 804-860.

Row-wise crops are the clean ones, since they never cut a panel in half:

    CROP = (0, 0, 1950, 1420)      panel (a) only
    CROP = (0, 0, 1950, 2150)      panels (a) (b) (c), drop (d)
    CROP = (0, 1420, 1950, 2400)   drop (a), keep (b) (c) (d)

To keep a single panel from the middle band, take its box from PANELS and
pad it a little, e.g. (b) alone is roughly (150, 1450, 830, 2150).

Run with --show first: it writes a preview with every panel outlined in red
and your CROP in blue, which is much quicker than guessing and rebuilding.
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw

# --- edit these -------------------------------------------------------------

# (left, top, right, bottom) in master pixels, or None to keep the whole figure.
CROP = None

# Width of the published image. The tile displays it well under this, so the
# extra pixels are just there for sharp rendering on high-density screens.
OUT_WIDTH = 1100

JPEG_QUALITY = 88

# ----------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MASTER = os.path.join(HERE, "figures", "facility_overview_master.png")
OUT = os.path.join(ROOT, "assets", "img", "research", "facility_overview.jpg")

PANELS = {
    "a  test stand": (176, 0, 1774, 1390),
    "b  hot fire": (176, 1483, 803, 2030),
    "c  wave map": (861, 1442, 1773, 2100),
    "d  high-speed": (176, 2150, 1774, 2399),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", action="store_true",
                    help="also write a preview with panel guides drawn on")
    args = ap.parse_args()

    if not os.path.isfile(MASTER):
        print(f"master not found: {MASTER}", file=sys.stderr)
        return 1

    im = Image.open(MASTER).convert("RGB")
    print(f"master      {im.width}x{im.height}")

    if args.show:
        guide = im.copy()
        d = ImageDraw.Draw(guide)
        for name, box in PANELS.items():
            d.rectangle(box, outline=(255, 0, 0), width=6)
            d.text((box[0] + 16, box[1] + 12), name, fill=(255, 0, 0))
        if CROP:
            d.rectangle(CROP, outline=(0, 160, 255), width=10)
        path = os.path.join(HERE, "figures", "facility_overview_guides.png")
        guide.resize((900, round(guide.height * 900 / guide.width)),
                     Image.LANCZOS).save(path)
        print(f"guides      {path}")

    if CROP:
        im = im.crop(CROP)
        print(f"cropped     {im.width}x{im.height}  CROP={CROP}")

    if im.width != OUT_WIDTH:
        im = im.resize((OUT_WIDTH, round(im.height * OUT_WIDTH / im.width)),
                       Image.LANCZOS)

    im.save(OUT, quality=JPEG_QUALITY, optimize=True, progressive=True)
    print(f"wrote       {os.path.relpath(OUT, ROOT)}  "
          f"{im.width}x{im.height}  {os.path.getsize(OUT) / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
