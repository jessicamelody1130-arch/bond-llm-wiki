from pathlib import Path
from html.parser import HTMLParser
import csv,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
source_map={'bond-basics':['SRC-001','SRC-003'],'bond-pricing':['SRC-002','SRC-006'],'bond-yields':['SRC-002','SRC-003','SRC-006','SRC-008'],'interest-rate-risk':['SRC-001','SRC-002','SRC-004','SRC-006'],'duration':['SRC-005','SRC-007'],'numeric-examples':['SRC-006','SRC-007']}
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.slides=[];self.ids=set();self.assets=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='section' and 'slide' in d.get('class','').split():self.slides.append(d)
  if 'id' in d:self.ids.add(d['id'])
  if tag in ('link','script'):
   self.assets.append(d.get('href',d.get('src','')))
h=(R/'slides/index.html').read_text(encoding='utf-8');p=Parser();p.feed(h)
checks=[]
def chk(name,ok,detail=''):checks.append({'name':name,'result':'PASS' if ok else 'FAIL','detail':detail})
chk('10_slides',len(p.slides)==10,str(len(p.slides)))
chk('every_slide_source_topics',all('data-sources' in s and all(t in source_map for t in s['data-sources'].split(',')) for s in p.slides))
chk('required_dom_elements',all(i in p.ids for i in ['quiz','quizResult','priceChart','prev','next','bar','progressLabel']))
chk('local_assets',all((R/'slides'/a).exists() for a in p.assets if a and not a.startswith('http')),str(p.assets))
chk('wiki_topics_exist',all((R/'wiki/concepts'/f'{t}.md').exists() for t in source_map))
proc=subprocess.run(['node','--check',str(R/'slides/script.js')],capture_output=True,text=True)
chk('js_syntax',proc.returncode==0,proc.stderr.strip())
with (R/'logs/slide-source-map.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['slide_id','wiki_topic_id','wiki_path','source_id','source_card'])
 for i,s in enumerate(p.slides,1):
  for t in s['data-sources'].split(','):
   for sid in source_map[t]:w.writerow([f'S{i:02d}',t,f'wiki/concepts/{t}.md',sid,f'wiki/sources/{sid.lower()}.md'])
# Browser smoke test via chromium headless and virtual-time DOM dump
try:
 res=subprocess.run(['chromium','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--virtual-time-budget=2000','--dump-dom',(R/'slides/index.html').as_uri()],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=25)
 chk('chromium_dom_loaded',res.returncode==0 and '01 / 10' in res.stdout and 'id="priceChart"' in res.stdout, 'Headless Chromium DOM load (not full manual keyboard test)')
except Exception as e:chk('chromium_dom_loaded',False,str(e))
report={'date':'2026-11-14','stage':'Gate C static + browser DOM smoke test','passed':sum(x['result']=='PASS' for x in checks),'failed':sum(x['result']=='FAIL' for x in checks),'checks':checks,'remaining':['Manual keyboard navigation and quiz click-flow not verified by this smoke test.','Source semantic review remains incomplete.','GitHub Pages deployment not performed.']}
(R/'logs/runs/2026-11-14-slides-test.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(bool(report['failed']))
