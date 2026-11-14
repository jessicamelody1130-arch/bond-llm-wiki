#!/usr/bin/env python3
"""Ingest HTML pages manually saved from original public source websites.

Use browser 'Save Page As -> HTML only' for sources in sources/manifest.json,
name them src-001.html etc, then run this script. Saved HTML is not bundled
in the publicly published project. A successful parser result establishes
an input file was parsed, not that its provenance is cryptographically proven.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
from ingest_original_web import parse_page

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_HASHES = {hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'tests/fixtures/source-html').glob('*.html')}


def ingest(input_dir: Path, report_path: Path, min_sources: int = 5):
    sources = json.loads((ROOT/'sources/manifest.json').read_text(encoding='utf-8'))['sources']
    archive_dir = ROOT/'raw/private-original-archive'
    archive_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for source in sources:
        sid = source['id']
        fp = input_dir/(sid.lower()+'.html')
        if not fp.exists():
            results.append({'id':sid,'status':'SKIP','reason':'HTML source file not provided'})
            continue
        try:
            raw = fp.read_bytes()
            if hashlib.sha256(raw).hexdigest() in FIXTURE_HASHES:
                raise ValueError('Synthetic test fixture is not eligible as an original source')
            if len(raw) < 1000:
                raise ValueError('Saved page too short to be a complete document')
            page = parse_page(raw, source['url'])
            result = {'id':sid,'status':'PASS','mode':'locally_saved_html',
                      'original_url_claimed':source['url'],
                      'sha256_html':hashlib.sha256(raw).hexdigest(),
                      'bytes':len(raw), 'word_count':page['word_count'],
                      'paragraph_count':page['paragraph_count'],
                      'note':'Content parsed from a user-supplied local HTML file; origin must be checked against source URL.'}
            page.update({'source_id':sid,'mode':'locally_saved_html',
                         'html_sha256':result['sha256_html'],
                         'retrieval_method':'Saved manually in browser, HTML only',
                         'provenance_verified':False,
                         'copyright_note':'Private research copy. Do not publish third-party complete text.'})
            (archive_dir/(sid.lower()+'.json')).write_text(json.dumps(page,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        except Exception as exc:
            result = {'id':sid,'status':'FAIL','reason':type(exc).__name__+': '+str(exc)}
        results.append(result)
    count = sum(r['status']=='PASS' for r in results)
    report = {'executed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'mode':'locally_saved_html', 'parsed_sources':count,
              'minimum_required':min_sources, 'gate_a_pass':count>=min_sources,
              'provenance_verified':False,
              'warning':'Successful local parsing alone does not prove HTML is the original source. Compare headings/content to source website.',
              'results':results}
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir',default=str(ROOT/'raw/saved-html'))
    ap.add_argument('--report',default=str(ROOT/'logs/runs/ingest-saved-html-latest.json'))
    ap.add_argument('--min-sources',type=int,default=5)
    args=ap.parse_args()
    r=ingest(Path(args.input_dir),Path(args.report),args.min_sources)
    for x in r['results']:
        print(x['id'],x['status'],x.get('word_count',x.get('reason','')))
    print(f"Result: {r['parsed_sources']}/{len(r['results'])}, gate_a_pass={r['gate_a_pass']}")
    return 0 if r['gate_a_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
