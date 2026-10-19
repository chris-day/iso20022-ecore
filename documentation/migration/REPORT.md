# Documentation migration report

## Scope and provenance

Migration baseline: `b07218320db134e6453a32e7f2c93d584a20328e`.
Canonical repository: https://github.com/chris-day/iso20022-ecore (matches origin).
Local and read-only remote wiki comparison commit:
`460fb39edfb8db36876ccb7ae8c6c78b9c7ced57`.
The remote wiki was accessible, not absent or authentication-blocked. Every local
wiki page matches the remote checkout byte for byte; see `wiki-comparison.json`.
The remote comparison checkout was temporary, outside the project. Neither wiki
was changed. Original root assets and binary reference documents remain intact.

`manifest.json` was created before bulk edits. Its source SHA-256 values describe
original files, not rewritten destinations. It accounts for repository docs, both
wiki copies, sidebar/footer inputs, README, configuration and original assets.
`MAP.md` is its human-readable source-to-destination view. New pages and intentionally
vendored assets are recorded separately. No filename/case collisions were found.

The sole initial untracked text file was a local operational helper, not public
project documentation. It remains unchanged and is excluded from navigation,
search, site and LLM exports. Dependency trees, virtual environments, caches and
build output were not treated as migration sources. The supplied additional-input
placeholder `<ITEM_6_AND_OTHER_REQUIREMENTS>` is not an actionable requirement;
the explicit requirements in the request govern this migration.

## Structure and ownership

`docs/` is canonical. Existing page filenames and `.html` URL paths are preserved:

- Home: index.
- Getting started: Quick Start, preserved CLI Examples, Project References.
- emf-read: CLI, filters, query deep dive, exports, JSON structures, graphs,
  paths, pruning/dry-run, grouped instances.
- xsd-enrich: CLI and mapping rules.
- Internals: API, architecture, troubleshooting, FAQ.
- Maintainers: documentation development and privacy.

The long README examples live in `docs/CLI-Examples.md`; root README is concise.
Wiki Home informs the index; its sidebar informs explicit navigation; neither
sidebar nor footer is published as an accidental standalone page. The newer wiki
pruning and emf-read details were retained, including reference-drop examples.
Links are ordinary relative Markdown in the site; historical GitHub Wiki sources
retain their extensionless-link convention. Binary `.doc` sources and the example
XSD are linked to their canonical repository copies, not silently converted.
GPL license text stays in LICENSE. There is no contribution/security policy to move.

## Hosting and compatibility decisions

The legacy config, existing Pages workflow and an HTTP 200 response agree on
https://chris-day.github.io/iso20022-ecore/ . This is an existing deployment, not
permission to publish the migration. No CNAME/custom domain was found. Existing
main-push/manual deployment triggers are retained; pull requests only verify.
No remote wiki edits, commits, pushes, publishing or hosting-setting changes occurred.

Zensical 0.0.71 uses root `zensical.toml`. The original config is preserved verbatim
as `mkdocs.legacy.yml`. The unsupported topology `graph` plugin is omitted; navigation
and search replace its discovery role, and model Mermaid diagrams remain. Unused
plugins installed by the legacy workflow are dropped. A reference to nonexistent
extra CSS is removed. Existing URLs need no redirect. This site cannot redirect
GitHub-hosted Wiki URLs. The old wiki remains historical, not a second maintained source.

## Technical corrections and limitations

Documentation was checked against both CLI parsers, installed help, loader,
exporter, query and XSD enrichment implementation. Corrections include:

- JSON structures now show real synthetic output, feature objects versus names,
  `many` rather than unimplemented bounds, subpackages and total counts. Grouped
  instance `total_objects` is a pre-filter count. Examples are not formal JSON Schemas.
- Query operators/functions reflect the restricted AST evaluator; arithmetic and
  arbitrary calls are not supported. Missing attributes and context collisions are described.
- GML is not GraphML. Class inclusion is exact, not automatic subtype inclusion.
  `BusinessAssociation` is not a class in the supplied 2013 Ecore; the conceptual
  example is preserved with a warning. Abstract DataType does not select all subclasses.
- Metamodel/supertype helper calls currently inspect EClass through an instance
  helper. Documented as an existing limitation, not fixed by this migration.
- Containment ancestors can be retained even if not explicitly selected. Dropping
  one opposite reference is not a guarantee it stays absent on reload.
- `--dump-model` has a pre-existing text-summary TypeError risk; Quick Start uses
  `--dump-model-json`. Historical commands are retained with the limitation stated.
- XSD trace annotations currently use an exact MessageElement class test that can
  miss concrete subclass traces. Fallback matching limitations are described.
- Existing resource/default mutation behavior is documented; default literals must
  not be mistaken for recovered original registration status.

