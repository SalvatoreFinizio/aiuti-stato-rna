/* RNA — IT/EN language toggle. Swaps DOM text + title/aria/placeholder/alt
   attributes against window.RNA_DICT (Italian → English). Originals are
   snapshotted so it toggles back. Preference persisted in localStorage.
   Chart.js <canvas> text (legends, axis titles, tick labels) is translated
   display-only — dataset.label / data are never mutated, so chart logic
   (tooltip callbacks that compare against Italian labels) stays intact.
   The D3 sankey renders SVG <text>, which lives in the DOM and is handled
   by the normal text-node swap. */
(function () {
  var KEY = 'rna_lang';
  var DICT = window.RNA_DICT || {};
  var TEXT = [], ATTR = [];
  var btn, lang = 'it';

  function norm(v) { return v.trim().replace(/\s+/g, ' '); }   // collapse newlines/indent

  function collect() {
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    var n;
    while ((n = w.nextNode())) {
      var v = n.nodeValue; if (!v) continue;
      var k = norm(v);
      if (k.length > 1 && DICT[k]) {
        var lead = v.match(/^\s*/)[0], trail = v.match(/\s*$/)[0];
        TEXT.push([n, v, lead, trail, k]);            // node, orig, leadWS, trailWS, key
      }
    }
    var A = ['title', 'aria-label', 'placeholder', 'alt'];
    document.querySelectorAll('[title],[aria-label],[placeholder],[alt]').forEach(function (el) {
      A.forEach(function (a) {
        var v = el.getAttribute(a); if (!v) return;
        var k = norm(v); if (DICT[k]) ATTR.push([el, a, v, k]);
      });
    });
  }

  // Display-only translation of Chart.js canvas text (legend + axis titles).
  // Snapshots live in a WeakMap — never stored on chart.options, which is a
  // reactive proxy that recurses if you hang custom props off it. We mutate
  // the raw config (chart.config.options) and call update(). dataset.label /
  // data are never touched, so tooltip-callback logic stays intact.
  function T(s) { return (lang === 'en' && typeof s === 'string' && DICT[s]) ? DICT[s] : s; }
  var SNAP = new WeakMap();   // options-node -> original strings

  function rawOptions(ch) {
    return (ch.config && ch.config.options) ? ch.config.options : ch.options;
  }

  function translateCharts() {
    if (!window.Chart || !Chart.instances) return;
    Object.keys(Chart.instances).forEach(function (id) {
      var ch = Chart.instances[id]; if (!ch) return;
      var o = rawOptions(ch); if (!o) return;

      var scales = o.scales || {};
      Object.keys(scales).forEach(function (sid) {
        var sc = scales[sid]; if (!sc) return;
        if (sc.title && typeof sc.title.text === 'string') {
          var s = SNAP.get(sc.title); if (!s) { s = { text: sc.title.text }; SNAP.set(sc.title, s); }
          sc.title.text = T(s.text);
        }
        if (!sc.ticks) sc.ticks = {};
        var ts = SNAP.get(sc.ticks);
        if (!ts) {                                   // wrap tick formatter once (category labels)
          ts = { cb: sc.ticks.callback || null }; SNAP.set(sc.ticks, ts);
          sc.ticks.callback = function (value, index, ticks) {
            var out = ts.cb ? ts.cb.call(this, value, index, ticks) : this.getLabelForValue(value);
            return T(out);
          };
        }
      });

      o.plugins = o.plugins || {};
      o.plugins.legend = o.plugins.legend || {};
      var lg = o.plugins.legend;
      lg.labels = lg.labels || {};
      var snap = SNAP.get(lg.labels);
      if (!snap) {                                   // wrap generateLabels once
        snap = { gen: lg.labels.generateLabels || null };
        SNAP.set(lg.labels, snap);
        lg.labels.generateLabels = function (chart) {
          var src = snap.gen || Chart.defaults.plugins.legend.labels.generateLabels;
          var items = src.call(this, chart) || [];
          items.forEach(function (it) { if (it && it.text) it.text = T(it.text); });
          return items;
        };
      }
      try { ch.update('none'); } catch (e) {}
    });
  }

  function apply(l) {
    lang = l;
    var en = l === 'en';
    TEXT.forEach(function (p) { p[0].nodeValue = en ? (p[2] + DICT[p[4]] + p[3]) : p[1]; });
    ATTR.forEach(function (p) { p[0].setAttribute(p[1], en ? DICT[p[3]] : p[2]); });
    translateCharts();
    document.documentElement.lang = en ? 'en' : 'it';
    try { localStorage.setItem(KEY, l); } catch (e) {}
    if (btn) { btn.textContent = en ? 'IT' : 'EN'; btn.title = en ? 'Passa all’italiano' : 'Switch to English'; }
  }

  // Re-scan for content rendered after init (D3 sankey, charts built on load).
  // Restore Italian first so re-collected originals are the true source text.
  function refresh() {
    var cur = lang;
    apply('it');
    TEXT = []; ATTR = [];
    collect();
    apply(cur);
  }

  function init() {
    var css = '#rna-lang{position:fixed;top:9px;right:14px;z-index:300;font-family:var(--mono,ui-monospace,monospace);'
      + 'font-size:12px;font-weight:500;letter-spacing:.04em;color:var(--amber,#1F5673);background:var(--card,#fff);'
      + 'border:1px solid var(--amber,#1F5673);border-radius:5px;padding:4px 11px;min-height:26px;cursor:pointer;'
      + 'box-shadow:0 2px 10px -3px rgba(40,35,30,.25);transition:background .15s,color .15s}'
      + '#rna-lang:hover{background:var(--amber,#1F5673);color:#fff}'
      + '@media(max-width:560px){#rna-lang{top:7px;right:10px;padding:3px 9px;font-size:11px}}';
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    btn = document.createElement('button'); btn.id = 'rna-lang'; btn.type = 'button';
    btn.addEventListener('click', function () {
      apply((localStorage.getItem(KEY) === 'en') ? 'it' : 'en');
    });
    document.body.appendChild(btn);
    collect();
    var saved = 'it';
    try { saved = localStorage.getItem(KEY) || 'it'; } catch (e) {}
    apply(saved);
    // catch late-rendered charts / sankey
    if (document.readyState === 'complete') setTimeout(refresh, 60);
    else window.addEventListener('load', function () { setTimeout(refresh, 60); });
  }

  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
