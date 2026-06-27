#!/usr/bin/env python3
# Generate focused topic pages from the canonical dashboard.html.
import sys, json, pathlib

ROOT = pathlib.Path("/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato")
src = (ROOT / "site/dashboard.html").read_text(encoding="utf-8")

# ── NUTS3 province map: geometry + data → injectable block ─────────────
geo = json.loads((ROOT/"data/generated/nuts3_paths.json").read_text())
by3 = json.loads((ROOT/"data/generated/by_nuts3.json").read_text())
D_NUTS3 = {}
for r in by3:
    code = r["nuts3"].split(" - ")[0].strip()
    if code in ("N/D", ""): continue
    nm = r["nuts3"].split(" - ",1)[1].strip() if " - " in r["nuts3"] else code
    D_NUTS3[code] = {"nm": nm, "esl": round(r["esl_mld"],4), "pct": round(r["pct"],3), "nf": r["n_firms"]}

NUTS3_TPL = r'''
  <!-- NUTS3 province choropleth (injected) -->
  <section id="s-nuts3">
    <div class="sec-hd">
      <h2>Dettaglio provinciale · NUTS3</h2>
      <span class="sec-note">Sede del beneficiario · 88,8% dell'<abbr title="Equivalente Sovvenzione Lorda">ESL</abbr> geolocalizzato</span>
    </div>
    <p class="note" style="margin:0 0 16px; max-width:880px;">
      Mappa a livello di <strong>provincia (NUTS3)</strong>, ottenuta incrociando ~1,58 mln di beneficiari
      con i codici Orbis (BvD): copre l'<strong>88,8%</strong> dell'ESL totale. <strong>Milano</strong>
      (€ 44,6 mld) e <strong>Roma</strong> (€ 39,5 mld) staccano nettamente. Con «media per impresa»
      emergono invece le province dove pochi grandi beneficiari concentrano il valore. La sede legale
      non coincide sempre con il luogo dell'investimento.
    </p>
    <style>
      /* scoped toggle — distinct class so the dashboard's .mt-btn handler ignores it */
      #nuts3-metric .n3btn{font-size:12px;color:var(--muted);background:none;border:1px solid var(--border);border-radius:4px;padding:6px 13px;cursor:pointer;min-height:32px;transition:color .15s,border-color .15s,background .15s;}
      #nuts3-metric .n3btn:hover{color:var(--text);border-color:var(--dim);}
      #nuts3-metric .n3btn.n3-active{color:#fff;background:var(--amber);border-color:var(--amber);}
    </style>
    <div class="metric-sel" id="nuts3-metric" role="group" aria-label="Metrica mappa provinciale">
      <span class="metric-lab">Vista</span>
      <button class="n3btn n3-active" data-m="esl" type="button">ESL totale</button>
      <button class="n3btn" data-m="perfirm" type="button">Media per impresa</button>
    </div>
    <div class="map-grid">
      <div class="map-card">
        <div class="map-wrap" style="height:auto;"><svg id="nuts3-map" style="width:100%;height:auto;display:block;"></svg></div>
        <div class="legend-bins" id="nuts3-legend"></div>
        <div class="legend-labels" id="nuts3-legend-lab"></div>
      </div>
      <div class="map-card">
        <div class="card-title">Prime 15 province</div>
        <div class="card-sub" id="nuts3-list-sub">per ESL totale · mld €</div>
        <div class="map-list" id="nuts3-list"></div>
      </div>
    </div>
    <details class="glossary" style="margin:18px 0 0; border-left-color:var(--steel);">
      <summary class="glossary-title" style="color:var(--steel);">Chi sono i non geolocalizzati?<span class="gl-hint">il 11,2% dell'ESL · € 57,2 mld · clicca per i dettagli</span></summary>
      <div style="margin-top:14px; font-size:12.5px; color:var(--muted); line-height:1.7; max-width:900px;">
        <p style="margin-bottom:10px;">L'aggancio avviene sulla <strong>partita IVA</strong> (codice Orbis/BvD). Il 11,2% di <abbr title="Equivalente Sovvenzione Lorda">ESL</abbr> che resta fuori dalla mappa non è «perso»: ha una spiegazione precisa.</p>
        <p style="margin-bottom:9px;"><strong style="color:var(--text);">Persone fisiche — € 39,3 mld (~69% del non agganciato).</strong> 2,97 mln di beneficiari sono persone fisiche (codice fiscale a 16 caratteri, non partita IVA): ditte individuali, agricoltori, imprenditori individuali. Per definizione non sono nell'universo societario Orbis, quindi non agganciabili sulla p.IVA.</p>
        <p style="margin-bottom:9px;"><strong style="color:var(--text);">Partite IVA pubbliche o non-market — € 17,8 mld.</strong> 399 mila p.IVA a 11 cifre restano non abbinate; le maggiori sono enti che Orbis copre male: agenzie regionali per la casa (<abbr title="Aziende Territoriali per l'Edilizia Residenziale">ATER</abbr>/ARCA), autorità portuali, comuni (Milano, Livigno), università (Salerno, Calabria, Salento), <abbr title="Agenzia nazionale per le nuove tecnologie, l'energia e lo sviluppo economico sostenibile">ENEA</abbr>, consorzi, istituti religiosi.</p>
        <p style="margin-bottom:9px;"><strong style="color:var(--text);">Quasi nessun grande beneficiario manca.</strong> Sopra i € 100 mln c'è una sola impresa non agganciata: <em>Bosia Roberto</em> (€ 104 mln), una persona fisica.</p>
        <p style="margin-bottom:0;"><strong style="color:var(--text);">Per settore</strong>, il non agganciato si concentra dove dominano micro-imprese e ditte individuali: commercio al dettaglio (G.47, € 8,6 mld), ristorazione (I.56, € 6,6 mld — aiuti COVID a bar e ristoranti), costruzioni specializzate (F.43, € 3,8 mld), agricoltura (A.01). La mappa coglie quindi soprattutto le imprese strutturate: i € 57 mld mancanti sono in larga parte aiuti diffusi a persone fisiche e micro-attività, non grandi beneficiari nascosti.</p>
      </div>
    </details>
    <div class="map-tooltip" id="nuts3-tip" role="tooltip" aria-live="polite"></div>
  </section>
  <script>
  (function(){
    var VB = %%VB%%, PATHS = %%PATHS%%, D = %%DATA%%;
    var svg = document.getElementById('nuts3-map'); if(!svg) return;
    var NS = 'http://www.w3.org/2000/svg';
    svg.setAttribute('viewBox','0 0 '+VB.w+' '+VB.h);
    var tip = document.getElementById('nuts3-tip');
    var COLORS = ['#E7E1D4','#C2CFCF','#90ABB4','#527C8E','#1F5673'], NOFILL = '#F0ECE3';
    var metric = 'esl', bins = [], vmin = 0;
    function val(c){ var d = D[c]; if(!d) return null; return metric==='esl' ? d.esl : (d.nf ? d.esl*1e6/d.nf : null); }
    function it(n,dec){ return n.toFixed(dec).replace('.',','); }
    var els = {};
    Object.keys(PATHS).forEach(function(c){
      var p = document.createElementNS(NS,'path');
      p.setAttribute('d', PATHS[c]); p.setAttribute('class','map-region'); p.setAttribute('data-c', c);
      p.addEventListener('mousemove', function(e){ showTip(e,c); });
      p.addEventListener('mouseleave', function(){ tip.style.display='none'; });
      svg.appendChild(p); els[c] = p;
    });
    function showTip(e,c){
      var d = D[c]; tip.style.display='block';
      tip.style.left = (e.clientX+14)+'px'; tip.style.top = (e.clientY+14)+'px';
      if(!d){ tip.innerHTML = '<strong>'+c+'</strong><div class="tt-sub">dato non disponibile</div>'; return; }
      tip.innerHTML = '<strong>'+d.nm+'</strong>'+
        '<div class="tt-esl">€ '+it(d.esl,2)+' mld</div>'+
        '<div class="tt-sub">'+it(d.pct,2)+'% del totale · '+d.nf.toLocaleString('it-IT')+' imprese · '+
        Math.round(d.esl*1e6/d.nf).toLocaleString('it-IT')+' k€/impresa</div>';
    }
    function quantiles(){
      var vs = Object.keys(PATHS).map(val).filter(function(v){ return v!=null; }).sort(function(a,b){ return a-b; });
      vmin = vs[0]; bins = [];
      for(var i=1;i<5;i++) bins.push(vs[Math.floor(vs.length*i/5)]);
    }
    function binIdx(v){ if(v==null) return -1; for(var i=0;i<bins.length;i++){ if(v<=bins[i]) return i; } return 4; }
    function paint(){
      quantiles();
      Object.keys(PATHS).forEach(function(c){ var bi = binIdx(val(c)); els[c].setAttribute('fill', bi<0 ? NOFILL : COLORS[bi]); });
      var lg = document.getElementById('nuts3-legend'); lg.innerHTML = '';
      COLORS.forEach(function(col){ var d = document.createElement('div'); d.className='legend-bin'; d.style.background=col; lg.appendChild(d); });
      var dec = metric==='esl' ? 1 : 0;
      var edges = [vmin].concat(bins).map(function(b){ return metric==='esl' ? it(b,dec) : Math.round(b); });
      document.getElementById('nuts3-legend-lab').innerHTML = edges.map(function(x){ return '<span>'+x+'</span>'; }).join('');
      document.getElementById('nuts3-list-sub').textContent = metric==='esl' ? 'per ESL totale · mld €' : 'per ESL media per impresa · k€';
      var arr = Object.keys(D).map(function(c){ return {c:c, v:val(c), d:D[c]}; }).filter(function(o){ return o.v!=null; })
                  .sort(function(a,b){ return b.v-a.v; }).slice(0,15);
      document.getElementById('nuts3-list').innerHTML = arr.map(function(o,i){
        var vv = metric==='esl' ? '€ '+it(o.d.esl,1) : Math.round(o.v).toLocaleString('it-IT')+' k€';
        return '<div class="map-row"><span class="map-rank">'+(i+1)+'</span><span class="map-name">'+o.d.nm+'</span><span class="map-val">'+vv+'</span></div>';
      }).join('');
    }
    document.querySelectorAll('#nuts3-metric .n3btn').forEach(function(b){
      b.addEventListener('click', function(){
        document.querySelectorAll('#nuts3-metric .n3btn').forEach(function(x){ x.classList.remove('n3-active'); });
        b.classList.add('n3-active'); metric = b.getAttribute('data-m'); paint();
      });
    });
    paint();
  })();
  </script>
'''
NUTS3_BLOCK = (NUTS3_TPL
    .replace("%%VB%%", json.dumps({"w": geo["w"], "h": geo["h"]}))
    .replace("%%PATHS%%", json.dumps(geo["paths"], separators=(",",":")))
    .replace("%%DATA%%", json.dumps(D_NUTS3, separators=(",",":"), ensure_ascii=False)))

