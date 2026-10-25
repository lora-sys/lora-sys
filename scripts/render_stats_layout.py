"""Materialize only the two statistics cards used by the profile."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CSS = ':root{color-scheme:light;--page:#ffffff;--text:#24211e;--muted:#70675d;--border:#ded8cf;--accent:#9a661b;--gold:#d6a03b;--chip:#f6f2ea}\n:root[data-theme=dark]{color-scheme:dark;--page:#161719;--text:#f4f0e9;--muted:#bfb6a8;--border:#3a3732;--accent:#e2b45d;--gold:#e0a62f;--chip:#25231f}\n*{box-sizing:border-box}\nbody{margin:0;background:var(--page);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI","Noto Sans CJK SC","Microsoft YaHei",sans-serif;-webkit-font-smoothing:antialiased}\nsvg{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}\n.sample{margin:0 auto;max-width:984px;padding:34px 42px 28px;background:var(--page)}\n.stat-card{border:1px solid var(--border);border-radius:12px;overflow:hidden;background:var(--chip);display:flex;flex-direction:column;min-width:0}\n.stat-heading{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:20px 22px 16px}\n.stat-title{display:flex;align-items:center;gap:9px;color:var(--accent)}\n.stat-title h3{margin:0;font-size:17px;line-height:1.4;font-weight:630;color:var(--text)}\n.stat-body{flex:1;min-height:226px;padding:0 22px 18px;display:flex;flex-direction:column;justify-content:center}\n.stat-live-image{display:block;width:100%;height:auto;max-width:100%;border-radius:5px}\n.stats-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}\n@media(max-width:680px){.sample{margin:0 10px;padding:14px 13px 12px}.stats-grid{grid-template-columns:minmax(0,1fr);gap:15px}.stat-heading{padding:20px 19px 14px}.stat-title h3{font-size:16px}.stat-body{padding:0 19px 17px;min-height:222px}}'

def write():
    cards = []
    for key, title, shape in [('stats', 'GitHub 总览', '<path d="M12 21V5M3 3c4-1 7 0 9 2 2-2 5-3 9-2v16c-4-1-7 0-9 2-2-2-5-3-9-2Z"/>'), ('languages', '仓库语言分布', '<path d="m8 5-6 7 6 7m8-14 6 7-6 7M14 3l-4 18"/>')]:
        cards.append(f'<article class="stat-card" id="{key}-card"><header class="stat-heading"><div class="stat-title"><svg viewBox="0 0 24 24" aria-hidden="true">{shape}</svg><h3>{title}</h3></div></header><div class="stat-body" id="{key}-body"></div></article>')
    markup = '<!doctype html><html lang="zh-CN" data-theme="light"><head><meta charset="utf-8"><title>Profile statistics</title><style>' + CSS + '</style></head><body><main class="sample"><div class="stats-grid">' + ''.join(cards) + '</div></main></body></html>'
    dest = ROOT / 'assets/profile/stats-layout.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markup, encoding='utf-8')

if __name__ == '__main__':
    write()
