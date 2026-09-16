"""Normalize approved SVG assets for GitHub's actual image renderer.

Flatten nested snake images to retain animation. Cap tile intrinsic widths for
GitHub's narrower mobile README column while preserving each SVG viewBox.
"""
import base64
import xml.etree.ElementTree as ET
from pathlib import Path

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def normalize(path: Path) -> bool:
    root = ET.fromstring(path.read_bytes())
    changed = False
    for parent in root.iter():
        for index, child in list(enumerate(list(parent))):
            if child.tag != f'{{{NS}}}image':
                continue
            href = child.get('href') or child.get('{http://www.w3.org/1999/xlink}href', '')
            prefix = 'data:image/svg+xml;base64,'
            if not href.startswith(prefix):
                continue
            nested = ET.fromstring(base64.b64decode(href[len(prefix):], validate=True))
            if nested.tag != f'{{{NS}}}svg':
                raise ValueError('Nested data is not SVG')
            for key in ('x', 'y', 'width', 'height', 'preserveAspectRatio'):
                if child.get(key) is not None:
                    nested.set(key, child.get(key))
            parent.remove(child)
            parent.insert(index, nested)
            changed = True
    if changed:
        path.write_text(ET.tostring(root, encoding='unicode'), encoding='utf-8')
    return changed


def cap_width(path: Path, target: int) -> bool:
    root = ET.fromstring(path.read_bytes())
    width, height = float(root.get('width')), float(root.get('height'))
    if width <= target:
        return False
    root.set('width', str(target))
    root.set('height', f'{height * target / width:.3f}')
    # Keep the original viewBox so geometry and image aspect ratios do not change.
    path.write_text(ET.tostring(root, encoding='unicode'), encoding='utf-8')
    return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    count = sum(normalize(path) for path in args.directory.glob('snake-*.svg'))
    tiles = 0
    for pattern, width in [('tool-*-mobile.svg', 148), ('tool-*-small.svg', 112), ('nav-*-small.svg', 112)]:
        tiles += sum(cap_width(path, width) for path in args.directory.glob(pattern))
    print(f'Flattened {count} snake SVGs; fitted {tiles} mobile tiles; content and colors unchanged')
