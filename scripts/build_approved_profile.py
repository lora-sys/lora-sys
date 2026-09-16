"""Render the approved profile into linked, GitHub-compatible SVG assets.

The build preserves the original banner, reads real statistics, and retains a
previous successful data snapshot if a provider is temporarily unavailable.
No font files, credentials, or invented statistics are published.
"""
from __future__ import annotations
import argparse, base64, hashlib, html, io, json, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/v5';OUT.mkdir(parents=True,exist_ok=True)
QA=ROOT/'qa';QA.mkdir(exist_ok=True)
RAW='https://raw.githubusercontent.com/lora-sys/lora-sys/output/v5/'
PALETTES={
 'light':dict(page='FFFFFF',bg='F6F2EA',fg='24211E',muted='70675D',line='DED8CF',accent='9A661B',gold='D6A03B'),
 'dark':dict(page='161719',bg='25231F',fg='F4F0E9',muted='BFB6A8',line='3A3732',accent='E2B45D',gold='E0A62F'),
}
LINES=['你好，我是 Lora。','写 AI Agent，做开源项目。','把读源码的过程做成交互教程。']
SIZES={'desktop':(1440,880,400,195),'mobile':(390,342,326,156),'small':(320,272,260,123)}
records={};components={};captured_at=datetime.now(timezone.utc).isoformat()

def download(url:str)->bytes:
 for attempt in range(3):
  try:
   request=Request(url,headers={'User-Agent':'lora-profile/5','Accept':'image/svg+xml,image/*,*/*'})
   with urlopen(request,timeout=40) as response:
    data=response.read(12_000_001)
    if len(data)>12_000_000:raise ValueError('Asset too large')
    return data
  except Exception:
   if attempt==2:raise
   time.sleep(2+attempt*3)
 raise RuntimeError('Unreachable')

def validate_svg(data:bytes,kind:str)->str:
 root=ET.fromstring(data)
 if root.tag.rsplit('}',1)[-1]!='svg':raise ValueError(kind+' is not SVG')
 words=' '.join(root.itertext())
 if re.search(r'something went wrong|could not fetch|bad credentials|rate limit|not found|application error|upstream error|access denied|too many requests',words,re.I):
  raise ValueError(kind+' returned an error image: '+words[:350])
 if kind=='overview' and not re.search(r'rank',data.decode(),re.I):raise ValueError('Overview rank missing')
 if kind=='languages' and not re.search(r'%|language',words,re.I):raise ValueError('Language data missing')
 return words

def endpoint(kind:str,theme:str)->str:
 p=PALETTES[theme]
 q=dict(username='lora-sys',bg_color=p['bg'],title_color=p['accent'],text_color=p['fg'],icon_color=p['accent'],hide_border='true',hide_title='true',disable_animations='true',locale='cn',card_width='410')
 if kind=='overview':
  q.update(show_icons='true',hide_rank='false',rank_icon='default',ring_color=p['gold'],card_width='520',line_height='31')
  return 'https://github-readme-stats-fast.vercel.app/api?'+urlencode(q)
 if kind=='languages':
  q.update(layout='compact',langs_count='6')
  return 'https://github-readme-stats-sigma-fawn-45.vercel.app/api/top-langs/?'+urlencode(q)
 q=dict(user='lora-sys',hide_border='true',background=p['bg'],stroke=p['line'],ring=p['accent'],fire=p['accent'],currStreakNum=p['fg'],sideNums=p['fg'],currStreakLabel=p['accent'],sideLabels=p['muted'],dates=p['muted'])
 return 'https://github-readme-streak-stats-eight.vercel.app/?'+urlencode(q)

