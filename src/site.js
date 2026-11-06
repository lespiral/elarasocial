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
})();
