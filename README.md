# Web d'Elara Social

Web estàtica d'Elara Social, feta amb el mateix sistema i el mateix aspecte que la web de Camins d'Esperança [Activa] (repositori `lespiral/esperancaactiva`).
Es publicarà amb GitHub Pages des de la carpeta `docs/`, primer a `lespiral.github.io/elarasocial` i, quan estigui aprovada, a `elarasocial.com`.

Estat: estructura a punt per omplir. Encara no hi ha pàgines: falta decidir quines n'hi haurà. GitHub Pages encara no està activat.

## On és cada cosa

- `data/site.json`: el nom, l'adreça pública, el menú (`nav`), el contacte, el peu i la pàgina d'inici (`home`).
- `data/pages/<adreça>.json`: una pàgina per fitxer. `data/pages/qui-som.json` es publica a `/qui-som/`.
- `src/templates/`: les plantilles. `page.html` pinta qualsevol pàgina; `parts.html` té les peces (seccions, targetes, preguntes, botons).
- `src/templates/infografies/`: les infografies animades. A `models/` hi ha les de Camins d'Esperança [Activa], com a model (no surten a cap pàgina).
- `src/site.css` i `src/site.js`: l'aspecte i el menú del mòbil.
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
    {"type": "contact", "title": "Escriu-nos", "text_html": "Escriu-nos a <a href=\"mailto:...\">...</a>."}
  ]
}
```

- Cada secció pot portar `"band": "white"`, `"green"` o `"slim"` (el fons de la franja), `"intro"` (una frase sota el títol), `"buttons"` i `"id"` (l'adreça per enllaçar-hi: `/qui-som/#proposit`; si no n'hi ha, es fa amb el títol).
- Els enllaços (`href`): una paraula sola és una pàgina de la web (`"contacte"` porta a `/contacte/`); també poden ser adreces completes (`https://…`), `mailto:`, `tel:` o `#seccio`.
- Les icones són les de `src/icons.json` (les mateixes que a Camins d'Esperança [Activa]).
- Els camps acabats en `_html` poden portar HTML (enllaços, negretes).
- Per posar la pàgina al menú, afegeix-la a `nav` de `data/site.json`: `{"slug": "qui-som", "title": "Qui som"}`. Un enllaç de fora va amb `href`: `{"title": "Camins d'Esperança [Activa]", "href": "https://…"}`.

## Infografies animades

Funcionen com a Camins d'Esperança [Activa]: una per fitxer, amb el codi del bloc INICI–FINAL, els colors i les lletres de `site.css`; s'animen quan surten a la pantalla i, amb «reduir moviment», surten ja acabades. Una infografia nova es desa a `src/templates/infografies/infografia-<nom>.html` i es posa a una pàgina amb una secció `{"type": "infografia", "name": "<nom>"}`.

Les de `models/` són les de Camins (7 passes, com funciona, Esperança Activa, ciutats, cursos…). Alguna fa servir dades de la web de Camins (els cursos o les ciutats): abans de fer-la servir aquí, cal adaptar-la.

## Publicació

- L'adreça i si surt als cercadors són a `data/site.json`, a `publish`. Ara: `https://lespiral.github.io/elarasocial/` i `"index": false` (no surt als cercadors mentre no estigui aprovada, perquè no faci competència a la web de WordPress).
- GitHub Pages (branca `main`, carpeta `/docs`) s'activarà quan hi hagi una primera versió aprovada.
- Quan es canviï el domini: canvia `url` a `publish`, posa `"index": true`, crea el fitxer `CNAME` amb el domini i torna a generar la web.
