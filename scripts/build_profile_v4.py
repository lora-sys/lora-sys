"""Build Lora profile artwork. Requires Pillow; no remote rendering service."""
from __future__ import annotations
import argparse
import base64
import hashlib
import io
import json
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from PIL import Image, ImageOps

PALETTES = {
    'light': dict(bg='#F7F4EE', panel='#EEE7DA', text='#211F1B', muted='#75634C', rule='#DCCFB9', accent='#B67D17', chip='#E8DDC9'),
    'dark': dict(bg='#1C1C1C', panel='#292621', text='#F5EFE4', muted='#C8BBA6', rule='#494137', accent='#E3B44D', chip='#393127'),
}
ROOT = 'https://raw.githubusercontent.com/lora-sys'
PROJECTS = [
    dict(slug='glassbox',title='Glassbox',kind='PERSONAL AGENT',status='开发中',repo='Glassbox-Agent-Harness',
         lines=['个人 Agent 工作台。','记录对话、管理任务与执行过程。'],
         source=f'{ROOT}/Glassbox-Agent-Harness/main/assets/readme/glassbox-hero.png',
         crop=[690,150,1630,650], local='glassbox.png',caption='项目插画'),
    dict(slug='zhihu',title='Zhihu Threads',kind='LEARNING APP',status='应用',repo='zhihu-threads',
         lines=['把选中的知乎摘录整理成学习线。','带来源，能追问、自测与导出。'],
         source=f'{ROOT}/zhihu-threads/main/assets/readme/lora-v3-project-zhihu-threads-zh.webp',
         crop=[700,305,1590,855],local='zhihu.webp',caption='项目插画'),
    dict(slug='arena',title='AgentArena',kind='MULTI-AGENT',status='实验',repo='AgentArena',
         lines=['让三支 Agent 团队处理同一任务。','保留提案、证据与对战回放。'],
         source=f'{ROOT}/AgentArena/main/docs/qa/visual-baselines/v052-home-desktop-20260725.png',
         crop=[620,220,1360,590],local='arena.png',caption='界面截图'),
    dict(slug='skills',title='Lora Skills',kind='AGENT SKILLS',status='工具',repo='skills',
         lines=['把常用的 Agent 工作流做成技能。','按需安装，保留来源与许可证。'],
         source=f'{ROOT}/skills/main/assets/readme/hero.png',
         crop=[670,25,1190,400],local='skills.png',caption='项目插画'),
    dict(slug='vllm',title='nano-vLLM',kind='INTERACTIVE GUIDE',status='教程',repo='nano-vllm-interactive-guide',
         lines=['结合源码与浏览器交互实验，','讲解推理调度、KV Cache 与采样。'],
         source=f'{ROOT}/nano-vllm-interactive-guide/main/assets/readme/hero-v1.webp',
         crop=[620,32,1175,340],local='vllm.webp',caption='项目插画'),
    dict(slug='vision',title='Free Vision Skill',kind='DEVELOPER TOOL',status='工具',repo='free-vision-skill',
         lines=['按任务提取图片中的相关信息。','将文本证据交给 Agent 继续处理。'],
         source=f'{ROOT}/free-vision-skill/main/assets/readme/hero-v1.webp',
         crop=[630,37,1173,326],local='vision.webp',caption='项目插画'),
]
FONT = '"Noto Sans CJK SC","Microsoft YaHei","PingFang SC",Arial,sans-serif'
MONO = 'ui-monospace,"SFMono-Regular",Consolas,monospace'

def svg(w:int,h:int,body:str,title:str,css:str='') -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title,quote=True)}"><title>{escape(title)}</title><style>text{{font-family:{FONT}}}.mono{{font-family:{MONO}}}{css}</style>{body}</svg>'

def text(x,y,s,size,color,extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(s)}</text>'

