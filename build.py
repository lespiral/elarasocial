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
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
DATA, SRC, OUT = ROOT / "data", ROOT / "src", ROOT / "docs"

ICONS = json.loads((SRC / "icons.json").read_text(encoding="utf-8"))

# Tipus de secció que saben pintar les plantilles (src/templates/parts.html, macro «section»)
SECTION_TYPES = {"text", "cards", "list", "faq", "note", "infografia", "cta", "contact"}


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
        if t == "faq":
            s["items"] = [(q, html(a), slugify(q)) for q, a in s.get("items", [])]
        if t == "infografia":
            f = SRC / "templates" / "infografies" / f"infografia-{s['name']}.html"
            if not f.exists():
                errors.append(f"{where}: no trobo la infografia {f.relative_to(ROOT)}")
        for it in s.get("items", []) if t in ("cards", "list") else []:
            if isinstance(it, dict) and it.get("icon") and it["icon"] not in ICONS:
                errors.append(f"{where}: la icona {it['icon']!r} no és a src/icons.json")
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
    pages.append(p)
slugs = {p["slug"] for p in pages}

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
env.globals.update(icon=icon, site=site, noindex=NOINDEX, version=str(int(time.time())),
                   logo=(img / "logo-elara.png").exists(),
                   favicon=(img / "favicon-48.png").exists(),
                   partners_logo=(img / "lespiral-elara.png").exists())

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
render("404.html", "404.html", page_title="Pàgina no trobada", root=BASE, base=BASE)

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

print(f"Fet: {len(pages) + 1} pàgines, {pending} marques [PENDENT]. adreça={SITE_URL} cercadors={'no' if NOINDEX else 'sí'}")
