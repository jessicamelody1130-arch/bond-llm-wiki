#!/usr/bin/env python3
"""Reproducible local ingest of reviewed *paraphrase notes*, NOT full webpage text.
Offline: this never contacts the external source, so a pass does not prove web page access.
"""
import json,hashlib,sys,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest={s['id']:s for s in json.loads((ROOT/'sources/manifest.json').read_text('utf-8'))['sources']}
source_dir=ROOT/'raw/curated'
out_dir=ROOT/'sources/ingested'
out_dir.mkdir(exist_ok=True)
checks=[];events=[];failed=[]
for f in sorted(source_dir.glob('src-*.json')):
    raw=f.read_bytes(); source_hash=hashlib.sha256(raw).hexdigest()
    try:
        obj=json.loads(raw);sid=obj['source_id']
        assert sid in manifest, 'source ID not in manifest'
        assert obj['source_url']==manifest[sid]['url'], 'URL mismatch with manifest'
        assert obj['input_type']=='curated_source_notes' and obj['full_original_text_acquired'] is False,'invalid source type'
        claims=obj['claim_records']; assert len(claims)>=2,'insufficient source notes'
        sections=set(manifest[sid]['sections'])
        # Section headings should be present among source's stated sections (case-insensitive match allowed).
        for c in claims:
            assert all(c.get(k) for k in ['claim_id','source_section','concept_tag','paraphrase_zh','scope_note']), 'missing claim field'
            assert len(c['paraphrase_zh'])>=35,'note too brief to count as useful knowledge'
            assert c['source_section'] in sections,'section not indexed in manifest: '+c['source_section']
        normalized={'source_id':sid,'input_type':obj['input_type'],'source_url':obj['source_url'],'input_sha256':source_hash,'full_original_text_acquired':False,'claims':claims,'claimed_sections':sorted({c['source_section'] for c in claims}), 'validation_scope':'local_integrity_only; semantic assertions manually spot-checked against cited public sections'}
        target=out_dir/(sid.lower()+'.json')
        target.write_text(json.dumps(normalized,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        checks.append({'source_id':sid,'status':'PASS','claim_count':len(claims),'input_sha256':source_hash,'output':str(target.relative_to(ROOT))})
        events.extend({'source_id':sid,'claim_id':c['claim_id'],'source_section':c['source_section'],'concept_tag':c['concept_tag']} for c in claims)
    except Exception as e:
        failed.append({'file':f.name,'reason':str(e)});checks.append({'source_id':f.stem.upper(),'status':'FAIL','reason':str(e)})
passed=sum(x['status']=='PASS' for x in checks)
report={'stage':'curated_source_notes_ingest','run_date':'2026-11-14','source_count_passed':passed,'claim_count':len(events),'gate_a_local_notes_passed':passed>=5 and not failed,'external_source_retrieval_in_this_run':False,'full_original_text_ingest_count':0,'checks':checks,'errors':failed,'limits':['Only human-reviewed paraphrase notes were ingested; article full-text retrieval was not completed.','The local pipeline verifies structural integrity and reproducibility, not full semantic equivalence with all source paragraphs.','For strict original-text ingest requirement, obtain permitted source texts or OpenStax-licensed fulltext separately.']}
logs=ROOT/'logs/runs';logs.mkdir(parents=True,exist_ok=True)
(logs/'2026-11-14-curated-ingest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(logs/'2026-11-14-claim-map.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['source_count_passed','claim_count','gate_a_local_notes_passed','full_original_text_ingest_count','errors']},ensure_ascii=False,indent=2))
sys.exit(0 if report['gate_a_local_notes_passed'] else 1)
