from pathlib import Path
from bs4 import BeautifulSoup
import json,csv,re,math,subprocess
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'sources/manifest.json').read_text())
checks=[]
def c(name,passed,detail=''):
 checks.append({'name':name,'status':'PASS' if passed else 'FAIL','detail':detail})
all_ids={x['id'] for x in manifest['sources']}
c('source_count_at_least_5',len(all_ids)>=5,str(len(all_ids)))
c('source_ids_unique',len(all_ids)==len(manifest['sources']))
index=(R/'wiki/index.md').read_text()
for sid in sorted(all_ids):
 c('source_index_'+sid,sid in index and (R/'wiki/sources'/f'{sid.lower()}.md').exists())
slide_html=(R/'slides/index.html').read_text();soup=BeautifulSoup(slide_html,'html.parser');slides=soup.select('section.slide')
c('slides_count',len(slides)==10,str(len(slides)))
lookup={x.stem:x.read_text() for x in (R/'wiki/concepts').glob('*.md')}
for n,sl in enumerate(slides,1):
 topics=sl.get('data-sources','').split(',');ok=all(t in lookup for t in topics)
 c(f'slide_{n:02d}_wiki_topics',ok,','.join(topics))
 for topic in topics:
  cites=re.findall('SRC-\\d{3}',lookup[topic].split('---',2)[1])
  c(f'slide_{n:02d}_topic_{topic}_source_refs',bool(cites) and all(k in all_ids for k in cites))
# Exclude http URLs, mailto, anchors; assert all internal site href/src target resolves
bad=[];links=0
for f in R.glob('**/*.html'):
 tree=BeautifulSoup(f.read_text(),'html.parser')
 for tag in tree.find_all(['a','link','script']):
  val=tag.get('href') or tag.get('src')
  if not val or val.startswith(('http:','https:','mailto:','#','data:')):continue
  target=(f.parent/val.split('#')[0].split('?')[0])
  if target.is_dir():target=target/'index.html'
  links+=1
  if not target.exists():bad.append(f'{f.relative_to(R)} => {val}')
c('internal_site_links',not bad,f'{links} inspected; missing={bad[:10]}')
# independent formulas
F=1000;C=40;N=5
prices={y:sum(C/(1+y)**t for t in range(1,N+1))+F/(1+y)**N for y in [.03,.04,.05]}
mac=sum((t*C + (N*F if t==N else 0))/(1.04)**t for t in range(1,N+1))/prices[.04]
mod=mac/1.04
# revised duration formula matches PV weighting
mac=sum(t*(C+(F if t==N else 0))/(1.04)**t for t in range(1,N+1))/prices[.04]
mod=mac/1.04
c('bond_price_examples',all(abs(prices[y]-expected)<1e-5 for y,expected in [(.03,1045.7970718719453),(.04,1000),(.05,956.7052332936915)]))
c('duration_approximation',abs(mac-4.629895)<.001 and abs(mod-4.4518)<.001,f'Mac={mac:.6f};Mod={mod:.6f}')
node=subprocess.run(['node','--check',str(R/'slides/script.js')],capture_output=True,text=True)
c('javascript_syntax',node.returncode==0,node.stderr[:250])
interaction=json.loads((R/'logs/runs/2026-11-14-interaction-simulation.json').read_text())
c('simulated_navigation_and_quiz',interaction['failed']==0,f"{interaction['passed']} simulated tests")
report={'date':'2026-11-14','scope':'final pre-deployment local static, math, index/source and simulated interactive checks','checks':checks,'passed':sum(x['status']=='PASS' for x in checks),'failed':sum(x['status']=='FAIL' for x in checks),'limitations':['Chromium navigation to local file:/// and loopback http:// was blocked by environment administrator (net::ERR_BLOCKED_BY_ADMINISTRATOR); no real browser interaction PASS is claimed.','Wiki contains structured extracts and paraphrases, not 8 complete ingested full-text documents.','Source semantic review focused on six teaching themes and specific citation defects, not a line-by-line comparison of all external sources.','GitHub Pages publication and real public link verification are deferred.'],'original_issues_and_repairs':['Current Yield assertion formerly lacked direct supporting citation; resolved via new SEC source SRC-008.','Arrow navigation failed when BUTTON had focus; changed input-focus filter, and 12/12 simulated tests then passed.']}
(R/'logs/runs/2026-11-14-final-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:report[k] for k in ['passed','failed','limitations','original_issues_and_repairs']},ensure_ascii=False,indent=2))
if report['failed']:raise SystemExit(1)
