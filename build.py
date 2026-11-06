#!/usr/bin/env python3
"""Genera la web estàtica d'Elara Social a la carpeta docs/.

Ús:  python3 build.py

Fa servir el mateix sistema que la web de Camins d'Esperança [Activa]
(lespiral/esperancaactiva): dades en JSON, plantilles Jinja i un sol full d'estils.

- data/site.json: el nom, l'adreça pública, el menú, el contacte, el peu i la pàgina d'inici.
- data/pages/<adreça>.json: una pàgina per fitxer (vegeu el README).
- data/es/: la versió en castellà (/es/), amb les adreces en castellà. Cada pàgina i article porta
  "ca": l'adreça de la mateixa pàgina en català. Els textos de les plantilles i de les infografies
  es tradueixen a data/es/plantilles.json (vegeu el README).

L'adreça pública i si la web ha de sortir als cercadors es configuren a
data/site.json, a "publish": {"url": ..., "index": true/false}.
"""
import json, re, shutil, sys, time, unicodedata
from pathlib import Path
from urllib.parse import urlparse
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent
DATA, SRC, OUT = ROOT / "data", ROOT / "src", ROOT / "docs"

ICONS = json.loads((SRC / "icons.json").read_text(encoding="utf-8"))

# Tipus de secció que saben pintar les plantilles (src/templates/parts.html, macro «section»)
SECTION_TYPES = {"text", "cards", "list", "faq", "note", "infografia", "cta", "contact", "form", "reviews", "articles"}

# Formulari de Google inserit a la pàgina (les respostes continuen arribant al compte que el va crear)
FORM_URL = "https://docs.google.com/forms/d/e/{}/viewform"


