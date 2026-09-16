"""Flatten nested SVG image data so Chromium animates the contribution snake.

The browser freezes animations inside an SVG used as a nested image. A nested
SVG element preserves its viewBox and CSS animation without JavaScript.
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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    count = sum(normalize(path) for path in args.directory.glob('snake-*.svg'))
    print(f'Flattened {count} snake SVGs without changing geometry, colors or contribution data')
