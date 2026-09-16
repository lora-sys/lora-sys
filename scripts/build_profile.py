"""Build the compact, self-contained typing line for the GitHub profile."""
from pathlib import Path
from html import escape
import argparse
import xml.etree.ElementTree as ET

TEXT = '个人 Agent · 开源工具 · 交互教程'
PALETTES = {
    'light': ('#57606a', '#9a6700'),
    'dark': ('#b1bac4', '#e3b341'),
}


def render(theme: str) -> str:
    """One short animation. The final text remains visible without animation."""
    foreground, accent = PALETTES[theme]
    x = 0.0
    items = []
    for index, char in enumerate(TEXT):
        # Monospaced Latin glyphs and full-width CJK glyphs have fixed advances.
        width = 12.2 if ord(char) < 128 or char == '·' else 20.0
        color = accent if char == '·' else foreground
        delay = .10 + index * .055
        items.append(
            f'<text class="letter" x="{x:.1f}" y="25" fill="{color}">'
            f'{escape(char)}<animate attributeName="opacity" values="0;1" '
            f'keyTimes="0;1" calcMode="discrete" dur="{delay:.3f}s" '
            'fill="freeze"/></text>'
        )
        x += width
    assert x <= 420, f'Text exceeds viewBox: {x}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="36" viewBox="0 0 420 36" role="img" aria-labelledby="title desc">
<title id="title">{TEXT}</title>
<desc id="desc">逐字显示一次后保留全文。无声音，无循环闪烁。</desc>
<style>text{{font:20px ui-monospace,SFMono-Regular,Consolas,"Noto Sans Mono CJK SC",monospace}}@media(prefers-reduced-motion:reduce){{.letter{{opacity:1!important}}}}</style>
{''.join(items)}
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('dist'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for theme in PALETTES:
        svg = render(theme)
        ET.fromstring(svg)
        assert '<script' not in svg and '<foreignObject' not in svg
        path = args.output / f'typing-v3-{theme}.svg'
        path.write_text(svg, encoding='utf-8')
    print('Generated 2 self-contained typing SVGs; XML validation passed')


if __name__ == '__main__':
    main()
