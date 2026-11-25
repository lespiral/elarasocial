// Elara Social · menú del mòbil, enllaços directes a seccions, desplegables «Vés directament a…» i títols que es mouen
(function () {
  window.elaraMoviment = true;

  // Títols que es mouen (només sense «reduir moviment»; els estils són a site.css, «Moviment»)
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce) {
    // El títol de la capçalera surt paraula a paraula
    Array.prototype.forEach.call(document.querySelectorAll('.pagehead h1, .hero__title'), function (h) {
      var i = 0;
      (function split(node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (n) {
          if (n.nodeType === 3) {
            var frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach(function (part) {
              if (!part) return;
              if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
              var w = document.createElement('span');
              w.className = 'w';
              w.style.setProperty('--i', i++);
              w.textContent = part;
              frag.appendChild(w);
            });
            node.replaceChild(frag, n);
          } else if (n.nodeType === 1) split(n);
        });
      })(h);
      h.classList.add('is-split');
    });
    // Cada títol de secció puja i es dibuixa la línia de sota quan arriba a la pantalla
    var titles = document.querySelectorAll('.band__kicker, .band__title');
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
        });
      }, { rootMargin: '0px 0px -10% 0px' });
      Array.prototype.forEach.call(titles, function (t) { io.observe(t); });
    } else {
      Array.prototype.forEach.call(titles, function (t) { t.classList.add('is-in'); });
    }
  }

  var bar = document.querySelector('.topbar');
  var btn = document.querySelector('.menu-btn');
  if (bar && btn) {
    btn.addEventListener('click', function () {
      var open = bar.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? (btn.getAttribute('data-label-close') || 'Tanca el menú') : (btn.getAttribute('data-label-open') || 'Obre el menú'));
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && bar.classList.contains('is-open')) { btn.click(); btn.focus(); }
    });
  }

  // Si l'adreça porta a una pregunta o un lloc plegat (p. ex. /pagina/#una-pregunta), obre el desplegable que el conté
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    var d = el.closest('details');
    var opened = false;
    while (d) { if (!d.open) { d.open = true; opened = true; } d = d.parentElement && d.parentElement.closest('details'); }
    if (el.tagName === 'DETAILS' && !el.open) { el.open = true; opened = true; }
    if (opened) el.scrollIntoView();
  }
  window.addEventListener('hashchange', openTarget);
  openTarget();

  // Desplegables «Vés directament a…»: porten al lloc triat dins la mateixa pàgina
  Array.prototype.forEach.call(document.querySelectorAll('select[data-jump]'), function (sel) {
    sel.addEventListener('change', function () {
      var id = sel.value;
      var el = id && document.getElementById(id);
      if (!el) return;
      if (decodeURIComponent(location.hash.slice(1)) === id) el.scrollIntoView();
      else location.hash = id;
      // El focus va al lloc triat (al primer enllaç de la targeta, si n'hi ha), perquè el teclat i els lectors de pantalla continuïn des d'allà
      var f = el.querySelector('.card__link') || el;
      if (f === el) { el.setAttribute('tabindex', '-1'); el.setAttribute('data-jump-target', ''); }
      try { f.focus({ preventScroll: true }); } catch (e) { f.focus(); }
      sel.value = '';
    });
  });
  // Formats de la portada: a l'ordinador, tot obert; al mòbil i a la tauleta, plegats (només el primer, obert)
  (function () {
    var fmts = Array.prototype.slice.call(document.querySelectorAll('.formats:not(.formats--list) .fmt'));
    if (!fmts.length || !window.matchMedia) return;
    var wide = window.matchMedia('(min-width: 1100px)');
    function apply() {
      fmts.forEach(function (d, i) { d.open = wide.matches ? true : (i === 0 ? true : d.open && d.dataset.touched === '1'); d.classList.toggle('fmt--static', wide.matches); });
    }
    fmts.forEach(function (d) {
      var sum = d.querySelector('summary');
      sum.addEventListener('click', function (e) { if (wide.matches) { e.preventDefault(); return; } d.dataset.touched = '1'; });
    });
    // Es plega un cop les escenes ja s'han construït (el seu codi corre a DOMContentLoaded, abans d'aquest)
    if (document.readyState === 'complete') apply(); else document.addEventListener('DOMContentLoaded', apply);
    if (wide.addEventListener) wide.addEventListener('change', apply); else if (wide.addListener) wide.addListener(apply);
  })();

  // Persones: els enllaços cap a una targeta (#prop-…) l'obren i hi porten; si la pàgina s'obre amb aquesta ancora, també
  (function () {
    var reduceM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function card(id) { var el = id && document.getElementById(id); return el && el.matches && el.matches('.formats--list details.fmt') ? el : null; }
    function openCard(el, hash) {
      el.open = true;
      el.scrollIntoView({ behavior: reduceM ? 'auto' : 'smooth', block: 'start' });
      var sum = el.querySelector('summary'); if (sum) { try { sum.focus({ preventScroll: true }); } catch (e) { sum.focus(); } }
      if (hash && history.replaceState) history.replaceState(null, '', hash);
    }
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#"]');
      var el = a && card(decodeURIComponent(a.getAttribute('href').slice(1)));
      if (el) { e.preventDefault(); openCard(el, a.getAttribute('href')); }
    });
    function fromHash() { var el = card(decodeURIComponent(location.hash.slice(1))); if (el) { el.open = true; setTimeout(function () { el.scrollIntoView(); }, 60); } }
    if (document.readyState === 'complete') fromHash(); else window.addEventListener('load', fromHash);
    window.addEventListener('hashchange', fromHash);
  })();

  // El Treball que Reconnecta: selector de durada (?durada=taller|cicle|cap-de-setmana), i formulari d'inscripció preomplert amb la durada o l'edició triada
  (function () {
    var box = document.querySelector('[data-durades]');
    if (!box) return;
    var tabs = Array.prototype.slice.call(box.querySelectorAll('[data-d]'));
    var items = Array.prototype.slice.call(document.querySelectorAll('.dur-item'));
    var forms = document.querySelector('.forms[data-prefill]');
    var frame = forms && forms.querySelector('iframe.form-frame');
    var alt = forms && forms.querySelector('.form-alt a');
    var entry = forms && forms.getAttribute('data-prefill');
    var base = frame && frame.getAttribute('src'), altBase = alt && alt.getAttribute('href'), cur = '';
    function setForm(v) {
      v = v || '';
      if (!frame || !entry || v === cur) return;
      cur = v;
      frame.setAttribute('src', v ? base + '&' + entry + '=' + encodeURIComponent(v) : base);
      if (alt) alt.setAttribute('href', v ? altBase + '?' + entry + '=' + encodeURIComponent(v) : altBase);
    }
    function panel(key) { return box.querySelector('.durades__panel[data-durada="' + key + '"]'); }
    function show(key, prefill, url) {
      box.classList.toggle('is-empty', !key);
      items.forEach(function (el) { el.classList.toggle('is-on', el.getAttribute('data-durada') === key); });
      tabs.forEach(function (t) { var on = t.getAttribute('data-d') === key; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.setAttribute('tabindex', on || (!key && t === tabs[0]) ? '0' : '-1'); });
      if (prefill && panel(key)) setForm(panel(key).getAttribute('data-form-value'));
      if (url && window.URL && history.replaceState) { var u = new URL(location.href); u.searchParams.set('durada', key); u.searchParams.delete('edicio'); history.replaceState(null, '', u); }
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(t.getAttribute('data-d'), true, true); });
      t.addEventListener('keydown', function (e) {
        var n = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!n) return;
        e.preventDefault();
        var o = tabs[(i + n + tabs.length) % tabs.length];
        o.focus(); show(o.getAttribute('data-d'), true, true);
      });
    });
    // Un botó que porta al formulari («Inscripció», «Reserva la meva plaça», «Avisa'm…») el preomple amb la seva durada o edició
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a');
      if (!a) return;
      if (a.hasAttribute('data-form-value')) setForm(a.getAttribute('data-form-value'));
      else if (a.getAttribute('href') === '#inscripcio' && a.closest('.durades__panel')) setForm(a.closest('.durades__panel').getAttribute('data-form-value'));
    });
    var q = window.URLSearchParams ? new URLSearchParams(location.search) : null;
    var key = q && q.get('durada');
    if (key && panel(key)) {
      show(key, true, false);
      var ed = q.get('edicio'), b = ed && panel(key).querySelector('[data-edicio="' + ed.replace(/"/g, '') + '"]');
      if (b) setForm(b.getAttribute('data-form-value'));
    } else show(box.getAttribute('data-default'), false, false);
  })();
  // Els passos animats (flow--anim) apareixen una sola vegada en veure's
  (function () {
    var els = document.querySelectorAll('[data-flow]');
    if (!els.length) return;
    if (!('IntersectionObserver' in window)) { Array.prototype.forEach.call(els, function (e) { e.classList.add('is-go'); }); return; }
    var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('is-go'); io.unobserve(x.target); } }); }, { threshold: .35 });
    Array.prototype.forEach.call(els, function (e) { io.observe(e); });
  })();
})();
