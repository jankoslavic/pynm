"""Zgradi celotno knjigo kot en PDF (jupyter book build --pdf, predloga pdf/template).

Beležnic v repozitoriju ne spreminja: knjigo najprej prepiše v _build/pdf_src/ in tam
pripravi kopije beležnic za tisk:
  * odstrani HTML izhode z vdelanimi base64 podatki (zvok, video ...), ki jih LaTeX ne zna;
  * dodatne naslove 1. ravni ("# Dodatno", "# Vprašanja za vaje") zniža na 2. raven, da ima
    vsaka beležnica en sam naslov (= poglavje) in MyST enako preslika nižje ravni.
Rezultat: _build/exports/<ime>.pdf; če obstaja _build/html/, PDF skopira tudi tja
(objavi se skupaj s spletno knjigo).

Zahteve: jupyter-book >= 2.1, xelatex + latexmk (TeX Live / TinyTeX), imagemagick.
Uporaba:  python .github/build_pdf.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

import yaml

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SRC = os.path.join(ROOT, '_build', 'pdf_src')
SKIP_DIRS = {'_build', '.git', '.venv', '.github', 'node_modules'}

cfg = yaml.safe_load(open(os.path.join(ROOT, 'myst.yml'), encoding='utf-8'))
exports = [e for e in cfg['project'].get('exports', []) if e.get('format') == 'pdf']
if not exports:
    sys.exit('myst.yml nima izvoza s format: pdf')
pdf_name = os.path.basename(exports[0]['output'])
toc_files = [e['file'] for e in cfg['project']['toc'] if 'file' in e]
toc_dirs = {f.split('/')[0] for f in toc_files if '/' in f}

# 1. kopija knjige
if os.path.isdir(SRC):
    shutil.rmtree(SRC)
os.makedirs(SRC)
for name in os.listdir(ROOT):
    path = os.path.join(ROOT, name)
    if name in SKIP_DIRS or name.startswith('.'):
        continue
    if os.path.isfile(path):
        shutil.copy2(path, SRC)
    elif name in toc_dirs or name == 'pdf':
        shutil.copytree(path, os.path.join(SRC, name), ignore=shutil.ignore_patterns('.ipynb_checkpoints', '__pycache__'))

# 2. priprava beležnic
H1 = re.compile(r'^# (?!#)')
for rel in toc_files:
    if not rel.endswith('.ipynb'):
        continue
    path = os.path.join(SRC, rel)
    nb = json.load(open(path, encoding='utf-8'))
    changed, seen_title, cells = [], False, []
    for cell in nb['cells']:
        cells.append(cell)
        if cell['cell_type'] == 'code':
            # SymPy izhodi (text/latex): MyST bi v PDF dal ASCII "risbo" (text/plain) ali veliko
            # sliko (image/png); namesto tega izraz zapišemo kot enačbo v novi markdown celici.
            math = []
            for out in list(cell.get('outputs', [])):
                latex = ''.join(out.get('data', {}).get('text/latex', []))
                if latex:
                    latex = re.sub(r'^\$\\displaystyle\s*|\$$', '', latex.strip())
                    math.append(latex.strip('$'))
                    cell['outputs'].remove(out)
            if math:
                cells.append({'cell_type': 'markdown', 'metadata': {},
                              'source': '$$\n' + '\n$$\n\n$$\n'.join(math) + '\n$$'})
                changed.append(f'{len(math)}x sympy izhod kot enačba')
        if cell['cell_type'] == 'markdown':
            lines, fenced = [], False
            for line in ''.join(cell['source']).split('\n'):
                if line.startswith('```'):
                    fenced = not fenced
                if not fenced and H1.match(line):
                    if seen_title:
                        line = '#' + line
                        changed.append(line)
                    seen_title = True
                lines.append(line)
            cell['source'] = '\n'.join(lines)
        for out in cell.get('outputs', []):
            data = out.get('data', {})
            html = ''.join(data.get('text/html', []))
            if 'base64' in html and 'data:' in html:
                del data['text/html']
                changed.append('odstranjen HTML izhod z base64 podatki')
    nb['cells'] = cells
    if changed:
        json.dump(nb, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        print(f'{rel}: ' + '; '.join(changed))

# 3. gradnja
subprocess.run(['jupyter', 'book', 'build', '--pdf'], cwd=SRC, check=True)

# 4. rezultat
built = os.path.join(SRC, '_build', 'exports', pdf_name)
if not os.path.isfile(built):
    sys.exit(f'PDF ni nastal: {built}')
os.makedirs(os.path.join(ROOT, '_build', 'exports'), exist_ok=True)
shutil.copy2(built, os.path.join(ROOT, '_build', 'exports', pdf_name))
print('PDF:', os.path.join('_build', 'exports', pdf_name), f'({os.path.getsize(built) / 1e6:.1f} MB)')
html = os.path.join(ROOT, '_build', 'html')
if os.path.isdir(html):
    shutil.copy2(built, os.path.join(html, pdf_name))
    print('PDF skopiran v _build/html/ (objavi se s knjigo)')
