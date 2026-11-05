# Web d'Elara Social

Web estàtica d'Elara Social, feta amb el mateix sistema i el mateix aspecte que la web de Camins d'Esperança [Activa] (repositori `lespiral/esperancaactiva`).
Es publica amb GitHub Pages des de la carpeta `docs/` al domini `elarasocial.com`.

Estat: publicada a elarasocial.com (GitHub Pages) des del 5 de novembre de 2026, amb tots els textos de la web de WordPress: les pàgines principals, les 8 propostes amb el seu formulari d'inscripció, les 7 passes i els 2 articles.

## On és cada cosa

- `data/site.json`: el nom, l'adreça pública, el menú (`nav`), el contacte, el peu i la pàgina d'inici (`home`). Al peu, `projects` posa els projectes d'Elara amb web pròpia (ara, Camins d'Esperança [Activa]) a totes les pàgines.
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

Funcionen com a Camins d'Esperança [Activa]: una per fitxer, amb el codi del bloc INICI–FINAL, els colors i les lletres de `site.css`; s'animen quan surten a la pantalla i, amb «reduir moviment», surten ja acabades. Una infografia nova es desa a `src/templates/infografies/infografia-<nom>.html` i es posa a una pàgina de dues maneres:

- Sola, en una franja pròpia: `{"type": "infografia", "name": "<nom>"}`.
- Dins d'una altra secció, sota el títol (a les targetes, sota el text de `before`): `"infografia": "<nom>"`. Amb `"variant"` es tria la versió quan n'hi ha més d'una (p. ex. `"persones"` o `"organitzacions"`).
- A la capçalera d'una pàgina: `"escena": "vida"` (o `"cuidar"`, `"mon"`, `"dia"`) al JSON de la pàgina.

Les que es fan servir ara:

| Infografia | On és | Ve de (Camins) |
|---|---|---|
| `esperanca-activa` | Inici, sota la capçalera | Què és l'Esperança Activa |
| `espiral` | Què fem, «La nostra metodologia» (variant `metodologia`, la de per defecte); «Què t'emportaràs…» de L'espiral de l'esperança activa (`taller`), El Treball que Reconnecta (`cicle`), Un pont d'esperança (`pont`) i el Grup regular (`grup`) | Com funciona, amb escenes noves |
| `nivells` | Què fem, «Adaptem la nostra metodologia a tres nivells d'impacte»: cercles Tu · Persones i grups · Equips i organitzacions · Comunitat, amb enllaç a cada pàgina | La iniciativa |
| `capcalera` | Capçalera de Persones (`vida`), Comunitats (`cuidar`) i Organitzacions (`dia`) | Capçalera dels cursos |
| `itinerari` | Persones «Què fem exactament?», Organitzacions «Com us acompanyem?» i Comunitats «Com ens organitzem?»: el camí amb tres parades i les propostes de cada parada. Els textos d'inici i final són a `"itinerari"` de la secció, i les propostes a `"propostes"` de cada targeta | Nova, amb la idea del camí |
| `cursos` | Les dues pàgines de les 7 passes, «Tria des d'on vols començar» (variants `persones` i `organitzacions`) | Els cursos, sense el tram de les ciutats |
| `7-passes` | Les dues pàgines de les 7 passes, «El recorregut en 7 passes» i «Com seria l'experiència» (variants `persones` i `organitzacions`) | 7 passes |
| `vinculacio` | 7 passes (organitzacions), «De la reflexió a la vinculació» | I després? |
| `rotllana` | «Explorarem…» de Cercles de paraula per a gestionar conflictes (`conflictes`) i de Cercles per sostenir organitzacions i col·lectius (`sostenir`): els 5 elements que creen seguretat | Nova |
| `stop-ground-choose` | Burnout, «Practicarem…»: aturar, ancorar, triar un pas mínim | Nova |

Cada infografia només hi pot ser un cop per pàgina (el codi busca la primera de la pàgina).

Les de `models/` són les de Camins, tal com són a esperançaactiva.cat (no surten a cap pàgina). Per fer-ne servir una aquí:

1. Copia-la a `src/templates/infografies/` i canvia-hi els textos pels de la web d'Elara (les dades de Camins, com les ciutats, no hi són).
2. Passa-la als colors d'Elara: `python3 tools/colors-elara.py src/templates/infografies/infografia-<nom>.html`. L'estructura passa al blau marí, la natura al verd del logo i els grisos verdosos a grisos blavosos; el groc del sol (`--sol`) es queda com l'únic color càlid.

## Publicació

- La web es publica amb GitHub Pages (branca `main`, carpeta `/docs`) al domini **elarasocial.com** (fitxer `CNAME`). Els registres DNS del domini són a Bluehost: `@` apunta a les 4 adreces de GitHub Pages i `www` a `lespiral.github.io`; el correu continua a Bluehost (`mail.elarasocial.com`).
- L'adreça i si surt als cercadors són a `data/site.json`, a `publish`: `https://elarasocial.com/` i `"index": true` (amb `sitemap.xml`).

## Ressenyes de Google

Una secció `{"type": "reviews"}` posa les ressenyes de `reviews` a `data/site.json`. Ara són les mateixes que surten a WordPress (copiades el 5 de novembre de 2026) i no s'actualitzen soles. A WordPress surten amb el connector de Trustindex per a WordPress, que no serveix fora de WordPress. Per tenir-les al dia aquí cal un giny de Trustindex fet a trustindex.io: dona una línia `<script … loader.js?codi>`, i si poses aquest codi a `"trustindex"`, surten les de Google al dia en lloc de les copiades.