def get_art(project:dict, local:Path|None):
    if local:
        data=(local/project['local']).read_bytes()
    else:
        with urlopen(Request(project['source'],headers={'User-Agent':'lora-profile-build'}),timeout=45) as response:
            data=response.read(12_000_000)
    with Image.open(io.BytesIO(data)) as original:
        cropped=original.convert('RGB').crop(project['crop'])
        if project['slug']=='skills':
            picture=Image.new('RGB',(880,380),cropped.getpixel((0,0)))
            subject=ImageOps.contain(cropped,(880,380),method=Image.Resampling.LANCZOS)
            picture.paste(subject,((880-subject.width)//2,0))
        else:
            picture=ImageOps.fit(cropped,(880,380),method=Image.Resampling.LANCZOS,centering=(.5,.45))
        buf=io.BytesIO();picture.save(buf,format='WEBP',quality=88,method=6)
    return base64.b64encode(buf.getvalue()).decode(),hashlib.sha256(data).hexdigest()

def card(project:dict, art:str, theme:str, mobile:bool=False):
    p=PALETTES[theme]
    w=360 if mobile else 440
    h=346 if mobile else 380
    image_h=156 if mobile else 190
    title_size=29 if mobile else 32
    pad=22 if mobile else 24
    b=f'<defs><clipPath id="frame"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16"/></clipPath></defs>'
    b+=f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16" fill="{p["bg"]}" stroke="{p["rule"]}"/>'
    b+=f'<g clip-path="url(#frame)"><image href="data:image/webp;base64,{art}" x="1" y="1" width="{w-2}" height="{image_h}" preserveAspectRatio="xMidYMid slice"/></g>'
    b+=f'<rect x="{w-79}" y="13" width="64" height="24" rx="12" fill="{p["bg"]}" fill-opacity=".96"/>'
    b+=text(w-47,29,project['caption'],11,p['muted'],'text-anchor="middle"')
    y=image_h+26
    b+=text(pad,y,project['kind'],10.5,p['muted'],'class="mono" letter-spacing="1.5"')
    b+=text(pad,y+41,project['title'],title_size,p['text'],'font-weight="700"')
    for i,line in enumerate(project['lines']):
        b+=text(pad,y+73+i*27,line,17.5 if mobile else 18,p['muted'])
    b+=f'<path d="M{pad} {h-43}H{w-pad}" stroke="{p["rule"]}"/>'
    b+=f'<circle cx="{pad+3}" cy="{h-22}" r="3" fill="{p["accent"]}"/>'
    b+=text(pad+14,h-17,project['status'],12,p['muted'])
    b+=text(w-pad,h-17,'查看项目',12,p['text'],'text-anchor="end"')
    return svg(w+16,h+16,'<g transform="translate(8 0)">'+b+'</g>',project['title']+'。'+''.join(project['lines'])+' '+project['status']+'。'+project['caption'])

def typing(theme:str,mobile=False,static=False):
    p=PALETTES[theme]
    w,h=(420,108) if mobile else (880,116)
    line_size=24 if mobile else 32
    rows=([
        ['我在写 AI Agent，','也做自己会用的工具。'],
        ['让 Agent 记住上下文，','执行任务，留下过程记录。'],
        ['读源码、做实验，','再把学到的东西分享出来。'],
    ] if mobile else [
        ['我在写 AI Agent，也做自己会用的工具。'],
        ['让 Agent 记住上下文、执行任务、留下过程记录。'],
        ['读源码、做实验，再把学到的东西分享出来。'],
    ])
    css=''
    body=''
    def extent(s):
        return sum(line_size if ord(c)>127 else line_size*.58 for c in s)
    for k,lines in enumerate(rows):
        if static and k>0:continue
        widths=[extent(t) for t in lines]
        x0=(w-max(widths))/2
        assert x0>=8,(lines,x0)
        visible=1 if k==0 else 0
        if not static:
            css+=f'.phrase{k}{{opacity:{visible};animation:phrase{k} 24s linear infinite;}}'
            if k==0:frames='0%,31%{opacity:1}33.33%,99.99%{opacity:0}100%{opacity:1}'
            elif k==1:frames='0%,33.32%{opacity:0}33.33%,64.33%{opacity:1}66.67%,100%{opacity:0}'
            else:frames='0%,66.66%{opacity:0}66.67%,97.67%{opacity:1}100%{opacity:0}'
            css+=f'@keyframes phrase{k}{{{frames}}}'
        body+=f'<g class="phrase{k}" opacity="{visible}">'
        events=[]
        for j,s in enumerate(lines):
            x=(w-widths[j])/2
            y=(40+j*38) if mobile else 61
            cursor=x
            for i,ch in enumerate(s):
                ident=f'char{k}{j}{i}'
                if not static:
                    start=(k*8+.25+j*1.35+i*.060)/24*100
                    erase=(k*8+6.7+(len(s)-i)*.018)/24*100
                    css+=f'.{ident}{{animation:{ident} 24s steps(1,end) infinite;}}'
                    css+=f'@keyframes {ident}{{0%{{opacity:0}}{start:.4f}%{{opacity:1}}{erase:.4f}%,100%{{opacity:0}}}}'
                    adv=line_size if ord(ch)>127 else line_size*.58
                    events.extend([(start,cursor+adv+3,y-line_size+4),(erase,cursor+3,y-line_size+4)])
                body+=text(round(cursor,2),y,ch,line_size,p['text'],f'class="{ident}" font-weight="600"')
                cursor+=line_size if ord(ch)>127 else line_size*.58
        if not static:
            cx=(w-widths[0])/2
            cy=(40 if mobile else 61)-line_size+4
            frames=f'0%{{transform:translate({cx:.2f}px,{cy:.2f}px)}}'
            for time,x,y in sorted(events):
                frames+=f'{time:.4f}%{{transform:translate({x:.2f}px,{y:.2f}px)}}'
            css+=f'.caret{k}{{animation:caret{k} 24s steps(1,end) infinite}}@keyframes caret{k}{{{frames}}}'
            body+=f'<g class="caret{k} cursor"><rect class="blink" width="2.5" height="{line_size}" fill="{p["accent"]}"/></g>'
        body+='</g>'
    if not static:
        css+='.blink{animation:blink 1.1s steps(1,end) infinite}@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}'
        css+='@media(prefers-reduced-motion:reduce){*{animation:none!important}.phrase0{opacity:1!important}.phrase1,.phrase2,.cursor{display:none}}'
    return svg(w,h,body,'我在写 AI Agent，也做自己会用的工具。',css)

def heading(theme:str,num:str,title:str,english:str,mobile=False):
    p=PALETTES[theme];w=420 if mobile else 880;h=88
    b=text(0,58,num,44,p['accent'],'class="mono" font-weight="500"')
    b+=text(74,47,title,26,p['text'],'font-weight="650"')
    b+=text(76,69,english,10,p['muted'],'class="mono" letter-spacing="2"')
    start=74+len(title)*27+25
    b+=f'<path d="M{start} 44H{w}" stroke="{p["rule"]}"/>'
    css=''
    if num=='01':
        b+=f'<path class="trace" d="M{start} 44H{w}" stroke="{p["accent"]}" stroke-width="2" stroke-dasharray="24 {w}"/>'
        css=f'.trace{{animation:trace 7s linear infinite}}@keyframes trace{{from{{stroke-dashoffset:{w}}}to{{stroke-dashoffset:-{w}}}}}@media(prefers-reduced-motion:reduce){{.trace{{animation:none}}}}'
    return svg(w,h,b,num+' '+title,css)

def button(theme,name,label):
    p=PALETTES[theme];w=160;h=44
    b=f'<rect x="1" y="1" width="158" height="42" rx="21" fill="{p["panel"]}" stroke="{p["rule"]}"/>'
    b+=text(80,28,label,18,p['text'],'text-anchor="middle" font-weight="600"')
    return svg(w,h,b,label)

def stack(theme,mobile=False):
    p=PALETTES[theme];w=420 if mobile else 880;cols=3 if mobile else 6;h=136 if mobile else 86
    names=[('TS','TypeScript'),('PY','Python'),('GO','Go'),('RE','React'),('N','Next.js'),('DK','Docker')]
    b='';gap=10;cw=(w-(cols-1)*gap)/cols
    for i,(mark,name) in enumerate(names):
        x=(i%cols)*(cw+gap);y=(i//cols)*64
        b+=f'<rect x="{x+1}" y="{y+1}" width="{cw-2}" height="53" rx="9" fill="{p["bg"]}" stroke="{p["rule"]}"/>'
        b+=text(x+14,y+33,mark,16,p['accent'],'class="mono" font-weight="700"')
        b+=text(x+cw-12,y+32,name,12,p['text'],'text-anchor="end"')
    return svg(w,h,b,'工具与技术。TypeScript、Python、Go、React、Next.js、Docker。')

def build(out:Path,local:Path|None):
    target=out/'v4';target.mkdir(parents=True,exist_ok=True)
    sources=[]
    for project in PROJECTS:
        art,digest=get_art(project,local)
        sources.append(dict(project=project['slug'],url=project['source'],sha256=digest,crop=project['crop'],caption=project['caption']))
        for theme in PALETTES:
            for mobile in (False,True):
                (target/f'project-{project["slug"]}-{theme}{"-mobile" if mobile else ""}.svg').write_text(card(project,art,theme,mobile),encoding='utf-8')
    for theme in PALETTES:
        for mobile in (False,True):
            suffix=f'{theme}{"-mobile" if mobile else ""}'
            for static in (False,True):
                (target/f'typing-{suffix}{"-static" if static else ""}.svg').write_text(typing(theme,mobile,static),encoding='utf-8')
            for num,name,en in [('01','作品','Selected work'),('02','工具与技术','My toolkit'),('03','开源贡献','Open source'),('04','代码记录','On GitHub')]:
                (target/f'section-{num}-{suffix}.svg').write_text(heading(theme,num,name,en,mobile),encoding='utf-8')
            (target/f'stack-{suffix}.svg').write_text(stack(theme,mobile),encoding='utf-8')
        for name,label in [('website','个人网站'),('projects','全部项目'),('writing','文章'),('contact','联系我')]:
            (target/f'nav-{name}-{theme}.svg').write_text(button(theme,name,label),encoding='utf-8')
    for path in target.glob('*.svg'):
        data=path.read_text();ET.fromstring(data)
        assert '<script' not in data and '<foreignObject' not in data,path
        assert 'http' not in data.replace('http://www.w3.org/2000/svg',''),path
    (target/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Validated {len(list(target.glob("*.svg")))} profile SVGs; source hashes recorded.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('dist'))
    parser.add_argument('--local-input',type=Path,help='Use reviewed local images instead of fetching sources')
    args=parser.parse_args();build(args.output,args.local_input)