# ── shared cross-page sub-nav ─────────────────────────────────────────
NAV_ITEMS = [
    ("panorama",    "./panorama.html",        "Panorama"),
    ("geografia",   "./geografia.html",       "Geografia"),
    ("controllate", "./controllate.html",     "Controllate di Stato"),
    ("quadro",      "./quadro-giuridico.html","Quadro giuridico"),
    ("green",       "./green-digitale.html",  "Green &amp; digitale"),
    ("innovazione", "./innovazione.html",     "Innovazione"),
]
def subnav(active):
    links = []
    for key, href, label in NAV_ITEMS:
        a = ' class="active" aria-current="page"' if key == active else ""
        links.append(f'      <a href="{href}"{a}>{label}</a>')
    links.append('      <a href="./esploratore.html" style="color:var(--amber);">Esploratore ↗</a>')
    return ('<div class="subnav-wrap">\n  <div class="wrap subnav">\n'
            '    <a class="page-back" href="./index.html">← Tutti i temi</a>\n'
            '    <nav class="subnav-links" aria-label="Navigazione temi">\n'
            + "\n".join(links) + '\n    </nav>\n  </div>\n</div>\n')

def hero(badge, lead, deck, srcline):
    return ('  <div class="home-hero">\n'
        f'    <div class="hdr-badge" style="display:inline-block;margin-bottom:14px;">{badge}</div>\n'
        f'    <h1 class="page-lead" style="font-size:34px;font-weight:700;">{lead}</h1>\n'
        f'    <p class="page-deck">{deck}</p>\n'
        f'    <p class="src">{srcline}</p>\n  </div>\n')

