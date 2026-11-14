#!/usr/bin/env python3
"""Index-based, auditable retrieval. No LLM answering from memory."""
from pathlib import Path
import json,re,datetime,sys
ROOT=Path(__file__).resolve().parents[1]
INDEX=(ROOT/'wiki/index.md').read_text(encoding='utf-8')
SOURCES={s['id']:s for s in json.loads((ROOT/'sources/manifest.json').read_text(encoding='utf-8'))['sources']}
QUERIES=[
 {'id':'Q1','question':'債券價格如何決定？','topics':['bond-pricing','numeric-examples'],'required':['SRC-006']},
 {'id':'Q2','question':'YTM 上升時價格為什麼下降？','topics':['interest-rate-risk','bond-pricing'],'required':['SRC-004','SRC-006']},
 {'id':'Q3','question':'Macaulay 與 Modified Duration 有何差異？','topics':['duration'],'required':['SRC-007']},
]
def lookup(q):
 hits=[];errors=[]
 for topic in q['topics']:
  rel='wiki/concepts/'+topic+'.md'
  if f'concepts/{topic}.md' not in INDEX:errors.append('not_indexed:'+topic);continue
  p=ROOT/rel
  if not p.exists():errors.append('missing:'+rel);continue
  body=p.read_text(encoding='utf-8')
  ids=list(dict.fromkeys(re.findall(r'SRC-\d{3}',re.search(r'^source_ids:\s*\[(.*?)\]',body,re.M).group(1)))) if re.search(r'^source_ids:\s*\[(.*?)\]',body,re.M) else []
  for sid in ids:
   if sid not in SOURCES or not (ROOT/SOURCES[sid]['local_path']).exists():errors.append('unresolved:'+sid)
  sections=re.findall(r'^## (.+)$',body,re.M)
  hits.append({'topic':topic,'wiki_path':rel,'source_ids':ids,'sections':sections,'status':re.search(r'^status:\s*(.+)$',body,re.M).group(1) if re.search(r'^status:\s*(.+)$',body,re.M) else 'unknown'})
 covered=set(x for h in hits for x in h['source_ids'])
 for sid in q['required']:
  if sid not in covered:errors.append('required_source_not_found:'+sid)
 return {'query_id':q['id'],'question':q['question'],'retrieved':hits,'source_ids':sorted(covered),'result':'PASS' if not errors else 'FAIL','issues':errors,'limitation':'結構化來源卡與 Wiki 草稿，不等於已對完整原文完成逐條語意驗證'}
if __name__=='__main__':
 results=[lookup(q) for q in QUERIES]
 out={'run_date':'2026-11-14','method':'Read wiki/index.md then topic Markdown then source manifest/cards','questions':results,'passed':sum(x['result']=='PASS' for x in results),'failed':sum(x['result']=='FAIL' for x in results)}
 path=ROOT/'logs/runs/2026-11-14-query-tests.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 for q in results:print(q['query_id'],q['result'],','.join(h['topic'] for h in q['retrieved']),','.join(q['source_ids']))
 sys.exit(bool(out['failed']))
