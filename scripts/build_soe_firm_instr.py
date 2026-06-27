import zipfile, time, collections, json, glob
from lxml import etree
NS='{http://www.rna.it/RNA_aiuto/schema}'
CF={'00811720580':'ENEL','09320630966':'Open Fiber','09291380153':'STMicroelectronics','00397130584':'Fincantieri',
 '13271390158':'Snam','00825790157':'Saipem','97103880585':'Poste Italiane','10354890963':"Acciaierie d'Italia"}
def bucket(s):
    s=s.lower()
    if 'garanzia' in s: return 'Garanzia'
    if 'rischio' in s: return 'Finanz. rischio'
    if 'prestito' in s or 'anticipo rimborsabile' in s: return 'Prestito'
    if 'fiscal' in s or 'esenzione' in s or 'agevolazione' in s: return "Credito d'imposta"
    if 'sovvenzione' in s or 'contributo' in s: return 'Sovvenzione'
    return 'Altro'
agg=collections.defaultdict(float); t0=time.time(); n=0
zips=sorted(glob.glob('/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato/data/data_rna/*.zip'))
for zi,Z in enumerate(zips):
    try: zf=zipfile.ZipFile(Z)
    except Exception as ex: print('zip err',Z,ex); continue
    for name in zf.namelist():
        if not name.endswith('.xml'): continue
        try:
          with zf.open(name) as fh:
            for ev,a in etree.iterparse(fh, tag=NS+'AIUTO', recover=True, huge_tree=True):
                n+=1
                cf=a.findtext(NS+'CODICE_FISCALE_BENEFICIARIO')
                if cf in CF:
                    yr=(a.findtext(NS+'DATA_CONCESSIONE') or '')[:4]
                    if yr.isdigit() and 2016<=int(yr)<=2025:
                        for st in a.iter(NS+'STRUMENTO_AIUTO'):
                            try: e=float(st.findtext(NS+'ELEMENTO_DI_AIUTO') or 0)
                            except: e=0.0
                            agg[(CF[cf],yr,bucket(st.findtext(NS+'DES_STRUMENTO') or ''))]+=e
                a.clear()
        except Exception as ex: print('skip',name,ex)
    print(f"  [{zi+1}/{len(zips)}] {n:,} records, {time.time()-t0:.0f}s", flush=True)
out=collections.defaultdict(lambda: collections.defaultdict(dict))
for (f,y,b),v in agg.items(): out[f][y][b]=round(v/1e9,4)   # mld €
json.dump(out, open('/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato/data/generated/soe_firm_instr.json','w'), ensure_ascii=False)
print(f"DONE_SOE_INSTR parsed {n:,} in {time.time()-t0:.0f}s, firms {len(out)}")
