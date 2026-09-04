import argparse
import os
from fontTools.ttLib import TTFont

HERE = os.path.dirname(__file__)
FONTS_DIR = os.path.join(HERE, "fonts")
SATOSHI_PATH = os.path.join(FONTS_DIR, "Satoshi-Variable.ttf")


def get_master_point(font, glyph_name, point_index, wght_tuple):
    # start from the glyph's default (regular master) outline coordinates
    glyf = font["glyf"][glyph_name]
    default_coords = list(glyf.coordinates)[point_index]

    # look up the gvar delta for this glyph at the requested axis tuple
    gvar = font["gvar"]
    for tv in gvar.variations.get(glyph_name, []):
        if tv.axes.get("wght") == wght_tuple:
            dx, dy = tv.coordinates[point_index]
            return (default_coords[0] + dx, default_coords[1] + dy)  # default + delta = master point
    return default_coords  # no matching tuple, so it stays at default


def interpolate(a, b, t):
    return a + (b - a) * t  # linear interpolation between two masters


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", default=SATOSHI_PATH, help="Path to a variable font")
    parser.add_argument("--glyph", default="A")
    parser.add_argument("--point", type=int, default=0,
                         help="glyf point index to read (default 0 — Satoshi's "
                              "'A' left-edge point, a clean left/right move as "
                              "wght changes)")
    args = parser.parse_args()

    font_path = args.font
    point_index = args.point

    font = TTFont(font_path)
    axis = font["fvar"].axes[0]  # only look at the font's first axis (e.g. wght)
    axis_min, axis_default, axis_max = axis.minValue, axis.defaultValue, axis.maxValue

    # gvar tuples are keyed by normalized (-1..0..1) axis position, where 0 is
    # always the default. Figure out which normalized tuple corresponds to
    # which real axis extreme, since Satoshi's default (900) IS its max, so
    # the default isn't in the middle of the range.
    min_tuple = (-1.0, -1.0, 0.0)
    max_tuple = (0.0, 1.0, 1.0)

    # fetch the real outline point at each end of the axis
    min_point = get_master_point(font, args.glyph, point_index, min_tuple)
    max_point = get_master_point(font, args.glyph, point_index, max_tuple)

    print(f"Real coordinates read from {font_path}:")
    print(f"  glyph {args.glyph!r}, point {point_index}, axis {axis.axisTag!r} "
          f"({axis_min:.0f}-{axis_default:.0f}-{axis_max:.0f})")
    print(f"  point at {axis.axisTag}={axis_min:.0f} = {min_point}")
    print(f"  point at {axis.axisTag}={axis_max:.0f} = {max_point}")
    print()

    print("min_point = {}".format(min_point))
    print("max_point = {}".format(max_point))
    print("def interpolate(a, b, t):")
    print("    return a + (b - a) * t")
    print(f"for {axis.axisTag} in ({axis_min:.0f}, ..., {axis_max:.0f}):")
    print(f"    t = ({axis.axisTag} - {axis_min:.0f}) / ({axis_max:.0f} - {axis_min:.0f})")
    print("    x = interpolate(min_point[0], max_point[0], t)")
    print(f'    print(f"{axis.axisTag}={{{axis.axisTag}}}: x={{x}}")')
    print()
    print("-" * 40)
    # sweep t from 0 to 1 and show the interpolated x at each step
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = interpolate(min_point[0], max_point[0], t)
        real_val = axis_min + t * (axis_max - axis_min)  # map t back to the real axis value
        print(f"{axis.axisTag}={real_val:.0f} (t={t}): x={x:.1f}")
    print("-" * 40)
