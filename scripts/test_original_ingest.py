#!/usr/bin/env python3
"""Create local synthetic sources and exercise the pipeline; not a real web fetch."""
from pathlib import Path
import subprocess, sys, json
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tests/fixtures/source-html'; FIX.mkdir(parents=True,exist_ok=True)
for n in range(1,7):
    paras=[]
    for k in range(5):
        paras.append(f'<h2 id="section-{k}">Section {k+1}</h2><p>'+('This intentionally synthetic training document describes the mechanics of reading educational sources and recording their structure. It is not an excerpt from the specified website and contains no claims about the actual original document. ' * 4)+'</p>')
    (FIX/f'src-{n:03d}.html').write_text(f'<!doctype html><html><head><title>Synthetic {n}</title></head><body><main><h1>Fixture source {n}</h1>'+''.join(paras)+'</main></body></html>',encoding='utf-8')
r=subprocess.run([sys.executable,str(ROOT/'scripts/ingest_original_web.py'),'--fixtures'],capture_output=True,text=True)
print(r.stdout)
if r.returncode: print(r.stderr);sys.exit(r.returncode)
report=json.loads((ROOT/'logs/runs/ingest-original-fixtures-latest.json').read_text())
assert report['passed']==6 and report['actual_original_ingest_gate_pass'] is False and report['original_source_ingested_count']==0
print('TEST PASS: Parser processes 6 synthetic documents; real original ingest correctly remains 0')
