#!/usr/bin/env python3
from pathlib import Path
import re
html=(Path(__file__).resolve().parents[1]/'index.html').read_text('utf-8')
scripts=re.findall(r'<script\b[^>]*>([\s\S]*?)</script>',html,re.IGNORECASE)
assert len(scripts)==1,'homepage should contain exactly 1 inline script'
Path('/tmp/ai-era-check-script.js').write_text(scripts[0],encoding='utf-8')
print('Extracted homepage JavaScript')