Application behavior was not changed. Package/readme version bumped to 0.1.114 for
new verification tooling. The existing GPL-3.0 LICENSE versus MIT package metadata
conflict requires a maintainer decision; no license claim was invented or replaced.
The exact 20250424 instance used by the historical examples/tests is unavailable
locally. A different dated instance exists, but is not silently substituted in
those tests. Full-resource and end-to-end XSD examples therefore remain unverified.

## Privacy and browser resources

Native consent offers accept, reject and manage, with optional GitHub statistics
unchecked. Accept saves the selected categories; it does not enable unchecked ones.
The persistent footer reopens settings. No analytics are configured. External font
loading is disabled; search is local. Mermaid 11.12.0 is vendored from its exact npm
archive with its MIT license, provenance and SHA-256 in the manifest. A dedicated
fence class prevents the theme's dynamic CDN Mermaid loader from activating.
Necessary requests are to the documentation host. Optional repository statistics
may contact api.github.com only after selection. Ordinary external links require
user navigation. Browser evidence records consent storage and all observed requests;
a banner alone is not evidence of legal compliance. GitHub Pages hosting policy
and any future analytics remain maintainer responsibilities.

## Reproduction, CI and rollback

Use the existing application `.venv`; no global installs or alternate environment:

```bash
.venv/bin/python -m pip install -r requirements-docs.txt -r requirements-docs-browser.txt -r requirements-test.txt
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m playwright install chromium
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q
.venv/bin/zensical serve -a 127.0.0.1:8000
# Stop preview before continuing if running in the same terminal.
.venv/bin/zensical build --clean --strict
.venv/bin/python scripts/check_docs.py
.venv/bin/python scripts/check_docs_browser.py
```

The dependency closures, not just Zensical, are pinned for Python 3.14/Linux.
`lock_docs.py` provides the explicit update procedure documented in the site.
The recorded dependencies were reinstalled into the healthy existing environment;
`pip check` passed. CI uses these same files, `.venv`, configuration and scripts.
Chromium's system prerequisites may require `playwright install --with-deps chromium`.
Browser dependencies are isolated in their own pinned file, not another environment.

For rollback restore the documentation/configuration/workflow from baseline commit
in a new reviewed commit, remove the Zensical config and rebuild using the prior
workflow. Do not reset unrelated work. Legacy dependency versions were unpinned,
so byte-identical historical builds cannot be promised. Deploy only via an authorized
merge to main or manual workflow dispatch after review.

## Verification evidence

Evidence lives in `evidence/`, outside `site/` so clean builds cannot erase it.
The static checker covers every public page exactly once in navigation and llmstxt,
generated links/anchors/assets, migration destinations, excluded source integrity,
CLI options, local operational content, Markdown exports and the favicon copy.
The browser checker covers every page and Mermaid fence, search's shadow DOM,
favicon decoding, repository links, generator notice, consent lifecycle, network,
storage, JavaScript errors and desktop/mobile screenshots. External GitHub request
availability is distinguished from consent gating. See the JSON results and
verification transcript for actual outcomes; screenshots are checked visually.

### Recorded results

- Clean strict Zensical build: passed, no issues reported.
- Static check: 21 public pages, 22 HTML files (including 404), 21 Markdown/LLM pages;
  no broken internal links, anchors, assets, navigation or migration destinations.
- Dependency reinstall: passed; `pip check`: no broken requirements.
- Application tests: 9 passed, 2 skipped (historical 20250424 resource missing).
- Real ISO20022.ecore metamodel-only JSON CLI example: passed, 85 classes.
- No JavaScript errors or local failed resources were observed in browser runs.
- Consent lifecycle: no external requests before selection, after reject or revoke;
  explicit GitHub opt-in caused only api.github.com requests. Its latest-release
  endpoint returned HTTP 404; repository metadata succeeded. Cached public repository
  statistics can remain in localStorage after revocation, but no new requests occur.
- Both Mermaid diagrams render from the local pinned bundle. Desktop screenshots
  show readable navigation, JSON/code formatting and diagrams with no generator notice.

Authoritative final browser status and mobile/search evidence are in `evidence/browser-check.json`.

## Upstream configuration references

- https://zensical.org/docs/setup/data-privacy/
- https://zensical.org/docs/compatibility/mkdocs/plugins/#llmstxt
- https://pawamoy.github.io/mkdocs-llmstxt/

Zensical's native implementation is used; the compatibility documentation, not an
assumption that arbitrary MkDocs plugins execute, determined this configuration.

Final browser run: **passed**. Search found the pruning material through the real
shadow-DOM result options. All 21 pages and both Mermaid diagrams loaded, favicon
decoded, repository links were present, and no generator notice appeared. Desktop
and mobile screenshots were visually reviewed; mobile content fits the viewport,
code blocks scroll horizontally and wide diagrams scale down. There were no
JavaScript errors, local HTTP errors or failed requests. The optional GitHub
latest-release 404 is retained in evidence rather than hidden or treated as a local
site failure. Evidence is reproducible with the checked-in scripts.
