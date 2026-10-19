"""Validate the built documentation, migration accounting and CLI examples."""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import tomllib
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SITE = ROOT / 'site'
config = tomllib.loads((ROOT / 'zensical.toml').read_text())['project']
errors = []

def check(ok, message):
    if not ok:
        errors.append(message)

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.ids = [], set()
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append((tag, attrs[key]))
        if 'srcset' in attrs:
            self.links.extend((tag, item.strip().split()[0]) for item in attrs['srcset'].split(','))

def nav_paths(node):
    if isinstance(node, str):
        return [node]
    if isinstance(node, list):
        return sum((nav_paths(item) for item in node), [])
    return sum((nav_paths(item) for item in node.values()), [])

pages = sorted(str(p.relative_to(ROOT / 'docs')) for p in (ROOT / 'docs').rglob('*.md'))
nav = nav_paths(config['nav'])
llm = sum(config['plugins']['llmstxt']['sections'].values(), [])
check(Counter(nav) == Counter(pages), 'Navigation must cover every public page exactly once')
check(Counter(llm) == Counter(pages), 'LLM selections must cover every public page exactly once')
base = config['site_url']
parsed = {}
for p in SITE.rglob('*.html'):
    parsed[p.resolve()] = Page(p.read_text())
for path, page in parsed.items():
    url = base + path.relative_to(SITE).as_posix()
    for tag, href in page.links:
        dest = urljoin(url, href)
        if not dest.startswith(base):
            if tag in ('script', 'img', 'iframe', 'link') and dest.startswith(('http:', 'https:')):
                # Canonical links describe the page, not a browser resource fetch.
                check(tag == 'link' and dest.startswith(config['site_url']), f'External asset: {path.name}: {href}')
            continue
        split = urlsplit(dest)
        rel = unquote(split.path[len(urlsplit(base).path):])
        target = SITE / rel
        if target.is_dir():
            target /= 'index.html'
        check(target.is_file(), f'Missing link: {path.name} -> {href}')
        if split.fragment and target.resolve() in parsed:
            check(unquote(split.fragment) in parsed[target.resolve()].ids,
                  f'Missing anchor: {path.name} -> {href}')

index = (SITE / 'llms.txt').read_text()
llm_links = re.findall(r'\]\(<?(https?://[^)>]+)>?\)', index)
check(Counter(llm_links) == Counter(base + p for p in llm), 'llms.txt links differ from selected Markdown paths')
for p in llm:
    check((SITE / p).is_file(), f'Missing Markdown export: {p}')
    check((SITE / p.replace('.md', '.html')).is_file(), f'Missing HTML page: {p}')
check((SITE / 'llms-full.txt').stat().st_size > 1000, 'Missing full LLM export')
for p in SITE.rglob('*.md'):
    for link in re.findall(r'\]\(<?([^)>]+)>?\)', p.read_text()):
        if link.startswith(base):
            target = SITE / unquote(link[len(base):].split('#')[0])
            check(target.is_file(), f'Broken Markdown export link: {p.name}: {link}')

manifest = json.loads((ROOT / 'documentation/migration/manifest.json').read_text())
for item in manifest['sources']:
    if item['destination']:
        check((ROOT / item['destination']).exists(), f'Migration destination missing: {item}')
    if item['disposition'] in ('exclude', 'retain') and (ROOT / item['source']).exists():
        check(sha256((ROOT / item['source']).read_bytes()).hexdigest() == item['sha256'], f'Retained/excluded source changed: {item["source"]}')
for item in manifest['new_files']:
    p = ROOT / item['destination']
    check(p.exists(), f'New artifact missing: {p}')
    if 'sha256' in item:
        check(sha256(p.read_bytes()).hexdigest() == item['sha256'], f'Vendored artifact changed: {p}')
accounted = {i['destination'] for i in manifest['sources'] + manifest['new_files']}
for p in (ROOT / 'docs').rglob('*'):
    if p.is_file():
        check(str(p.relative_to(ROOT)) in accounted, f'Unaccounted documentation file: {p}')
check((SITE / config['theme']['favicon']).read_bytes() == (ROOT / 'docs' / config['theme']['favicon']).read_bytes(), 'Favicon was not copied into the site')
check(config['extra']['generator'] is False, 'Generator notice enabled')

# Check options only in runnable CLI fences, not the synopsis with placeholders.
from emf_reader.cli import build_parser
from emf_reader.xsd_enrich_cli import build_parser as xsd_parser
options = {name: {o for a in factory()._actions for o in a.option_strings}
           for name, factory in [('emf-read', build_parser), ('xsd-enrich', xsd_parser)]}
for p in (ROOT / 'docs').rglob('*.md'):
    for block in re.findall(r'```bash\n(.*?)```', p.read_text(), re.S):
        for cmd in re.split(r'\n(?=(?:emf-read|xsd-enrich)\b)', block):
            match = re.match(r'(emf-read|xsd-enrich)\b', cmd.strip())
            if match:
                for option in re.findall(r'(?<!\w)--[a-z][a-z-]+', cmd):
                    check(option in options[match[1]], f'Unknown CLI flag in {p.name}: {option}')
# Never export the local session helper or its contents.
for p in SITE.rglob('*'):
    if p.is_file() and p.suffix in ('.html', '.md', '.txt', '.json', '.xml'):
        text = p.read_text(errors='replace')
        for forbidden in ('codex resume ', 'helper.txt', '/home/abinitio/', '/var/software/gitrepos/'):
            check(forbidden not in text, f'Excluded/local operational content in {p}: {forbidden}')

result = {'pages': len(pages), 'html_files': len(parsed), 'llm_pages': len(llm), 'errors': errors}
print(json.dumps(result, indent=2))
evidence = ROOT / 'documentation/migration/evidence'
evidence.mkdir(parents=True, exist_ok=True)
(evidence / 'static-check.json').write_text(json.dumps(result, indent=2) + '\n')
raise SystemExit(bool(errors))
