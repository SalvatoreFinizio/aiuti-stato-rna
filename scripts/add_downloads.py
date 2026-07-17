#!/usr/bin/env python3
# Inject the per-figure CSV download engine (assets/download.js) before </body>
# on every page. Idempotent. Run AFTER gen_pages.py (like add_i18n.py).
import re, glob, pathlib
ROOT = pathlib.Path("/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato")
BLOCK = '<!--DOWNLOAD--><script src="assets/download.js"></script><!--/DOWNLOAD-->'
for p in sorted(glob.glob(str(ROOT / "site" / "*.html"))):
    s = pathlib.Path(p).read_text(encoding="utf-8")
    s = re.sub(r'<!--DOWNLOAD-->.*?<!--/DOWNLOAD-->', '', s, flags=re.S)   # idempotent
    if '</body>' in s:
        s = s.replace('</body>', BLOCK + '\n</body>', 1)
        pathlib.Path(p).write_text(s, encoding="utf-8")
        print("  +", pathlib.Path(p).name)