def stats_asset(kind:str,theme:str)->bytes:
 url=endpoint(kind,theme);key=kind+'-'+theme
 try:
  data=download(url);words=validate_svg(data,kind)
  record=dict(url=url,fetched_at=captured_at,sha256=hashlib.sha256(data).hexdigest(),text=words[:4000],status='fresh')
 except Exception as exc:
  old=ROOT/'previous/v5/data'/(key+'.svg')
  if not old.is_file():raise RuntimeError('First publication requires valid '+key+': '+str(exc)) from exc
  data=old.read_bytes();validate_svg(data,kind)
  prior=json.loads((ROOT/'previous/v5/sources.json').read_text())['statistics'][key]
  record={**prior,'status':'retained_previous','refresh_error':str(exc)[:300]}
 (OUT/'data').mkdir(exist_ok=True)
 (OUT/'data'/(key+'.svg')).write_bytes(data);records[key]=record
 return data

def uri(data:bytes,mime='image/svg+xml')->str:
 return 'data:'+mime+';base64,'+base64.b64encode(data).decode()

def save_svg(name:str,markup:str):
 ET.fromstring(markup)
 if '<script' in markup or '<foreignObject' in markup:raise ValueError('Unsupported SVG '+name)
 (OUT/(name+'.svg')).write_text(markup,encoding='utf-8')

def raster_svg(name:str,data:bytes,css_width:float,title:str,pad=0):
 with Image.open(io.BytesIO(data)) as im:
  w,h=im.size;buf=io.BytesIO();im.save(buf,format='WEBP',lossless=True,method=6)
 height=h/w*css_width
 label=html.escape(title,quote=True)
 save_svg(name,f'<svg xmlns="http://www.w3.org/2000/svg" width="{css_width+pad:.2f}" height="{height+pad:.2f}" viewBox="0 0 {css_width+pad:.2f} {height+pad:.2f}" role="img" aria-label="{label}"><title>{html.escape(title)}</title><image x="{pad/2}" y="0" width="{css_width:.2f}" height="{height:.2f}" href="{uri(buf.getvalue(),"image/webp")}"/></svg>')

def typing_svg(page,theme,mode,static=False):
 p=PALETTES[theme];w=SIZES[mode][1];size=30 if mode=='desktop' else 22;h=88 if mode=='desktop' else 100
 font=f'650 {size}px system-ui, "Noto Sans CJK SC", sans-serif'
 lengths=page.evaluate('''({lines,font})=>{const c=document.createElement('canvas').getContext('2d');c.font=font;return lines.map(t=>[...t].map(ch=>c.measureText(ch).width));}''',dict(lines=LINES,font=font))
 layouts=[];times=[];offset=0
 for line,widths in zip(LINES,lengths):
  rows=[[]];rw=0
  for ch,adv in zip(line,widths):
   if rw+adv>w-16 and rows[-1]:rows.append([]);rw=0
   rows[-1].append((ch,adv));rw+=adv
  points=[]
  for rowid,row in enumerate(rows):
   x=(w-sum(a for _,a in row))/2;y=(h-(len(rows)-1)*size*1.5)/2+size*.35+rowid*size*1.5
   for ch,adv in row:points.append((ch,x,y,adv));x+=adv
  duration=.18+len(line)*.095+3.2+len(line)*.046+.38
  layouts.append(points);times.append((offset,duration));offset+=duration
 total=offset
 css='text{font-family:system-ui,"Noto Sans CJK SC","Microsoft YaHei",sans-serif;letter-spacing:.01em;font-weight:650;}'
 body=''
 for j,points in enumerate(layouts):
  if static and j>0:break
  off,dur=times[j]
  for i,(ch,x,y,adv) in enumerate(points):
   name=f'c{j}_{i}';extra=''
   if not static:
    start=(off+.18+(i+1)*.095)/total*100
    end=(off+.18+len(points)*.095+3.2+(len(points)-i)*.046)/total*100
    css+=f'.{name}{{animation:{name} {total:.3f}s steps(1,end) infinite}}@keyframes {name}{{0%{{opacity:0}}{start:.5f}%{{opacity:1}}{end:.5f}%,100%{{opacity:0}}}}'
    extra=f' class="{name}"'
   body+=f'<text{extra} x="{x:.3f}" y="{y:.3f}" font-size="{size}" fill="#{p["accent"]}">{html.escape(ch)}</text>'
  if not static:
   events=[(off/total*100,points[0][1],points[0][2]-size*.82)]
   for i,(_,x,y,adv) in enumerate(points):events.append(((off+.18+(i+1)*.095)/total*100,x+adv+5,y-size*.82))
   for i in range(len(points)-1,-1,-1):
    _,x,y,_=points[i];events.append(((off+.18+len(points)*.095+3.2+(len(points)-i)*.046)/total*100,x+3,y-size*.82))
   frames=''.join(f'{t:.5f}%{{transform:translate({x:.3f}px,{y:.3f}px)}}' for t,x,y in events)
   a=off/total*100;b=(off+dur-.02)/total*100
   css+=f'.cursor{j}{{animation:move{j} {total:.3f}s steps(1,end) infinite,show{j} {total:.3f}s steps(1,end) infinite}}@keyframes move{j}{{{frames}}}@keyframes show{j}{{0%{{opacity:0}}{a:.5f}%{{opacity:1}}{b:.5f}%,100%{{opacity:0}}}}'
   body+=f'<g class="cursor{j}"><rect class="blink" width="2" height="{size*.9}" fill="#{p["accent"]}"/></g>'
 if not static:css+=' .blink{animation:blink 1.1s steps(1,end) infinite}@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}'
 save_svg(f'typing-{theme}-{mode}'+('-static' if static else ''),f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(" ".join(LINES))}</title><style>{css}</style>{body}</svg>')