def override_css(show_rules):
    return ("<style>\n  /* focused-page overrides */\n"
        "  .topbar{display:none!important}\n"
        "  .intro,.glossary,.kpi-row{display:none!important}\n"
        "  main section{display:none!important}\n"
        f"  {show_rules}{{display:block!important}}\n"
        "  .method{display:none!important}\n"
        "  main section{margin-bottom:40px}\n</style>\n")

PAGES = [
  dict(file="geografia.html", active="geografia",
       show="main section:has(#s-mappa),section#s-nuts3", inject=True,
       badge="GEOGRAFIA",
       lead="La mappa degli aiuti, regione e provincia",
       deck=("Dove finiscono gli aiuti — o meglio, dove hanno sede legale i beneficiari. "
             "Prima per <strong>regione</strong> (tre letture: assoluto, pro capite, concentrazione), "
             "poi nel dettaglio di <strong>provincia (NUTS3)</strong>."),
       src=("<abbr title=\"Equivalente Sovvenzione Lorda\">ESL</abbr> per area di sede del beneficiario · "
            "la sede legale non sempre coincide con il luogo dell'investimento")),
  dict(file="controllate.html", active="controllate",
       show="main section:has(#s-soe)",
       badge="CONTROLLATE DI STATO",
       lead="Le società pubbliche che ricevono aiuti",
       deck=("Le imprese a partecipazione pubblica — controllate direttamente dal "
             "<abbr title=\"Ministero dell'Economia e delle Finanze\">MEF</abbr> o tramite "
             "<abbr title=\"Cassa Depositi e Prestiti\">CDP</abbr> — sono insieme tra i maggiori beneficiari "
             "e i principali erogatori di aiuti. Qui il perimetro completo, l'evoluzione, gli strumenti e la geografia."),
       src="Perimetro ufficiale Gruppo MEF (I–III livello) incrociato con i beneficiari <abbr title=\"Registro Nazionale Aiuti\">RNA</abbr>"),
  dict(file="quadro-giuridico.html", active="quadro",
       show="main section:has(#s-tipologie)",
       badge="QUADRO GIURIDICO",
       lead="Con quali regole si concedono gli aiuti",
       deck=("Ogni aiuto è autorizzato sotto un regime giuridico europeo — esenzione per categoria "
             "(<abbr title=\"General Block Exemption Regulation\">GBER</abbr>), quadri temporanei di crisi, "
             "de minimis — ed erogato con uno strumento (garanzia, sovvenzione, credito d'imposta). "
             "Qui il peso di ciascun regime e strumento e come è cambiato nel tempo."),
       src="<abbr title=\"Equivalente Sovvenzione Lorda\">ESL</abbr> per base giuridica e strumento · 2016–2025"),
  dict(file="green-digitale.html", active="green",
       show="main section:has(#s-green),main section:has(#s-digitale)",
       badge="GREEN &amp; DIGITALE",
       lead="La doppia transizione: ambiente e digitale",
       deck=("Quanto degli aiuti di Stato sostiene la transizione ecologica "
             "(€ 67,8 mld, 13,3%) e quella digitale (€ 30,7 mld, 6,0%), chi ne beneficia "
             "e come si distribuisce nel tempo."),
       src="Definizione larga green/energia e digitale · <abbr title=\"Equivalente Sovvenzione Lorda\">ESL</abbr> 2016–2025"),
]

