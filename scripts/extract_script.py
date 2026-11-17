#!/usr/bin/env python3
"""Extract executable inline JavaScript, ignoring JSON-LD and other data scripts."""
from pathlib import Path
from html.parser import HTMLParser

class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script = False
        self.chunks = []
        self.scripts = []
    def handle_starttag(self, tag, attrs):
        if tag != "script":
            return
        attrs = dict(attrs)
        self.in_script = not attrs.get("src") and attrs.get("type", "").lower() not in ("application/ld+json", "application/json")
        self.chunks = []
    def handle_data(self, data):
        if self.in_script:
            self.chunks.append(data)
    def handle_endtag(self, tag):
        if tag == "script" and self.in_script:
            self.scripts.append("".join(self.chunks))
            self.in_script = False

markup = (Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
parser = InlineScripts()
parser.feed(markup)
assert len(parser.scripts) == 1, f"homepage should contain exactly 1 executable inline script (got {len(parser.scripts)})"
Path("/tmp/ai-era-check-script.js").write_text(parser.scripts[0], encoding="utf-8")
print("Extracted homepage JavaScript; schema.org JSON-LD excluded")
