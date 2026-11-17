#!/usr/bin/env python3
"""Build the AI-era handbook PDF from the published Markdown sources.

No generated, anonymized or synthetic employment outcomes are added here.
Source document dates are not rewritten as 'verified today'.
"""
from __future__ import annotations
import hashlib
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit
import markdown
from weasyprint import HTML, CSS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pdf" / "ai-era-survival-guide.pdf"
MANIFEST = ROOT / "pdf" / "edition.json"
SOURCES = [
    "GUIDE.md",
    "docs/START-HERE.md",
    "docs/07-seven-days.md",
    "docs/08-thirty-days.md",
    "docs/09-ninety-days.md",
    "docs/11-career-defense.md",
    "docs/15-evaluation-protocol.md",
    "docs/19-policy-and-opportunities.md",
    "docs/20-real-world-cases.md",
    "docs/21-why-change.md",
    "docs/SOURCES.md",
    "docs/FAQ.md",
]
PROJECT = "https://github.com/AIPMAndy/ai-era-survival-guide"
WEBSITE = "https://aipmandy.github.io/ai-era-survival-guide/"
INTRO = """<section class="cover">
<div class="eyebrow">AI CHIEF ANDY / KNOWLEDGE EDITION</div>
<h1>AI 时代<br>不被淘汰</h1>
<p class="subtitle">2027—2029 中国职场应对攻略</p>
<p class="lead">30 类岗位的 AI 实操、主业升级、职业风险防线与行动计划。</p>
<div class="cover-rule"></div>
<p>作者：AI 酋长 Andy · 星觉科技</p>
<p>微信 AIPMAndy · <a href="https://metaver.vip/">个人官网</a> ·
<a href="https://www.a6no1.cn/">公司官网</a></p>
<p><a href="https://metaver.vip/services">职业咨询与 AI 陪跑服务</a> ·
<a href="https://github.com/AIPMAndy/ai-era-survival-guide">开源仓库 / 来源</a></p>
<p class="muted">免费公开版。职业判断与案例保留原文的证据级别、适用范围和日期；
历史来源不等于 2026-11-17 已完成政策重核。教学模拟不代表真实业务收入或录用结果。</p>
</section>"""
STYLES = """
@page { size: A5; margin: 17mm 15mm 19mm;
  @bottom-center { content: counter(page); font: 8pt 'Noto Sans CJK SC'; color: #666; }
}
@page:first { @bottom-center { content: none; } }
html { font-family: 'Noto Sans CJK SC', 'Noto Sans CJK', sans-serif; color: #1a2028; }
body { font-size: 9.4pt; line-height: 1.7; }
h1, h2, h3 { color: #111820; break-after: avoid; line-height: 1.3; }
h1 { font-size: 21pt; margin-top: 13mm; bookmark-level: 1; }
h2 { font-size: 15pt; border-bottom: 1px solid #c5cad0; margin: 9mm 0 3mm; padding-bottom: 2mm; bookmark-level: 2; }
h3 { font-size: 11pt; margin: 5mm 0 2mm; bookmark-level: 3; }
p { margin: 0 0 2.8mm; orphans: 3; widows: 3; }
a { color: #23486c; text-decoration: underline; text-decoration-thickness: .3pt; }
ul, ol { padding-left: 6mm; }
li { margin-bottom: 2mm; }
pre, code { font-family: monospace; font-size: 8pt; white-space: pre-wrap; overflow-wrap: anywhere; }
pre { padding: 3mm; background: #f1f3f5; }
blockquote { border-left: 2pt solid #a1aab3; margin: 4mm 0; padding-left: 3mm; color: #414a55; }
table { border-collapse: collapse; font-size: 7.8pt; width: 100%; table-layout: fixed; }
th, td { border: .4pt solid #d4d9de; padding: 1.5mm; overflow-wrap: anywhere; }
th { background: #f0f2f4; }
img { max-width: 100%; height: auto; }
.cover { break-after: page; padding: 25mm 0 10mm; }
.cover h1 { font-size: 37pt; line-height: 1.18; margin: 10mm 0; letter-spacing: -.5pt; }
.cover .eyebrow { font-size: 9pt; font-weight: 600; letter-spacing: 2pt; color: #64707a; }
.cover .subtitle { font-size: 15pt; margin: 0 0 10mm; font-weight: 600; }
.cover .lead { font-size: 12pt; line-height: 1.7; }
.cover-rule { background: #1a2028; width: 25mm; height: 1.2pt; margin: 15mm 0 8mm; }
.cover .muted { margin-top: 10mm; font-size: 8pt; color: #68727b; }
.section-divider { break-before: page; font-size: 8pt; letter-spacing: 1pt; color: #6c7884; }
.section-divider + h1 { margin-top: 5mm; }
"""
def localize_assets(markup: str, part: str) -> str:
    parent = Path(part).parent
    def link(m):
        uri = html.unescape(m.group(2))
        if not uri or uri.startswith(("#","http://","https://","mailto:","tel:","data:")):
            return m.group(0)
        target, fragment = (uri.split("#", 1) + [""])[:2]
        rel = (parent / unquote(target)).as_posix()
        if m.group(1) == "src":
            location = (ROOT / rel).resolve()
            if not location.is_relative_to(ROOT.resolve()) or not location.is_file():
                raise ValueError(f"Missing local PDF image in {part}: {uri}")
            absolute = location.as_uri()
        else:
            absolute = PROJECT + "/blob/main/" + quote(rel, safe="/") 
            if fragment:
                absolute += "#" + quote(fragment, safe="-_")
        return m.group(1) + '="' + html.escape(absolute, quote=True) + '"'
    return re.sub(r'(href|src)="([^"]+)"', link, markup)