def snake_svg(theme,mode,static=False):
 p=PALETTES[theme];w=SIZES[mode][1]
 data=(ROOT/'dist'/('snake-'+theme+'.svg')).read_bytes()
 if static:data=data.replace(b'</svg>',b'<style>*{animation:none!important;transition:none!important}</style></svg>')
 inner=ET.fromstring(data);iw=float(inner.get('width','1220'));ih=float(inner.get('height','200'))
 margin=20 if mode=='desktop' else 12;draw_w=w-2*margin;dh=ih/iw*draw_w;h=dh+110
 font=html.escape('font-family:system-ui,"Noto Sans CJK SC","Microsoft YaHei",sans-serif',quote=True)
 markup=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h:.2f}" viewBox="0 0 {w} {h:.2f}" role="img"><title>lora-sys 的真实 GitHub 贡献贪吃蛇</title><rect x=".5" y=".5" width="{w-1}" height="{h-1:.2f}" rx="12" fill="#{p["bg"]}" stroke="#{p["line"]}"/><g style="{font}"><text x="{margin}" y="34" fill="#{p["fg"]}" font-size="17" font-weight="650">贡献贪吃蛇</text><text x="{margin}" y="{h-19:.2f}" fill="#{p["muted"]}" font-size="11">GitHub Actions 每日生成 · Platane/snk</text></g><image x="{margin}" y="56" width="{draw_w}" height="{dh:.2f}" href="{uri(data)}"/></svg>'
 save_svg(f'snake-{theme}-{mode}'+('-static' if static else ''),markup)

SPECS=[
 ('heading-work','.work-heading',None),
 ('feature-glassbox','.work-feature:nth-child(1)','card'),('feature-zhihu','.work-feature:nth-child(2)','card'),
 ('compact-arena','.work-compact:nth-child(1)','card'),('compact-skills','.work-compact:nth-child(2)','card'),('compact-vllm','.work-compact:nth-child(3)','card'),('compact-vision','.work-compact:nth-child(4)','card'),
 ('heading-tool','.tool-section>.next-heading',None),('heading-stats','.stats-section>.next-heading',None),
 ('overview','#stats-card','card'),('languages','#languages-card','card'),('streak','#streak-card',None),
 ('heading-writing','.tail-writing>.tail-heading',None),('heading-contributions','.tail-contributions>.tail-heading',None),
 ('article-budget','.tail-post-link:nth-child(1)',None),('article-tau','.tail-post-link:nth-child(2)',None),('article-harness','.tail-post-link:nth-child(3)',None),
 ('pr-eino','.tail-pr:nth-child(1)',None),('pr-nad','.tail-pr:nth-child(2)',None),('pr-moss','.tail-pr:nth-child(3)',None),
 ('contact','.tail-contact',None),
]

