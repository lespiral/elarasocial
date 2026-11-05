# Web d'Elara Social

Web estàtica d'Elara Social, feta amb el mateix sistema i el mateix aspecte que la web de Camins d'Esperança [Activa] (repositori `lespiral/esperancaactiva`).
Es publicarà amb GitHub Pages des de la carpeta `docs/`, primer a `lespiral.github.io/elarasocial` i, quan estigui aprovada, a `elarasocial.com`.

Estat: estructura A (la de la web de WordPress, endreçada) amb tots els textos de la web actual: les pàgines principals, les 8 propostes amb el seu formulari d'inscripció, les 7 passes i els 2 articles. GitHub Pages encara no està activat.

## On és cada cosa

- `data/site.json`: el nom, l'adreça pública, el menú (`nav`), el contacte, el peu i la pàgina d'inici (`home`).
- `data/pages/<adreça>.json`: una pàgina per fitxer. `data/pages/qui-som.json` es publica a `/qui-som/`.
- `data/articles/<adreça>.json`: un article per fitxer (`title`, `date` en format 2026-03-20, `author`, `image` dins de `src/img/`, i `body`: paràgrafs i títols `{"h2": …}` o `{"h3": …}`). Es publica a `/<adreça>/` i surt sol a la pàgina Articles (secció `{"type": "articles"}`), del més nou al més antic.
- `src/templates/`: les plantilles. `page.html` pinta qualsevol pàgina; `parts.html` té les peces (seccions, targetes, preguntes, botons).
- `src/templates/infografies/`: les infografies animades. A `models/` hi ha les de Camins d'Esperança [Activa], com a model (no surten a cap pàgina).
- `src/site.css` i `src/site.js`: l'aspecte (amb els colors d'Elara: blau marí i verd del logo) i el menú del mòbil.
- `src/img/`: els logos d'Elara Social (de la carpeta de Drive) i el logo conjunt de L'Espiral i Elara Social.
- `docs/`: la web generada. No s'edita a mà: es torna a generar.

## Com es fa un canvi

1. Canvia el text al fitxer de `data/`.
2. Genera la web: `python3 build.py`. Si hi ha alguna errada (un tipus de secció que no existeix, una infografia que no hi és, un enllaç del menú a una pàgina que no existeix), ho diu i no genera res.
3. Desa i puja els canvis.

No s'han d'inventar dades: si en falta alguna, es deixa marcada amb `[PENDENT]`. En generar la web, `build.py` diu quantes marques `[PENDENT]` queden.

## Una pàgina

```json
{
  "title": "Qui som",
  "kicker": "Elara Social",
  "lead": "Una frase sota el títol.",
  "description": "El text que surt als cercadors (si no hi és, fa servir lead).",
  "sections": [
    {"type": "text", "title": "Propòsit", "paragraphs": ["Primer paràgraf.", "Segon paràgraf."]},
    {"type": "cards", "title": "Treballem amb", "items": [
      {"icon": "users-three", "title": "Persones", "text": "Una frase.", "href": "persones", "button": "Saber-ne més"}
    ]},
    {"type": "list", "title": "Què t'emportaràs", "items": ["Una cosa.", "Una altra."]},
    {"type": "faq", "title": "Preguntes", "items": [["La pregunta?", "La resposta, que pot portar <a href=\"...\">enllaços</a>."]]},
    {"type": "note", "style": "care", "title": "Abans de començar", "paragraphs": ["Un avís de cura."]},
    {"type": "infografia", "name": "com-funciona", "title": "Com funciona"},
    {"type": "cta", "title": "Parlem-ne", "paragraphs": ["Una frase."], "buttons": [{"text": "Contacte", "href": "contacte"}]},
    {"type": "contact", "title": "Parlem-ne", "paragraphs": ["Una frase."]},
    {"type": "form", "id": "inscripcio", "title": "Inscripció", "forms": [{"label": "Inscripció al taller", "form": "1FAIpQL...", "height": 3000}]}
  ]
}
```

