"""Check the public GitHub profile, not a locally reconstructed page."""
from pathlib import Path
import hashlib
import json
import os
import sys
from urllib.request import Request, urlopen
from playwright.sync_api import sync_playwright

OUT=Path('qa');OUT.mkdir(exist_ok=True)
README=Path('README.md').read_text()
if 'output/v5/' not in README:
    (OUT/'report.json').write_text(json.dumps({'status':'waiting_for_v5_readme','passed':False}))
    print('Approved assets built; waiting for README publication')
    sys.exit(0)

report={'source':'https://github.com/lora-sys','sha':os.getenv('GITHUB_SHA'),'views':[],'errors':[]}
views=[('light',1440,False),('dark',1440,False),('light',768,False),('dark',768,False),('light',390,False),('dark',390,False),('light',320,False),('dark',390,True)]
geometry='''el=>{
 const canonical=url=>{try{const u=new URL(url);if(u.hostname==='camo.githubusercontent.com'){const h=u.pathname.split('/').pop();if(/^[0-9a-f]+$/i.test(h))return decodeURIComponent(h.replace(/../g,x=>'%'+x));}}catch{}return url};
 const images=[...el.querySelectorAll('img')].map(i=>{const r=i.getBoundingClientRect();return {alt:i.alt,loaded:i.complete&&i.naturalWidth>0,src:canonical(i.currentSrc),x:r.x,y:r.y,width:r.width,height:r.height,href:i.closest('a')?.href||null}});
 const r=el.getBoundingClientRect();return {width:el.clientWidth,scrollWidth:el.scrollWidth,documentWidth:document.documentElement.scrollWidth,viewport:innerWidth,images,links:[...el.querySelectorAll('a')].map(a=>a.href),box:{x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height}};
}'''
with sync_playwright() as p:
 browser=p.chromium.launch()
 for theme,width,reduce in views:
  page=browser.new_page(viewport={'width':width,'height':1000},color_scheme=theme,reduced_motion='reduce' if reduce else 'no-preference',device_scale_factor=1)
  label=f'{theme}-{width}'+('-static' if reduce else '')
  try:
   for attempt in range(5):
    response=page.goto('https://github.com/lora-sys?profile-review='+str(attempt),wait_until='domcontentloaded',timeout=45000)
    page.wait_for_timeout(1500)
    if page.locator('article.markdown-body img[alt^="你好，我是 Lora"]').count():break
    page.wait_for_timeout(2500)
   assert response and response.status==200,'GitHub did not return HTTP 200'
   article=page.locator('article.markdown-body').first
   assert article.count(),'Profile README not found'
   page.evaluate('(theme)=>{document.documentElement.dataset.colorMode=theme;document.documentElement.dataset.lightTheme="light";document.documentElement.dataset.darkTheme="dark"}',theme)
   page.wait_for_function('''()=>{const a=document.querySelector('article.markdown-body');return a&&a.querySelectorAll('img').length>=35&&[...a.querySelectorAll('img')].every(i=>i.complete&&i.naturalWidth>0)}''',timeout=60000)
   page.wait_for_timeout(3500)
   page.evaluate('scrollTo(0,0)')
   data=article.evaluate(geometry)
   assert data['scrollWidth']<=data['width']+1,'README horizontal overflow'
   assert data['documentWidth']<=width+1,'Page horizontal overflow'
   for image in data['images']:
    assert image['loaded'],image['alt']+' not loaded'
    if '/v5/' in image['src']:
     assert ('-dark-' in image['src'])==(theme=='dark'),'Wrong image theme '+image['src']
     if reduce and any(n in image['src'] for n in ('/typing-','/snake-')):
      assert '-static.svg' in image['src'],'Reduced-motion source is animated'
   features=[i for i in data['images'] if '/feature-' in i['src']]
   compact=[i for i in data['images'] if '/compact-' in i['src']]
   assert len(features)==2 and len(compact)==4,'Project A requires two featured and four compact cards'
   if width in (1440,):
    assert abs(features[0]['y']-features[1]['y'])<4,'Featured cards must be side by side'
   if width<680:
    assert len({round(i['x']) for i in features+compact})<=2,'Project cards must wrap on mobile'
    assert features[1]['y']>features[0]['y']+features[0]['height']*.8,'Featured cards overlap on mobile'
   for repo in ('Glassbox-Agent-Harness','zhihu-threads'):
    assert 'https://github.com/lora-sys/'+repo in data['links'],'Missing project link '+repo
   for url in ('https://github.com/cloudwego/eino-examples/pull/227','https://github.com/portdeveloper/nad-agent/pull/49','https://github.com/nishuzumi/moss/pull/29','mailto:lorasys@outlook.com'):
    assert url in data['links'],'Missing approved link '+url
   page.screenshot(path=str(OUT/f'page-{label}.png'),full_page=True,timeout=30000)
   article.screenshot(path=str(OUT/f'profile-{label}.png'),timeout=30000)
   if theme=='light' and width==1440:
    (OUT/'profile.html').write_text(page.content())
    typing=article.locator('img[alt^="你好，我是 Lora"]')
    typing.screenshot(path=str(OUT/'typing-a.png'))
    page.wait_for_timeout(2000)
    typing.screenshot(path=str(OUT/'typing-b.png'))
    report['typing_frames_differ']=(OUT/'typing-a.png').read_bytes()!=(OUT/'typing-b.png').read_bytes()
   report['views'].append({'label':label,'status':'passed',**data})
  except Exception as exc:
   report['errors'].append({'label':label,'error':str(exc)})
   try:
    page.screenshot(path=str(OUT/f'failure-{label}.png'),full_page=True,timeout=20000)
    (OUT/f'failure-{label}.html').write_text(page.content())
   except Exception:pass
  finally:page.close()
 browser.close()
report['passed']=not report['errors'] and len(report['views'])==len(views)
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'passed':report['passed'],'views':len(report['views']),'errors':report['errors']},ensure_ascii=False))
if not report['passed']:sys.exit(1)
