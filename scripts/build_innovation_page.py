#!/usr/bin/env python3
import json, pathlib
ROOT = pathlib.Path("/Users/salvatorefinizio/Library/CloudStorage/OneDrive-LondonSchoolofEconomics/aiuti_stato")
data = json.loads((ROOT/"data/generated/innovation.json").read_text())
geo  = json.loads((ROOT/"data/generated/nuts3_paths.json").read_text())
m = data["meta"]
byyear = data.get("by_year")  # optional {year: n_families}

TIME_SECTION = ""
TIME_DATA = "null"
if byyear:
    TIME_DATA = json.dumps(byyear, separators=(",",":"))
    TIME_SECTION = '''
  <section id="iv-time">
    <div class="sec-hd">
      <h2>⑤ L'innovazione nel tempo</h2>
      <span class="sec-note">Famiglie brevettuali delle imprese beneficiarie · per anno di primo deposito</span>
    </div>
    <div class="card">
      <div class="card-title">Famiglie brevettuali per anno di primo deposito (earliest filing year)</div>
      <div class="card-sub">Solo imprese che hanno ricevuto aiuti di Stato · fonte: PATSTAT TLS201</div>
      <div class="chart-h" style="height:340px;"><canvas id="ivTimeChart"></canvas></div>
    </div>
    <p class="note" style="max-width:900px;">Il deposito dei brevetti precede in gran parte il periodo degli aiuti registrati nell'RNA: misura la <em>propensione a innovare</em> delle imprese aiutate, non un effetto causale dell'aiuto. <strong>Il calo dopo il 2021</strong> riflette il ritardo di pubblicazione dei brevetti (le domande più recenti non sono ancora tutte nei dati PATSTAT), non una flessione reale.</p>
  </section>'''

# ── ⑥ Imprese di Stato (SOE patents) — rendered if data["soe"] present ──
soe = data.get("soe")
SOE_SECTION = ""; SOE_DATA = "null"; SOE_NAV = ""
if soe:
    SOE_DATA = json.dumps(soe, ensure_ascii=False, separators=(",", ":"))
    SOE_NAV = '<a href="#iv-soe">⑥ Imprese di Stato</a>'
    nf = f"{soe['meta']['n_families']:,}".replace(",", "."); ne = soe['meta']['n_entities']
    trends_card = ('''
    <div class="card" style="margin-top:12px;">
      <div class="card-title">I brevetti delle imprese di Stato nel tempo</div>
      <div class="card-sub">Famiglie brevettuali per anno di primo deposito · fonte PATSTAT TLS201</div>
      <div class="chart-h" style="height:300px;"><canvas id="ivSoeTimeChart"></canvas></div>
    </div>''' if soe.get("by_year") else "")
    tech_card = ('''
    <div class="card" style="margin-top:12px;">
      <div class="card-title">Le tecnologie delle imprese di Stato</div>
      <div class="card-sub">Sottoclassi tecnologiche (<abbr title="Cooperative Patent Classification">CPC</abbr>) più frequenti nei brevetti delle prime imprese di Stato · fonte PATSTAT TLS224</div>
      <div class="chart-h" style="height:430px;"><canvas id="ivSoeTechChart"></canvas></div>
    </div>''' if soe.get("techs") else "")
    SOE_SECTION = ('''
  <section id="iv-soe">
    <div class="sec-hd"><h2>⑥ I brevetti delle imprese di Stato</h2><span class="sec-note">società a controllo pubblico · ''' + nf + ''' famiglie</span></div>
    <p class="note" style="margin:0 0 16px;max-width:880px;">L'innovazione pubblica è <strong>concentratissima</strong>: tra i beneficiari a controllo statale solo <strong>''' + str(ne) + ''' imprese</strong> detengono brevetti, e una sola — <strong>STMicroelectronics</strong> (microelettronica, partecipata MEF) — vale circa l'80% delle famiglie. Seguono i campioni industriali strategici: Leonardo (difesa e spazio), Versalis/ENI (chimica), Ansaldo Energia (turbine), Enel, Fincantieri.</p>
    <div class="card">
      <div class="card-title">I maggiori detentori di brevetti tra le imprese di Stato</div>
      <div class="card-sub">Famiglie brevettuali · imprese a controllo pubblico con almeno 2 brevetti</div>
      <div class="chart-h" style="height:420px;"><canvas id="ivSoeFirmChart"></canvas></div>
    </div>''' + trends_card + tech_card + '''
  </section>''')

