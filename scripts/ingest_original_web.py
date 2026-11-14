#!/usr/bin/env python3
"""Retrieve and parse actual webpages into private local source archives.

Default mode fetches the exact URLs in sources/manifest.json.
--fixtures is ONLY a pipeline self-test on synthetic HTML, NEVER real ingestion.
A URL string or curated summary is not accepted as original-source input.
Do not publish archived third-party article text in GitHub Pages.
"""
import argparse, datetime, hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'sources/manifest.json'
MIN_WORDS = 120
MIN_PARAGRAPHS = 3


def parse_page(raw: bytes, url: str):
    soup = BeautifulSoup(raw, 'html.parser')
    for tag in soup.select('script,style,nav,footer,header,aside,form,noscript,svg,iframe'):
        tag.decompose()
    title_tag = soup.find('h1') or soup.find('title')
    title = title_tag.get_text(' ', strip=True) if title_tag else ''
    main = soup.find('main') or soup.find('article') or soup.find(attrs={'role':'main'}) or soup.body
    if not main:
        raise ValueError('No main document text')
    blocks = []
    for el in main.find_all(['h1','h2','h3','h4','p','li'], recursive=True):
        # Avoid twice counting list wrappers and navigation-style tiny snippets.
        if el.name == 'li' and el.find(['p','li']):
            continue
        value = re.sub(r'\s+', ' ', el.get_text(' ', strip=True)).strip()
        if len(value) < (5 if el.name.startswith('h') else 24):
            continue
        if len(value) > 1800:
            value = value[:1800]
        blocks.append({'kind':'heading' if el.name.startswith('h') else 'text',
                       'tag':el.name, 'text':value,
                       'anchor':el.get('id') or (el.find_parent(attrs={'id':True}).get('id') if el.find_parent(attrs={'id':True}) else None)})
    # De-duplicate adjacent identical blocks from nested markup.
    filtered=[]
    for b in blocks:
        if not filtered or b['text'] != filtered[-1]['text']:
            filtered.append(b)
    word_count = sum(len(b['text'].split()) for b in filtered if b['kind']=='text')
    para_count = sum(b['tag']=='p' for b in filtered)
    if word_count < MIN_WORDS or para_count < MIN_PARAGRAPHS:
        raise ValueError(f'Insufficient extracted body: {word_count} words, {para_count} paragraphs; likely blocked, truncated or wrong page')
    if not title:
        raise ValueError('Missing article heading')
    return {'title':title,'url':url,'word_count':word_count,'paragraph_count':para_count,'blocks':filtered}


def ingest_one(src, mode, fixture_dir, private_dir, timeout):
    sid=src['id']; url=src['url']; parsed=urlparse(url)
    if parsed.scheme != 'https' or not parsed.netloc:
        raise ValueError('Manifest URL must be HTTPS')
    if mode=='fixtures':
        fp=fixture_dir/f'{sid.lower()}.html'
        if not fp.exists():
            raise FileNotFoundError(f'Synthetic test fixture missing: {fp.name}')
        raw=fp.read_bytes()
        effective_url=url
    else:
        res=requests.get(url,timeout=timeout,headers={'User-Agent':'Mozilla/5.0 (educational source research; contact site for access policy)'},allow_redirects=True)
        res.raise_for_status()
        effective_url=res.url
        if not (res.headers.get('Content-Type','').lower().startswith('text/html')):
            raise ValueError(f'Not HTML: {res.headers.get("Content-Type")}')
        if urlparse(effective_url).scheme != 'https':
            raise ValueError('Redirected to non-HTTPS URL')
        raw=res.content
    record=parse_page(raw,effective_url)
    record.update({'source_id':sid,'requested_url':url,'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'mode':mode,'sha256_raw':hashlib.sha256(raw).hexdigest(),'byte_count':len(raw),
                   'rights_note':'Local research copy only; do not republish third-party full text.'})
    # In fixture mode nothing is actual source text; archive separately.
    target=(private_dir / (sid.lower()+'.json'))
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'id':sid,'status':'PASS','mode':mode,'effective_url':effective_url,
            'word_count':record['word_count'],'paragraph_count':record['paragraph_count'],
            'sha256_raw':record['sha256_raw'],'archive':str(target.relative_to(ROOT))}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fixtures',action='store_true',help='TEST ONLY: use synthetic local HTML; NEVER counts as original-source ingest')
    ap.add_argument('--min-sources',type=int,default=5)
    ap.add_argument('--timeout',type=int,default=18)
    ap.add_argument('--limit',type=int,default=6)
    args=ap.parse_args()
    sources=json.loads(MANIFEST.read_text('utf-8'))['sources'][:args.limit]
    mode='fixtures' if args.fixtures else 'live'
    fixture_dir=ROOT/'tests/fixtures/source-html'
    private_dir=ROOT/'raw/private-fixture-archive' if args.fixtures else ROOT/'raw/private-original-archive'
    rows=[]
    for src in sources:
        try:
            row=ingest_one(src,mode,fixture_dir,private_dir,args.timeout)
        except Exception as exc:
            row={'id':src['id'],'status':'FAIL','mode':mode,'reason':f'{type(exc).__name__}: {exc}'}
        rows.append(row)
        print(f'{row["id"]} {row["status"]}: {row.get("word_count",row.get("reason"))}')
    passed=sum(x['status']=='PASS' for x in rows)
    report={'run_at':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'mode':mode,
            'source_count':len(rows),'passed':passed,'required':args.min_sources,
            'original_source_ingested_count':passed if mode=='live' else 0,
            'gate_a_pass':passed>=args.min_sources,
            'actual_original_ingest_gate_pass':mode=='live' and passed>=args.min_sources,
            'warning':'Fixture-mode pass only demonstrates the parser; it does not indicate actual original sources were retrieved.' if args.fixtures else None,
            'results':rows}
    report_path=ROOT/'logs/runs'/f'ingest-original-{mode}-latest.json'
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Summary {passed}/{len(rows)}; original-source evidence count={report["original_source_ingested_count"]}; report={report_path.relative_to(ROOT)}')
    return 0 if report['gate_a_pass'] else 1

if __name__=='__main__':
    sys.exit(main())
