#!/usr/bin/env python3
"""Check source content, Markdown links, HTML local paths, SVG structure and product consistency.
No third-party dependencies: safe to run in GitHub Actions.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse
import re, struct, sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
errors=[]
required=['README.md','README_EN.md','GUIDE.md','QUICKSTART.md','index.html','article.html','PUBLISH.md','docs/SOURCES.md','docs/07-seven-days.md','docs/08-thirty-days.md','docs/09-ninety-days.md','docs/FAQ.md','prompts/README.md','templates/README.md','CONTRIBUTING.md','LICENSE-CODE','LICENSE-CONTENT','assets/wechat-cover-900x383.png','.github/workflows/check.yml','docs/START-HERE.md','docs/ADVERSARIAL_AUDIT.md','docs/15-evaluation-protocol.md','docs/11-career-defense.md','docs/19-policy-and-opportunities.md','docs/20-real-world-cases.md','docs/21-why-change.md','templates/policy-check.md','templates/verified-case-card.md','templates/job-market-evidence.md','labs/feedback-24.csv','labs/feedback-24-gold.csv','lab.html','scripts/grade_feedback.py','tests/test_grader.py']
for f in required:
 if not (ROOT/f).is_file(): errors.append('Missing '+f)
if errors:
 for x in errors:print('ERROR:',x)
 sys.exit(1)
def path_ok(pathname,raw):
 raw=raw.strip()
 if not raw or raw.startswith(('#','mailto:','data:','javascript:','tel:','//')):return
 u=urlparse(raw)
 if u.scheme in ('http','https'):return
 if u.scheme:errors.append(f'Unexpected URL scheme {pathname}: {raw}');return
 if not u.path:return
 dest=(pathname.parent/unquote(u.path)).resolve()
 try:dest.relative_to(ROOT.resolve())
 except ValueError:errors.append(f'Link escapes project in {pathname.relative_to(ROOT)}: {raw}');return
 if not dest.exists():errors.append(f'Broken link {pathname.relative_to(ROOT)} → {raw}')
for file in ROOT.rglob('*.md'):
 txt=file.read_text(encoding='utf8')
 # standard inline links/images, full url links with parentheses should use angle brackets
 for raw in re.findall(r'!?\[[^\]\n]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)',txt):path_ok(file,raw)
class Scan(HTMLParser):
 def __init__(self,path):super().__init__();self.path=path;self.scripts=0;self.images=0
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  for att in ('src','href'):
   if att in attrs:path_ok(self.path,attrs[att])
  if tag=='script':self.scripts+=1
  if tag=='img':self.images+=1
for file in ROOT.rglob('*.html'):
 txt=file.read_text(encoding='utf8')
 scan=Scan(file);scan.feed(txt)
 if re.search(r'text-align\s*:\s*(start|end)\b',txt,re.I):errors.append('Nonstandard text align '+str(file.relative_to(ROOT)))
 if file == ROOT/'index.html' and scan.scripts!=1:errors.append('Homepage requires one interactive script')
 if file.name=='article.html' and scan.images<5:errors.append('Article missing diagrams')
 if file.name=='lab.html' and scan.scripts!=1:errors.append('Lab page requires one evaluation script')
for file in (ROOT/'assets').glob('*.svg'):
 try:ET.fromstring(file.read_text(encoding='utf8'))
 except ET.ParseError as e:errors.append('SVG invalid '+file.name+': '+str(e))
with (ROOT/'assets/wechat-cover-900x383.png').open('rb') as f:
 head=f.read(24)
if head[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',head[16:24])!=(900,383):errors.append('Invalid 900x383 WeChat PNG cover')
if len(list((ROOT/'prompts').glob('[0-9][0-9]-*.md')))!=12:errors.append('Prompt count must be 12')
if len(list((ROOT/'templates').glob('*.md')))!=16:errors.append('Template count must be 15 + README')
if len(list((ROOT/'examples').glob('*.md')))!=7:errors.append('Need 7 role examples including PM')
guide=(ROOT/'GUIDE.md').read_text(encoding='utf8')
for word in ['岗位','任务','主业','副业','2027','2028','2029','失业','面试','咨询']:
 if word not in guide:errors.append('Guide missing '+word)
if 'AI时代不被淘汰保姆级攻略' not in (ROOT/'README.md').read_text(encoding='utf8'):errors.append('README title mismatch')
if len(re.findall(r'^## [一二三四五六七八九十]+、',guide,re.M))!=11:errors.append('Expected 11 numbered guide chapters')
import csv
with (ROOT/'labs/feedback-24.csv').open(encoding='utf-8-sig',newline='') as f:sample=list(csv.DictReader(f))
with (ROOT/'labs/feedback-24-gold.csv').open(encoding='utf-8-sig',newline='') as f:gold=list(csv.DictReader(f))
if len(sample)!=24 or len(gold)!=24:errors.append('Expected 24 rows in both lab sample and gold')
if [r['id'] for r in sample]!=[str(i) for i in range(1,25)]:errors.append('Lab IDs must be 1..24 in order')
if {r['id'] for r in gold}!={str(i) for i in range(1,25)}:errors.append('Gold IDs must be 1..24')
for f in ['assets/cover-v6.svg'] + [f'assets/latest-{i:02d}.svg' for i in range(1,10)]:
 if not (ROOT/f).is_file():errors.append('Missing new illustration '+f)
if errors:
 print('FAIL: '+str(len(errors))+' problem(s)')
 for e in errors:print(' - '+e)
 sys.exit(1)
print('PASS: local links, latest 11-chapter guide, new cover and 9 SVG, old tool assets, datasets, policy and cases')
