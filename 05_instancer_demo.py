"""
Command:
    python3 05_instancer_demo.py

Command (pin a different weight):
    python3 05_instancer_demo.py --wght 750

Equivalent real-world CLI (say this out loud on stage):
    fonttools varLib.instancer Satoshi-Variable.ttf wght=600 -o Satoshi-600-static.ttf
"""
import argparse
import os
import subprocess
import sys

from fontTools.ttLib import TTFont

HERE = os.path.dirname(__file__)
FONTS_DIR = os.path.join(HERE, "fonts")
OUTPUT_DIR = os.path.join(HERE, "output")
SATOSHI_PATH = os.path.join(FONTS_DIR, "Satoshi-Variable.ttf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wght", type=float, default=600.0,
                         help="wght value to pin at (Satoshi's range is "
                              "300-900, default 600).")
    parser.add_argument("--font", default=SATOSHI_PATH,
                         help="Path to the variable font to instance.")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    vf_path = args.font
    wght = args.wght
    static_path = os.path.join(OUTPUT_DIR, f"Satoshi-wght{wght:.0f}-static.ttf")

    print(f"Using {vf_path}\n")

    wght_arg = f"wght={wght:.0f}" if wght == int(wght) else f"wght={wght}"
    cli_command = f"fonttools varLib.instancer {vf_path} {wght_arg} -o {static_path}"
    print("Equivalent real-world CLI command (say this out loud on stage):")
    print(f"  $ {cli_command}\n")

    print("Running it now via subprocess...\n")
    print("-" * 60)
    result = subprocess.run(
        [sys.executable, "-m", "fontTools.varLib.instancer",
         vf_path, wght_arg, "-o", static_path],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)
    print("-" * 60)

    before = TTFont(vf_path)
    after = TTFont(static_path)
    print(f"\nBefore: {vf_path}")
    print(f"  has fvar (variable)? {'fvar' in before}")
    if "fvar" in before:
        for axis in before["fvar"].axes:
            print(f"  axis {axis.axisTag}: {axis.minValue}-{axis.maxValue}, "
                  f"default {axis.defaultValue}")

    print(f"\nAfter:  {static_path}")
    print(f"  has fvar (variable)? {'fvar' in after}")
    print(f"  -> pinned to a single static instance at wght={wght:.0f}, cut from")
    print("     the variable font above")
