# emf_reader

Version: 0.1.117

Python 3.11+ library and CLI tools for Eclipse EMF `.ecore` metamodels and XMI/XML
instances, using pyecore and lxml.

- `emf-read`: inspect, query, export graphs and prune instance resources.
- `xsd-enrich`: annotate ISO 20022 XSDs with model identities, definitions and trace links.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
emf-read --help
xsd-enrich --help
```

## Documentation

[Documentation site](https://chris-day.github.io/iso20022-ecore/) ·
[Quick start](docs/Quick-Start.md) · [CLI examples](docs/CLI-Examples.md) ·
[Python API](docs/API-Usage.md) · [Pruning](docs/Pruning-and-Dry-Run.md)

The repository's `docs/` is the canonical documentation source. The separate wiki
is retained as historical material; migrate any future wiki changes through review.
The site migration is not published until the normal Pages workflow runs.

## Develop and verify

For the full pinned development environment:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install --no-deps --no-build-isolation -e ".[dev]"
```

```bash
.venv/bin/python -m pip install -r requirements-docs.txt
.venv/bin/zensical serve
.venv/bin/zensical build --clean --strict
.venv/bin/python scripts/check_docs.py
```

See [documentation development](docs/Documentation-Development.md) for browser
verification, tests, dependency updates and deployment. External ISO 20022 input
files used in examples must be supplied locally.

## License

See [LICENSE](LICENSE). The root license text is GPL-3.0; package metadata currently
says MIT. This existing conflict needs a maintainer decision before redistribution.
