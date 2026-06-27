#!/usr/bin/env python3
# SOE patent datamart -> innovation.json["soe"]  (section ⑥ on innovazione.html)
# Joins state-owned beneficiaries to their patents (families, filing years, CPC tech).
#
# Prerequisite intermediates (see build/README.md for the exact shell/awk):
#   /tmp/soe_pairs.csv  (bvdid,family)      -- SOE bvdids joined to bvdid_docdb_family.csv
#   /tmp/soe_appln.csv  (family,year,appln) -- build/run_soe_tls201.sh  (PATSTAT TLS201)
#   /tmp/soe_cpc.csv    (appln,"cpc")       -- build/run_soe_tls224.sh  (PATSTAT TLS224)
import json, csv, collections, pathlib
ROOT = pathlib.Path("/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato")

# 1. SOE bvdid -> (label, branch, esl) from the explorer graph × firms_bvdid
g = json.loads((ROOT/"src/data/soe_graph.json").read_text())
soe_cf = {str(n['cf']).strip(): (n.get('label') or n['id'], n.get('branch') or n['id'], n.get('esl') or 0.0)
          for n in g['nodes'] if n.get('cf')}
csv.field_size_limit(10**7)
bv2 = {}
with open(ROOT/"firms_bvdid.csv") as f:
    for x in csv.DictReader(f):
        if x['codice_fiscale'] in soe_cf and x['bvdid']:
            bv2[x['bvdid']] = soe_cf[x['codice_fiscale']]
pathlib.Path('/tmp/soe_bvdids.txt').write_text('\n'.join(sorted(bv2)) + '\n')

# 2. entities: patent families per SOE (needs /tmp/soe_pairs.csv)
CLEAN = {"Stm Holding NV":"STMicroelectronics","VERSALIS S.p.a.":"Versalis","ANSALDO ENERGIA S.p.a.":"Ansaldo Energia",
 "FINCANTIERI S.p.a.":"Fincantieri","ENEL X WAY S.r.l.":"Enel X Way","TELESPAZIO S.p.a.":"Telespazio","LARIMART S.p.a.":"Larimart",
 "ANAS S.p.a.":"Anas","FSTECHNOLOGY S.p.a.":"FS Technology","Gse":"GSE","POSTEL S.p.a.":"Postel","TEKLA S.r.l.":"Tekla",
 "POSTEPAY S.p.a.":"PostePay","MONTE PASCHI FIDUCIARIA S.p.a.":"MPS Fiduciaria","SICAMB S.r.l.":"Sicamb","SICAMB S.p.a.":"Sicamb"}
GRP = {"STM HOLDING":"STMicroelectronics","LEONARDO":"Leonardo","ENI":"ENI","CDP":"CDP","ENEL":"Enel",
 "FERROVIE DELLO STATO ITALIANE":"Ferrovie dello Stato","POSTE ITALIANE":"Poste","AGENZIA ATTR INVEST INVITALIA":"Invitalia"}
cnt = collections.Counter()
for line in open('/tmp/soe_pairs.csv'):
    bv, fa = line.strip().split(','); cnt[bv] += 1
ent = []
for bv, fc in cnt.items():
    lab, br, esl = bv2[bv]
    ent.append({"nm": CLEAN.get(lab, lab), "fam": fc, "esl": round(esl, 3), "grp": GRP.get(br, br.title())})
ent.sort(key=lambda e: -e["fam"])

# 3. trends: SOE families by earliest filing year (needs /tmp/soe_appln.csv)
fy = {}; applns = set()
for line in open('/tmp/soe_appln.csv'):
    p = line.strip().split(',')
    if len(p) != 3: continue
    fam, y, ap = p
    try: y = int(y)
    except: continue
    applns.add(ap)
    if 1900 <= y <= 2026 and (fam not in fy or y < fy[fam]): fy[fam] = y
by = collections.Counter()
for fam, y in fy.items():
    if 1990 <= y <= 2024: by[str(y)] += 1
by_year = {y: by[y] for y in sorted(by)}

# 4. technologies: top CPC subclasses by distinct family (needs /tmp/soe_cpc.csv)
a2f = {}
for line in open('/tmp/soe_appln.csv'):
    p = line.strip().split(',')
    if len(p) == 3: a2f[p[2]] = p[0]
LAB = {
 'H01L':'Semiconduttori — dispositivi','H10D':'Semiconduttori — diodi e transistor','H10B':'Memorie a semiconduttore',
 'H10N':'Semiconduttori — altri dispositivi','G11C':'Memorie digitali','G06F':'Elaborazione dati digitale',
 'H03K':'Circuiti logici a impulsi','H02M':'Conversione di potenza elettrica','H03F':'Amplificatori',
 'G01R':'Misura di grandezze elettriche','H04L':'Trasmissione digitale di dati','B81B':'Microstrutture / MEMS',
 'B81C':'Fabbricazione di MEMS','G05F':'Regolazione di tensione e corrente','H04N':'Trasmissione di immagini (video)',
 'H03M':'Codifica e decodifica digitale','H04B':'Comunicazioni / trasmissione','G01C':'Navigazione e giroscopi',
 'C08F':'Polimeri (macromolecole)','G02B':'Ottica','G01S':'Radar e radiolocalizzazione','F01D':'Turbine',
 'H02K':'Macchine elettriche (generatori)','B63B':'Costruzione navale','H01M':'Batterie e celle a combustibile'}
sub = collections.defaultdict(set)
for line in open('/tmp/soe_cpc.csv'):
    p = line.rstrip('\n').split(',', 1)
    if len(p) != 2: continue
    fam = a2f.get(p[0])
    if not fam: continue
    sc = p[1].strip().strip('"').replace(' ', '')[:4]
    if len(sc) >= 4 and sc[0].isalpha() and sc[0] != 'Y':   # drop CPC Y* tagging scheme
        sub[sc].add(fam)
techs = [{"cpc": sc, "lab": LAB.get(sc, sc), "n": len(f)}
         for sc, f in sorted(sub.items(), key=lambda kv: -len(kv[1]))[:14]]

# 5. write into the innovation datamart
d = json.loads((ROOT/"src/data/innovation.json").read_text())
d["soe"] = {"meta": {"n_entities": len(ent), "n_families": sum(e["fam"] for e in ent)},
            "entities": ent, "by_year": by_year, "techs": techs}
(ROOT/"src/data/innovation.json").write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
print(f"soe: {len(ent)} entities, {d['soe']['meta']['n_families']} families, "
      f"{len(by_year)} years, {len(techs)} tech classes")
