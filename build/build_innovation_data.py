#!/usr/bin/env python3
import csv, json, collections, pathlib
ROOT = pathlib.Path("/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato")

# per-bvdid patent family count (aid firms only)
fam = {}
for line in open('/tmp/fam_counts.csv'):
    b,c = line.strip().split(','); fam[b]=int(c)

# aggregate firms_bvdid to ONE row per bvdid (dedup the multi-CF rows)
F = {}  # bvdid -> dict
csv.field_size_limit(10**7)
with open(ROOT/'firms_bvdid.csv') as f:
    for x in csv.DictReader(f):
        b = x['bvdid']
        if not b: continue
        try: esl=float(x['esl_eur'])
        except: esl=0.0
        d = F.get(b)
        if d is None:
            F[b] = {'esl':esl, 'nm':(x['orbis_name'] or x['denominazione']),
                    'ateco':(x['ateco'] or ''), 'nuts3':x['nuts3'], 'reg':x['regione']}
        else:
            d['esl'] += esl
            if not d['ateco'] and x['ateco']: d['ateco']=x['ateco']
            if not d['nuts3'] and x['nuts3']: d['nuts3']=x['nuts3']

def ateco_div(s):
    s=(s or '').strip()
    if '.' not in s: return None
    sec, rest = s.split('.',1)
    d2 = ''.join(ch for ch in rest if ch.isdigit())[:2]
    return (sec+'.'+d2) if (d2 and sec) else None

tot_esl = sum(d['esl'] for d in F.values())
pat_bvdids = [b for b in F if b in fam]
pat_esl = sum(F[b]['esl'] for b in pat_bvdids)
fam_links = sum(fam[b] for b in pat_bvdids)

# ---- TOP FIRMS ----
top = sorted(pat_bvdids, key=lambda b: -fam[b])[:25]
top_firms = [{"nm":F[b]['nm'][:40], "fam":fam[b], "esl":round(F[b]['esl']/1e6,1),
              "ateco":(ateco_div(F[b]['ateco']) or '—'), "prov":(F[b]['nuts3'].split(' - ')[-1] if F[b]['nuts3'] else '')}
             for b in top]

# ---- SECTORS (NACE 2-digit) ----
NACE2 = {
 '01':'Agricoltura','03':'Pesca','05':'Estraz. carbone','06':'Estraz. petrolio/gas','08':'Estraz. minerali',
 '10':'Alimentari','11':'Bevande','13':'Tessile','14':'Abbigliamento','15':'Pelle/calzature','16':'Legno',
 '17':'Carta','18':'Stampa','19':'Coke/raffinazione','20':'Chimica','21':'Farmaceutica','22':'Gomma/plastica',
 '23':'Minerali non metalliferi','24':'Metallurgia','25':'Prodotti in metallo','26':'Elettronica/ottica',
 '27':'App. elettriche','28':'Macchinari','29':'Autoveicoli','30':'Altri mezzi trasporto','31':'Mobili',
 '32':'Altre manifatture','33':'Riparaz./install. macchine','35':'Energia elettrica/gas','36':'Acqua',
 '37':'Reti fognarie','38':'Rifiuti','41':'Costruz. edifici','42':'Ingegneria civile','43':'Costruz. specializzate',
 '45':'Commercio autoveicoli','46':"Commercio all'ingrosso",'47':'Commercio al dettaglio','49':'Trasporto terrestre',
 '50':'Trasporto marittimo','51':'Trasporto aereo','52':'Magazzinaggio/logistica','53':'Poste','55':'Alloggio',
 '56':'Ristorazione','58':'Editoria','59':'Cinema/audiovisivo','60':'Radio/TV','61':'Telecomunicazioni',
 '62':'Software/IT','63':'Servizi informativi','64':'Servizi finanziari','65':'Assicurazioni','68':'Immobiliare',
 '69':'Legale/contabilità','70':'Direzione/consulenza','71':'Architettura/ingegneria','72':'Ricerca e sviluppo',
 '73':'Pubblicità','74':'Altre attività prof.','77':'Noleggio/leasing','78':'Lavoro','79':'Agenzie viaggio',
 '80':'Vigilanza','81':'Servizi edifici','82':'Servizi alle imprese','84':'Pubblica amministrazione',
 '85':'Istruzione','86':'Sanità','87':'Assistenza residenziale','88':'Assistenza sociale','90':'Arte/spettacolo',
 '91':'Biblioteche/musei','93':'Sport/intrattenimento','94':'Associazioni','95':'Riparazioni','96':'Altri servizi',
}
# aggregate by ATECO division number (merge e.g. M.72 / N.72 -> one R&D row)
sec = collections.defaultdict(lambda:[0.0,0,0])      # div2 -> [esl, fam, nfirms]
domsec = collections.defaultdict(lambda: collections.defaultdict(float))  # div2 -> {section: esl}
for b,d in F.items():
    ad = ateco_div(d['ateco'])
    if not ad: continue
    sect_letter, div2 = ad.split('.')
    sec[div2][0]+=d['esl']; sec[div2][2]+=1
    domsec[div2][sect_letter]+=d['esl']
    if b in fam: sec[div2][1]+=fam[b]
