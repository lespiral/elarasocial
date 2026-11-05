// Elara Social · menú del mòbil, enllaços directes a seccions i desplegables «Vés directament a…»
(function () {
  var bar = document.querySelector('.topbar');
  var btn = document.querySelector('.menu-btn');
  if (bar && btn) {
    btn.addEventListener('click', function () {
      var open = bar.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Tanca el menú' : 'Obre el menú');
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
