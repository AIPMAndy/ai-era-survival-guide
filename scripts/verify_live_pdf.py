#!/usr/bin/env python3
"""Independent public GitHub Pages / PDF SHA release verification.

--local: verify repository source + semantic SEO/GEO + PDF without network.
--live: GET actual Pages URLs and byte-compare to checked-out release.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://aipmandy.github.io/ai-era-survival-guide/"
PDF = "pdf/ai-era-survival-guide.pdf"
CHECK = ["index.html", "article.html", "lab.html", "docs/SOURCES.html", "docs/START-HERE.html", "robots.txt", "sitemap.xml", PDF]
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def local() -> dict:
    edition = json.loads((ROOT/"pdf/edition.json").read_text(encoding="utf-8"))
    qa = json.loads((ROOT/"pdf/qa-report.json").read_text(encoding="utf-8"))
    binary = (ROOT/PDF).read_bytes()
    assert sha(binary) == edition["sha256"] == qa["pdf_sha256"], "PDF release mismatch"
    assert qa["status"] == "automatic_text_and_raster_qa_passed"
    assert qa["rasterized_pages"] == qa["pages"] >= 18
    assert qa["human_high_magnification_review"] == "PENDING", "Do not claim human review"
    index = (ROOT/"index.html").read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{BASE}">' in index
    assert 'href="pdf/ai-era-survival-guide.pdf"' in index
    assert "AIPMAndy" in index and "https://metaver.vip/services" in index
    assert "https://www.a6no1.cn/" in index
    block = re.search(r'<script type="application/ld\\+json">(.+?)</script>', index, re.S)
    if not block:
        # JSON-LD type marker must be present, not merely any script tag.
        block = re.search(r'<script type="application/ld[^"]*json">(.+?)</script>', index, re.S)
    assert block, "No homepage JSON-LD"
    graph = json.loads(block.group(1))
    books = [item for item in graph.get("@graph", []) if item.get("@type")=="Book" and item.get("url")==BASE+PDF]
    assert len(books)==1 and books[0]["url"] == BASE+PDF
    assert books[0]["author"]["name"] == "AI 酋长 Andy"
    assert books[0]["publisher"]["url"] == "https://www.a6no1.cn/"
    robot = (ROOT/"robots.txt").read_text(encoding="utf-8")
    assert f"Sitemap: {BASE}sitemap.xml" in robot
    sitemap = ET.fromstring((ROOT/"sitemap.xml").read_text(encoding="utf-8"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [x.text for x in sitemap.findall("s:url/s:loc", ns)]
    required = [BASE, BASE+"article.html", BASE+"lab.html", BASE+"docs/SOURCES.html", BASE+"docs/START-HERE.html"]
    assert len(urls)==len(set(urls)), "Duplicate sitemap location"
    assert all(u in urls for u in required), f"Missing self-canonical sitemap pages: {set(required)-set(urls)}"
    for rel in ["article.html", "lab.html", "docs/SOURCES.html", "docs/START-HERE.html"]:
        page = (ROOT/rel).read_text(encoding="utf-8")
        assert f'<link rel="canonical" href="{BASE+rel}">' in page, f"Wrong canonical {rel}"
        assert f'<meta property="og:url" content="{BASE+rel}">' in page, f"Wrong OG URL {rel}"
        schemas = re.findall(r'<script type="application/ld[^"]*json">(.+?)</script>', page, re.S)
        assert schemas and any(
            node.get("@type") == "WebPage" and node.get("url") == BASE+rel
            for schema in schemas for node in json.loads(schema).get("@graph", [])
        ), f"Missing WebPage schema {rel}"
    return {"pages": qa["pages"], "bookmarks": qa["bookmarks"], "links": qa["links"], "pdf_sha256": edition["sha256"], "status":"repository_preflight_pass"}
def fetch(relative: str) -> bytes:
    uri=BASE+relative
    request=Request(uri,headers={"User-Agent":"Xingjue-AIEra-Site-QA/1.0"})
    with urlopen(request,timeout=30) as response:
        assert response.status==200, (relative,response.status)
        assert response.geturl()==uri, f"Redirect for {relative}: {response.geturl()}"
        return response.read()
def live() -> dict:
    report=local()
    results={}
    for relative in CHECK:
        local_data=(ROOT/relative).read_bytes()
        remote=fetch(relative)
        assert sha(local_data)==sha(remote), f"Live {relative} differs from current repo SHA"
        results[relative]=sha(remote)
    report.update({"status":"live_pages_sha_verified","url":BASE,"resources":results})
    return report
if __name__ == "__main__":
    if "--local" in sys.argv:
        result=local()
    elif "--live" in sys.argv:
        for attempt in range(1,21):
            try:
                result=live()
                break
            except Exception as exc:
                if attempt==20:
                    raise
                print(f"Pages propagation {attempt}/20: {exc}",flush=True)
                time.sleep(8)
    else:
        raise SystemExit("Use --local or --live explicitly")
    (ROOT/"live-qa.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PASS",json.dumps({k:v for k,v in result.items() if k!="resources"},ensure_ascii=False))
