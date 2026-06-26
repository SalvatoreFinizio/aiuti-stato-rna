# Build pipeline

How the site's pages are generated. The site is a set of **self-contained static
HTML files** (data + JS inlined, no runtime fetch). `dashboard.html` ("Tutto in una
pagina") is the canonical source; the focused topic pages are **generated** from it.

> ⚠️ **Paths.** These scripts were written for one machine. They hardcode the repo
> root (`ROOT = .../aiuti_stato`), read large source files from `~/Library/.../Dropbox/...`,
> and use `/tmp/*.csv` intermediates produced by the shell steps below. Adjust paths
> before re-running elsewhere. They are saved here mainly so the **logic** is not lost.

## Pages and how they are produced

| Page | Produced by |
|------|-------------|
| `dashboard.html`, `esploratore.html`, `index.html`, `panorama.html` | hand-authored / edited directly |
| `geografia.html`, `controllate.html`, `quadro-giuridico.html`, `green-digitale.html` | **`gen_pages.py`** (derived from `dashboard.html`, chrome hidden, one topic shown) |
| `innovazione.html` | **`build_innovation_page.py`** |
| `assets/news.css` | extracted once from `dashboard.html`'s `<style>` |

`gen_pages.py` also **injects the NUTS3 province map** into `geografia.html`.

## Data inputs

- `firms_bvdid.csv` — RNA beneficiaries matched to Orbis BvD IDs (cols: …`ateco`…`bvdid`…`nuts2`,`nuts3`,`nace`).
- `~/…/Dropbox/orbis_extracted_data/bvdid_patstat_correspondence/bvdid_docdb_family.csv` — BvD ID ↔ DOCDB patent family (~1.3 GB, global).
- `~/…/Dropbox/PATSTAT/Autumn 2025/unzipped/tls201_appln_part0{1,2,3}.csv` — PATSTAT applications (~25.6 GB); cols 16 = `earliest_filing_year`, 22 = `docdb_family_id`.
- `src/data/by_nuts3.json`, `src/data/nuts_meta.json` — NUTS3 ESL aggregates (produced upstream from `nuts_sectors/`).

## Run order

### 0. Shell prep — BvD × PATSTAT joins (produce /tmp intermediates)

```bash
PF=~/…/Dropbox/orbis_extracted_data/bvdid_patstat_correspondence/bvdid_docdb_family.csv

# aid-firm BvD IDs
awk -F, 'NR>1 && $7!="" {print $7}' firms_bvdid.csv | LC_ALL=C sort -u > /tmp/aid_bvdids.txt

# patent families per aid firm  ->  /tmp/fam_counts.csv  (bvdid,count)
LC_ALL=C awk -F, 'NR==FNR{a[$1]=1;next} ($1 in a){c[$1]++} END{for(b in c)print b","c[b]}' \
  /tmp/aid_bvdids.txt "$PF" > /tmp/fam_counts.csv

# distinct families of aid firms  ->  /tmp/aid_families.txt
LC_ALL=C awk -F, 'NR==FNR{a[$1]=1;next} ($1 in a){print $2}' \
  /tmp/aid_bvdids.txt "$PF" | LC_ALL=C sort -u > /tmp/aid_families.txt

# earliest filing year per family from PATSTAT TLS201  ->  /tmp/fam_year.csv  (~7 min)
bash build/run_tls201.sh
```

### 1. NUTS3 geometry  ->  `src/data/nuts3_paths.json`
```bash
python3 build/build_nuts3_geo.py     # downloads Eurostat NUTS 2021 03M, Douglas–Peucker simplify
```

### 2. Innovation datamart  ->  `src/data/innovation.json`
```bash
python3 build/build_innovation_data.py            # joins fam_counts + firms_bvdid (dedup by bvdid)
# merge PATSTAT filing years into the datamart (build_innovation_data.py preserves it on re-runs):
python3 - <<'PY'
import json, collections, pathlib
p = pathlib.Path("src/data/innovation.json"); d = json.loads(p.read_text())
by = collections.Counter()
for line in open('/tmp/fam_year.csv'):
    _, y = line.strip().split(','); y = int(y)
    if 1990 <= y <= 2024: by[str(y)] += 1
d["by_year"] = {y: by[y] for y in sorted(by)}
p.write_text(json.dumps(d, ensure_ascii=False, separators=(',',':')))
PY
```

### 3. Generate pages
```bash
python3 build/build_innovation_page.py   # innovation.json + nuts3_paths.json -> innovazione.html
python3 build/gen_pages.py               # dashboard.html -> geografia/controllate/quadro/green (+ NUTS3 map)
```

### 4. Deploy
```bash
cp index.html dashboard.html esploratore.html panorama.html \
   geografia.html controllate.html quadro-giuridico.html green-digitale.html innovazione.html dist/
cp assets/news.css dist/assets/
git add -A && git commit -m "…"
git push origin main
git subtree push --prefix dist origin gh-pages   # publishes dist/ to GitHub Pages
```

## Notes
- The focused pages (`geografia` etc.) are ~200 KB each because they embed the full dashboard
  (all data + code present, interactivity guaranteed identical). Trade-off accepted for robustness.
- `test_pages.js` headless-renders pages via puppeteer-core + system Chrome and checks for console
  errors / that charts and SVGs draw. Run with `NODE_PATH=./node_modules node build/test_pages.js`.
