# Build pipeline (`scripts/`)

Repository layout after the reorg:

```
data/             raw inputs (.csv, data_rna/, nuts_sectors/)
data/generated/   all python-produced data (.json datamarts)
scripts/          all computation + page-generation scripts (this folder)
site/             all visualizations: .html pages + assets/  ← deploys to gh-pages
```

The site is a set of **self-contained static HTML files** (data + JS inlined, no runtime
fetch). `site/dashboard.html` ("Tutto in una pagina") is the canonical source; the focused
topic pages are **generated** from it.

> ⚠️ **Paths.** Scripts hardcode the repo root (`ROOT = .../aiuti_stato`), read inputs from
> `ROOT/data/` and large external files from `~/…/Dropbox/…`, and use `/tmp/*.csv`
> intermediates produced by the shell/`run_*.sh` steps. Adjust before re-running elsewhere.

## Pages and how they are produced

| Page (in `site/`) | Produced by |
|------|-------------|
| `dashboard.html`, `esploratore.html`, `index.html`, `panorama.html` | hand-authored |
| `geografia.html`, `controllate.html`, `quadro-giuridico.html`, `green-digitale.html` | `gen_pages.py` (derived from `dashboard.html`; chrome hidden, one topic shown; injects the NUTS3 map into `geografia.html`) |
| `innovazione.html` | `build_innovation_page.py` |
| `assets/news.css` | extracted once from `dashboard.html`'s `<style>` |

## External data inputs

- `data/firms_bvdid.csv` — RNA beneficiaries matched to Orbis BvD IDs (`…ateco…bvdid…nuts2,nuts3,nace`).
- `~/…/Dropbox/orbis_extracted_data/bvdid_patstat_correspondence/bvdid_docdb_family.csv` — BvD ID ↔ DOCDB family (~1.3 GB).
- `~/…/Dropbox/PATSTAT/Autumn 2025/unzipped/tls201_appln_part0{1,2,3}.csv` — applications (~25.6 GB); col 16 `earliest_filing_year`, col 22 `docdb_family_id`, col 1 `appln_id`.
- `~/…/Dropbox/PATSTAT/Autumn 2025/unzipped/tls224_appln_cpc_part0{1,2}.csv` — CPC per application (~11 GB); col 1 `appln_id`, col 2 `cpc_class_symbol`.
- `data/generated/by_nuts3.json`, `data/generated/soe_graph.json` — produced upstream / by the explorer build.

## Run order

### 0. Shell prep — BvD × PATSTAT joins (→ /tmp intermediates)
```bash
PF=~/…/Dropbox/orbis_extracted_data/bvdid_patstat_correspondence/bvdid_docdb_family.csv
cd data
awk -F, 'NR>1 && $7!="" {print $7}' firms_bvdid.csv | LC_ALL=C sort -u > /tmp/aid_bvdids.txt
LC_ALL=C awk -F, 'NR==FNR{a[$1]=1;next} ($1 in a){c[$1]++} END{for(b in c)print b","c[b]}' /tmp/aid_bvdids.txt "$PF" > /tmp/fam_counts.csv
bash ../scripts/run_tls201.sh        # earliest filing year per aid-firm family → /tmp/fam_year.csv (~7 min)
```

### 1. NUTS3 geometry → `data/generated/nuts3_paths.json`
```bash
# first download Eurostat NUTS 2021 03M into data/nuts3_03m.geojson, then:
python3 scripts/build_nuts3_geo.py
```

### 2. Innovation datamart → `data/generated/innovation.json`
```bash
python3 scripts/build_innovation_data.py     # joins fam_counts + firms_bvdid (dedup by bvdid)
# then merge PATSTAT filing years (build_innovation_data.py preserves by_year on re-runs):
python3 - <<'PY'
import json, collections, pathlib
p = pathlib.Path("data/generated/innovation.json"); d = json.loads(p.read_text())
by = collections.Counter()
for line in open('/tmp/fam_year.csv'):
    _, y = line.strip().split(','); y = int(y)
    if 1990 <= y <= 2024: by[str(y)] += 1
d["by_year"] = {y: by[y] for y in sorted(by)}
p.write_text(json.dumps(d, ensure_ascii=False, separators=(',',':')))
PY
```

### 3. SOE patents section ⑥ → `data/generated/innovation.json["soe"]`
```bash
# SOE bvdids → families  (after building /tmp/soe_bvdids.txt via build_soe_data.py's step 1)
python3 scripts/build_soe_data.py   # writes /tmp/soe_bvdids.txt, then needs the joins below, then run again
PF=~/…/Dropbox/orbis_extracted_data/bvdid_patstat_correspondence/bvdid_docdb_family.csv
LC_ALL=C awk -F, 'NR==FNR{a[$1]=1;next} ($1 in a){print $1","$2}' /tmp/soe_bvdids.txt "$PF" > /tmp/soe_pairs.csv
cut -d, -f2 /tmp/soe_pairs.csv | sort -u > /tmp/soe_families.txt
bash scripts/run_soe_tls201.sh      # family,year,appln  → /tmp/soe_appln.csv  (~7 min)
cut -d, -f3 /tmp/soe_appln.csv | sort -u > /tmp/soe_applns.txt
bash scripts/run_soe_tls224.sh      # appln,cpc         → /tmp/soe_cpc.csv     (~4 min)
python3 scripts/build_soe_data.py   # final: entities + by_year + top CPC techs
```

### 4. Generate pages (into `site/`)
```bash
python3 scripts/build_innovation_page.py   # data/generated/innovation.json + nuts3_paths.json → site/innovazione.html
python3 scripts/gen_pages.py               # site/dashboard.html → site/{geografia,controllate,quadro,green}.html
python3 scripts/add_glossaries.py          # inject per-page acronym glossary (run AFTER gen_pages)
python3 scripts/add_i18n.py                # inject IT/EN toggle scripts (assets/i18n*.js)
python3 scripts/add_downloads.py           # inject per-figure CSV download buttons (assets/download.js)
```

### 5. Deploy (`site/` is the published tree)
```bash
git add -A && git commit -m "…"
git push origin main
git subtree push --prefix site origin gh-pages   # publishes site/ to GitHub Pages
```

## Notes
- Focused pages (`geografia` etc.) are ~200 KB because they embed the full dashboard
  (data + code present → interactivity guaranteed identical). Trade-off accepted for robustness.
- CPC `Y` classes (Y02/Y10 tagging scheme) are excluded from the SOE technologies chart.
- Two data-prep scripts that still feed the live site are kept here but **not version-controlled**:
  `match_bvdid.py` (→ `data/firms_bvdid.csv`) and `enrich_nuts_nace.py` (→ `data/generated/by_nuts3.json`).
  Scripts that only produced things no longer on the site (figure generators, the energia focus,
  the old Observable datamarts, the raw RNA downloader) have been removed.
