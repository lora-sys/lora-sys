"""Verify the exact published asset set, provenance, README links and motion."""
import base64
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright
from build_approved_profile import CARDS, PALETTES, SIZES, ROOT


def validate_files(root: Path, readme: str):
    expected_sources = {f'{kind}-{theme}' for kind in CARDS for theme in PALETTES}
    source = json.loads((root / 'sources.json').read_text())
    assert set(source['statistics']) == expected_sources, 'Unexpected statistics sources'
    for key, item in source['statistics'].items():
        assert item['status'] in ('fresh', 'retained_previous'), key
        assert item.get('fetched_at'), key
        actual_hash = hashlib.sha256((root / 'data' / f'{key}.svg').read_bytes()).hexdigest()
        assert item['sha256'] == actual_hash, f'Source checksum mismatch: {key}'

    expected_assets = {
        f'{kind}-{theme}-{mode}{suffix}.svg'
        for kind in (*CARDS, 'snake')
        for theme in PALETTES
        for mode in SIZES
        for suffix in (('', '-static') if kind == 'snake' else ('',))
    }
    actual_assets = {p.name for p in root.glob('*.svg')}
    assert actual_assets == expected_assets, f'Asset mismatch: {actual_assets ^ expected_assets}'
    referenced = set(re.findall(r'output/v5/([\w-]+\.svg)', readme))
    assert referenced == expected_assets, f'README asset mismatch: {referenced ^ expected_assets}'
    for path in root.rglob('*.svg'):
        data = path.read_text()
        ET.fromstring(data)
        assert not re.search(r'<(?:\w+:)?(?:script|foreignObject)\b', data), path
        assert '@font-face' not in data and 'font/woff' not in data, path
    return source


def main():
    root = ROOT / 'dist/v5'
    source = validate_files(root, (ROOT / 'README.md').read_text())
    motion = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 980, 'height': 700})
        for theme in PALETTES:
            for mode in SIZES:
                for suffix in ('', '-static'):
                    name = f'snake-{theme}-{mode}{suffix}'
                    data = base64.b64encode((root / f'{name}.svg').read_bytes()).decode()
                    page.set_content(f'<img src="data:image/svg+xml;base64,{data}">')
                    page.wait_for_function('document.images[0].complete && document.images[0].naturalWidth > 0')
                    page.wait_for_timeout(150)
                    first = page.screenshot()
                    page.wait_for_timeout(1500)
                    different = first != page.screenshot()
                    motion[name] = {'frames_differ': different}
                    assert different == (suffix == ''), f'Unexpected motion: {name}'
        browser.close()
    (ROOT / 'qa/motion.json').write_text(json.dumps(motion, indent=2))
    retained = [key for key, item in source['statistics'].items() if item['status'] == 'retained_previous']
    print(f'Verified assets, source checksums, README references and {len(motion)} motion variants')
    if retained:
        print('::warning::Statistics refresh failed; retained verified snapshots: ' + ', '.join(retained))


if __name__ == '__main__':
    main()
