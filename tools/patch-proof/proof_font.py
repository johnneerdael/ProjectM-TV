"""Stable bitmap labels for patch-proof comparison images."""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path

from PIL import FontFile, Image, ImageFont
import PIL


ROOT = Path(__file__).resolve().parent
FONT_PATH = ROOT / 'assets/proof-5x7.pil'
ATLAS_PATH = ROOT / 'assets/proof-5x7.pbm'
FONT_SOURCE_PATH = ROOT / 'assets/proof-5x7-glyphs.json'


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def proof_font() -> ImageFont.ImageFont:
    """Load the committed Pillow legacy bitmap font without FreeType."""
    return ImageFont.load(str(FONT_PATH))


def draw_text(draw, xy: tuple[int, int], text: str, fill) -> None:
    """Draw text with a fixed 5x7 atlas and one-pixel line spacing."""
    supported = set(json.loads(FONT_SOURCE_PATH.read_text()))
    unsupported = set(text.replace('\n', '')) - supported
    if unsupported:
        raise ValueError('Unsupported proof-font characters: ' + ''.join(sorted(unsupported)))
    x, y = xy
    font = proof_font()
    for line in text.split('\n'):
        draw.text((x, y), line, fill=fill, font=font)
        y += 8


def identity() -> dict[str, str]:
    """Return source and raster identities for comparison-image labels."""
    return {
        'format': 'Pillow legacy PIL bitmap font',
        'pillow_version': PIL.__version__,
        'renderer_sha256': _sha(Path(__file__)),
        'glyph_data_sha256': _sha(FONT_SOURCE_PATH),
        'font_sha256': _sha(FONT_PATH),
        'atlas_sha256': _sha(ATLAS_PATH),
    }


def write_font_assets(directory: Path) -> None:
    """Build the committed .pil/.pbm pair from the hand-authored glyph atlas."""
    glyphs = json.loads(FONT_SOURCE_PATH.read_text())
    font = FontFile.FontFile()
    for char, rows in glyphs.items():
        width, height = len(rows[0]), len(rows)
        pixels = [pixel == '#' for row in rows for pixel in row]
        bitmap = Image.new('1', (width, height))
        bitmap.putdata(pixels)
        font.glyph[ord(char)] = ((width + 1, 0), (0, -height, width, 0),
                                 (0, 0, width, height), bitmap)
    directory.mkdir(parents=True, exist_ok=True)
    font.save(str(directory / FONT_PATH.stem))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-assets', action='store_true')
    args = parser.parse_args()
    if not args.write_assets:
        parser.error('pass --write-assets to regenerate the committed font assets')
    write_font_assets(FONT_PATH.parent)