def source_fingerprint() -> str:
    h = hashlib.sha256()
    h.update(Path(__file__).read_bytes())
    for name in SOURCES:
        p = ROOT / name
        if not p.is_file():
            raise FileNotFoundError(name)
        h.update(name.encode("utf-8") + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()

def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = source_fingerprint()
    if MANIFEST.exists() and OUTPUT.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if previous.get("source_sha256") == fingerprint and previous.get("sha256") == hashlib.sha256(OUTPUT.read_bytes()).hexdigest():
            print("Same verified source; reuse published PDF bytes.")
            return
    sections = [INTRO]
    for part in SOURCES:
        source = (ROOT / part).read_text(encoding="utf-8")
        rendered = markdown.markdown(source, extensions=["tables","fenced_code","toc","sane_lists"])
        rendered = localize_assets(rendered, part)
        sections.append('<div class="section-divider">SOURCE · ' + html.escape(part) + '</div>' + rendered)
    document = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>AI 时代不被淘汰 · AI 酋长 Andy</title></head><body>' + "\n".join(sections) + '</body></html>'
    HTML(string=document, base_url=ROOT.as_uri() + "/").write_pdf(str(OUTPUT), stylesheets=[CSS(string=STYLES)], presentational_hints=True, pdf_identifier=fingerprint[:32])
    data = OUTPUT.read_bytes()
    MANIFEST.write_text(json.dumps({
        "title": "AI 时代不被淘汰保姆级攻略",
        "author": "AI 酋长 Andy",
        "publisher": "星觉科技",
        "source_files": SOURCES,
        "source_sha256": fingerprint,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "website": WEBSITE,
        "pdf_url": WEBSITE + "pdf/ai-era-survival-guide.pdf",
        "contacts": {
            "wechat": "AIPMAndy",
            "personal": "https://metaver.vip/",
            "company": "https://www.a6no1.cn/",
            "services": "https://metaver.vip/services",
        },
        "evidence_policy": "Source dates are preserved; predictions and teaching simulations are not measured client outcomes.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Created", OUTPUT, len(data), "bytes", "source SHA", fingerprint)

if __name__ == "__main__":
    build()
