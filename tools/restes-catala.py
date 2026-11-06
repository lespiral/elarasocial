#!/usr/bin/env python3
"""Busca restes de català a la versió en castellà (docs/es/), un cop generada la web.

Ús:  python3 tools/restes-catala.py

Mira el text de les pàgines, els atributs (aria-label, title, alt) i les cadenes del codi de les
infografies. Avisa de paraules que només són catalanes (amb, els, perquè…), de les lletres que el
castellà no fa servir (à, è, ò, ç, l·l) i dels apòstrofs (l’, d’). Els noms propis catalans
(Camins d'Esperança [Activa], L’Espiral, El Prat de Llobregat…) no compten.
"""
import html, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES = ROOT / "docs" / "es"

# Noms propis i adreces que es queden en català
ALLOWED = [
    "Camins d'Esperança [Activa]", "Camins d’Esperança [Activa]", "esperançaactiva.cat", "L’Espiral", "L'Espiral",
    "El Prat de Llobregat", "Jaume Casanovas", "Ferran Castellarnau", "Català", "lespiral.cat", "elarasocial.com",
]
WORDS = set("""amb els les per perquè també molt sense fins dins aquest aquesta aquests aquestes nosaltres vosaltres
teu teva teus teves seu seva seus seves mateix mateixa és són però què quan quin quina quins quines cap més
fer fem feu tenim teniu podem pots puc vol volem voleu cal hi ho això allò aquí allà dels pels als
nostre nostra nostres vostre vostra vostres cada vegada sempre també tothom ningú res gaire potser així
una dues tres quatre cinc sis set vuit nou deu hores sessions setmana setmanes passes passa cercle cercles
paraula paraules taller tallers trobada trobades comunitat comunitats persones organització organitzacions
treball treballem incertesa suport acció esperança""".split())
# Paraules que també són castellanes o de noms propis (no són restes)
WORDS -= {"una", "res", "cada", "set", "nou", "les", "taller", "tres", "aquí", "allà"}
APOS = re.compile(r"\b[ldsmtn]['’][a-zàèéíòóú]", re.I)
LETTERS = re.compile(r"[àèòçï]|l·l", re.I)


def texts(src):
    """El text visible, els atributs i les cadenes de codi (dins de <script>) d'una pàgina."""
    out = []
    for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", src, re.S):
        # Sense comentaris; i només cadenes que semblen text (no noms de classe, d'escena o adreces)
        code = re.sub(r"/\*.*?\*/", " ", m.group(1), flags=re.S)
        code = re.sub(r"(^|[\s;{}(,])//[^\n]*", r"\1", code)
        strs = [a or b for a, b in re.findall(r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'', code)]
        out += [("codi", x) for x in strs if not re.fullmatch(r"[.#]?[\w-]+", x) and "://" not in x]
    body = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", src, flags=re.S)
    out += [("atribut", html.unescape(v)) for v in re.findall(r'(?:aria-label|title|alt|content)="([^"]*)"', body)]
    out += [("text", html.unescape(t)) for t in re.findall(r">([^<]+)<", body)]
    return out


def suspicious(s):
    s2 = s
    for a in ALLOWED:
        s2 = s2.replace(a, " ")
    s2 = re.sub(r"https?://\S+", " ", s2)
    words = {w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ·]+", s2)}
    why = sorted(words & WORDS)
    if LETTERS.search(s2):
        why.append("lletra " + LETTERS.search(s2).group(0))
    if APOS.search(s2):
        why.append("apòstrof «" + APOS.search(s2).group(0) + "»")
    return why


def main():
    if not ES.exists():
        sys.exit("No hi ha docs/es/: genera la web abans (python3 build.py).")
    found = 0
    for f in sorted(ES.rglob("*.html")):
        seen = set()
        for kind, s in texts(f.read_text(encoding="utf-8")):
            s = " ".join(s.split())
            if len(s) < 2 or s in seen:
                continue
            why = suspicious(s)
            if why:
                seen.add(s)
                found += 1
                print(f"{f.relative_to(ROOT)} [{kind}] {', '.join(why)}: {s[:160]}")
    print(f"{found} textos per revisar." if found else "No hi ha restes de català a docs/es/.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
