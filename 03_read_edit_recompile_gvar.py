import argparse
import os
from fontTools.ttLib import TTFont

HERE = os.path.dirname(__file__)
FONTS_DIR = os.path.join(HERE, "fonts")
OUTPUT_DIR = os.path.join(HERE, "output")
SATOSHI_PATH = os.path.join(FONTS_DIR, "Satoshi-Variable.ttf")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", default=SATOSHI_PATH)
    parser.add_argument("--glyph", default="A")
    parser.add_argument("--point", type=int, default=0,
                         help="glyf point index to edit (default 0 — "
                              "Satoshi's 'A' left-edge point).")
    parser.add_argument("--push", type=int, default=-150,
                         help="Units to add to the delta's x value "
                              "(default -150, pushing the thin master's "
                              "left edge further left).")
    parser.add_argument("--tuple-min", action="store_true", default=True,
                         help="Target the tuple moving toward the axis "
                              "MINIMUM — (-1.0,-1.0,0.0). This is Satoshi's "
                              "only tuple, since its default sits at max. "
                              "Pass --no-tuple-min for a font whose default "
                              "sits mid-range, to target (0.0,1.0,1.0) instead.")
    parser.add_argument("--no-tuple-min", dest="tuple_min", action="store_false")
    args = parser.parse_args()

    vf_path = args.font
    glyph = args.glyph
    point_index = args.point
    push = args.push
    # normalized gvar tuple to target, based on which axis extreme we want
    target_tuple = (-1.0, -1.0, 0.0) if args.tuple_min else (0.0, 1.0, 1.0)
    target_label = "Thin master (wght=300)" if args.tuple_min else "Bold master (wght=900)"
    edited_path = os.path.join(OUTPUT_DIR, "Satoshi-Variable_EDITED.ttf")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Using {vf_path}\n")

    # --- Step 1: open the font ---
    font = TTFont(vf_path)
    gvar = font["gvar"]

    # --- Step 2: read the raw delta for one point, one master ---
    tuple_variations = gvar.variations[glyph]
    target_tv = next(tv for tv in tuple_variations if tv.axes.get("wght") == target_tuple)  # find the matching master tuple

    original_delta = target_tv.coordinates[point_index]
    print(f"Glyph {glyph!r}, point {point_index}, {target_label}:")
    print(f"  BEFORE edit -> delta = {original_delta}")

    # --- Step 3: edit ONE delta value directly ---
    dx, dy = original_delta
    new_delta = (dx + push, dy)  # only shift x, leave y untouched
    target_tv.coordinates[point_index] = new_delta
    print(f"  Editing delta by hand: {original_delta} -> {new_delta}")
    print(f"  (This is literally: target_tv.coordinates[{point_index}] = {new_delta})")

    # --- Step 4: recompile to a new .ttf ---
    font.save(edited_path)
    print(f"\n  Recompiled -> {edited_path}")

    # --- Step 5: reopen and show the shape actually changed ---
    reopened = TTFont(edited_path)  # fresh read from disk, not the in-memory font
    reopened_tv = next(
        tv for tv in reopened["gvar"].variations[glyph]
        if tv.axes.get("wght") == target_tuple
    )
    confirmed_delta = reopened_tv.coordinates[point_index]
    print(f"  AFTER reopening the saved file -> delta = {confirmed_delta}")

    if confirmed_delta == new_delta:
        extreme_label = target_label.split("(")[1].rstrip(")")
        direction = "left" if push < 0 else "right"
        print(f"  At the {extreme_label} extreme, this glyph's edge now lands")
        print(f"  {abs(push)} units further {direction} than it did in the original font")
    else:
        print("\n  MISMATCH — the edit did not round-trip as expected.")


if __name__ == "__main__":
    main()
