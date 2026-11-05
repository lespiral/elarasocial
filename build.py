#!/usr/bin/env python3
"""Genera la web estàtica d'Elara Social a la carpeta docs/.

Ús:  python3 build.py

Fa servir el mateix sistema que la web de Camins d'Esperança [Activa]
(lespiral/esperancaactiva): dades en JSON, plantilles Jinja i un sol full d'estils.

- data/site.json: el nom, l'adreça pública, el menú, el contacte, el peu i la pàgina d'inici.
- data/pages/<adreça>.json: una pàgina per fitxer (vegeu el README).

L'adreça pública i si la web ha de sortir als cercadors es configuren a
data/site.json, a "publish": {"url": ..., "index": true/false}.
"""
import json, re, shutil, sys, time, unicodedata
from pathlib import Path
from urllib.parse import urlparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
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


def card_icon(href):
    if not href:
        return None
    page = href.split("#")[0].strip("/")
    if page in CARD_ICONS:
        return CARD_ICONS[page]
    for k, v in CARD_ICONS.items():
        if k in href:
            return v
    return None


# Icona de les llistes de les seccions de text, segons el títol ("list_icon" a la secció per triar-ne una altra)
LIST_ICONS = [("explorarem", "compass"), ("practicarem", "footprints"), ("emportar", "leaf"), ("treballarem", "hand-heart")]


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


def prepare_sections(sections, where):
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
            if isinstance(it, dict) and "icon" not in it and card_icon(it.get("href")):
                it["icon"] = card_icon(it.get("href"))
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

home = site["home"]
home["sections"] = prepare_sections(home.get("sections"), "data/site.json (home)")

pages = []
for f in sorted((DATA / "pages").glob("*.json")):
    p = json.loads(f.read_text(encoding="utf-8"))
    p.setdefault("slug", f.stem)
    if p["slug"] != f.stem:
        errors.append(f"{f.relative_to(ROOT)}: el camp slug ({p['slug']}) ha de ser igual que el nom del fitxer")
    p["sections"] = prepare_sections(p.get("sections"), str(f.relative_to(ROOT)))
    # "metafora": {"name": ..., "text": ...}: l'escena petita sota el títol (src/templates/infografies/infografia-metafora.html)
    if p.get("metafora"):
        m = p["metafora"]
        escenes = re.findall(r'SCENES(?:\.([\w]+)|\["([\w-]+)"\])\s*=', (SRC / "templates" / "infografies" / "infografia-metafora.html").read_text(encoding="utf-8"))
        if m.get("name") not in {a or b for a, b in escenes}:
            errors.append(f"{f.relative_to(ROOT)}: l'escena «{m.get('name')}» de \"metafora\" no existeix (n'hi ha: {', '.join(sorted(a or b for a, b in escenes))})")
    pages.append(p)
slugs = {p["slug"] for p in pages}

# Articles: data/articles/<adreça>.json → /<adreça>/ (les mateixes adreces que a WordPress)
MESOS = ["gener", "febrer", "març", "abril", "maig", "juny", "juliol", "agost", "setembre", "octubre", "novembre", "desembre"]


def data_llarga(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    mes = MESOS[m - 1]
    return f"{d} {'d’' if mes[0] in 'ao' else 'de '}{mes} de {y}"


articles = []
for f in sorted((DATA / "articles").glob("*.json")) if (DATA / "articles").exists() else []:
    a = json.loads(f.read_text(encoding="utf-8"))
    a["slug"] = f.stem
    if a["slug"] in slugs:
        errors.append(f"{f.relative_to(ROOT)}: ja hi ha una pàgina amb l'adreça /{a['slug']}/")
    if a.get("image") and not (SRC / "img" / a["image"]).exists():
        errors.append(f"{f.relative_to(ROOT)}: no trobo la imatge src/img/{a['image']}")
    a["date_text"] = data_llarga(a["date"])
    first = next(b for b in a["body"] if isinstance(b, str))
    a["summary"] = a.get("summary") or (first if len(first) <= 230 else first[:230].rsplit(" ", 1)[0] + "…")
    a["words"] = sum(len(b.split()) for b in a["body"] if isinstance(b, str))
    articles.append(a)
articles.sort(key=lambda a: a["date"], reverse=True)

# El menú només pot portar a pàgines que existeixen (o a l'inici, "")
for n in site.get("nav", []):
    for item in [n] + n.get("children", []):
        if item.get("slug") not in slugs | {""} and not item.get("href"):
            errors.append(f"data/site.json (nav): «{item.get('title')}» porta a /{item.get('slug')}/, però no hi ha data/pages/{item.get('slug')}.json")

if errors:
    print("No s'ha generat la web. Cal arreglar:", *("- " + e for e in errors), sep="\n")
    sys.exit(1)

img = SRC / "img"
env = Environment(loader=FileSystemLoader(SRC / "templates"), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
# |cap: la primera lletra en majúscula (els avantítols de WordPress anaven en minúscula perquè es pintaven en majúscules)
env.filters["cap"] = lambda s: (s[:1].upper() + s[1:]) if s else s
env.globals.update(icon=icon, site=site, noindex=NOINDEX, version=str(int(time.time())),
                   logo=(img / "logo-elara.png").exists(),
                   favicon=(img / "favicon-48.png").exists(),
                   partners_logo=(img / "lespiral-elara.png").exists(),
                   articles=articles)

PAGES = []


def render(template, path, **ctx):
    depth = len([p for p in path.split("/") if p])
    root = ctx.pop("root", "../" * depth)
    canonical = None if path.endswith(".html") else SITE_URL + (path + "/" if path else "")
    if canonical:
        PAGES.append(canonical)
    out = env.get_template(template).render(root=root, canonical=canonical, **ctx)
    dest = OUT / path / "index.html" if not path.endswith(".html") else OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    return out


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

pending = 0
pending += render("home.html", "", section="", h=home).count("[PENDENT]")
for p in pages:
    pending += render("page.html", p["slug"], section=p["slug"], page_title=p["title"], page_description=p.get("description") or p.get("lead"), page=p).count("[PENDENT]")
for a in articles:
    pending += render("article.html", a["slug"], section="articles", page_title=a["title"], page_description=a["summary"], article=a).count("[PENDENT]")
render("404.html", "404.html", page_title="Pàgina no trobada", root=BASE, base=BASE)

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

print(f"Fet: {len(pages) + 1} pàgines, {len(articles)} articles, {n_redirects} adreces antigues redirigides, {pending} marques [PENDENT]. adreça={SITE_URL} cercadors={'no' if NOINDEX else 'sí'}")
