import sys
from fontTools.ttLib import TTFont


def inspect(path: str) -> None:
    font = TTFont(path)

    print(f"=== {path} ===")
    is_variable = "fvar" in font
    print(f"Is variable font (has 'fvar')? {is_variable}")
    print()

    if not is_variable:
        print("No 'fvar' table — this is a static font, nothing more to show here.")
        return

    # ---- fvar: declares the axes and their ranges ----
    fvar = font["fvar"]
    print(f"[fvar] — {len(fvar.axes)} axes declared")
    for axis in fvar.axes:
        print(
            f"  {axis.axisTag:6s}  "
            f"min={axis.minValue:<8g} "
            f"default={axis.defaultValue:<8g} "
            f"max={axis.maxValue:<8g}"
        )
    print()

    print(f"[fvar] — {len(fvar.instances)} named instances (preset points along the axes)")
    name_table = font["name"]
    for inst in fvar.instances[:6]:
        inst_name = name_table.getDebugName(inst.subfamilyNameID) or f"(nameID {inst.subfamilyNameID})"
        coords = ", ".join(f"{tag}={val:g}" for tag, val in inst.coordinates.items())
        print(f"  {inst_name:20s} {coords}")
    if len(fvar.instances) > 6:
        print(f"  ... and {len(fvar.instances) - 6} more")
    print()

    # ---- gvar: the interpolation rulebook ----
    if "gvar" not in font:
        print("No 'gvar' table — unusual for a variable font, but technically possible")
        print("if every axis is handled entirely through table substitution instead.")
        return

    gvar = font["gvar"]
    glyph_order = font.getGlyphOrder()
    cmap = font.getBestCmap()
    char = "A"
    sample_name = cmap.get(ord(char), glyph_order[3])

    variations = gvar.variations.get(sample_name, [])
    print(f"[gvar] glyph='{sample_name}'  variation records={len(variations)}")
    for i, var in enumerate(variations[:5]):
        axes = ", ".join(f"{tag}:{peak:g}" for tag, (_, peak, _) in var.axes.items())
        print(f"  [{i}] axes=({axes})")
        print(f"      deltas={var.coordinates}")
    if len(variations) > 5:
        print(f"  ... and {len(variations) - 5} more records")
    print()

    # ---- live demo: same glyph, two settings on wght specifically ----
    print(f"[demo] '{char}' advance width across the 'wght' axis")
    try:
        from fontTools.varLib.instancer import instantiateVariableFont

        wght_axis = next((a for a in fvar.axes if a.axisTag == "wght"), None)
        if wght_axis is None:
            print("  (this font has no 'wght' axis)")
        else:
            for wght_val in (wght_axis.minValue, wght_axis.maxValue):
                static = instantiateVariableFont(font, {"wght": wght_val}, inplace=False)
                advance, _ = static["hmtx"][sample_name]
                print(f"  wght={wght_val:<6g} -> advanceWidth={advance}")
    except Exception as e:
        print(f"  (skipped live demo: {e})")
    print()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "fonts/Roboto_Flex/RobotoFlex-VariableFont_GRAD,XOPQ,XTRA,YOPQ,YTAS,YTDE,YTFI,YTLC,YTUC,opsz,slnt,wdth,wght.ttf"
    inspect(path)