- Cada secció pot portar `"band": "white"`, `"soft"` o `"slim"` (el fons de la franja), `"intro"` (una frase sota el títol), `"buttons"` i `"id"` (l'adreça per enllaçar-hi: `/qui-som/#proposit`; si no n'hi ha, es fa amb el títol).
- Els enllaços (`href`): una paraula sola és una pàgina de la web (`"contacte"` porta a `/contacte/`); també poden ser adreces completes (`https://…`), `mailto:`, `tel:` o `#seccio`.
- Les icones són les de `src/icons.json` (les mateixes que a Camins d'Esperança [Activa]).
- Els camps acabats en `_html` poden portar HTML (enllaços, negretes). Amb `"html": true` a la secció, també els paràgrafs i les llistes.
- Altres camps de secció: `"kicker"` (avantítol petit), `"before"` (paràgrafs abans de les targetes), `"list"` i `"after"` (a les de text), `"quote"`, `"align": "left"` (targetes alineades a l'esquerra).
- Les targetes poden portar `subtitle`, `meta` (p. ex. `["4 hores", "Màx. 16 participants"]`), `paragraphs`, `list`, `foot`, `badge`, `href` i `button` (el text del botó).
- El contacte (correu, telèfon, WhatsApp, adreça) surt de `contact` a `data/site.json`.

## Formularis d'inscripció

Són els formularis de Google del compte lespiral.cat@gmail.com, inserits a la pàgina com a WordPress: les respostes hi continuen arribant igual. Cada un va en una secció `{"type": "form"}` amb el codi del formulari publicat (el tros de l'adreça entre `/forms/d/e/` i `/viewform`, que comença per `1FAIpQL`) i l'alçada en píxels. Si una proposta en té dos (el taller obert i la versió per a un equip), surten plegats, l'un sota l'altre.

## Adreces antigues

Les adreces de la web de WordPress que ja no són una pàgina (les tres «Propostes a nivell…», els formularis i les pàgines de Camins) porten soles a la pàgina nova. Es configuren a `redirects` de `data/site.json`: `"adreça-antiga": "pagina/#seccio"` o una adreça completa.
- Per posar la pàgina al menú, afegeix-la a `nav` de `data/site.json`: `{"slug": "qui-som", "title": "Qui som"}`. Un enllaç de fora va amb `href`: `{"title": "Camins d'Esperança [Activa]", "href": "https://…"}`.

## Infografies animades

Funcionen com a Camins d'Esperança [Activa]: una per fitxer, amb el codi del bloc INICI–FINAL, els colors i les lletres de `site.css`; s'animen quan surten a la pantalla i, amb «reduir moviment», surten ja acabades. Una infografia nova es desa a `src/templates/infografies/infografia-<nom>.html` i es posa a una pàgina amb una secció `{"type": "infografia", "name": "<nom>"}`.

Les de `models/` són les de Camins (7 passes, com funciona, Esperança Activa, ciutats, cursos…). Alguna fa servir dades de la web de Camins (els cursos o les ciutats): abans de fer-la servir aquí, cal adaptar-la.

## Publicació

- L'adreça i si surt als cercadors són a `data/site.json`, a `publish`. Ara: `https://lespiral.github.io/elarasocial/` i `"index": false` (no surt als cercadors mentre no estigui aprovada, perquè no faci competència a la web de WordPress).
- GitHub Pages (branca `main`, carpeta `/docs`) s'activarà quan hi hagi una primera versió aprovada.
- Quan es canviï el domini: canvia `url` a `publish`, posa `"index": true`, crea el fitxer `CNAME` amb el domini i torna a generar la web.

## Ressenyes de Google

Una secció `{"type": "reviews"}` posa les ressenyes de `reviews` a `data/site.json`. Ara són les mateixes que surten a WordPress (copiades el 5 de novembre de 2026) i no s'actualitzen soles. A WordPress surten amb el connector de Trustindex per a WordPress, que no serveix fora de WordPress. Per tenir-les al dia aquí cal un giny de Trustindex fet a trustindex.io: dona una línia `<script … loader.js?codi>`, i si poses aquest codi a `"trustindex"`, surten les de Google al dia en lloc de les copiades.
