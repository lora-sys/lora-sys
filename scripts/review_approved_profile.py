"""Read-only verification and screenshots of the actual public GitHub profile."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, sys
from urllib.request import Request, urlopen
from PIL import Image
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
            page.wait_for_function('''()=>[...document.querySelectorAll('article.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0)''',timeout=45000)
            page.evaluate('window.scrollTo(0,0)')
            page.wait_for_timeout(2400)
            data=article.evaluate('''el=>({width:el.clientWidth,scrollWidth:el.scrollWidth,images:[...el.querySelectorAll('img')].map(i=>({alt:i.alt,src:i.currentSrc,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height,x:i.getBoundingClientRect().x,y:i.getBoundingClientRect().y})),links:[...el.querySelectorAll('a[href]')].map(a=>a.href)})''')
            assert data['scrollWidth']<=data['width']+1,'README horizontal overflow'
            features=[i for i in data['images'] if '/feature-' in i['src']]
            tools=[i for i in data['images'] if '/tool-' in i['src']]
            assert len(features)==2,'Expected two featured projects'
            assert len(tools)==8,'Expected eight toolkit links'
            for name in ('overview','languages','streak','snake'):
                assert any('/'+name+'-' in i['src'] for i in data['images']),name+' card missing'
            for image in data['images']:
                if '/v5/' in image['src']:
                    assert ('-dark-' in image['src'])==(theme=='dark'),'Wrong theme: '+image['src']
                    if reduce and ('/typing-' in image['src'] or '/snake-' in image['src']):
                        assert '-static.svg' in image['src'],'Reduced motion fallback missing'
            if width>=1200:
                assert abs(features[0]['y']-features[1]['y'])<3,'Featured cards are not side by side'
            else:
                assert abs(features[0]['x']-features[1]['x'])<3,'Mobile cards are not one column'
            box=article.bounding_box()
            full_path=out/f'github-{label}.png'
            page.screenshot(path=str(full_path),full_page=True,timeout=30000)
            # Crop the actual full-page screenshot instead of scrolling a tall
            # locator into view, which can put GitHub's sticky tabs in the middle.
            with Image.open(full_path) as image:
                x,y=round(box['x']),round(box['y'])
                image.crop((x,y,x+round(box['width']),y+round(box['height']))).save(out/f'readme-{label}.png')
            if theme=='light' and width==1440:
                (out/'profile.html').write_text(page.content(),encoding='utf-8')
                for name,pause in [('typing',4300),('snake',1900)]:
                    element=article.locator('img[src*="'+name+'-"]').first
                    first=element.screenshot(path=str(out/(name+'-a.png')))
                    page.wait_for_timeout(pause)
                    second=element.screenshot(path=str(out/(name+'-b.png')))
                    report[name+'_frames_differ']=hashlib.sha256(first).digest()!=hashlib.sha256(second).digest()
                    assert report[name+'_frames_differ'],name+' does not animate in the real page'
                report['native_pins']=page.locator('.pinned-item-list-item-content .repo').all_text_contents()
            if reduce:
                for name in ('typing','snake'):
                    element=article.locator('img[src*="'+name+'-"]').first
                    first=element.screenshot()
                    page.wait_for_timeout(1200)
                    second=element.screenshot()
                    assert hashlib.sha256(first).digest()==hashlib.sha256(second).digest(),name+' is not static'
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
        with urlopen(Request(url,headers={'User-Agent':'lora-profile-review'}),timeout=25) as response:
            body=response.read(2_000_000).decode('utf-8','replace')
            title=re.search(r'<title>(.*?)</title>',body,re.S)
            report['links'].append({'url':url,'status':response.status,'title':title.group(1) if title else ''})
    except Exception as exc:report['links'].append({'url':url,'error':str(exc)})
report['passed']=not report['errors'] and len(report['views'])==6
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'views':len(report['views']),'errors':report['errors'],'links':report['links']},ensure_ascii=False))
if not report['passed']:sys.exit(1)
