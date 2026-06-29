#!/usr/bin/env python3
# Inject a per-page "Acronimi in questa pagina" glossary at the top of each page.
# Idempotent (re-running replaces the existing block). Run AFTER gen_pages.py
# (the generated pages get their glossary here too).
import re, pathlib
ROOT = pathlib.Path("/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato")

MASTER = {
 'RNA':   'Registro Nazionale Aiuti di Stato — banca dati pubblica di tutte le misure di aiuto concesse in Italia',
 'ESL':   'Equivalente Sovvenzione Lorda — valore standardizzato UE del vantaggio economico netto per il beneficiario',
 'ATECO': 'Classificazione delle Attività Economiche — versione italiana della NACE (es. C.28 macchinari, D.35 energia)',
 'NACE':  'Classificazione statistica europea delle attività economiche',
 'MEF':   "Ministero dell'Economia e delle Finanze",
 'CDP':   'Cassa Depositi e Prestiti — istituto di promozione controllato dal MEF',
 'GBER':  'General Block Exemption Regulation (Reg. UE 651/2014) — esonera certe categorie di aiuto dalla notifica preventiva',
 'TCTF':  'Temporary Crisis and Transition Framework — quadro UE temporaneo per le crisi 2022–2024',
 'IPCEI': 'Important Projects of Common European Interest — grandi progetti strategici europei coordinati tra Stati membri',
 'SIEG':  'Servizi di Interesse Economico Generale',
 'CPC':   'Cooperative Patent Classification — classificazione tecnologica dei brevetti',
 'NUTS':  'Nomenclature of Territorial Units for Statistics — livelli territoriali UE (NUTS3 = provincia)',
 'BvD':   'Bureau van Dijk — identificativo societario del database Orbis usato per l\'aggancio dei beneficiari',
 'PIL':   'Prodotto Interno Lordo',
 'GSE':   'Gestore Servizi Energetici — ente pubblico che eroga incentivi per le rinnovabili',
 'PATSTAT':'Database statistico mondiale dei brevetti dell\'EPO (Ufficio Europeo dei Brevetti)',
}
PAGE_ACROS = {
 'index.html':           ['RNA','ESL'],
 'panorama.html':        ['ESL','ATECO','RNA','MEF','CDP','GBER','SIEG'],
 'geografia.html':       ['ESL','RNA','NUTS','BvD'],
 'controllate.html':     ['ESL','MEF','CDP','RNA','ATECO'],
 'quadro-giuridico.html':['ESL','GBER','TCTF','SIEG','IPCEI','GSE','RNA'],
 'green-digitale.html':  ['ESL','RNA','GSE'],
 'innovazione.html':     ['ESL','CPC','BvD','PATSTAT','RNA','MEF','CDP','ATECO'],
 'esploratore.html':     ['MEF','CDP','RNA','ESL'],
}

MASTER = {k: v.replace(' — ', ': ', 1) for k, v in MASTER.items()}  # "ACRO — Full name: description"

def glossary(acros):
    items = "\n".join(
        f'      <div class="gl-item"><strong>{a}</strong> — {MASTER[a]}</div>' for a in acros)
    return ('<!--GLOSSARY-->\n'
        '  <details class="glossary" style="margin:0 0 30px;">\n'
        f'    <summary class="glossary-title">Acronimi in questa pagina<span class="gl-hint">{len(acros)} termini · clicca per espandere</span></summary>\n'
        '    <div class="glossary-grid">\n'
        f'{items}\n'
        '    </div>\n  </details>\n<!--/GLOSSARY-->')

def end_of_homehero(s):
    i = s.find('<div class="home-hero"')
    if i < 0: return -1
    depth = 0
    for m in re.finditer(r'<div\b|</div>', s[i:]):
        depth += 1 if m.group(0) != '</div>' else -1
        if depth == 0: return i + m.end()
    return -1

for fn, acros in PAGE_ACROS.items():
    p = ROOT / "site" / fn
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'\n?<!--GLOSSARY-->.*?<!--/GLOSSARY-->\n?', '\n', s, flags=re.S)  # idempotent
    block = glossary(acros)
    pos = end_of_homehero(s)
    if pos < 0:                                   # esploratore: after </header>
        h = s.find('</header>')
        pos = h + len('</header>') if h >= 0 else -1
    if pos < 0:
        print(f"  SKIP {fn}: no anchor"); continue
    s = s[:pos] + "\n" + block + s[pos:]
    p.write_text(s, encoding="utf-8")
    print(f"  {fn}: glossary with {len(acros)} terms")
