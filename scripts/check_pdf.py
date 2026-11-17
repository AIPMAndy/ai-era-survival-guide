#!/usr/bin/env python3
"""Fail publication for unreadable/unrenderable, incomplete or out-of-bounds PDF."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "pdf/ai-era-survival-guide.pdf"
EDITION = ROOT / "pdf/edition.json"
REPORT = ROOT / "pdf/qa-report.json"
PREVIEWS = ROOT / "pdf-qa"

def check() -> None:
    edition = json.loads(EDITION.read_text(encoding="utf-8"))
    binary = PDF.read_bytes()
    assert hashlib.sha256(binary).hexdigest() == edition["sha256"], "Edition SHA mismatch"
    doc = fitz.open(stream=binary, filetype="pdf")
    assert not doc.is_encrypted, "PDF is encrypted"
    assert 18 <= len(doc) <= 400, f"Unexpected page count: {len(doc)}"
    toc = doc.get_toc()
    assert len(toc) >= 10, f"Bookmarked chapter navigation missing ({len(toc)})"
    text_parts, links, bad_pages, empty_pages = [], 0, [], []
    PREVIEWS.mkdir(exist_ok=True)
    sample_pages = {0, len(doc)//2, len(doc)-1}
    for number, page in enumerate(doc):
        text = page.get_text("text")
        text_parts.append(text)
        if number and len(text.strip()) < 4:
            empty_pages.append(number+1)
        links += len(page.get_links())
        for block in page.get_text("blocks"):
            if len(block) < 5 or not str(block[4]).strip():
                continue
            rect = fitz.Rect(block[:4])
            if (rect.x0 < -2 or rect.y0 < -2 or
                rect.x1 > page.rect.width + 2 or rect.y1 > page.rect.height + 2):
                bad_pages.append(number+1)
        # Every page has to rasterize successfully, not only selected samples.
        page.get_pixmap(matrix=fitz.Matrix(.7,.7), alpha=False)
        if number in sample_pages:
            page.get_pixmap(matrix=fitz.Matrix(1.7,1.7), alpha=False).save(
                PREVIEWS / f"page-{number+1:03d}.png")
    full_text = "\n".join(text_parts)
    for needle in ("AI 酋长 Andy", "AIPMAndy", "2027", "2028", "2029", "岗位", "来源"):
        assert needle in full_text, f"Required text lost from PDF: {needle}"
    assert len(full_text) >= 16000, f"Text coverage too small: {len(full_text)}"
    assert links >= 6, f"Insufficient PDF clickable links: {links}"
    assert not empty_pages, f"Unexpected blank pages: {empty_pages}"
    assert not bad_pages, f"Text outside page bounds: {sorted(set(bad_pages))}"
    report = {
        "status": "automatic_text_and_raster_qa_passed",
        "pages": len(doc), "bookmarks": len(toc), "links": links,
        "characters": len(full_text), "rasterized_pages": len(doc),
        "pdf_sha256": edition["sha256"],
        "human_high_magnification_review": "PENDING",
        "ios_android_real_device_review": "PENDING",
        "source_policy_review": "PENDING",
        "source_files": edition["source_files"],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("PDF QA PASS", json.dumps(report, ensure_ascii=False))
    doc.close()

if __name__ == "__main__":
    check()
