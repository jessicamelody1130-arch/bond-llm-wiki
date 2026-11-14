#!/usr/bin/env python3
"""Actual Chromium DOM/JS interaction test without navigating blocked file/localhost URLs.
Browser executes in a synthetic about:blank document with repository HTML/CSS/JS injected.
This does NOT verify network paths, GitHub Pages hosting, or browser navigation to deployed URLs.
"""
import json, datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'slides'
checks=[]
def check(name,actual,expected=True):
    ok=actual==expected
    checks.append({'check':name,'pass':ok,'observed':str(actual),'expected':str(expected)})
    if not ok: print('FAIL',name,actual,expected)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1280,'height':800})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content((D/'index.html').read_text(encoding='utf-8'),wait_until='domcontentloaded')
    page.add_style_tag(content=(D/'style.css').read_text(encoding='utf-8'))
    page.add_script_tag(content=(D/'script.js').read_text(encoding='utf-8'))
    count=lambda:page.locator('#progressLabel').inner_text()
    check('initial slide',count(),'01 / 10')
    check('initial active slide',page.locator('.slide.active').count(),1)
    check('previous disabled at start',page.locator('#prev').is_disabled())
    page.locator('#next').click()
    check('next button',count(),'02 / 10')
    page.keyboard.press('ArrowRight')
    check('keyboard right after button focus',count(),'03 / 10')
    page.keyboard.press('ArrowLeft')
    check('keyboard left',count(),'02 / 10')
    page.locator('.brand').click()
    page.wait_for_timeout(150)
    check('return-home hash link',count(),'01 / 10')
    page.evaluate("location.hash='#7'")
    page.wait_for_timeout(100)
    check('manual hash nav',count(),'07 / 10')
    check('SVG curve renders',page.locator('#priceChart polyline').count(),1)
    check('SVG data markers render',page.locator('#priceChart circle').count(),3)
    page.locator('#next').click()
    check('next 8',count(),'08 / 10')
    page.locator('#next').click()
    check('quiz slide visible',count(),'09 / 10')
    page.locator('#quiz button').click()
    check('incomplete quiz message','未作答' in page.locator('#quizResult').inner_text())
    page.locator('input[name=q1][value=b]').check()
    page.locator('input[name=q2][value=a]').check()
    page.locator('input[name=q3][value=c]').check()
    page.locator('#quiz button').click()
    check('3-of-3 quiz score','答對 3 / 3 題' in page.locator('#quizResult').inner_text())
    page.locator('input[name=q3][value=b]').check()
    page.locator('#quiz button').click()
    check('2-of-3 quiz score','答對 2 / 3 題' in page.locator('#quizResult').inner_text())
    page.locator('#next').click()
    check('last slide',count(),'10 / 10')
    check('next disabled at last',page.locator('#next').is_disabled())
    check('10 slides exist',page.locator('.slide').count(),10)
    check('JS runtime errors',len(errors),0)
    page.screenshot(path=str(ROOT/'logs/runs/chromium-slide10.png'),full_page=True)
    browser.close()
report={'date':'2026-11-14','method':'real Chromium headless, synthetic document via set_content and injected local CSS/JS','limits':'does not test navigation to file://, localhost or deployed GitHub Pages; those URLs are blocked by browser policy','passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks,'js_errors':errors}
out=ROOT/'logs/runs/2026-11-14-chromium-embedded.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f"CHROMIUM {report['passed']}/{report['total']} - {out}")
raise SystemExit(0 if report['passed']==report['total'] else 1)
