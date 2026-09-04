"""
Command:
    python3 08_attempt_merge.py

Command, against Google Sans:
    python3 08_attempt_merge.py \\
        --roman "fonts/GoogleSans-VariableFont_GRAD_opsz_wght.ttf" \\
        --italic "fonts/GoogleSans-Italic-VariableFont_GRAD_opsz_wght.ttf" \\
        --out "output/GoogleSans-Merged-VF.ttf"
"""
import argparse
import os
import sys

from fontTools import varLib
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

sys.path.insert(0, os.path.dirname(__file__))
from build_designspace import write_designspace  # noqa: E402

HERE = os.path.dirname(__file__)
FONTS_DIR = os.path.join(HERE, "fonts")
OUTPUT_DIR = os.path.join(HERE, "output")


def ensure_static(path, out_dir):
    """If `path` is itself a variable font (has fvar — true of both
    Satoshi and Google Sans), instance it down to a static font pinned
    at its own default axis values and return the new path. Otherwise
    return `path` unchanged."""
    font = TTFont(path)
    if "fvar" not in font:
        return path

    axis_defaults = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
    print(f"  {os.path.basename(path)} already has its own fvar {axis_defaults} —")
    print(f"    instancing down to a static font at those default values first.")

    inst = instancer.instantiateVariableFont(font, axis_defaults)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(path))[0]
    static_path = os.path.join(out_dir, f"{stem}-STATIC.ttf")
    inst.save(static_path)
    return static_path


def attempt_merge(roman_path, italic_path, out_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    instanced_dir = os.path.join(OUTPUT_DIR, "instanced_masters")

    print("Checking whether the input masters are themselves variable fonts...")
    roman_static = ensure_static(roman_path, instanced_dir)
    italic_static = ensure_static(italic_path, instanced_dir)
    if roman_static != roman_path or italic_static != italic_path:
        print("  Done — using the instanced static files as masters below.\n")
    else:
        print("  Neither input has an fvar — using them as-is.\n")

    ds_path = os.path.join(OUTPUT_DIR, "attempted.designspace")
    write_designspace(roman_static, italic_static, ds_path)
    print(f"Wrote hand-built designspace: {ds_path}")
    print("(No real UFO/designspace source exists for these fonts, so this")
    print(" points directly at the two compiled TTFs as makeshift masters —")
    print(" a workaround, not the real thing, per the brief's Section 7 framing.)\n")

    ds = DesignSpaceDocument.fromfile(ds_path)

    print(f"Attempting varLib.build() against {len(ds.sources)} masters...\n")
    print("-" * 60)
    try:
        varfont, model, master_ttfs = varLib.build(ds)
    except Exception as e:
        print("-" * 60)
        print("\n*** MERGE FAILED OUTRIGHT ***\n")
        print(f"{type(e).__name__}: {e}")
        return None

    print("-" * 60)
    varfont.save(out_path)
    print(f"\n'Succeeded' — wrote {out_path}")

    # Verify what actually landed
    gvar = varfont["gvar"] if "gvar" in varfont else None
    total = varfont["maxp"].numGlyphs
    if gvar is None:
        print("No gvar table produced — every glyph was static/incompatible.")
        return out_path

    with_variations = [g for g in gvar.variations if gvar.variations[g]]
    without_variations = total - len(with_variations)

    print(f"\nGlyphs WITH gvar deltas (actually interpolate): {len(with_variations)}")
    print(f"Glyphs WITHOUT gvar deltas: {without_variations}")
    print(f"Total glyphs in font: {total}")
    print(f"\n=> {without_variations} of {total}")

    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--roman", default=os.path.join(FONTS_DIR, "Satoshi-Variable.ttf"))
    parser.add_argument("--italic", default=os.path.join(FONTS_DIR, "Satoshi-VariableItalic.ttf"))
    parser.add_argument("--out", default=os.path.join(OUTPUT_DIR, "Satoshi-Merged-VF.ttf"))
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    attempt_merge(args.roman, args.italic, args.out)