sectors=[]
for div2,(e,fa,nf) in sec.items():
    dom = max(domsec[div2].items(), key=lambda kv:kv[1])[0]
    sectors.append({"code":dom+'.'+div2, "lab":NACE2.get(div2,div2), "esl":round(e/1e9,3), "fam":fa,
                    "as":round(e/tot_esl*100,3), "ps":round(fa/fam_links*100,3)})
sectors=[s for s in sectors if s['as']>=0.3 or s['ps']>=0.3]
sectors.sort(key=lambda s:-(s['as']+s['ps']))

# ---- NUTS3 (provinces) ----
prov = collections.defaultdict(lambda:[0,0,0])  # code -> [fam, n_pat_firms, n_aid_firms]
name = {}
for b,d in F.items():
    if not d['nuts3']: continue
    code=d['nuts3'].split(' - ')[0].strip(); name[code]=d['nuts3'].split(' - ',1)[-1].strip()
    prov[code][2]+=1
    if b in fam:
        prov[code][0]+=fam[b]; prov[code][1]+=1
nuts3={c:{"nm":name[c],"fam":fa,"pf":pf,"nf":nf} for c,(fa,pf,nf) in prov.items() if c not in ('N/D','')}

out={"meta":{"tot_esl_mld":round(tot_esl/1e9,1),"pat_esl_mld":round(pat_esl/1e9,1),
             "pat_esl_pct":round(pat_esl/tot_esl*100,1),"n_pat_firms":len(pat_bvdids),
             "n_firms":len(F),"fam_links":fam_links},
     "top_firms":top_firms,"sectors":sectors,"nuts3":nuts3}
# preserve a previously-merged filing-year series, if present
prev = ROOT/'src/data/innovation.json'
if prev.exists():
    old = json.loads(prev.read_text())
    if old.get("by_year"): out["by_year"] = old["by_year"]
prev.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))

m=out['meta']
print(f"firms(distinct bvdid): {m['n_firms']:,}  patenting: {m['n_pat_firms']:,} ({m['n_pat_firms']/m['n_firms']*100:.1f}%)")
print(f"ESL tot €{m['tot_esl_mld']}B  patenting €{m['pat_esl_mld']}B ({m['pat_esl_pct']}%)  fam-links {m['fam_links']:,}")
print(f"sectors kept: {len(sectors)}  provinces: {len(nuts3)}  by_year preserved: {'yes' if out.get('by_year') else 'no'}")
print("TOP firms (deduped):")
for t in top_firms[:12]: print(f"  {t['fam']:>5}  €{t['esl']:>7.1f}M  {t['nm'][:30]:<30} {t['ateco']:<6}  {t['prov']}")
print("TOP sectors by patent share:")
for s in sorted(sectors,key=lambda s:-s['ps'])[:10]: print(f"  {s['code']:<6} {s['lab'][:22]:<22} aid {s['as']:>5.1f}%  pat {s['ps']:>5.1f}%  scarto {s['ps']-s['as']:+5.1f}  €{s['esl']}B")
