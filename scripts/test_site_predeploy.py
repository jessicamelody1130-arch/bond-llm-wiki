"""Offline predeployment audit, no external network or real browser claimed."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, unquote
import json, math, subprocess
R=Path(__file__).resolve().parents[1]
checks=[]
def check(name, okay, detail=''):
 checks.append({'name':name,'status':'PASS' if okay else 'FAIL','detail':str(detail)})
htmls=list(R.rglob('*.html'))
site=[p for p in htmls if 'private-fixture-archive' not in str(p) and 'raw' not in p.parts]
missing=[]; checked=0
for f in site:
 try: doc=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
 except Exception as e:missing.append(f'{f}:parse:{e}');continue
 for el in doc.select('[href], [src]'):
  href=el.get('href') or el.get('src') or ''
  if not href or href.startswith(('https:','http:','mailto:','data:','javascript:')):continue
  parsed=urlsplit(href)
  target=f if not parsed.path else (f.parent/unquote(parsed.path))
  if target.is_dir():target=target/'index.html'
  checked+=1
  if not target.is_file():missing.append(f'{f.relative_to(R)} -> {href}')
  elif parsed.fragment and target.suffix=='.html' and not (target==R/'slides/index.html' and parsed.fragment.isdigit()):
   t=BeautifulSoup(target.read_text(encoding='utf-8'),'html.parser')
   if not t.find(id=unquote(parsed.fragment)):missing.append(f'{f.relative_to(R)} -> {href} missing anchor')
check('all_local_page_asset_and_anchor_links',not missing,f'{checked} checked; {missing[:8]}')
slides=BeautifulSoup((R/'slides/index.html').read_text(encoding='utf-8'),'html.parser').select('section.slide')
check('ten_slide_sections',len(slides)==10,len(slides))
manifest=json.loads((R/'sources/manifest.json').read_text(encoding='utf-8'))
sources={s['id'] for s in manifest['sources']}
all_topics={p.stem for p in (R/'wiki/concepts').glob('*.md')}
for i,slide in enumerate(slides,1):
 topics=slide.get('data-sources','').split(',')
 check(f'slide_{i:02d}_wiki_mapping',bool(topics) and set(topics)<=all_topics,','.join(topics))
 check(f'slide_{i:02d}_has_heading',bool(slide.select_one('h1, h2')))
for s in manifest['sources']:
 check('source_card_'+s['id'],(R/s['local_path']).is_file() and bool(s.get('url','').startswith('https://')))
# independent recomputation; no LLM values reused in formula computation
F=1000; coupon=F*.04; n=5
def price(r):return sum(coupon/(1+r)**t for t in range(1,n+1))+F/(1+r)**n
expect=[1045.80,1000.00,956.71]
check('prices_independent',all(abs(price(r)-x)<.006 for r,x in zip([.03,.04,.05],expect)))
check('price_yield_monotonicity',price(.03)>price(.04)>price(.05))
mac=sum(t*(coupon+(F if t==n else 0))/(1.04)**t for t in range(1,n+1))/price(.04)
mod=mac/1.04
check('duration_independent',abs(mac-4.6299)<.0001 and abs(mod-4.4518)<.0001,f'Mac={mac:.6f}; Mod={mod:.6f}')
node=subprocess.run(['node',str(R/'scripts/test_interactions_offline.cjs')],capture_output=True,text=True)
if node.returncode==0:
 sim=json.loads(node.stdout)
 check('isolated_dom_simulation',sim['failed']==0,sim['passed'])
else:check('isolated_dom_simulation',False,node.stderr[-500:])
check('all_sources_not_misrepresented_as_fulltext',all(s.get('ingest_status')!='full_text' for s in manifest['sources']))
report={'date':'2026-11-14','kind':'offline static/anchor/math/DOM simulation - NOT real browser or live site test','passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'checks':checks,'known_blockers':['Live full-text ingestion has 0 verified successes in this environment.','Chromium headless timed out again; real browser interaction not verified.','GitHub Pages is not deployed.']}
out=R/'logs/runs/2026-11-14-predeploy-site-audit.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'failed':report['failed'],'failures':[c for c in checks if c['status']=='FAIL']},ensure_ascii=False,indent=2))
raise SystemExit(bool(report['failed']))
