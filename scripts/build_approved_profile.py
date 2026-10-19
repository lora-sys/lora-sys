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
RAW='https://raw.githubusercontent.com/lora-sys/lora-sys/output/'
PALETTES={
 'light':dict(page='FFFFFF',bg='F6F2EA',fg='24211E',muted='70675D',line='DED8CF',accent='9A661B',gold='D6A03B'),
 'dark':dict(page='161719',bg='25231F',fg='F4F0E9',muted='BFB6A8',line='3A3732',accent='E2B45D',gold='E0A62F'),
}
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
  return 'https://github-readme-stats-fast.vercel.app/api/top-langs/?'+urlencode(q)
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
 ('overview','#stats-card','card'),('languages','#languages-card','card'),('streak','#streak-card',None),
]
CARDS=('overview','languages','streak')

def build(local=False):
 from prepare_approved_layout import write
 write()
 source=ROOT/'assets/profile/approved-layout.html'
 soup=BeautifulSoup(source.read_text(),'html.parser')
 banner=ROOT/'assets/readme/hero-v1.webp'
 data=banner.read_bytes()
 soup.find('img',src='assets/banner.webp')['src']=uri(data,'image/webp')
 art_records={'banner':{'source':str(banner),'sha256':hashlib.sha256(data).hexdigest()}}
 assert local or art_records['banner']['sha256']=='c2573c101012c3480a282920a82f9ab28ebbe35920009c4072d88dd6bd9ee7ff','Original banner changed'
 for el in soup.select('.work-actions,.tail-socials,.tail-end'):el.decompose()
 if soup.select_one('#overview-provider-label'):soup.select_one('#overview-provider-label').string='Stats Fast'
 for el in soup.select('.stat-source'):el.string='每日更新'
 for el in soup.select('.stat-footer span'):el.string='公开数据快照'
 stats={}
 if not local:
  for theme in PALETTES:
   for kind in CARDS:stats[(theme,kind)]=stats_asset(kind,theme)
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
     if local and name in CARDS:continue
     el=page.locator(sel);title=el.inner_text().strip().replace('\n','。')
     link=el.get_attribute('href') or (el.locator('a').first.get_attribute('href') if el.locator('a').count() else None)
     components.setdefault(name,dict(alt=title,href=link))
     raster_svg(f'{name}-{theme}-{mode}',el.screenshot(animations='disabled',omit_background=True),cw if kind=='card' else full,title,pad=8 if kind=='card' else 0)
    for static in (False,True):
     if not local:snake_svg(theme,mode,static)
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
  filename=f'v5/{name}-{theme}-{mode}'+('-static' if still else '')+'.svg'
  return f'<source media="{media}" srcset="{RAW+filename}">'
 for still in ([True,False] if static else [False]):
  prefix='(prefers-reduced-motion: reduce) and ' if still else ''
  for maxw,mode in [(360,'small'),(680,'mobile')]:
   sources+=[src(prefix+f'(max-width: {maxw}px) and (prefers-color-scheme: dark)','dark',mode,still),src(prefix+f'(max-width: {maxw}px)','light',mode,still)]
  sources.append(src(prefix+'(prefers-color-scheme: dark)','dark','desktop',still))
  if still:sources.append(src('(prefers-reduced-motion: reduce)','light','desktop',True))
 pic='<picture>'+''.join(sources)+f'<img src="{RAW+"v5/"+name}-light-desktop.svg" alt="{html.escape(alt,quote=True)}"></picture>'
 return '<a href="'+html.escape(href,quote=True)+'">'+pic+'</a>' if href else pic

def make_readme():
 group=lambda names:'<p align="center">\n'+'\n'.join('    '+picture(n) for n in names)+'\n</p>\n'
 md='    <!-- Lora approved profile v5. Asset provenance: output/v5/sources.json. -->\n'
 md+='    <a id="top"></a>\n'
 md+='    <p align="center"><a href="https://lora-sys.github.io/loraSys/"><img src="./assets/readme/hero-v1.webp" width="100%" alt="Lora 与 Mochi，原版插画 banner"></a></p>\n\n'
 md+='    <h1 align="center">Lora</h1>\n'
 md+='    <p align="center">学生开发者 · 中国西安 · 写 AI Agent，也写把源码讲明白的交互教程</p>\n\n'
 md+='    <p align="center"><a href="https://lora-sys.github.io/loraSys/">网站</a> · <a href="https://lora-sys.github.io/loraSys/projects">项目</a> · <a href="https://lora-sys.github.io/loraSys/blog">文章</a> · <a href="https://lora-sys.github.io/loraSys/rss.xml">RSS</a> · <a href="mailto:lorasys@outlook.com">邮箱</a></p>\n\n'
 md+='    ## 做过的\n\n'
 md+='    - **[Glassbox](https://github.com/lora-sys/Glassbox-Agent-Harness)** — 权限优先的个人 Agent 工作台，管理身份、记忆、权限与任务执行。119 个 Issue、67 个已合并 PR 在推进。\n'
 md+='    - **[nano-vLLM 交互教程](https://lora-sys.github.io/nano-vllm-interactive-guide/guide/00-start)** — 把推理调度、KV Cache 和采样讲成可以在浏览器里跑的实验。\n'
 md+='    - **[Free Vision Skill](https://github.com/lora-sys/free-vision-skill)** — 把图片压成文本证据，给不支持视觉的模型用。★ 17\n'
 md+='    - **[AgentArena](https://github.com/lora-sys/AgentArena)** — 让三支 Agent 团队处理同一任务，留下提案、证据与对战回放。\n'
 md+='    - 向 [cloudwego/eino-examples](https://github.com/cloudwego/eino-examples/pull/227)、[portdeveloper/nad-agent](https://github.com/portdeveloper/nad-agent/pull/49)、[nishuzumi/moss](https://github.com/nishuzumi/moss/pull/29) 等 13 个仓库提交过 174 个已合并 PR。\n\n'
 md+='    ## 写过的\n\n'
 md+='    179 篇笔记，写 Agent 架构、记忆与评测，都按可以照着复现的方式拆。最近的几篇：[Agent 该继续跑还是重新开一轮](https://lora-sys.github.io/loraSys/blog/agent-budget-memory-evaluation) · [把 Agent 拆成三层](https://lora-sys.github.io/loraSys/blog/tau-agent-architecture) · [Agent 开发的测试与审查](https://lora-sys.github.io/loraSys/blog/ai-engineering-harness)。\n\n'
 md+='    ## 数据和贡献\n\n'
 md+='    '+group(['overview','languages'])+'\n'
 md+='    '+picture('streak')+'\n\n'+'    '+picture('snake','lora-sys 的贡献贪吃蛇。根据 GitHub 贡献记录每日生成。',link='https://github.com/Platane/snk',static=True)+'\n\n'
 md+=f'    <p align="center"><sub>数据每日刷新，校验失败时保留上一次成功结果。<a href="{RAW}v5/sources.json">数据来源与更新时间</a></sub></p>\n\n'
 md+='    <p align="center"><a href="https://lora-sys.github.io/loraSys/">lora-sys.github.io/loraSys</a> · <a href="mailto:lorasys@outlook.com">lorasys@outlook.com</a> · <a href="#top">回到顶部</a></p>\n'
 return '\n'.join(line[4:] for line in md.splitlines())

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--local',action='store_true');args=parser.parse_args();build(args.local)
