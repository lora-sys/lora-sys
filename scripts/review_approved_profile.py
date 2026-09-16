"""Read-only browser verification of the actual GitHub profile, not a mock page."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, sys
from urllib.request import Request, urlopen
from playwright.sync_api import sync_playwright

out=Path('qa-live');out.mkdir(exist_ok=True)
readme=Path('README.md').read_text()
if 'output/v5/' not in readme:
    (out/'report.json').write_text(json.dumps({'status':'assets_ready_waiting_for_readme_release'}))
    sys.exit(0)
report={'source':'https://github.com/lora-sys','checked_at':datetime.now(timezone.utc).isoformat(),'commit':os.environ.get('GITHUB_SHA'),'views':[],'errors':[],'links':[]}
with sync_playwright() as p:
    browser=p.chromium.launch()
    for theme,width,reduce in [('light',1440,False),('dark',1440,False),('light',390,False),('dark',390,False),('light',320,False),('dark',390,True)]:
        label=f'{theme}-{width}'+('-static' if reduce else '')
        page=browser.new_page(viewport={'width':width,'height':1000},color_scheme=theme,reduced_motion='reduce' if reduce else 'no-preference')
        try:
            for attempt in range(6):
                response=page.goto('https://github.com/lora-sys?profile-release=v5&attempt='+str(attempt),wait_until='domcontentloaded',timeout=45000)
                page.wait_for_timeout(2000)
                if page.locator('article.markdown-body img[src*="v5/"]').count():break
                page.wait_for_timeout(4000)
            assert response and response.status==200,'GitHub did not return HTTP 200'
            page.evaluate('(theme)=>{document.documentElement.dataset.colorMode=theme;document.documentElement.dataset.lightTheme="light";document.documentElement.dataset.darkTheme="dark"}',theme)
            article=page.locator('article.markdown-body').first
            assert article.count(),'No rendered profile README'
            imgs=article.locator('img')
            for i in range(imgs.count()):
                imgs.nth(i).scroll_into_view_if_needed(timeout=10000)
                page.wait_for_timeout(70)
            article.scroll_into_view_if_needed()
            page.wait_for_function('''()=>[...document.querySelectorAll('article.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0)''',timeout=45000)
            page.wait_for_timeout(2400)
            data=article.evaluate('''el=>({width:el.clientWidth,scrollWidth:el.scrollWidth,images:[...el.querySelectorAll('img')].map(i=>({alt:i.alt,src:i.currentSrc,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height,x:i.getBoundingClientRect().x,y:i.getBoundingClientRect().y})),links:[...el.querySelectorAll('a[href]')].map(a=>a.href)})''')
            assert data['scrollWidth']<=data['width']+1,'README horizontal overflow'
            features=[i for i in data['images'] if '/feature-' in i['src']]
            tools=[i for i in data['images'] if '/tool-' in i['src']]
            assert len(features)==2,'Expected two featured projects'
            assert len(tools)==8,'Expected eight toolkit links'
            assert any('/overview-' in i['src'] for i in data['images']),'Overview card missing'
            assert any('/languages-' in i['src'] for i in data['images']),'Language card missing'
            assert any('/streak-' in i['src'] for i in data['images']),'Streak card missing'
            assert any('/snake-' in i['src'] for i in data['images']),'Snake missing'
            for i in data['images']:
                if '/v5/' in i['src']:
                    assert ('-dark-' in i['src'])==(theme=='dark'),'Wrong picture theme: '+i['src']
                    if reduce and ('/typing-' in i['src'] or '/snake-' in i['src']):assert '-static.svg' in i['src'],'Reduced motion fallback missing'
            if width>=1200:assert abs(features[0]['y']-features[1]['y'])<3,'Featured cards are not side by side'
            else:assert abs(features[0]['x']-features[1]['x'])<3,'Mobile cards are not one column'
            page.screenshot(path=str(out/f'github-{label}.png'),full_page=True,timeout=30000)
            article.screenshot(path=str(out/f'readme-{label}.png'),timeout=30000)
            if theme=='light' and width==1440:
                (out/'profile.html').write_text(page.content(),encoding='utf-8')
                typing=article.locator('img[src*="typing-"]').first
                typing.screenshot(path=str(out/'typing-a.png'))
                page.wait_for_timeout(4300)
                typing.screenshot(path=str(out/'typing-b.png'))
                report['typing_frames_differ']=hashlib.sha256((out/'typing-a.png').read_bytes()).digest()!=hashlib.sha256((out/'typing-b.png').read_bytes()).digest()
                snake=article.locator('img[src*="snake-"]').first
                snake.screenshot(path=str(out/'snake-a.png'))
                page.wait_for_timeout(1900)
                snake.screenshot(path=str(out/'snake-b.png'))
                report['snake_frames_differ']=hashlib.sha256((out/'snake-a.png').read_bytes()).digest()!=hashlib.sha256((out/'snake-b.png').read_bytes()).digest()
                # Native pins are inspected only. This script never changes account settings.
                report['native_pins']=page.locator('.pinned-item-list-item-content .repo').all_text_contents()
            report['views'].append({'label':label,'status':'passed',**data})
        except Exception as exc:
            report['errors'].append({'label':label,'error':str(exc)})
            try:
                page.screenshot(path=str(out/f'failure-{label}.png'),full_page=True,timeout=20000)
                (out/f'failure-{label}.html').write_text(page.content())
            except Exception:pass
        finally:page.close()
    browser.close()

urls=[
 'https://lora-sys.github.io/loraSys/blog/agent-budget-memory-evaluation',
 'https://lora-sys.github.io/loraSys/blog/tau-agent-architecture',
 'https://lora-sys.github.io/loraSys/blog/ai-engineering-harness',
 'https://lora-sys.github.io/nano-vllm-interactive-guide/guide/00-start',
]
for url in urls:
    try:
        with urlopen(Request(url,headers={'User-Agent':'lora-profile-review'}),timeout=25) as r:
            body=r.read(2_000_000).decode('utf-8','replace');title=re.search(r'<title>(.*?)</title>',body,re.S)
            report['links'].append({'url':url,'status':r.status,'title':title.group(1) if title else ''})
    except Exception as exc:report['links'].append({'url':url,'error':str(exc)})
report['passed']=not report['errors'] and len(report['views'])==6
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'views':len(report['views']),'errors':report['errors'],'links':report['links']},ensure_ascii=False))
if not report['passed']:sys.exit(1)
