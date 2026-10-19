# Documentation development

`docs/` is the canonical source. Existing page filenames and `.html` URLs are
preserved. The GitHub Wiki remains an unchanged historical source; do not maintain
parallel copies. Review any future wiki edits and merge their useful content here.
Source links inside this site use `.md` paths so Zensical can validate and rewrite
them. Links within the historical GitHub Wiki use extensionless page names.

## Setup and preview

Run commands from the checkout root. Use the same application `.venv` for all tools.
Python 3.14 is the validated documentation and CI environment; the library still
advertises Python 3.11 or later.

```bash
python3.14 -m venv .venv  # only if .venv is absent
.venv/bin/python -m pip install -e .
.venv/bin/python -m pip install -r requirements-docs.txt
.venv/bin/zensical serve -a 127.0.0.1:8000
```

## Build and check

```bash
.venv/bin/zensical build --clean --strict
.venv/bin/python scripts/check_docs.py
.venv/bin/python -m pip check
```

The native llmstxt implementation generates `site/llms.txt`, `site/llms-full.txt`
and Markdown copies. Every intended public page appears exactly once in explicit
navigation and LLM selections. No separate mkdocs-llmstxt package or preprocess hook
is used. The checker validates generated links, anchors, assets, manifest coverage,
CLI options, navigation and Markdown exports.

## Browser verification

```bash
.venv/bin/python -m pip install -r requirements-docs-browser.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python scripts/check_docs_browser.py
```

The browser script serves the built site under its project subpath on localhost,
checks desktop/mobile pages, search, every Mermaid diagram and the favicon, and
exercises consent before a choice, rejection, acceptance and revocation. Evidence
is saved under `documentation/migration/evidence/`, outside the cleaned site output.
It records network requests, JavaScript failures and browser storage. The optional
GitHub request is monitored; its external availability is reported separately from
consent gating. These checks are optional local tools; the publishing workflow does not run them.

## Dependency updates

The complete installed dependency closures are pinned in `requirements-docs.txt`,
`requirements-docs-browser.txt` and `requirements-test.txt`. Update deliberately in
the same `.venv`, then regenerate and review all pins:

```bash
.venv/bin/python -m pip install --upgrade zensical playwright pytest
.venv/bin/python scripts/lock_docs.py
.venv/bin/python -m pip install --force-reinstall -r requirements-docs.txt -r requirements-docs-browser.txt
.venv/bin/python -m pip check
.venv/bin/zensical build --clean --strict
.venv/bin/python scripts/check_docs.py
.venv/bin/python scripts/check_docs_browser.py
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m pytest -q
```

The lock writer evaluates dependency markers for the current platform. Validate a
new platform/Python version before claiming the lock is portable. Mermaid updates
are separate: obtain an exact npm release, preserve its LICENSE, replace the full
browser bundle, and update provenance/checksums in the migration manifest before
running every diagram and network check. Do not switch to an unpinned CDN URL.

## Deployment and rollback

The established target is `https://chris-day.github.io/iso20022-ecore/`; the old
configuration and Pages workflow agree, and it returned HTTP 200 during migration.
No CNAME/custom domain was found. The existing main-branch/manual deployment triggers
are retained. Pull requests do not run this publishing workflow.
This migration does not publish or change Pages settings. Deployment happens only
after a maintainer merges/pushes the reviewed changes or dispatches the workflow.

The legacy configuration is retained at
[mkdocs.legacy.yml](https://github.com/chris-day/iso20022-ecore/blob/main/documentation/migration/mkdocs.legacy.yml).
For rollback, restore documentation, README, configuration and the docs workflow from
commit `b07218320db134e6453a32e7f2c93d584a20328e` in a new reviewed commit, remove the
Zensical configuration in that rollback, then rebuild with the previous workflow.
Do not reset unrelated application work. The old MkDocs dependencies were unpinned,
so rollback reproduces source configuration, not a guaranteed identical environment.

The unsupported documentation topology `graph` plugin is deliberately omitted;
explicit navigation, search and model Mermaid diagrams replace its discovery role.
The old missing `stylesheets/extra.css` reference is removed. Unused plugins installed
by the old workflow are not carried forward. GitHub Wiki URLs cannot be redirected
by this site; historical wiki sources remain available. Existing site URLs require
no redirects because page filenames and `use_directory_urls = false` are preserved.

## Hosted runner compatibility

The workflow follows the [standard Zensical GitHub Pages flow](https://zensical.org/docs/publish-your-site/):
configure Pages, check out the repository, set up Python, install Zensical, build,
upload the Pages artifact and deploy. It uses Node.js 24 action releases. Python
remains 3.14 in the checkout's `.venv`, with pinned documentation dependencies.

It does not install the application, run pytest, execute static/browser checks or
upload verification evidence. Those tools remain available locally. ISO 20022
integration tests skip when external inputs are absent; the generated metamodel
test runs without external files.
