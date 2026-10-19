"""Serve the project subpath and verify rendered pages and consent with Chromium."""
import functools
import http.server
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit
import tomllib
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CONFIG = tomllib.loads((ROOT / 'zensical.toml').read_text())['project']
PREFIX = urlsplit(CONFIG['site_url']).path
EVIDENCE = ROOT / 'documentation/migration/evidence'
EVIDENCE.mkdir(parents=True, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith(PREFIX):
            path = '/' + path[len(PREFIX):]
        return super().translate_path(path)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT / 'site')))
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}' + PREFIX
report = {'states': {}, 'diagrams': [], 'errors': [], 'failed_requests': [], 'http_errors': [], 'screenshots': []}
requests = []

def snapshot(page, context, state):
    page.wait_for_timeout(1000)
    report['states'][state] = {
        'requests': list(requests),
        'localStorage': page.evaluate('({...localStorage})'),
        'cookies': context.cookies(),
    }
    requests.clear()

def external(items):
    return [u for u in items if not u.startswith(BASE.split(PREFIX)[0])]

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        page = context.new_page()
        page.on('request', lambda r: requests.append(r.url))
        page.on('pageerror', lambda e: report['errors'].append(str(e)))
        page.on('requestfailed', lambda r: report['failed_requests'].append({'url': r.url, 'failure': r.failure}))
        page.on('response', lambda r: report['http_errors'].append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
        page.goto(BASE, wait_until='networkidle')
        consent = page.locator('[data-md-component="consent"]')
        consent.get_by_role('button', name='Reject', exact=True).wait_for(state='visible')
        assert not page.locator('input[name="github"]').is_checked()
        snapshot(page, context, 'before')
        assert not external(report['states']['before']['requests'])
        consent.get_by_role('button', name='Reject', exact=True).click()
        page.wait_for_load_state('networkidle')
        snapshot(page, context, 'rejected')
        assert not external(report['states']['rejected']['requests'])
        page.get_by_role('link', name='Change cookie settings', exact=True).click()
        page.locator('label[for="__settings"]').click()
        assert not page.locator('input[name="github"]').is_checked()
        # Native accept saves selected categories, so choose GitHub explicitly.
        page.locator('label').filter(has=page.locator('input[name="github"]')).click()
        consent.get_by_role('button', name='Accept', exact=True).click()
        page.wait_for_load_state('networkidle')
        snapshot(page, context, 'accepted')
        assert external(report['states']['accepted']['requests']), 'No optional request observed after opt-in'
        assert all(urlsplit(u).hostname == 'api.github.com' for u in external(report['states']['accepted']['requests']))
        page.get_by_role('link', name='Change cookie settings', exact=True).click()
        assert page.locator('input[name="github"]').is_checked()
        consent.get_by_role('button', name='Reject', exact=True).click()
        page.wait_for_load_state('networkidle')
        snapshot(page, context, 'revoked')
        assert not external(report['states']['revoked']['requests'])
        page.get_by_role('link', name='Change cookie settings', exact=True).click()
        assert not page.locator('input[name="github"]').is_checked()
        consent.get_by_role('button', name='Reject', exact=True).click()
        page.wait_for_load_state('networkidle')
        assert page.locator(f'a[href="{CONFIG["repo_url"]}"]').count() > 0
        assert 'Made with Zensical' not in page.locator('body').inner_text()
        favicon = page.locator('link[rel="icon"]').get_attribute('href')
        assert page.evaluate('''async (url) => {const image = new Image(); image.src = url;
            await image.decode(); return image.naturalWidth > 0 && image.naturalHeight > 0;}''', favicon)
        for source in sorted((ROOT / 'docs').glob('*.md')):
            page.goto(BASE + source.with_suffix('.html').name, wait_until='networkidle')
            assert page.locator('main h1').count() == 1
            expected = source.read_text().count('```mermaid')
            if expected:
                page.wait_for_function('(count) => document.querySelectorAll(".local-diagram[data-rendered] svg").length === count', arg=expected)
                assert page.locator('.local-diagram[data-error]').count() == 0
                report['diagrams'].append({'page': source.name, 'rendered': expected})
            if source.name in ('index.md', 'Pruning-and-Dry-Run.md', 'JSON-Schemas.md'):
                filename = source.stem + '-desktop.png'
                page.screenshot(path=str(EVIDENCE / filename), full_page=True)
                report['screenshots'].append(filename)
        # Playwright locators pierce the search component's open shadow DOM.
        page.locator('button.md-search__button').click()
        search = page.get_by_placeholder('Search', exact=True)
        search.fill('associationDomain')
        page.wait_for_timeout(1000)
        matches = page.locator('dialog').get_by_role('option').filter(has_text='Pruning')
        matches.first.wait_for(state='visible')
        assert matches.count() > 0
        report['search'] = {'query': 'associationDomain', 'matching_links': matches.all_text_contents()}
        page.keyboard.press('Escape')
        page.set_viewport_size({'width': 390, 'height': 844})
        page.goto(BASE + 'Pruning-and-Dry-Run.html', wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll(".local-diagram[data-rendered] svg").length === 2')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(EVIDENCE / 'pruning-mobile.png'), full_page=True)
        report['screenshots'].append('pruning-mobile.png')
        assert not report['errors'], report['errors']
        assert not [r for r in report['failed_requests'] if r['url'].startswith(BASE)], report['failed_requests']
        assert not [r for r in report['http_errors'] if r['url'].startswith(BASE)], report['http_errors']
        # Rejection remains active while inspecting all public pages.
        assert not external(requests), external(requests)
        report['result'] = 'passed'
        browser.close()
except Exception as error:
    report['result'] = 'failed'
    report['exception'] = repr(error)
    raise
finally:
    server.shutdown()
    (EVIDENCE / 'browser-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k,v in report.items() if k != 'states'}, indent=2))
