"""
Not meant to be run directly — imported by 08_attempt_merge.py.
"""
import os

DESIGNSPACE_TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
<designspace format="4.0">
  <axes>
    <axis tag="ital" name="Italic" minimum="0" maximum="1" default="0"/>
  </axes>
  <sources>
    <source filename="{roman_path}" name="master-roman">
      <location>
        <dimension name="Italic" xvalue="0"/>
      </location>
    </source>
    <source filename="{italic_path}" name="master-italic">
      <location>
        <dimension name="Italic" xvalue="1"/>
      </location>
    </source>
  </sources>
  <instances>
    <instance name="Roman" familyname="{family_name}" stylename="Regular">
      <location>
        <dimension name="Italic" xvalue="0"/>
      </location>
    </instance>
    <instance name="Italic" familyname="{family_name}" stylename="Italic">
      <location>
        <dimension name="Italic" xvalue="1"/>
      </location>
    </instance>
  </instances>
</designspace>
"""


def write_designspace(roman_path, italic_path, out_path, family_name="Merged Family"):
    """Writes a designspace file. Paths are stored relative to the
    designspace file's own directory, matching how fontTools resolves
    <source filename="..."> entries."""
    out_dir = os.path.dirname(os.path.abspath(out_path))
    rel_roman = os.path.relpath(os.path.abspath(roman_path), out_dir)
    rel_italic = os.path.relpath(os.path.abspath(italic_path), out_dir)

    xml = DESIGNSPACE_TEMPLATE.format(
        roman_path=rel_roman, italic_path=rel_italic, family_name=family_name
    )
    with open(out_path, "w") as f:
        f.write(xml)
    return out_path


if __name__ == "__main__":
    here = os.path.dirname(__file__)
    roman = os.path.join(here, "..", "fonts", "Satoshi-Variable.ttf")
    italic = os.path.join(here, "..", "fonts", "Satoshi-VariableItalic.ttf")
    out = os.path.join(here, "..", "fonts", "satoshi.designspace")
    write_designspace(roman, italic, out, family_name="Satoshi")
    print(f"Wrote {out}")
