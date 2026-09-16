"""Generate self-contained profile SVGs using the Python standard library."""
from pathlib import Path
from html import escape
import argparse
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=Path('dist'))
ASSETS = parser.parse_args().output
ASSETS.mkdir(parents=True, exist_ok=True)
INTRO = '我是 Lora。我在做能长期使用的个人 Agent，也写工具、做产品。这里记录我的开源项目，以及读源码时做的交互教程。'
PALETTES = {
 'light': dict(bg='#F7F4EE', panel='#EEE8DD', fg='#1A1A1A', muted='#796248', line='#D9CCB9', accent='#B67D17', cursor='#C58B21'),
 'dark': dict(bg='#191A1D', panel='#242529', fg='#F7F4EE', muted='#D0B899', line='#42403C', accent='#E0A62F', cursor='#E0A62F')
}

def advance(char: str, size: float) -> float:
    if char == ' ': return size * .34
    if ord(char) < 128:
        if char in 'ilI.,': return size * .35
        if char in 'mwMW': return size * .84
        return size * .59
    return size

def typing_svg(theme: str, mobile: bool = False, static: bool = False) -> str:
    p = PALETTES[theme]
    w, h = (480, 318) if mobile else (880, 232)
    x0 = 28 if mobile else 38
    lines = ([('我是 Lora。',38,89),('我在做能长期使用的个人 Agent，',25,143),('也写工具、做产品。',25,190),('这里记录我的开源项目，',25,237),('以及读源码时做的交互教程。',25,284)] if mobile else
             [('我是 Lora。',38,91),('我在做能长期使用的个人 Agent，也写工具、做产品。',26,150),('这里记录我的开源项目，以及读源码时做的交互教程。',26,191)])
    assert ''.join(s for s,_,_ in lines) == INTRO
    elements, cursor_events = [], []
    t = .15
    for text, size, baseline in lines:
        x = x0
        for char in text:
            delay = t
            color = p['accent'] if char in 'Lora' and baseline in (89,91) else p['fg']
            bold = '700' if size == 38 else '450'
            animation = '' if static else f'<animate attributeName="opacity" values="0;1" keyTimes="0;1" calcMode="discrete" dur="{delay:.3f}s" fill="freeze"/>'
            elements.append(f'<text class="char" x="{x:.2f}" y="{baseline}" fill="{color}" font-size="{size}" font-weight="{bold}">{escape(char)}{animation}</text>')
            x += advance(char,size)
            cursor_events.append((delay,x+4,baseline-size*.82,size*.94))
            t += .025 if char.isspace() else (.10 if char in '。，、' else .045)
        assert x < w - 20, f'Line exceeds viewport: {text}'
        t += .08
    end = t + .18
    assert end < 5, end
    initial=(0,x0,lines[0][2]-lines[0][1]*.82,lines[0][1]*.94)
    points=[initial]+cursor_events+[(end,*cursor_events[-1][1:])]
    times=';'.join(f'{sec/end:.6f}' for sec,_,_,_ in points)
    positions=';'.join(f'{x:.2f} {y:.2f}' for _,x,y,_ in points)
    heights=';'.join(f'{height:.2f}' for *_,height in points)
    cursor='' if static else f'''<g class="cursor-move" opacity="0">
<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.999;1" calcMode="discrete" dur="{end:.3f}s" fill="freeze"/>
<animateTransform attributeName="transform" type="translate" values="{positions}" keyTimes="{times}" calcMode="discrete" dur="{end:.3f}s" fill="freeze"/>
<rect width="2.5" height="30" fill="{p['cursor']}">
<animate attributeName="height" values="{heights}" keyTimes="{times}" calcMode="discrete" dur="{end:.3f}s" fill="freeze"/>
<animate attributeName="opacity" values="1;0" keyTimes="0;0.5" calcMode="discrete" dur=".7s" repeatCount="6"/>
</rect></g>'''
    rule='' if static else f'<animate attributeName="stroke-dashoffset" values="{w};0" dur="1.2s" fill="freeze"/>'
    css='@media(prefers-reduced-motion:reduce){.char{opacity:1!important}.cursor-move{display:none}.rule{stroke-dashoffset:0!important}}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{INTRO}</title>
