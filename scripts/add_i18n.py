#!/usr/bin/env python3
# Inject the IT/EN toggle scripts (assets/i18n_dict.js + assets/i18n.js) before
# </body> on every page. Idempotent. Run AFTER gen_pages.py.
import re, glob, pathlib
ROOT = pathlib.Path("/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato")
BLOCK = ('<!--I18N--><script src="assets/i18n_dict.js"></script>'
         '<script src="assets/i18n.js"></script><!--/I18N-->')
for p in sorted(glob.glob(str(ROOT / "site" / "*.html"))):
    s = pathlib.Path(p).read_text(encoding="utf-8")
    s = re.sub(r'<!--I18N-->.*?<!--/I18N-->', '', s, flags=re.S)   # idempotent
    if '</body>' in s:
        s = s.replace('</body>', BLOCK + '\n</body>', 1)
        pathlib.Path(p).write_text(s, encoding="utf-8")
        print("  +", pathlib.Path(p).name)