TPL = r'''<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Innovazione — Aiuti di Stato · RNA</title>
  <meta name="description" content="L'aiuto di Stato raggiunge chi innova? I beneficiari incrociati con i loro brevetti (PATSTAT): imprese, settori e geografia dell'innovazione.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=DM+Mono:wght@400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/news.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    #iv-metric .n3btn{font-size:12px;color:var(--muted);background:none;border:1px solid var(--border);border-radius:4px;padding:6px 13px;cursor:pointer;min-height:32px;transition:color .15s,border-color .15s,background .15s;}
    #iv-metric .n3btn:hover{color:var(--text);border-color:var(--dim);}
    #iv-metric .n3btn.n3-active{color:#fff;background:var(--teal);border-color:var(--teal);}
    .split-bar{display:flex;height:34px;border-radius:5px;overflow:hidden;border:1px solid var(--border);font-size:11px;font-family:var(--mono);}
    .split-bar > div{display:flex;align-items:center;justify-content:center;color:#fff;white-space:nowrap;}
  </style>
</head>
<body>

<div class="subnav-wrap">
  <div class="wrap subnav">
    <a class="page-back" href="./index.html">← Tutti i temi</a>
    <nav class="subnav-links" aria-label="Navigazione temi">
      <a href="./panorama.html">Panorama</a>
      <a href="./geografia.html">Geografia</a>
      <a href="./controllate.html">Controllate di Stato</a>
      <a href="./quadro-giuridico.html">Quadro giuridico</a>
      <a href="./green-digitale.html">Green &amp; digitale</a>
      <a href="./innovazione.html" class="active" aria-current="page">Innovazione</a>
      <a href="./esploratore.html" style="color:var(--amber);">Esploratore ↗</a>
    </nav>
  </div>
</div>

<main>
<div class="wrap">

  <div class="home-hero">
    <div class="hdr-badge" style="display:inline-block;margin-bottom:14px;">INNOVAZIONE</div>
    <h1 class="page-lead" style="font-size:34px;font-weight:700;">L'aiuto di Stato raggiunge chi innova?</h1>
    <p class="page-deck">
      Incrociando i beneficiari con i loro <strong>brevetti</strong> (famiglie DOCDB di PATSTAT, via codice Orbis BvD):
      solo l'<strong>1,6% delle imprese aiutate</strong> detiene brevetti, ma cattura il <strong>10,7% dell'aiuto</strong>.
      <strong>STMicroelectronics</strong> da sola pesa 7.127 famiglie brevettuali e € 2,6 mld di aiuti.
    </p>
    <p class="src">~124.800 famiglie brevettuali collegate ai beneficiari <abbr title="Registro Nazionale Aiuti">RNA</abbr> · aiuto = <abbr title="Equivalente Sovvenzione Lorda">ESL</abbr> agganciato all'universo Orbis (88,8%)</p>
    <nav class="subnav-links" style="margin-left:0;margin-top:18px;gap:6px;" aria-label="Sezioni">
      <a href="#iv-quanto">① Quanto</a><a href="#iv-chi">② Chi</a><a href="#iv-settori">③ Settori</a><a href="#iv-mappa">④ Dove</a>%%TIMENAV%%%%SOENAV%%
    </nav>
  </div>

  <!-- ① QUANTO -->
  <section id="iv-quanto">
    <div class="sec-hd"><h2>① Quanto aiuto va a chi innova</h2><span class="sec-note">imprese con almeno un brevetto vs. resto</span></div>
    <div class="kpi-row" style="margin-bottom:22px;">
      <div class="kpi"><div class="kpi-label">Beneficiari che brevettano</div><div class="kpi-val">%%PCTFIRMS%% %</div><div class="kpi-sub">%%NPAT%% su %%NFIRMS%% imprese</div></div>
      <div class="kpi"><div class="kpi-label">Quota di aiuto che ricevono</div><div class="kpi-val">%%PCTESL%% %</div><div class="kpi-sub">€ %%PATESL%% mld su %%TOTESL%% mld</div></div>
      <div class="kpi"><div class="kpi-label">Famiglie brevettuali</div><div class="kpi-val">%%FAMK%%</div><div class="kpi-sub">collegamenti impresa–brevetto</div></div>
      <div class="kpi"><div class="kpi-label">Primo innovatore</div><div class="kpi-val">7.127</div><div class="kpi-sub">famiglie · STMicroelectronics</div></div>
    </div>
    <div class="card">
      <div class="card-title">€ %%TOTESL%% mld di aiuto agganciato · dove va, per tipo di impresa</div>
      <div class="split-bar" style="margin-top:14px;">
        <div style="width:%%PCTESL%%%;background:var(--teal);" title="Imprese che brevettano">brevettano · € %%PATESL%% mld (%%PCTESL%%%)</div>
        <div style="flex:1;background:var(--steel);" title="Altre imprese">altre imprese · € %%RESTESL%% mld</div>
      </div>
    </div>
  </section>

  <!-- ② CHI -->
  <section id="iv-chi">
    <div class="sec-hd"><h2>② Chi innova tra i beneficiari</h2><span class="sec-note">prime 20 imprese per famiglie brevettuali</span></div>
    <div class="card">
      <div class="card-title">Top 20 beneficiari per numero di famiglie brevettuali</div>
      <div class="card-sub">Passa il mouse per aiuto ricevuto, settore e provincia · <span style="color:var(--teal);">le università innovano con aiuti quasi nulli</span></div>
      <div class="chart-h" style="height:560px;"><canvas id="ivFirmChart"></canvas></div>
    </div>
  </section>

  <!-- ③ SETTORI -->
  <section id="iv-settori">
    <div class="sec-hd"><h2>③ Lo scarto settoriale</h2><span class="sec-note">quota sugli aiuti vs quota sui brevetti · ATECO</span></div>
    <div class="card">
      <div class="card-title">Aiuto e innovazione per settore (<abbr title="Classificazione delle Attività Economiche">ATECO</abbr>)</div>
      <div class="card-sub">Per ogni settore, la <span style="color:var(--steel);">●&nbsp;quota sugli aiuti</span> e la <span style="color:var(--teal);">●&nbsp;quota sui brevetti</span>: la distanza tra i due punti è lo <strong>scarto</strong> · scala logaritmica</div>
      <div class="chart-h" style="height:%%SECTH%%px;"><canvas id="ivSectChart"></canvas></div>
      <p class="note" style="margin-top:12px;max-width:900px;">In alto i settori che <span style="color:var(--teal);">innovano più di quanto ricevono</span> — macchinari (16,7% dei brevetti, 3,1% degli aiuti) ed elettronica (8,5% vs 1,4%). In basso quelli che <span style="color:var(--steel);">ricevono più di quanto innovano</span> — commercio, energia, ristorazione, costruzioni: settori di micro-imprese e ditte individuali.</p>
    </div>
  </section>

  <!-- ④ DOVE -->
  <section id="iv-mappa">
    <div class="sec-hd"><h2>④ La geografia dell'innovazione</h2><span class="sec-note">famiglie brevettuali per provincia (NUTS3)</span></div>
    <p class="note" style="margin:0 0 16px;max-width:880px;">La cintura dell'innovazione: <strong>Milano</strong> e <strong>Monza-Brianza</strong> (STMicro), poi <strong>Bologna</strong>, <strong>Torino</strong>, <strong>Brescia</strong> e il cluster veneto (Vicenza, Padova, Treviso). Da confrontare con la <a href="./geografia.html" style="color:var(--teal);">mappa degli aiuti</a>: <strong>Roma</strong> riceve molto aiuto ma brevetta poco.</p>
    <div class="metric-sel" id="iv-metric" role="group" aria-label="Metrica mappa innovazione">
      <span class="metric-lab">Vista</span>
      <button class="n3btn n3-active" data-m="fam" type="button">Famiglie totali</button>
      <button class="n3btn" data-m="perfirm" type="button">Per 1.000 imprese</button>
    </div>
    <div class="map-grid">
      <div class="map-card">
        <div class="map-wrap" style="height:auto;"><svg id="iv-map" style="width:100%;height:auto;display:block;"></svg></div>
        <div class="legend-bins" id="iv-legend"></div>
        <div class="legend-labels" id="iv-legend-lab"></div>
      </div>
      <div class="map-card">
        <div class="card-title">Prime 15 province</div>
        <div class="card-sub" id="iv-list-sub">per famiglie brevettuali</div>
        <div class="map-list" id="iv-list"></div>
      </div>
    </div>
    <div class="map-tooltip" id="iv-tip" role="tooltip" aria-live="polite"></div>
  </section>
%%TIMESECTION%%
%%SOESECTION%%
</div>
</main>

<footer>
  <div class="wrap"><div class="foot">
    <span><abbr title="Registro Nazionale Aiuti di Stato">RNA</abbr> Aiuti di Stato × PATSTAT · Elaborazione propria</span>
    <div class="foot-links"><a href="index.html">Home</a><a href="geografia.html">Geografia</a><a href="esploratore.html">Esploratore</a></div>
  </div></div>
</footer>

<script>
Chart.defaults.color='#9A938A'; Chart.defaults.font.family="'DM Sans', system-ui, sans-serif"; Chart.defaults.font.size=11;
Chart.defaults.plugins.tooltip.backgroundColor='#FBFAF6'; Chart.defaults.plugins.tooltip.borderColor='#E4E0D7';
Chart.defaults.plugins.tooltip.borderWidth=1; Chart.defaults.plugins.tooltip.padding=10; Chart.defaults.plugins.tooltip.cornerRadius=4;
Chart.defaults.plugins.tooltip.titleColor='#1A1A17'; Chart.defaults.plugins.tooltip.bodyColor='#56524C';
var GRID='rgba(205,199,188,.7)';
var TOP=%%TOPFIRMS%%, SECT=%%SECTORS%%, NUTS=%%NUTS%%, GEOM=%%GEOM%%, BYYEAR=%%TIMEDATA%%, SOE=%%SOE%%;

/* ② top firms */
(function(){
  var lab=TOP.map(function(t){return t.nm;}), val=TOP.map(function(t){return t.fam;});
  new Chart(document.getElementById('ivFirmChart'),{type:'bar',
    data:{labels:lab,datasets:[{data:val,backgroundColor:TOP.map(function(t){return t.esl>=50?'rgba(31,86,115,.85)':'rgba(78,138,107,.82)';}),borderRadius:2,borderSkipped:false}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,animation:{duration:700},
      plugins:{legend:{display:false},tooltip:{callbacks:{
        label:function(c){return c.parsed.x.toLocaleString('it-IT')+' famiglie brevettuali';},
        afterLabel:function(c){var t=TOP[c.dataIndex];return 'Aiuto: € '+t.esl.toLocaleString('it-IT')+' mln · ATECO '+t.ateco+' · '+t.prov;}}}},
      scales:{x:{grid:{color:GRID},ticks:{color:'#9A938A'},border:{display:false}},
        y:{grid:{display:false},ticks:{color:'#56524C',font:{size:10}},border:{display:false}}}}});
})();

/* ③ sector dumbbell: aid share vs patent share per ATECO sector */
(function(){
  var S=SECT;  // pre-selected & sorted (highest scarto first) in the builder
  var labels=S.map(function(s){return s.disp;});
  var byLab={}; S.forEach(function(s){byLab[s.disp]=s;});
  var aiuti=S.map(function(s){return {x:Math.max(s.as,0.25),y:s.disp};});
  var brev =S.map(function(s){return {x:Math.max(s.ps,0.25),y:s.disp};});
  var connector={id:'conn',beforeDatasetsDraw:function(ch){
    var ctx=ch.ctx,m0=ch.getDatasetMeta(0).data,m1=ch.getDatasetMeta(1).data; ctx.save(); ctx.lineWidth=2.4;
    for(var i=0;i<m0.length;i++){var a=m0[i],b=m1[i]; if(!a||!b)continue;
      ctx.strokeStyle=(b.x>=a.x)?'rgba(78,138,107,.45)':'rgba(127,151,166,.5)';
      ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();}
    ctx.restore();}};
  new Chart(document.getElementById('ivSectChart'),{type:'scatter',
    data:{labels:labels,datasets:[
      {label:'Quota sugli aiuti',data:aiuti,backgroundColor:'rgba(127,151,166,.95)',pointRadius:6,pointHoverRadius:8},
      {label:'Quota sui brevetti',data:brev,backgroundColor:'rgba(78,138,107,.95)',pointRadius:6,pointHoverRadius:8}]},
    options:{responsive:true,maintainAspectRatio:false,layout:{padding:{right:10}},
      plugins:{legend:{display:true,position:'top',align:'start',labels:{usePointStyle:true,boxWidth:8,padding:16,color:'#56524C'}},
        tooltip:{callbacks:{title:function(i){var s=byLab[i[0].raw.y];return s.lab+' · '+s.code;},
          label:function(c){return c.dataset.label+': '+c.raw.x.toFixed(1)+'%';},
          afterBody:function(i){var s=byLab[i[0].raw.y];return 'scarto '+((s.ps-s.as)>=0?'+':'')+(s.ps-s.as).toFixed(1)+' pp · € '+s.esl+' mld aiuti';}}}},
      scales:{
        x:{type:'logarithmic',position:'top',min:0.2,suggestedMax:20,title:{display:true,text:'quota sul totale (%) · scala logaritmica',color:'#8C867B'},
           grid:{color:GRID},ticks:{color:'#9A938A',callback:function(v){return [0.5,1,2,5,10,20].indexOf(v)>=0?v+'%':'';}},border:{display:false}},
        y:{type:'category',labels:labels,grid:{display:false},ticks:{color:'#56524C',font:{size:10.5},autoSkip:false},border:{display:false}}}},
    plugins:[connector]});
})();

/* ④ NUTS3 innovation map */
(function(){
  var svg=document.getElementById('iv-map'); if(!svg) return;
  var NS='http://www.w3.org/2000/svg'; svg.setAttribute('viewBox','0 0 '+GEOM.w+' '+GEOM.h);
  var tip=document.getElementById('iv-tip');
  var COLORS=['#E9ECDF','#CBD8B8','#9DBE86','#6E9E5A','#3E7A3E'], NOFILL='#F0ECE3';
  var metric='fam', bins=[], vmin=0, els={};
  function val(c){var d=NUTS[c]; if(!d) return null; if(metric==='fam') return d.fam; return d.nf? d.fam/d.nf*1000 : null;}
  function it(n,dec){return n.toFixed(dec).replace('.',',');}
  Object.keys(GEOM.paths).forEach(function(c){
    var p=document.createElementNS(NS,'path'); p.setAttribute('d',GEOM.paths[c]); p.setAttribute('class','map-region');
    p.addEventListener('mousemove',function(e){showTip(e,c);}); p.addEventListener('mouseleave',function(){tip.style.display='none';});
    svg.appendChild(p); els[c]=p;
  });
  function showTip(e,c){var d=NUTS[c]; tip.style.display='block'; tip.style.left=(e.clientX+14)+'px'; tip.style.top=(e.clientY+14)+'px';
    if(!d){tip.innerHTML='<strong>'+c+'</strong><div class="tt-sub">nessun beneficiario brevettante</div>';return;}
    tip.innerHTML='<strong>'+d.nm+'</strong><div class="tt-esl" style="color:var(--teal);">'+d.fam.toLocaleString('it-IT')+' famiglie</div>'+
      '<div class="tt-sub">'+d.pf.toLocaleString('it-IT')+' imprese brevettano · '+(d.fam/d.nf*1000).toFixed(0)+' ogni 1.000 imprese</div>';}
  function quant(){var vs=Object.keys(GEOM.paths).map(val).filter(function(v){return v!=null;}).sort(function(a,b){return a-b;});
    vmin=vs[0];bins=[];for(var i=1;i<5;i++)bins.push(vs[Math.floor(vs.length*i/5)]);}
  function bi(v){if(v==null)return -1;for(var i=0;i<bins.length;i++){if(v<=bins[i])return i;}return 4;}
  function paint(){quant();
    Object.keys(GEOM.paths).forEach(function(c){var k=bi(val(c));els[c].setAttribute('fill',k<0?NOFILL:COLORS[k]);});
    var lg=document.getElementById('iv-legend');lg.innerHTML='';COLORS.forEach(function(col){var d=document.createElement('div');d.className='legend-bin';d.style.background=col;lg.appendChild(d);});
    var dec=metric==='fam'?0:1;var edges=[vmin].concat(bins).map(function(b){return metric==='fam'?Math.round(b):it(b,dec);});
    document.getElementById('iv-legend-lab').innerHTML=edges.map(function(x){return '<span>'+x+'</span>';}).join('');
    document.getElementById('iv-list-sub').textContent=metric==='fam'?'per famiglie brevettuali':'per famiglie ogni 1.000 imprese';
    var arr=Object.keys(NUTS).map(function(c){return {c:c,v:val(c),d:NUTS[c]};}).filter(function(o){return o.v!=null;}).sort(function(a,b){return b.v-a.v;}).slice(0,15);
    document.getElementById('iv-list').innerHTML=arr.map(function(o,i){var vv=metric==='fam'?o.d.fam.toLocaleString('it-IT'):it(o.v,1);
      return '<div class="map-row"><span class="map-rank">'+(i+1)+'</span><span class="map-name">'+o.d.nm+'</span><span class="map-val" style="color:var(--teal);">'+vv+'</span></div>';}).join('');}
  document.querySelectorAll('#iv-metric .n3btn').forEach(function(b){b.addEventListener('click',function(){
    document.querySelectorAll('#iv-metric .n3btn').forEach(function(x){x.classList.remove('n3-active');});
    b.classList.add('n3-active');metric=b.getAttribute('data-m');paint();});});
  paint();
})();

/* ⑤ time */
if(BYYEAR){(function(){
  var el=document.getElementById('ivTimeChart'); if(!el) return;
  var ys=Object.keys(BYYEAR).map(Number).filter(function(y){return y>=1990&&y<=2024;}).sort(function(a,b){return a-b;});
  new Chart(el,{type:'bar',data:{labels:ys,datasets:[{data:ys.map(function(y){return BYYEAR[y];}),backgroundColor:'rgba(78,138,107,.8)',borderRadius:1}]},
    options:{responsive:true,maintainAspectRatio:false,animation:{duration:600},
      plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return c.parsed.y.toLocaleString('it-IT')+' famiglie';}}}},
      scales:{x:{grid:{display:false},ticks:{color:'#56524C',font:{size:9},maxRotation:0,autoSkip:true,maxTicksLimit:12},border:{display:false}},
        y:{grid:{color:GRID},ticks:{color:'#9A938A'},border:{display:false}}}}});
})();}

/* ⑥ imprese di Stato */
if(SOE){
  (function(){
    var E=SOE.entities.filter(function(e){return e.fam>=2;});
    new Chart(document.getElementById('ivSoeFirmChart'),{type:'bar',
      data:{labels:E.map(function(e){return e.nm;}),datasets:[{data:E.map(function(e){return e.fam;}),
        backgroundColor:E.map(function(e,i){return i===0?'rgba(31,86,115,.88)':'rgba(78,138,107,.82)';}),borderRadius:2,borderSkipped:false}]},
      options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,animation:{duration:700},
        plugins:{legend:{display:false},tooltip:{callbacks:{
          label:function(c){return c.parsed.x.toLocaleString('it-IT')+' famiglie brevettuali';},
          afterLabel:function(c){var e=E[c.dataIndex];return 'Gruppo: '+e.grp+' · aiuti € '+e.esl.toLocaleString('it-IT')+' mld';}}}},
        scales:{x:{grid:{color:GRID},ticks:{color:'#9A938A'},border:{display:false}},
          y:{grid:{display:false},ticks:{color:'#56524C',font:{size:10.5}},border:{display:false}}}}});
  })();
  if(SOE.by_year){(function(){
    var el=document.getElementById('ivSoeTimeChart'); if(!el) return;
    var ys=Object.keys(SOE.by_year).map(Number).filter(function(y){return y>=1990&&y<=2024;}).sort(function(a,b){return a-b;});
    new Chart(el,{type:'bar',data:{labels:ys,datasets:[{data:ys.map(function(y){return SOE.by_year[y];}),backgroundColor:'rgba(31,86,115,.8)',borderRadius:1}]},
      options:{responsive:true,maintainAspectRatio:false,animation:{duration:600},
        plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return c.parsed.y.toLocaleString('it-IT')+' famiglie';}}}},
        scales:{x:{grid:{display:false},ticks:{color:'#56524C',font:{size:9},maxRotation:0,autoSkip:true,maxTicksLimit:12},border:{display:false}},
          y:{grid:{color:GRID},ticks:{color:'#9A938A'},border:{display:false}}}}});
  })();}
  if(SOE.techs){(function(){
    var el=document.getElementById('ivSoeTechChart'); if(!el) return;
    var T=SOE.techs;
    new Chart(el,{type:'bar',data:{labels:T.map(function(t){return t.lab;}),datasets:[{data:T.map(function(t){return t.n;}),
      backgroundColor:'rgba(127,151,166,.85)',borderRadius:2,borderSkipped:false}]},
      options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,animation:{duration:700},
        plugins:{legend:{display:false},tooltip:{callbacks:{
          title:function(i){return T[i[0].dataIndex].lab;},
          label:function(c){return c.parsed.x.toLocaleString('it-IT')+' famiglie · CPC '+T[c.dataIndex].cpc;}}}},
        scales:{x:{grid:{color:GRID},ticks:{color:'#9A938A'},border:{display:false}},
          y:{grid:{display:false},ticks:{color:'#56524C',font:{size:10}},border:{display:false}}}}});
  })();}
}
</script>
</body>
</html>
'''