<desc id="desc">逐字出现一次后保留全文，无声音。减少动态效果时直接显示完整文字。</desc>
<style>text {{ font-family:'Noto Sans CJK SC','Microsoft YaHei','PingFang SC',sans-serif; }} {css}</style>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="16" fill="{p['bg']}" stroke="{p['line']}" stroke-width="1.5"/>
<path class="rule" d="M{x0} 47H{w-x0}" stroke="{p['accent']}" stroke-width="2" stroke-dasharray="{w}" stroke-dashoffset="0">{rule}</path>
<text x="{x0}" y="31" fill="{p['muted']}" font-size="12" letter-spacing="1.2">lora-sys / README</text>
<text x="{w-x0}" y="31" fill="{p['muted']}" font-size="12" text-anchor="end">关于我</text>
{''.join(elements)}
{cursor}
</svg>'''

ICONS = {
 'glassbox': '<rect x="8" y="9" width="51" height="42" rx="7"/><path d="M8 21h51M34 21v30M14 31h12m-12 9h12"/><circle cx="47" cy="34" r="5"/><path d="m45 41 3 3 7-9"/>',
 'zhihu': '<path d="M14 9h31l12 12v35H14zM44 9v14h13M23 31h25M23 38h20M23 45h12"/><circle cx="10" cy="15" r="5"/>',
 'arena': '<path d="M10 15h49v34H10zM26 15v34M42 15v34"/><circle cx="18" cy="31" r="4"/><circle cx="34" cy="28" r="4"/><circle cx="50" cy="34" r="4"/><path d="M18 39v10M34 36v13M50 42v7"/>',
 'skills': '<rect x="9" y="9" width="20" height="20" rx="4"/><rect x="37" y="9" width="20" height="20" rx="4"/><rect x="9" y="37" width="20" height="20" rx="4"/><path d="M47 36v22M36 47h22"/>'
}
CARDS = [
 ('glassbox','Glassbox','个人 Agent 系统','开发中'),
 ('zhihu','Zhihu Threads','带来源的学习线','应用'),
 ('arena','AgentArena','团队竞技与证据回放','实验'),
 ('skills','Lora Skills','可安装的技能集合','工具')
]

def card_svg(theme: str, slug: str, title: str, subtitle: str, kind: str) -> str:
    p=PALETTES[theme]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="164" viewBox="0 0 480 164" role="img" aria-label="{title}，{subtitle}，{kind}">
<title>{title}</title><desc>项目导航卡片，不是产品截图。</desc>
<rect x=".75" y=".75" width="478.5" height="162.5" rx="13" fill="{p['bg']}" stroke="{p['line']}" stroke-width="1.5"/>
<rect x="22" y="34" width="84" height="91" rx="12" fill="{p['panel']}"/>
<g transform="translate(30 45)" fill="none" stroke="{p['accent']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[slug]}</g>
<g font-family="'Noto Sans CJK SC','Microsoft YaHei','PingFang SC',sans-serif">
<text x="126" y="43" fill="{p['muted']}" font-size="12" letter-spacing="1.5">{kind}</text>
<text x="126" y="80" fill="{p['fg']}" font-weight="700" font-size="29">{title}</text>
<text x="126" y="112" fill="{p['muted']}" font-size="19">{subtitle}</text>
</g><path d="M438 30h12v12m-12 0 12-12" stroke="{p['muted']}" fill="none" stroke-width="1.5"/>
</svg>'''

for theme in PALETTES:
    for mobile in (False,True):
        for static in (False,True):
            name=f'intro-{theme}{"-mobile" if mobile else ""}{"-static" if static else ""}.svg'
            (ASSETS/name).write_text(typing_svg(theme,mobile,static),encoding='utf-8')
    for slug,title,subtitle,kind in CARDS:
        (ASSETS/f'card-{slug}-{theme}.svg').write_text(card_svg(theme,slug,title,subtitle,kind),encoding='utf-8')
for asset in ASSETS.glob('*.svg'):
    ET.fromstring(asset.read_text(encoding='utf-8'))
print('Generated 16 SVGs; XML validation passed')
