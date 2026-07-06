/* RNA — IT/EN language toggle. Swaps DOM text + title/aria/placeholder/alt
   attributes against window.RNA_DICT (Italian → English). Originals are
   snapshotted so it toggles back. Preference persisted in localStorage.
   Chart text drawn on <canvas> is not translated (out of DOM). */
(function () {
  var KEY = 'rna_lang';
  var DICT = window.RNA_DICT || {};
  var TEXT = [], ATTR = [], btn;

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

  function apply(lang) {
    var en = lang === 'en';
    TEXT.forEach(function (p) { p[0].nodeValue = en ? (p[2] + DICT[p[4]] + p[3]) : p[1]; });
    ATTR.forEach(function (p) { p[0].setAttribute(p[1], en ? DICT[p[3]] : p[2]); });
    document.documentElement.lang = en ? 'en' : 'it';
    try { localStorage.setItem(KEY, lang); } catch (e) {}
    if (btn) { btn.textContent = en ? 'IT' : 'EN'; btn.title = en ? 'Passa all’italiano' : 'Switch to English'; }
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
  }

  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
