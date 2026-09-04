"""
06_inspect_gsub.py — compare GSUB feature/lookup structure between two
fonts.

Command:
    python3 06_inspect_gsub.py "fonts/GoogleSans-VariableFont_GRAD_opsz_wght.ttf" "fonts/GoogleSans-Italic-VariableFont_GRAD_opsz_wght.ttf"

Also works against Satoshi:
    python3 06_inspect_gsub.py "fonts/Satoshi-Variable.ttf" "fonts/Satoshi-VariableItalic.ttf"
"""
import sys
from fontTools.ttLib import TTFont


def get_features(font):
    if "GSUB" not in font:
        return []
    return [
        (fr.FeatureTag, fr.Feature.LookupCount)
        for fr in font["GSUB"].table.FeatureList.FeatureRecord
    ]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    roman = TTFont(sys.argv[1])
    italic = TTFont(sys.argv[2])

    r_features = get_features(roman)
    i_features = get_features(italic)

    if not r_features or not i_features:
        print("One or both fonts have no GSUB table — nothing to compare.")
        sys.exit(0)

    print(f"Roman GSUB features:  {r_features}")
    print(f"Italic GSUB features: {i_features}")
    print()

    mismatches_found = False
    for i, (r, it) in enumerate(zip(r_features, i_features)):
        if r != it:
            mismatches_found = True
            print(f"  [{i}] Roman: {r}  vs  Italic: {it}")

    if not mismatches_found:
        print("  No feature/lookup-count mismatches found — these two fonts'")
        print("  GSUB structures are compatible at this shallow level.")
    else:
        print()
        print("Roman and italic have matching feature TAGS, but the LookupCount")
        print("for at least one feature differs")
