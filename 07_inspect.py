"""
07_inspect.py — check axis structure and rough outline compatibility
between two variable font masters before attempting a merge.

Command:
    python3 07_inspect.py fonts/Satoshi-Variable.ttf fonts/Satoshi-VariableItalic.ttf

Also works against any other pair of fonts, e.g. Google Sans:
    python3 07_inspect.py "fonts/GoogleSans-VariableFont_GRAD_opsz_wght.ttf" "fonts/GoogleSans-Italic-VariableFont_GRAD_opsz_wght.ttf"
"""
import sys
from fontTools.ttLib import TTFont


def inspect(path):
    font = TTFont(path)
    name = font["name"]
    print(f"=== {path} ===")
    print(f"  Family:      {name.getDebugName(1)}")
    print(f"  Subfamily:   {name.getDebugName(2)}")
    print(f"  Full name:   {name.getDebugName(4)}")
    print(f"  PostScript:  {name.getDebugName(6)}")

    if "fvar" in font:
        print("  Axes:")
        for axis in font["fvar"].axes:
            print(f"    {axis.axisTag}: min={axis.minValue} "
                  f"default={axis.defaultValue} max={axis.maxValue}")
    else:
        print("  NO fvar — this is a STATIC font, not variable!")

    print(f"  Glyph count: {font['maxp'].numGlyphs}")
    print(f"  Units per em: {font['head'].unitsPerEm}")
    return font


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    roman = inspect(sys.argv[1])
    italic = inspect(sys.argv[2])

    roman_glyphs = set(roman.getGlyphOrder())
    italic_glyphs = set(italic.getGlyphOrder())

    print("=== COMPATIBILITY CHECK ===")
    print(f"  Shared glyph names: {len(roman_glyphs & italic_glyphs)}")
    only_roman = roman_glyphs - italic_glyphs
    only_italic = italic_glyphs - roman_glyphs
    if only_roman:
        print(f"  Glyphs only in roman:  {len(only_roman)}")
    if only_italic:
        print(f"  Glyphs only in italic: {len(only_italic)}")

    shared = sorted(roman_glyphs & italic_glyphs)
    mismatches = []
    if "glyf" in roman and "glyf" in italic:
        for gname in shared:
            try:
                rg = roman["glyf"][gname]
                ig = italic["glyf"][gname]
                if rg.isComposite() or ig.isComposite():
                    continue
                rpts = getattr(rg, "numberOfContours", None)
                ipts = getattr(ig, "numberOfContours", None)
                if rpts != ipts:
                    mismatches.append((gname, rpts, ipts))
            except Exception:
                continue

    print(f"  Glyphs with mismatched contour counts: {len(mismatches)}")
    if mismatches:
        print("  First 10 mismatches (glyph, roman_contours, italic_contours):")
        for gname, rpts, ipts in mismatches[:10]:
            print(f"    ({gname!r}, {rpts}, {ipts})")
