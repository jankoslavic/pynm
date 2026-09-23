"""Po gradnji (jupyter book build --html) ustvari preusmeritvene strani na starih
naslovih knjige (Sphinx / Jupyter Book 1), da stare povezave (e-učilnica,
moj.ladisk.si, zaznamki) še delujejo.

Stari naslov:  notebooks/Predavanje 07 - Interpolacija.html
Novi naslov:   notebooks/predavanje-07-interpolacija/

Uporaba:  python .github/redirects.py [_build/html]
"""
import os
import re
import sys

import yaml

OUT = sys.argv[1] if len(sys.argv) > 1 else '_build/html'

# Stara imena datotek s šumniki (pred preimenovanjem 23. 9. 2026) -> sedanja imena
LEGACY = {
    'Študijski in izpitni red': 'Studijski in izpitni red',
    'Predavanje 04 - Objektno programiranje, simbolno računanje': 'Predavanje 04 - Objektno programiranje, simbolno racunanje',
    'Predavanje 05 - Uvod v numerične metode in sistemi linearnih enačb 1': 'Predavanje 05 - Uvod v numericne metode in sistemi linearnih enacb 1',
    'Predavanje 06 - Sistemi linearnih enačb 2': 'Predavanje 06 - Sistemi linearnih enacb 2',
    'Predavanje 09 - Reševanje enačb': 'Predavanje 09 - Resevanje enacb',
    'Predavanje 10 - Numerično odvajanje': 'Predavanje 10 - Numericno odvajanje',
    'Predavanje 11 - Numerično integriranje': 'Predavanje 11 - Numericno integriranje',
    'Predavanje 12 - Numerično reševanje diferencialnih enačb - začetni problem': 'Predavanje 12 - Numericno resevanje diferencialnih enacb - zacetni problem',
    'Predavanje 13 - Numerično reševanje diferencialnih enačb - robni problem': 'Predavanje 13 - Numericno resevanje diferencialnih enacb - robni problem',
    'Predavanje 14 - Testiranje pravilnosti kode, uporabniški vmesnik': 'Predavanje 14 - Testiranje pravilnosti kode, uporabniski vmesnik',
}

TEMPLATE = """<!DOCTYPE html>
<html lang="sl"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{url}">
<title>Preusmeritev</title></head>
<body><p>Stran se je preselila: <a href="{url}">{url}</a></p></body></html>
"""


def slug(name):
    """Posnema MyST: male črke, ne-alfanumerični znaki -> '-', največ 50 znakov."""
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return s[:50].rstrip('-')


def write(path, url):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(TEMPLATE.format(url=url))


cfg = yaml.safe_load(open('myst.yml', encoding='utf-8'))
n = 0
for entry in cfg['project']['toc']:
    file = entry.get('file', '')
    if not file.startswith('notebooks/'):
        continue
    name = os.path.splitext(os.path.basename(file))[0]
    target = f'{slug(name)}/'
    if not os.path.isdir(os.path.join(OUT, 'notebooks', slug(name))):
        print('OPOZORILO: ciljna mapa ne obstaja:', target)
    write(os.path.join(OUT, 'notebooks', name + '.html'), target); n += 1
    for old, new in LEGACY.items():
        if new == name:
            write(os.path.join(OUT, 'notebooks', old + '.html'), target); n += 1

write(os.path.join(OUT, 'README.html'), './'); n += 1
print(f'ustvarjenih {n} preusmeritev v {OUT}')
