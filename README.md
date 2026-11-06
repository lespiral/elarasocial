# Web d'Elara Social

Web estàtica d'Elara Social, feta amb el mateix sistema i el mateix aspecte que la web de Camins d'Esperança [Activa] (repositori `lespiral/esperancaactiva`).
Es publica amb GitHub Pages des de la carpeta `docs/` al domini `elarasocial.com`.

Estat: publicada a elarasocial.com (GitHub Pages) des del 5 de novembre de 2026, amb tots els textos de la web de WordPress: les pàgines principals, les 8 propostes amb el seu formulari d'inscripció, les 7 passes i els 2 articles. Des del 6 de novembre de 2026, també en castellà a elarasocial.com/es/ (vegeu «Versió en castellà»).

## On és cada cosa

- `data/site.json`: el nom, l'adreça pública, el menú (`nav`), el contacte, el peu i la pàgina d'inici (`home`). Al peu, `projects` posa els projectes d'Elara amb web pròpia (ara, Camins d'Esperança [Activa], esperançaactiva.cat, i Caminos de Esperanza [Activa], esperanzaactiva.org, la seva web en castellà) a totes les pàgines, i `projects.email` el correu dels projectes (esperanza@elarasocial.com). El correu de contacte d'Elara (`contact.email`) també és esperanza@elarasocial.com des del 6 de novembre de 2026 (abans, elarasocial.com@gmail.com).
- `data/pages/<adreça>.json`: una pàgina per fitxer. `data/pages/qui-som.json` es publica a `/qui-som/`.
- `data/articles/<adreça>.json`: un article per fitxer (`title`, `date` en format 2026-03-20, `author`, `image` dins de `src/img/`, i `body`: paràgrafs i títols `{"h2": …}` o `{"h3": …}`). Es publica a `/<adreça>/` i surt sol a la pàgina Articles (secció `{"type": "articles"}`), del més nou al més antic.
- `src/templates/`: les plantilles. `page.html` pinta qualsevol pàgina; `parts.html` té les peces (seccions, targetes, preguntes, botons).
- `src/templates/infografies/`: les infografies animades. A `models/` hi ha les de Camins d'Esperança [Activa], com a model (no surten a cap pàgina).
- `src/site.css` i `src/site.js`: l'aspecte (amb els colors d'Elara: blau marí i verd del logo) i el menú del mòbil.
- `src/img/`: els logos d'Elara Social (de la carpeta de Drive) i el logo conjunt de L'Espiral i Elara Social.
- `docs/`: la web generada. No s'edita a mà: es torna a generar.
- `data/es/`: la versió en castellà (vegeu «Versió en castellà»).
- `tools/restes-catala.py`: busca textos en català que s'hagin quedat a la versió en castellà.

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
- **Negreta**: a qualsevol text, `**així**` surt en negreta (dins dels paràgrafs, amb un subratllat de retolador verd). Els camps acabats en `_html` poden portar HTML (enllaços, negretes). Amb `"html": true` a la secció, també els paràgrafs i les llistes.
- Altres camps de secció: `"kicker"` (avantítol petit), `"before"` (paràgrafs abans de les targetes), `"list"` i `"after"` (a les de text), `"quote"`, `"align": "left"` (targetes alineades a l'esquerra).
- Les targetes poden portar `subtitle`, `meta` (p. ex. `["4 hores", "Màx. 16 participants"]`), `paragraphs`, `list`, `foot`, `badge`, `href` i `button` (el text del botó). Amb `photo` (p. ex. `"equip/aleix-boronat.jpg"`, a `src/img/`) porten una foto rodona a dalt; les de Sobre nosaltres són quadrades, de 320 × 320 px, en JPG.
- El contacte (correu, telèfon, WhatsApp, adreça) surt de `contact` a `data/site.json`.

## Com es veu cada secció

- **Text** (`"type": "text"`): el primer paràgraf surt més gran, com a entrada. Si no hi ha llista, la resta de paràgrafs van dins d'un quadre de color (verd clar a les franges blanques, blanc a les altres).
- **Llistes** d'una secció de text (`"list"`): cada element en un quadre amb una icona, en dues columnes si n'hi ha 4 o més. La icona surt del títol de la secció: «Explorarem…» → brúixola (`compass`), «Practicarem…» → petjades (`footprints`), «Què t'emportaràs…» → fulla (`leaf`), «…treballarem…» → mà amb cor (`hand-heart`); la resta, `check`. Per triar-ne una altra: `"list_icon": "<icona>"` a la secció (vegeu `LIST_ICONS` a `build.py`).
- **Durada, places i preus** (`"type": "note"` sense `"style"`, o `"style": "info"`): un quadre blau marí. El títol porta un rellotge; cada paràgraf, una icona segons el que diu (`€` → monedes, «participants» → persones, la resta → calendari), i els preus surten en negreta sols.
- **Avís de cura** (`"style": "care"`): com abans, rosat.
- **Última crida** (`"type": "cta"`): un quadre blau marí com la portada; el `kicker` hi fa de títol gran i el primer botó és verd clar.
- **Targetes de propostes**: si una targeta porta a una proposta (`href`) i no té `icon`, agafa la icona de la proposta (`CARD_ICONS` a `build.py`: 7 passes → `steps`, Acompanyament → `hand-heart`, L'Espiral → `spiral`, El TqR → `tree`, Un pont → `bridge`, Grup regular → `moon-stars`, Cercles per a conflictes → `chats-circle`, Cercles per sostenir → `circles-three`, Burnout → `campfire`, Contacte → `chat-circle-dots`, Camins → `map-trifold`, i els quatre cursos de Thinkific). Amb `"icon": ""` no en porta cap. Les targetes sense icona porten una franja verda a dalt.
- **Preguntes** (FAQ): amb una icona d'interrogant.
- **Avantítols** (`"kicker"` d'una secció): en cursiva verda, amb el sol al davant; la primera lletra surt sola en majúscula.
- **Títols que es mouen**: el títol de la capçalera surt paraula a paraula; cada títol de secció puja i es dibuixa la línia d'ona (amb el sol al final) quan arriba a la pantalla. Amb «reduir moviment» o sense JavaScript, tot surt quiet. Els estils són al final de `site.css` («Més vida»), i el codi a `site.js`.

Les icones són de Phosphor (les mateixes que a Camins d'Esperança [Activa]); n'hi ha més a `src/icons.json` (`clock`, `calendar-dots`, `coins`, `users`, `compass`, `leaf`, `bridge`, `campfire`, `spiral`, `moon-stars`…).

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
| `metafora` | Sota el títol de cada proposta: una escena petita que explica la proposta amb una imatge, i una frase a sota. Es posa amb `"metafora": {"name": "<escena>", "text": "La frase"}` al JSON de la pàgina. Escenes: `passes` (7 passes: pedres per travessar el riu), `passes-comunitat` (el mateix, amb la comunitat a l'altra riba), `costat` (Acompanyament: dues persones que caminen plegades), `falguera` (L'Espiral: falgueres que es desenrotllen), `arrels` (El TqR: arrels que es troben sota terra), `pont` (Un pont: els taulons es posen un a un), `llunes` (Grup regular: les fases de la lluna sobre una rotllana al voltant del foc), `paraula` (Cercles per a conflictes: el bastó de la paraula fa la volta i la tensió es torna onada), `sostenir` (Cercles per sostenir: el cercle es tanca i la casa es redreça), `foc` (Burnout: el foc que crema es torna foc que escalfa) | Noves |

Cada infografia només hi pot ser un cop per pàgina (el codi busca la primera de la pàgina).

Les de `models/` són les de Camins, tal com són a esperançaactiva.cat (no surten a cap pàgina). Per fer-ne servir una aquí:

1. Copia-la a `src/templates/infografies/` i canvia-hi els textos pels de la web d'Elara (les dades de Camins, com les ciutats, no hi són).
2. Passa-la als colors d'Elara: `python3 tools/colors-elara.py src/templates/infografies/infografia-<nom>.html`. L'estructura passa al blau marí, la natura al verd del logo i els grisos verdosos a grisos blavosos; el groc del sol (`--sol`) es queda com l'únic color càlid.

## Versió en castellà

La web en castellà és a `/es/`, amb les adreces en castellà (`/es/personas/`, `/es/sobre-nosotros/`…). A la capçalera, el selector **CA · ES** porta a la mateixa pàgina en l'altra llengua; cada pàgina diu als cercadors quina és la seva en l'altra llengua (`hreflang`), i el `sitemap.xml` porta les adreces de totes dues.

- `data/es/site.json`: només el que canvia respecte a `data/site.json` (la descripció, el menú amb les adreces en castellà, el peu i la pàgina d'inici). El contacte i la resta són els mateixos.
- `data/es/pages/<adreça>.json` i `data/es/articles/<adreça>.json`: com les catalanes, però amb el text en castellà i un camp més, `"ca"`, que diu quina és la mateixa pàgina en català (p. ex. `"ca": "persones"` a `personas.json`). Els enllaços d'aquestes pàgines (`href`) porten a les adreces en castellà (`"contacto"`, `"personas/#propuestas"`).
- `data/es/plantilles.json`: els textos de les plantilles i de les infografies en castellà, en parells `["text en català, tal com és a la plantilla", "text en castellà"]`, per fitxer de `src/templates/`. Les plantilles i les infografies són les mateixes per a les dues llengües: en generar la web en castellà, `build.py` hi canvia aquests textos. Si es canvia un text català d'una plantilla o d'una infografia, `build.py` avisa que també cal canviar-lo aquí (i no genera res fins que hi és).
- Quan es canvia una pàgina en català, s'ha de canviar també la seva en castellà. Si una pàgina catalana no en té, `build.py` ho avisa i el selector porta a l'inici en castellà.
- Després de generar la web, `python3 tools/restes-catala.py` diu si a `docs/es/` hi ha quedat algun text en català.
- **Formularis**: les pàgines en castellà porten còpies en castellà dels formularis de Google, a la mateixa carpeta del Drive (`Elara Social (castellà) - …`), amb els avisos per correu de les respostes noves activats com els originals. Les respostes de cada còpia queden dins del formulari (no van a cap full de càlcul). Les còpies es van fer amb el projecte d'Apps Script «Elara Social - formularis en castellà» del compte lespiral.cat.
- Camins d'Esperança [Activa] i els cursos de Thinkific de les 7 passes són en català: les pàgines en castellà ho diuen.
- Al mòbil i fins a 1023 px d'amplada, el menú és el desplegable (amb el selector de llengua al costat); entre 1024 i 1199 px, el menú és una mica més compacte. En castellà, com que els noms són més llargs, el menú és compacte a totes les amplades d'ordinador (`html[lang="es"]` a `site.css`).

## Publicació

- La web es publica amb GitHub Pages (branca `main`, carpeta `/docs`) al domini **elarasocial.com** (fitxer `CNAME`). Els registres DNS del domini són a Bluehost: `@` apunta a les 4 adreces de GitHub Pages i `www` a `lespiral.github.io`; el correu continua a Bluehost (`mail.elarasocial.com`).
- L'adreça i si surt als cercadors són a `data/site.json`, a `publish`: `https://elarasocial.com/` i `"index": true` (amb `sitemap.xml`).

## Ressenyes de Google

Des del 5 de novembre de 2026 no surten a cap pàgina (l'Aleix les va fer treure). Si mai es volen tornar a posar: una secció `{"type": "reviews"}` posa les ressenyes de `reviews` a `data/site.json`. Ara són les mateixes que surten a WordPress (copiades el 5 de novembre de 2026) i no s'actualitzen soles. A WordPress surten amb el connector de Trustindex per a WordPress, que no serveix fora de WordPress. Per tenir-les al dia aquí cal un giny de Trustindex fet a trustindex.io: dona una línia `<script … loader.js?codi>`, i si poses aquest codi a `"trustindex"`, surten les de Google al dia en lloc de les copiades.