A_STYLE = "  <style>\n    /* ── tokens"
A_BODY  = "<body>\n\n<div class=\"topbar\" id=\"topbar\">"
A_MAIN  = "<main>\n<div class=\"wrap\">\n"
A_END   = "\n</div>\n</main>"
for a, name in [(A_STYLE,"style"),(A_BODY,"body"),(A_MAIN,"main"),(A_END,"end")]:
    if src.count(a) != 1: sys.exit(f"ANCHOR ERROR: '{name}' x{src.count(a)}")

ok = []
for p in PAGES:
    out = src
    out = out.replace(A_STYLE, '  <link rel="stylesheet" href="assets/news.css">\n' + A_STYLE, 1)
    out = out.replace(A_BODY, "<body>\n\n" + subnav(p["active"]) + override_css(p["show"]) + '\n<div class="topbar" id="topbar">', 1)
    out = out.replace(A_MAIN, A_MAIN + hero(p["badge"], p["lead"], p["deck"], p["src"]) + "\n", 1)
    if p.get("inject"):
        out = out.replace(A_END, "\n" + NUTS3_BLOCK + A_END, 1)
    ttl = p['badge'].replace('&amp;', '&').title()
    out = out.replace("<title>RNA — Aiuti di Stato Italia 2023–2026</title>",
                      f"<title>{ttl} — Aiuti di Stato · RNA</title>", 1)
    (ROOT / "site" / p["file"]).write_text(out, encoding="utf-8")
    ok.append(f"{p['file']}  ({len(out)//1024} KB)")

print(f"NUTS3 provinces with data: {len(D_NUTS3)}  geometry: {len(geo['paths'])}  viewBox {geo['w']}x{geo['h']}")
print("Generated:\n  " + "\n  ".join(ok))
