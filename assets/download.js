/* RNA — per-figure data download. Adds a small "CSV" button to every
   Chart.js figure, the D3 sankey, and every KPI stat card, exporting the
   aggregated data behind it. Fully generic: chart data is read from the
   live Chart instance, sankey flows from the SVG's bound data, KPI values
   from the card markup — no per-page wiring. Decoupled asset, like i18n. */
(function () {
  // ---------- CSV helpers ----------
  function esc(v) { v = v == null ? '' : String(v); return /[",\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
  function toCSV(rows) { return rows.map(function (r) { return r.map(esc).join(','); }).join('\r\n'); }
  function slug(s) {
    return (s || 'dati').toLowerCase().replace(/[àáâ]/g, 'a').replace(/[èé]/g, 'e').replace(/[ìí]/g, 'i')
      .replace(/[òó]/g, 'o').replace(/[ùú]/g, 'u').replace(/[^\w]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'dati';
  }
  var used = {};
  function uniqueName(base) {
    var n = slug(base), k = n, i = 2;
    while (used[k]) { k = n + '-' + (i++); }
    used[k] = 1; return k + '.csv';
  }
  function save(name, csv) {
    var blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });   // BOM → Excel reads UTF-8
    var url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 150);
  }

  // ---------- button factory ----------
  function addBtn(host, title, builder) {
    if (!host) return;
    if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
    var n = host.querySelectorAll(':scope > .dl-btn').length;      // stack if a host holds several
    var b = document.createElement('button');
    b.className = 'dl-btn'; b.type = 'button';
    b.style.right = (8 + n * 60) + 'px';
    b.setAttribute('aria-label', 'Scarica i dati (CSV): ' + title);
    b.title = 'Scarica i dati in CSV';
    b.innerHTML = '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="M7 11l5 5 5-5"/><path d="M4 21h16"/></svg><span>CSV</span>';
    b.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      var csv = builder(); if (csv == null) return;
      save(uniqueName(title), csv);
    });
    host.appendChild(b);
  }

  // ---------- extractors ----------
  function chartToCSV(ch) {
    var d = ch.data || {}, ds = d.datasets || [], labels = d.labels || [];
    var xy = ds.length && Array.isArray(ds[0].data) && ds[0].data.length &&
      ds[0].data[0] && typeof ds[0].data[0] === 'object' && 'y' in ds[0].data[0];
    var rows = [];
    if (xy) {
      rows.push(['serie', 'x', 'y']);
      ds.forEach(function (s) { (s.data || []).forEach(function (p) { rows.push([s.label || '', p.x, p.y]); }); });
    } else {
      var head = ['']; ds.forEach(function (s, i) { head.push(s.label || ('serie ' + (i + 1))); });
      rows.push(head);
      var n = labels.length || ds.reduce(function (m, s) { return Math.max(m, (s.data || []).length); }, 0);
      for (var i = 0; i < n; i++) {
        var row = [labels[i] != null ? labels[i] : i];
        ds.forEach(function (s) { var v = s.data ? s.data[i] : ''; row.push(v && typeof v === 'object' ? (v.y != null ? v.y : JSON.stringify(v)) : (v == null ? '' : v)); });
        rows.push(row);
      }
    }
    return toCSV(rows);
  }

  function sankeyCSV() {
    var paths = document.querySelectorAll('#sankey path');
    var rows = [['origine', 'destinazione', 'valore_mld_eur']], ok = false;
    paths.forEach(function (p) {
      var d = p.__data__;
      if (d && d.source && d.target && typeof d.value !== 'undefined') {
        ok = true;
        rows.push([d.source.name != null ? d.source.name : d.source, d.target.name != null ? d.target.name : d.target, d.value]);
      }
    });
    return ok ? toCSV(rows) : null;
  }

  // ---------- wiring ----------
  function wireCharts() {
    if (!window.Chart || !Chart.instances) return;
    Object.keys(Chart.instances).forEach(function (id) {
      var ch = Chart.instances[id]; if (!ch || !ch.canvas) return;
      var host = ch.canvas.closest('.card') || ch.canvas.closest('.chart-h') || ch.canvas.parentElement;
      if (!host || host.querySelector(':scope > .dl-btn[data-cv="' + ch.canvas.id + '"]')) return;
      var card = ch.canvas.closest('.card');
      var tEl = card && card.querySelector('.card-title');
      var title = (tEl ? tEl.textContent : '') || ch.canvas.id || 'grafico';
      addBtn(host, title.trim(), function () { return chartToCSV(ch); });
      var mark = host.querySelector(':scope > .dl-btn:last-child'); if (mark) mark.setAttribute('data-cv', ch.canvas.id);
    });
  }

  function wireSankey() {
    var svg = document.getElementById('sankey'); if (!svg) return;
    var host = svg.closest('.card') || document.getElementById('sankey-wrap') || svg.parentElement;
    if (!host || host.querySelector(':scope > .dl-btn')) return;
    var card = svg.closest('.card'), tEl = card && card.querySelector('.card-title');
    addBtn(host, (tEl ? tEl.textContent.trim() : 'flussi-sankey'), sankeyCSV);
  }

  function wireKPIs() {
    document.querySelectorAll('.kpi').forEach(function (k) {
      if (k.querySelector(':scope > .dl-btn')) return;
      var label = (k.querySelector('.kpi-label') || {}).textContent || '';
      var val = (k.querySelector('.kpi-val') || {}).textContent || '';
      var sub = (k.querySelector('.kpi-sub') || {}).textContent || '';
      if (!val) return;
      addBtn(k, label.trim() || 'valore', function () {
        return toCSV([['indicatore', 'valore', 'nota'], [label.trim(), val.trim(), sub.trim()]]);
      });
    });
  }

  function wireAll() { try { wireCharts(); } catch (e) {} try { wireSankey(); } catch (e) {} try { wireKPIs(); } catch (e) {} }

  function init() {
    var css = '.dl-btn{position:absolute;top:8px;z-index:4;display:inline-flex;align-items:center;gap:4px;'
      + 'font-family:var(--mono,ui-monospace,monospace);font-size:10.5px;font-weight:600;letter-spacing:.03em;'
      + 'color:var(--amber,#1F5673);background:var(--card,#fff);border:1px solid rgba(31,86,115,.35);'
      + 'border-radius:5px;padding:3px 7px;cursor:pointer;opacity:.55;transition:opacity .15s,background .15s,color .15s;'
      + 'box-shadow:0 1px 4px -2px rgba(40,35,30,.4)}'
      + '.dl-btn:hover{opacity:1;background:var(--amber,#1F5673);color:#fff;border-color:var(--amber,#1F5673)}'
      + '.dl-btn svg{display:block}'
      + '.card:hover .dl-btn,.kpi:hover .dl-btn{opacity:.9}'
      + '@media print{.dl-btn{display:none}}';
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    wireAll();
    // catch charts / sankey rendered after DOMContentLoaded
    if (document.readyState === 'complete') setTimeout(wireAll, 120);
    else window.addEventListener('load', function () { setTimeout(wireAll, 120); });
  }

  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