def icon(name, cls=None):
    vb = ICONS.get(name + "__vb", "0 0 256 256")
    c = "i" + (" " + cls if cls else "")
    return Markup(f'<svg class="{c}" viewBox="{vb}" fill="currentColor" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def slugify(s):
    s = s.replace("l·l", "ll").replace("L·L", "LL")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def html(s):
    """Els camps acabats en _html són HTML escrit per nosaltres (enllaços, negretes): es pinten tal qual."""
    return Markup(s) if s else s


BOLD = re.compile(r"\*\*(.+?)\*\*")


def bold(v):
    """**text** en qualsevol text d'una secció → negreta. Recorre llistes, targetes i preguntes."""
    if isinstance(v, Markup):
        return Markup(BOLD.sub(r"<strong>\1</strong>", str(v))) if "**" in v else v
    if isinstance(v, str):
        return Markup(BOLD.sub(r"<strong>\1</strong>", str(escape(v)))) if "**" in v else v
    if isinstance(v, list):
        return [bold(x) for x in v]
    if isinstance(v, tuple):
        return tuple(bold(x) for x in v)
    if isinstance(v, dict):
        return {k: (bold(x) if k not in ("id", "href", "icon", "type", "form", "url", "name", "variant", "band") else x) for k, x in v.items()}
    return v


# Icona de cada proposta, perquè les targetes que hi porten la tinguin sense haver-la d'escriure a cada pàgina.
# Una targeta amb "icon" propi la manté; amb "icon": "" no en porta cap.
CARD_ICONS = {
    "7-passes-cap-a-lesperanca-activa": "steps",
    "7-passes-cap-a-lesperanca-activa-comunitats": "steps",
    "acompanyament-individual": "hand-heart",
    "lespiral-de-lesperanca-activa": "spiral",
    "el-treball-que-reconnecta": "tree",
    "un-pont-desperanca-2": "bridge",
    "grup-regular-de-el-treball-que-reconnecta": "moon-stars",
    "cercles-de-paraula-per-a-gestionar-conflictes": "chats-circle",
    "cercles-per-sostenir-organitzacions-i-col·lectius": "circles-three",
    "burnout": "campfire",
    "contacte": "chat-circle-dots",
    "xn--esperanaactiva-mjb.cat": "map-trifold",
    # Els quatre cursos de les 7 passes (Thinkific)
    "Quan-sostenir-la-vida": "plant",
    "Quan-el-mon-et-preocupa": "globe",
    "Quan-cuidar-nos": "users-three",
    "Quan-la-vida-et-desborda": "cloud-rain",
}


def card_icon(href, lang="ca"):
    if not href:
        return None
    page = href.split("#")[0].strip("/")
    page = TO_CA.get(lang, {}).get(page, page)
    if page in CARD_ICONS:
        return CARD_ICONS[page]
    for k, v in CARD_ICONS.items():
        if k in href:
            return v
    return None


# Icona de les llistes de les seccions de text, segons el títol ("list_icon" a la secció per triar-ne una altra)
LIST_ICONS = [("explorarem", "compass"), ("practicarem", "footprints"), ("emportar", "leaf"), ("treballarem", "hand-heart"),
              ("llevar", "leaf"), ("trabajaremos", "hand-heart")]   # «exploraremos» i «practicaremos» ja hi són


def list_icon(title):
    t = (title or "").lower()
    return next((ic for k, ic in LIST_ICONS if k in t), "check")


# Quadre de dades d'una proposta (nota "info"): cada línia amb la seva icona i els preus en negreta
PRICE = re.compile(r"(\d+(?:,\d+)?(?:\s?/\s?\d+(?:,\d+)?)*\s?€)")


def note_rows(paragraphs):
    rows = []
    for p in paragraphs or []:
        t = str(p)
        ic = "coins" if "€" in t else "users" if "participant" in t else "calendar-dots"
        h = t if isinstance(p, Markup) else str(escape(t))
        rows.append({"icon": ic, "html": Markup(PRICE.sub(r"<strong>\1</strong>", h))})
    return rows


errors = []


def prepare_sections(sections, where, lang="ca"):
    """Revisa les seccions d'una pàgina i hi posa un id per enllaçar-hi (/pagina/#el-titol)."""
    ids = []
    for i, s in enumerate(sections or []):
        t = s.get("type")
        if t not in SECTION_TYPES:
            errors.append(f"{where}: la secció {i + 1} té un tipus desconegut ({t!r}). Tipus possibles: {', '.join(sorted(SECTION_TYPES))}")
            continue
        s["id"] = s.get("id") or (slugify(s["title"]) if s.get("title") else f"seccio-{i + 1}")
        ids.append(s["id"])
        for k in list(s):
            if k.endswith("_html"):
                s[k] = html(s[k])
        # Amb "html": true, els paràgrafs i les llistes poden portar <strong>, <a>, etc.
        if s.get("html"):
            for k in ("paragraphs", "list", "after"):
                s[k] = [html(p) for p in s.get(k) or []]
            for it in s.get("items", []) if t == "cards" else []:
                for k in ("paragraphs", "list"):
                    it[k] = [html(p) for p in it.get(k) or []]
        if t == "form":
            for fm in s.get("forms", []):
                if not re.fullmatch(r"1FAIpQL[\w-]{40,60}", fm.get("form", "")):
                    errors.append(f"{where}: el formulari «{fm.get('label')}» ha de portar el codi del formulari publicat (comença per 1FAIpQL)")
                fm["url"] = FORM_URL.format(fm.get("form", ""))
        if t == "faq":
            s["items"] = [(q, html(a), slugify(q)) for q, a in s.get("items", [])]
        # Una infografia sola (tipus "infografia", amb "name") o sota el títol d'una altra secció ("infografia": "<nom>")
        for name in [s.get("name")] if t == "infografia" else [s.get("infografia")] if s.get("infografia") else []:
            f = SRC / "templates" / "infografies" / f"infografia-{name}.html"
            if not f.exists():
                errors.append(f"{where}: no trobo la infografia {f.relative_to(ROOT)}")
        for it in s.get("items", []) if t in ("cards", "list") else []:
            if isinstance(it, dict) and "icon" not in it and card_icon(it.get("href"), lang):
                it["icon"] = card_icon(it.get("href"), lang)
            if isinstance(it, dict) and it.get("photo") and not (SRC / "img" / it["photo"]).exists():
                errors.append(f"{where}: no trobo la foto src/img/{it['photo']}")
            if isinstance(it, dict) and it.get("icon") and it["icon"] not in ICONS:
                errors.append(f"{where}: la icona {it['icon']!r} no és a src/icons.json")
        if t == "text" and s.get("list"):
            s["list_icon"] = s.get("list_icon") or list_icon(s.get("title"))
            if s["list_icon"] not in ICONS:
                errors.append(f"{where}: la icona {s['list_icon']!r} no és a src/icons.json")
        if t == "note" and s.get("style", "info") == "info":
            s["rows"] = note_rows(bold(s.get("paragraphs")))
        for k in list(s):
            if k not in ("rows",):
                s[k] = bold(s[k]) if k not in ("id", "type", "band", "infografia", "variant", "name", "list_icon", "style", "align") else s[k]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errors.append(f"{where}: seccions amb el mateix id {sorted(dup)}: posa'ls un \"id\" diferent")
    return sections or []


site = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
SITE_URL = site["publish"]["url"].rstrip("/") + "/"
NOINDEX = not site["publish"].get("index", False)
BASE = urlparse(SITE_URL).path or "/"   # p. ex. /elarasocial/ a GitHub Pages, / amb domini propi

# Llengües: el català a l'arrel (/) i el castellà a /es/, amb les seves adreces.
# data/es/ té la mateixa forma que data/: site.json (només el que canvia), pages/ i articles/.
LANGS = {
    "ca": {"prefix": "", "data": DATA, "locale": "ca_ES", "short": "CA", "name": "Català"},
    "es": {"prefix": "es/", "data": DATA / "es", "locale": "es_ES", "short": "ES", "name": "Castellano"},
}
LANGS = {k: v for k, v in LANGS.items() if k == "ca" or (v["data"] / "site.json").exists()}
TO_CA = {}       # adreça en una llengua → adreça en català (per a les icones de les targetes)
FROM_CA = {}     # adreça en català → adreça en cada llengua (per al selector de llengua i hreflang)

MESOS = {
    "ca": ["gener", "febrer", "març", "abril", "maig", "juny", "juliol", "agost", "setembre", "octubre", "novembre", "desembre"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
}


def data_llarga(iso, lang="ca"):
    y, m, d = (int(x) for x in iso.split("-"))
    mes = MESOS[lang][m - 1]
    if lang == "es":
        return f"{d} de {mes} de {y}"
    return f"{d} {'d’' if mes[0] in 'ao' else 'de '}{mes} de {y}"


def merge(base, over):
    """data/es/site.json només porta el que canvia: els diccionaris es barregen, la resta se substitueix."""
    out = dict(base)
    for k, v in over.items():
        out[k] = merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def load_lang(lang):
    L = LANGS[lang]
    d = L["data"]
    s = site if lang == "ca" else merge(site, json.loads((d / "site.json").read_text(encoding="utf-8")))
    if lang != "ca":
        s.pop("redirects", None)   # les adreces antigues de WordPress només són en català
    pgs = []
    for f in sorted((d / "pages").glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        p.setdefault("slug", f.stem)
        if p["slug"] != f.stem:
            errors.append(f"{f.relative_to(ROOT)}: el camp slug ({p['slug']}) ha de ser igual que el nom del fitxer")
        pgs.append((f, p))
    arts = []
    for f in sorted((d / "articles").glob("*.json")) if (d / "articles").exists() else []:
        a = json.loads(f.read_text(encoding="utf-8"))
        a["slug"] = f.stem
        arts.append((f, a))
    return s, pgs, arts


raw = {lang: load_lang(lang) for lang in LANGS}

# Les pàgines de cada llengua diuen quina és la seva en català ("ca"): així el selector porta a la mateixa pàgina
ca_slugs = {p["slug"] for _, p in raw["ca"][1]} | {a["slug"] for _, a in raw["ca"][2]}
for lang in LANGS:
    TO_CA[lang], FROM_CA[lang] = {}, {"": ""}
    for f, x in raw[lang][1] + raw[lang][2]:
        ca = x["slug"] if lang == "ca" else x.get("ca")
        if lang != "ca" and ca not in ca_slugs:
            errors.append(f"{f.relative_to(ROOT)}: \"ca\" ha de ser l'adreça de la mateixa pàgina en català (ara: {ca!r})")
            continue
        TO_CA[lang][x["slug"]] = ca
        FROM_CA[lang][ca] = x["slug"]
for lang in LANGS:
    if lang != "ca":
        falten = sorted(ca_slugs - set(FROM_CA[lang]))
        if falten:
            print(f"Avís: aquestes pàgines encara no tenen versió {LANGS[lang]['name']}: {', '.join(falten)}")

ESCENES = {a or b for a, b in re.findall(r'SCENES(?:\.([\w]+)|\["([\w-]+)"\])\s*=', (SRC / "templates" / "infografies" / "infografia-metafora.html").read_text(encoding="utf-8"))}

LANG = {}
for lang in LANGS:
    s, pgs, arts = raw[lang]
    home = s["home"]
    home["sections"] = prepare_sections(home.get("sections"), f"data/{LANGS[lang]['prefix']}site.json (home)", lang)
    pages = []
    for f, p in pgs:
        p["sections"] = prepare_sections(p.get("sections"), str(f.relative_to(ROOT)), lang)
        # "metafora": {"name": ..., "text": ...}: l'escena petita sota el títol (src/templates/infografies/infografia-metafora.html)
        if p.get("metafora") and p["metafora"].get("name") not in ESCENES:
            errors.append(f"{f.relative_to(ROOT)}: l'escena «{p['metafora'].get('name')}» de \"metafora\" no existeix (n'hi ha: {', '.join(sorted(ESCENES))})")
        pages.append(p)
    slugs = {p["slug"] for p in pages}
    # Articles: data/articles/<adreça>.json → /<adreça>/ (les mateixes adreces que a WordPress)
    articles = []
    for f, a in arts:
        if a["slug"] in slugs:
            errors.append(f"{f.relative_to(ROOT)}: ja hi ha una pàgina amb l'adreça /{a['slug']}/")
        if a.get("image") and not (SRC / "img" / a["image"]).exists():
            errors.append(f"{f.relative_to(ROOT)}: no trobo la imatge src/img/{a['image']}")
        a["date_text"] = data_llarga(a["date"], lang)
        first = next(b for b in a["body"] if isinstance(b, str))
        a["summary"] = a.get("summary") or (first if len(first) <= 230 else first[:230].rsplit(" ", 1)[0] + "…")
        a["words"] = sum(len(b.split()) for b in a["body"] if isinstance(b, str))
        articles.append(a)
    articles.sort(key=lambda a: a["date"], reverse=True)
    # El menú només pot portar a pàgines que existeixen (o a l'inici, "")
    for n in s.get("nav", []):
        for item in [n] + n.get("children", []):
            if item.get("slug") not in slugs | {""} and not item.get("href"):
                errors.append(f"data/{LANGS[lang]['prefix']}site.json (nav): «{item.get('title')}» porta a /{LANGS[lang]['prefix']}{item.get('slug')}/, però no hi ha la pàgina")
    LANG[lang] = {"site": s, "home": home, "pages": pages, "slugs": slugs, "articles": articles}

# Compatibilitat amb la resta del fitxer (adreces antigues): les pàgines en català
slugs = LANG["ca"]["slugs"]

if errors:
    print("No s'ha generat la web. Cal arreglar:", *("- " + e for e in errors), sep="\n")
    sys.exit(1)


def cap(s):
    """La primera lletra en majúscula, encara que davant hi hagi «¿», «¡» o cometes (p. ex. «¿qué nos mueve?»)."""
    if not s:
        return s
    out = re.sub(r"^([¿¡«“\"'(]*)(\w)", lambda m: m.group(1) + m.group(2).upper(), str(s), count=1)
    return Markup(out) if isinstance(s, Markup) else out


class TranslatedLoader(FileSystemLoader):
    """Plantilles d'una altra llengua: les mateixes de src/templates/, amb els textos canviats segons
    data/<llengua>/plantilles.json: {"base.html": [["text en català", "text traduït"], ...], ...}.
    Si un text en català ja no hi és (perquè s'ha canviat la plantilla), ho diu i no genera res."""

    def __init__(self, path, lang):
        super().__init__(path)
        f = LANGS[lang]["data"] / "plantilles.json"
        self.where = f.relative_to(ROOT)
        self.repl = {k: v for k, v in json.loads(f.read_text(encoding="utf-8")).items() if not k.startswith("_")} if f.exists() else {}
        self.used = set()

    def get_source(self, environment, template):
        src, filename, uptodate = super().get_source(environment, template)
        pairs = self.repl.get(template)
        if pairs:
            self.used.add(template)
            missing = [a for a, b in pairs if a not in src]
            if missing:
                raise SystemExit(f"No s'ha generat la web. A {self.where}, «{template}» té textos que ja no són a la plantilla:\n" + "\n".join("- " + m for m in missing))
            # Tots alhora i el més llarg primer, perquè un text traduït no es torni a traduir
            table = dict(pairs)
            rx = re.compile("|".join(re.escape(a) for a in sorted(table, key=len, reverse=True)))
            src = rx.sub(lambda m: table[m.group(0)], src)
        return src, filename, uptodate


img = SRC / "img"
ENVS = {}
for lang in LANGS:
    loader = FileSystemLoader(SRC / "templates") if lang == "ca" else TranslatedLoader(SRC / "templates", lang)
    env = Environment(loader=loader, autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    # |cap: la primera lletra en majúscula (els avantítols de WordPress anaven en minúscula perquè es pintaven en majúscules)
    env.filters["cap"] = cap
    env.globals.update(icon=icon, site=LANG[lang]["site"], noindex=NOINDEX, version=str(int(time.time())),
                       logo=(img / "logo-elara.png").exists(),
                       favicon=(img / "favicon-48.png").exists(),
                       partners_logo=(img / "lespiral-elara.png").exists(),
                       articles=LANG[lang]["articles"], lang=lang, locale=LANGS[lang]["locale"])
    ENVS[lang] = env

PAGES = []


def alternates(lang, slug):
    """Les adreces de la mateixa pàgina en cada llengua (per al selector i per a hreflang)."""
    ca = TO_CA[lang].get(slug, slug) if slug else ""
    out = []
    for l, L in LANGS.items():
        s = FROM_CA[l].get(ca)
        out.append({"lang": l, "short": L["short"], "name": L["name"], "current": l == lang,
                    "missing": s is None, "path": L["prefix"] + (s + "/" if s else "")})
    return out


def render(template, path, lang="ca", slug=None, **ctx):
    depth = len([p for p in path.split("/") if p])
    pre = len([p for p in LANGS[lang]["prefix"].split("/") if p])
    aroot = ctx.pop("aroot", "../" * depth)                  # fins a l'arrel de la web (assets/)
    root = ctx.pop("root", "../" * (depth - pre))            # fins a l'inici de la llengua (enllaços)
    canonical = None if path.endswith(".html") else SITE_URL + (path + "/" if path else "")
    if canonical:
        PAGES.append(canonical)
    alts = alternates(lang, slug if slug is not None else "") if canonical and len(LANGS) > 1 else []
    for a in alts:
        a["url"] = SITE_URL + a["path"]
        a["href"] = aroot + a["path"]
    out = ENVS[lang].get_template(template).render(root=root, aroot=aroot, canonical=canonical, alts=alts, **ctx)
    dest = OUT / path / "index.html" if not path.endswith(".html") else OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    return out


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

pending = 0
for lang, L in LANG.items():
    pre = LANGS[lang]["prefix"]
    pending += render("home.html", pre.rstrip("/"), lang, "", section="", h=L["home"]).count("[PENDENT]")
    for p in L["pages"]:
        pending += render("page.html", pre + p["slug"], lang, p["slug"], section=p["slug"], page_title=p["title"], page_description=p.get("description") or p.get("lead"), page=p).count("[PENDENT]")
    art_section = next((p["slug"] for p in L["pages"] if any(s.get("type") == "articles" for s in p["sections"])), "articles")
    for a in L["articles"]:
        pending += render("article.html", pre + a["slug"], lang, a["slug"], section=art_section, page_title=a["title"], page_description=a["summary"], article=a, articles_slug=art_section).count("[PENDENT]")
    unused = set(ENVS[lang].loader.repl) - ENVS[lang].loader.used if lang != "ca" else set()
    if unused:
        errors.append(f"data/{pre}plantilles.json: aquestes plantilles no es fan servir enlloc: {', '.join(sorted(unused))}")
render("404.html", "404.html", page_title="Pàgina no trobada", root=BASE, aroot=BASE, base=BASE)
home = LANG["ca"]["home"]
pages = LANG["ca"]["pages"]
articles = LANG["ca"]["articles"]

# Adreces antigues de la web de WordPress que ja no són una pàgina: porten a la nova.
# A data/site.json, "redirects": {"adreça-antiga": "pagina/#seccio" o "https://..."}
REDIRECT = """<!doctype html>
<html lang="ca"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>{title}</title><link rel="canonical" href="{to}"><meta http-equiv="refresh" content="0; url={to}">
</head><body><p>Aquesta pàgina ha canviat d'adreça: <a href="{to}">{to}</a></p></body></html>
"""
n_redirects = 0
for old, to in (site.get("redirects") or {}).items():
    old = old.strip("/")
    if old in slugs:
        errors.append(f"data/site.json (redirects): /{old}/ és una pàgina de la web; no pot portar a una altra")
        continue
    if not to.startswith("http"):
        page = to.split("#")[0].strip("/")
        if page and page not in slugs:
            errors.append(f"data/site.json (redirects): /{old}/ porta a /{page}/, que no existeix")
            continue
        to = SITE_URL + to.lstrip("/")
    dest = OUT / old / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(REDIRECT.format(title=site["name"], to=to), encoding="utf-8")
    n_redirects += 1
if errors:
    print("No s'ha generat la web. Cal arreglar:", *("- " + e for e in errors), sep="\n")
    shutil.rmtree(OUT)
    sys.exit(1)

(OUT / "assets").mkdir(exist_ok=True)
shutil.copy(SRC / "site.css", OUT / "assets" / "site.css")
shutil.copy(SRC / "site.js", OUT / "assets" / "site.js")
if img.exists():
    shutil.copytree(img, OUT / "assets" / "img")
(OUT / ".nojekyll").write_text("")
if NOINDEX:
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
else:
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n")
    today = time.strftime("%Y-%m-%d")
    urls = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
if (ROOT / "CNAME").exists():
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")

langs = ", ".join(f"{L['name'].lower()}: {len(LANG[l]['pages']) + 1} pàgines i {len(LANG[l]['articles'])} articles" for l, L in LANGS.items())
print(f"Fet: {langs}; {n_redirects} adreces antigues redirigides, {pending} marques [PENDENT]. adreça={SITE_URL} cercadors={'no' if NOINDEX else 'sí'}")
