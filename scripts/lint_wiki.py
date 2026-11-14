from pathlib import Path
import json,re,math,datetime
P=Path(__file__).resolve().parents[1]
M=json.loads((P/'sources/manifest.json').read_text())['sources']
errors=[];warnings=[];checks=[]
def check(name,ok,info=''):
 checks.append({'check':name,'result':'PASS' if ok else 'FAIL','detail':info})
 if not ok:errors.append(name+': '+info)
check('at_least_5_distinct_sources',len(M)>=5 and len({x['url'] for x in M})==len(M),f'count={len(M)}')
check('unique_source_ids',len({x['id'] for x in M})==len(M))
for s in M:
 check('metadata_'+s['id'],all(s.get(k) for k in ['id','title','publisher','url','accessed_at','sections','local_path']),s['title'])
 check('source_card_'+s['id'],(P/s['local_path']).is_file())
 C=(P/s['local_path']).read_text(encoding='utf8')
 check('source_location_'+s['id'],'來源定位' in C and 'http' in C)
wiki=P/'wiki'
idx=(wiki/'index.md').read_text(encoding='utf8')
concepts=list((wiki/'concepts').glob('*.md'))
check('concept_count',len(concepts)==6,str(len(concepts)))
for f in concepts:
 content=f.read_text(encoding='utf8')
 ids=re.findall(r'SRC-\d{3}',content.split('---',2)[1] if content.startswith('---') else '')
 check('frontmatter_'+f.stem,'topic_id:' in content and 'source_ids:' in content and 'last_checked_at:' in content)
 check('source_refs_'+f.stem,bool(ids) and all(x in {a['id'] for a in M} for x in ids))
 check('indexed_'+f.stem,f'concepts/{f.name}' in idx)
 check('source_card_links_'+f.stem,all((wiki/'sources'/f'{x.lower()}.md').exists() for x in ids))
# independent valuation arithmetic
F,c,m,N=1000,.04,1,5
price=lambda y: sum(F*c/m/(1+y/m)**t for t in range(1,N+1))+F/(1+y/m)**N
p3,p4,p5=price(.03),price(.04),price(.05)
check('price_yield_monotonic',p3>p4>p5,f'{p3:.4f}>{p4:.4f}>{p5:.4f}')
check('par_at_coupon_rate',abs(p4-1000)<1e-8,f'{p4:.6f}')
cf=[40,40,40,40,1040]
mac=sum((t+1)*x/(1.04**(t+1)) for t,x in enumerate(cf))/p4
modified=mac/1.04
check('duration_consistency',0<modified<mac<5 and abs(modified-(-((price(.040001)-price(.039999))/.000002)/p4))<1e-7,f'mac={mac:.8f},modified={modified:.8f}')
report={'generated_at':'2026-11-14','scope':'Gate A structural / Gate B numerical smoke tests only','source_cards':len(M),'concept_pages':len(concepts),'passed':sum(c['result']=='PASS' for c in checks),'failed':len(errors),'warnings':['Web full-text snapshots were not saved; claims require source-semantic spot check before final publication.','External link live availability is confirmed through web browsing, not locally reproducible by this script.','Current Yield source was augmented with SEC glossary SRC-008; source-semantic spot checks are still narrower than a full editorial audit.'], 'example':{'face_value':F,'coupon_rate':c,'payments_per_year':m,'remaining_periods':N,'prices':{'3%':p3,'4%':p4,'5%':p5},'macaulay_duration_years':mac,'modified_duration':modified},'checks':checks,'errors':errors}
(P/'logs/runs/2026-11-14-lint-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps({k:report[k] for k in ['source_cards','concept_pages','passed','failed','example','warnings']},ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
