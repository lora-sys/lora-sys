"""Screenshot the actual public GitHub profile after assets are published."""
from pathlib import Path
import hashlib
import json
import os
import sys
from playwright.sync_api import sync_playwright

out=Path('qa');out.mkdir(exist_ok=True)
if 'output/v4/' not in Path('README.md').read_text():
    (out/'report.json').write_text(json.dumps({'status':'waiting_for_readme_switch'}))
    sys.exit(0)
report={'source':'https://github.com/lora-sys','sha':os.environ.get('GITHUB_SHA'),'views':[]}
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch()
    for theme,width,reduce in [('light',1440,False),('dark',1440,False),('light',390,False),('dark',390,False),('light',320,False),('dark',390,True)]:
        page=browser.new_page(viewport={'width':width,'height':1000},color_scheme=theme,reduced_motion='reduce' if reduce else 'no-preference',device_scale_factor=1)
        label=f'{theme}-{width}'+('-static' if reduce else '')
        try:
            for attempt in range(10):
                response=page.goto('https://github.com/lora-sys?profile-review='+str(attempt),wait_until='domcontentloaded',timeout=45000)
                page.wait_for_timeout(1500)
                if page.locator('article.markdown-body img[alt^="Lora Sys"]').count():break
                page.wait_for_timeout(4000)
            assert response and response.status==200, 'GitHub page did not return 200'
            page.evaluate('(theme)=>{document.documentElement.dataset.colorMode=theme;document.documentElement.dataset.lightTheme="light";document.documentElement.dataset.darkTheme="dark"}',theme)
            article=page.locator('article.markdown-body').first
            article.scroll_into_view_if_needed()
            page.wait_for_function('''() => [...document.querySelectorAll('article.markdown-body img')].length>=18 && [...document.querySelectorAll('article.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0)''',timeout=45000)
            page.wait_for_timeout(3000)
            data=article.evaluate('''el=>({width:el.clientWidth,scrollWidth:el.scrollWidth,images:[...el.querySelectorAll('img')].map(i=>({alt:i.alt,loaded:i.complete&&i.naturalWidth>0,src:i.currentSrc,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height})),cards:[...el.querySelectorAll('img')].filter(i=>i.currentSrc.includes('/project-')).map(i=>({x:i.getBoundingClientRect().x,y:i.getBoundingClientRect().y,width:i.getBoundingClientRect().width}))})''')
            assert data['scrollWidth']<=data['width']+1,'README horizontal overflow'
            assert len(data['cards'])==6,'Expected six project pictures'
            for image in data['images']:
                if '/v4/' in image['src']:
                    assert ('-dark' in image['src'])==(theme=='dark'), 'Wrong theme: '+image['src']
                if reduce and '/typing-' in image['src']:
                    assert '-static.svg' in image['src'],'Typing is not static'
            if width<600:
                assert len({round(c['x']) for c in data['cards']})==1,'Mobile cards must form one column'
            else:
                assert len({round(c['y']) for c in data['cards']})==3,'Desktop cards must form three rows'
            article.screenshot(path=str(out/f'profile-{label}.png'),timeout=20000)
            page.screenshot(path=str(out/f'page-{label}.png'),full_page=True,timeout=20000)
            if theme=='light' and width==1440:
                (out/'profile.html').write_text(page.content(),encoding='utf-8')
                typing=article.locator('img[alt^="我在写"]')
                typing.screenshot(path=str(out/'typing-frame-a.png'))
                page.wait_for_timeout(1800)
                typing.screenshot(path=str(out/'typing-frame-b.png'))
                report['typing_frames_differ']=hashlib.sha256((out/'typing-frame-a.png').read_bytes()).digest()!=hashlib.sha256((out/'typing-frame-b.png').read_bytes()).digest()
            report['views'].append({'label':label,'status':'passed',**data})
        except Exception as exc:
            errors.append({'label':label,'error':str(exc)})
            try:page.screenshot(path=str(out/f'failure-{label}.png'),full_page=True)
            except Exception:pass
        finally:page.close()
    browser.close()
report['errors']=errors
report['passed']=not errors and len(report['views'])==6
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'views':len(report['views']),'errors':errors},ensure_ascii=False))
if errors:sys.exit(1)
