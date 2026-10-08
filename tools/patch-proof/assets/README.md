# Patch-proof bitmap font

`proof-5x7-glyphs.json` contains original, hand-authored pixel patterns created for
the comparison labels in this tool. The glyphs are not copied or derived from a
third-party font or BDF file. The `.pil` metrics file and `.pbm` atlas are generated
from those patterns with Pillow's `PIL.FontFile.FontFile.save` API; runtime loading
uses Pillow's legacy bitmap-font loader and does not use FreeType. These files are
distributed under the repository's LGPL-2.1 license in `LICENSE`.

Regenerate the Pillow font pair with:

```sh
python3 tools/patch-proof/proof_font.py --write-assets
```