def build(local=False):
 from prepare_approved_layout import write
 write()
 source=ROOT/'assets/profile/approved-layout.html'
 soup=BeautifulSoup(source.read_text(),'html.parser')
 arts={
  'banner':ROOT/'assets/readme/hero-v1.webp',
  'glassbox':'https://raw.githubusercontent.com/lora-sys/Glassbox-Agent-Harness/main/assets/readme/glassbox-hero.png',
  'zhihu':'https://raw.githubusercontent.com/lora-sys/zhihu-threads/main/assets/readme/lora-v3-project-zhihu-threads-zh.webp',
  'arena':'https://raw.githubusercontent.com/lora-sys/AgentArena/main/docs/qa/visual-baselines/v052-home-desktop-20260725.png',
  'skills':'https://raw.githubusercontent.com/lora-sys/skills/main/assets/readme/hero.png',
  'vllm':'https://raw.githubusercontent.com/lora-sys/nano-vllm-interactive-guide/main/assets/readme/hero-v1.webp',
  'vision':'https://raw.githubusercontent.com/lora-sys/free-vision-skill/main/assets/readme/hero-v1.webp',
 }
 art_records={}
 for key,location in arts.items():
  if local:data=(ROOT/'local-assets'/(key+'.webp')).read_bytes()
  else:data=location.read_bytes() if isinstance(location,Path) else download(location)
  mime='image/png' if data.startswith(b'\x89PNG') else 'image/webp'
  soup.find('img',src='assets/'+key+'.webp')['src']=uri(data,mime)
  art_records[key]={'source':str(location),'sha256':hashlib.sha256(data).hexdigest()}
 assert local or art_records['banner']['sha256']=='c2573c101012c3480a282920a82f9ab28ebbe35920009c4072d88dd6bd9ee7ff','Original banner changed'
 for el in soup.select('.work-actions,.tail-socials,.tail-end'):el.decompose()
 soup.select_one('#overview-provider-label').string='Stats Fast'
 for el in soup.select('.stat-source'):el.string='每日更新'
 for el in soup.select('.stat-footer span'):el.string='公开数据快照'
 stats={}
 if not local:
  for theme in PALETTES:
   for kind in ('overview','languages','streak'):stats[(theme,kind)]=stats_asset(kind,theme)
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(executable_path='/usr/bin/chromium' if local else None)
  for theme in PALETTES:
   for mode,(viewport,full,cw,tw) in SIZES.items():
    page=browser.new_page(viewport={'width':viewport,'height':1000},device_scale_factor=2,reduced_motion='reduce',color_scheme=theme)
    markup=str(soup).replace('data-theme="light"',f'data-theme="{theme}"')
    page.set_content(markup,wait_until='load')
    page.add_style_tag(content='body{background:transparent!important}.sample{border:0;border-radius:0;background:transparent!important}.tail-contact-right{min-width:0}.tail-contact-main{align-items:center}.tail-contact{margin-bottom:0}.stat-body img{max-width:100%;height:auto}.work-feature-copy{padding-bottom:0}')
    for kind,host in [('overview','#stats-body'),('languages','#languages-body'),('streak','#streak-card .stat-body')]:
     if not local:page.locator(host).evaluate('(el,src)=>{el.replaceChildren(Object.assign(new Image(),{src,alt:"lora-sys real statistics",className:"stat-live-image"}));}',uri(stats[(theme,kind)]))
    page.wait_for_function('()=>[...document.images].every(i=>!i.src || (i.complete&&i.naturalWidth>0))')
    page.evaluate('()=>document.fonts.ready')
    for name,sel,kind in SPECS:
     if local and name in ('overview','languages','streak'):continue
     el=page.locator(sel);title=el.inner_text().strip().replace('\n','。')
     link=el.get_attribute('href') or (el.locator('a').first.get_attribute('href') if el.locator('a').count() else None)
     if name=='contact':link='mailto:lorasys@outlook.com'
     if name.startswith('compact-'):link=el.locator('.work-compact-foot a').get_attribute('href')
     components.setdefault(name,dict(alt=title,href=link))
     raster_svg(f'{name}-{theme}-{mode}',el.screenshot(animations='disabled',omit_background=True),cw if kind=='card' else full,title,pad=8 if kind=='card' else 0)
    for idx in range(8):
     el=page.locator('.tool-tile').nth(idx);name='tool-'+str(idx)
     components.setdefault(name,dict(alt=el.inner_text().replace('\n','。'),href=el.get_attribute('href')))
     raster_svg(f'{name}-{theme}-{mode}',el.screenshot(animations='disabled',omit_background=True),tw,components[name]['alt'],pad=8)
    for idx in range(4):
     el=page.locator('.nav a').nth(idx);name='nav-'+str(idx)
     components.setdefault(name,dict(alt=el.inner_text(),href=el.get_attribute('href')))
     raster_svg(f'{name}-{theme}-{mode}',el.screenshot(animations='disabled',omit_background=True),138 if mode=='desktop' else 124,el.inner_text(),pad=8)
    colors=PALETTES[theme]
    divider=f'<svg xmlns="http://www.w3.org/2000/svg" width="{full}" height="30" viewBox="0 0 {full} 30"><style>.flow{{animation:flow 9s linear infinite}}@keyframes flow{{from{{stroke-dashoffset:48}}to{{stroke-dashoffset:-{full}}}}}@media(prefers-reduced-motion:reduce){{.flow{{animation:none}}}}</style><path d="M0 15H{full}" stroke="#{colors["line"]}"/><path class="flow" d="M0 15H{full}" stroke="#{colors["gold"]}" stroke-width="2" stroke-dasharray="48 {full}"/></svg>'
    save_svg(f'divider-{theme}-{mode}',divider)
    for static in (False,True):
     typing_svg(page,theme,mode,static)
     if not local:snake_svg(theme,mode,static)
    page.locator('main').screenshot(path=str(QA/f'approved-render-{theme}-{mode}.png'),animations='disabled')
    page.close()
  browser.close()
 metadata=dict(build_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),generated_at=captured_at,artwork=art_records,statistics=records,components=components)
 (OUT/'sources.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'dist/README.md').write_text(make_readme(),encoding='utf-8')
 (OUT/'candidate-README.md').write_text(make_readme(),encoding='utf-8')
 for path in OUT.rglob('*.svg'):ET.fromstring(path.read_bytes())
 print('Built',len(list(OUT.glob('*.svg'))),'assets; all SVGs parsed.')

def picture(name,alt=None,link=None,static=False):
 meta=components.get(name,{})
 alt=alt or meta.get('alt',name);href=link if link is not None else meta.get('href')
 sources=[]
 def src(media,theme,mode,still=False):
  filename=f'{name}-{theme}-{mode}'+('-static' if still else '')+'.svg'
  return f'<source media="{media}" srcset="{RAW+filename}">'
 for still in ([True,False] if static else [False]):
  prefix='(prefers-reduced-motion: reduce) and ' if still else ''
  for maxw,mode in [(360,'small'),(680,'mobile')]:
   sources+=[src(prefix+f'(max-width: {maxw}px) and (prefers-color-scheme: dark)','dark',mode,still),src(prefix+f'(max-width: {maxw}px)','light',mode,still)]
  sources.append(src(prefix+'(prefers-color-scheme: dark)','dark','desktop',still))
  if still:sources.append(src('(prefers-reduced-motion: reduce)','light','desktop',True))
 pic='<picture>'+''.join(sources)+f'<img src="{RAW+name}-light-desktop.svg" alt="{html.escape(alt,quote=True)}"></picture>'
 return '<a href="'+html.escape(href,quote=True)+'">'+pic+'</a>' if href else pic

def make_readme():
 group=lambda names:'<p align="center">\n'+'\n'.join(picture(n) for n in names)+'\n</p>\n'
 md='''<!-- Lora approved profile v5. Asset provenance: output/v5/sources.json. -->
<a id="top"></a>
<p align="center"><a href="https://lora-sys.github.io/loraSys/"><img src="./assets/readme/hero-v1.webp" width="100%" alt="Lora 与 Mochi，原版插画 banner"></a></p>
'''
 md+='<p align="center">'+picture('typing','你好，我是 Lora。写 AI Agent，做开源项目。把读源码的过程做成交互教程。',static=True)+'</p>\n'
 md+='''<p align="center">我做 AI 应用和开发者工具，也把读源码的过程做成交互教程。<br>正在开发 <a href="https://github.com/lora-sys/Glassbox-Agent-Harness">Glassbox</a>，研究个人 Agent 的记忆、权限与任务执行。</p>
'''
 md+=group(['nav-'+str(i) for i in range(4)])+'\n'+picture('divider','暖色动态分隔线')+'\n\n'
 md+=picture('heading-work')+'\n\n'+group(['feature-glassbox','feature-zhihu'])
 md+='''<p align="center"><a href="https://github.com/lora-sys/Glassbox-Agent-Harness/blob/main/.plans/03-personal-agent-foundation.md">Glassbox 当前计划</a> · <a href="https://github.com/lora-sys/zhihu-threads#快速开始">Zhihu Threads 使用说明</a></p>
<p>工具、实验与教程</p>
'''
 md+=group(['compact-arena','compact-skills','compact-vllm','compact-vision'])
 md+='\n[AI Engineering Harness](https://github.com/lora-sys/ai-engineering-harness) · 更多工程工作流见仓库。\n\n'
 md+=picture('heading-tool')+'\n\n'+group(['tool-'+str(i) for i in range(8)])
 md+='<p><sub>用于应用开发、数据存储和测试。点击图标查看项目依赖。</sub></p>\n\n'
 md+=picture('heading-stats')+'\n\n'+group(['overview','languages'])
 md+='<p><sub>总览来自 Stats Fast，保留字母等级。语言分布来自自托管服务，不代表熟练度。</sub></p>\n'
 md+=picture('streak')+'\n\n'+picture('snake','lora-sys 的贡献贪吃蛇。根据 GitHub 贡献记录每日生成。',link='https://github.com/Platane/snk',static=True)+'\n\n'
 md+=f'<p><sub>统计与动画每日刷新。接口失败时保留上一次成功结果。<a href="{RAW}sources.json">数据来源与更新时间</a></sub></p>\n\n'
 md+=picture('heading-writing')+'\n\n'+group(['article-budget','article-tau','article-harness'])
 md+=picture('heading-contributions')+'\n\n'+group(['pr-eino','pr-nad','pr-moss'])
 md+=picture('contact')+'\n\n'
 md+='''<p align="center"><a href="https://lora-sys.github.io/loraSys/">个人网站</a> · <a href="https://github.com/lora-sys">GitHub</a> · <a href="https://www.zhihu.com/people/lorry-23-28-30">知乎</a> · <a href="https://x.com/MierPiter33280">X</a></p>
<p align="center"><sub>Lora · lora-sys</sub> · <a href="#top">回到顶部</a></p>

<details>
<summary>文字目录与无图阅读</summary>

'''
 for name,meta in components.items():
  if name.startswith(('feature-','compact-','article-','pr-')):
   md+=f'[{meta["alt"].split("。")[0]}]({meta["href"]})  \n{meta["alt"]}\n\n'
 md+='邮箱 [lorasys@outlook.com](mailto:lorasys@outlook.com)。\n\n</details>\n'
 return md

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--local',action='store_true');args=parser.parse_args();build(args.local)