rest_esl = round(m["tot_esl_mld"] - m["pat_esl_mld"], 1)

# curate sectors for the dumbbell: material sectors, both extremes of "scarto"
mat = [s for s in data["sectors"] if s["as"] >= 0.8 or s["ps"] >= 0.8]
mat.sort(key=lambda s: -(s["ps"] - s["as"]))            # highest scarto first
sel = (mat[:13] + mat[-11:]) if len(mat) > 24 else mat   # top innovators + most aid-heavy
for s in sel:
    s["disp"] = s["code"] + "  " + s["lab"]
sect_h = len(sel) * 26 + 120

html = (TPL
  .replace("%%SECTH%%", str(sect_h))
  .replace("%%TIMESECTION%%", TIME_SECTION)
  .replace("%%SOESECTION%%", SOE_SECTION)
  .replace("%%TIMENAV%%", '<a href="#iv-time">⑤ Tempo</a>' if byyear else "")
  .replace("%%SOENAV%%", SOE_NAV)
  .replace("%%SOE%%", SOE_DATA)
  .replace("%%TIMEDATA%%", TIME_DATA)
  .replace("%%PCTFIRMS%%", "1,6")
  .replace("%%NPAT%%", f"{m['n_pat_firms']:,}".replace(",", "."))
  .replace("%%NFIRMS%%", "1,58 mln")
  .replace("%%PCTESL%%", str(m["pat_esl_pct"]).replace(".", ","))
  .replace("%%PATESL%%", str(m["pat_esl_mld"]).replace(".", ","))
  .replace("%%TOTESL%%", str(m["tot_esl_mld"]).replace(".", ","))
  .replace("%%RESTESL%%", str(rest_esl).replace(".", ","))
  .replace("%%FAMK%%", f"{m['fam_links']:,}".replace(",", "."))
  .replace("%%TOPFIRMS%%", json.dumps(data["top_firms"][:20], ensure_ascii=False, separators=(",",":")))
  .replace("%%SECTORS%%", json.dumps(sel, ensure_ascii=False, separators=(",",":")))
  .replace("%%NUTS%%", json.dumps(data["nuts3"], ensure_ascii=False, separators=(",",":")))
  .replace("%%GEOM%%", json.dumps({"w":geo["w"],"h":geo["h"],"paths":geo["paths"]}, separators=(",",":"))))
(ROOT/"site/innovazione.html").write_text(html, encoding="utf-8")
print(f"innovazione.html written ({len(html)//1024} KB)  time-section: {'yes' if byyear else 'no (pending TLS201)'}")
