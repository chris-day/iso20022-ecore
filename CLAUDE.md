# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`emf_reader` is a Python library and CLI for loading Eclipse EMF `.ecore` metamodels and instance files (XMI/XML) using **pyecore**. It targets the ISO 20022 financial messaging standard's Ecore repository but works with any EMF model. It provides two CLI tools: `emf-read` (metamodel/instance exploration and export) and `xsd-enrich` (annotating XSD files with xmi:id metadata from the eRepository).

## Common Commands

```bash
# Install (editable mode)
python -m pip install -e .

# Run tests
pytest

# Run a single test
pytest tests/test_cli.py::test_name

# Build docs (MkDocs Material)
mkdocs serve
mkdocs build
```

## Architecture

The package is `emf_reader/` with six modules forming a clear pipeline:

- **loader.py** — Loads `.ecore` metamodels into a pyecore `ResourceSet`, registers packages, and loads XMI instance files. All metamodel introspection helpers (`metamodel_stats`, `summarize_metamodel`, `summarize_instances`) live here.
- **export.py** — Builds in-memory object graphs from loaded instances and exports to JSON, CSV edges, Mermaid, PlantUML, GML, and path formats. Handles filtering, neighborhood expansion, and graph traversal.
- **query.py** — Implements the filter expression language used by `--filter-expr`. Parses expressions like `is_kind_of('BusinessComponent') and name == 'Account'` using Python's `ast` module with a safe evaluator.
- **cli.py** — CLI entrypoint for `emf-read` (registered as console script).
- **xsd_enrich.py** — Core logic for mapping XSD elements/types to eRepository objects and injecting `xs:annotation/xs:appinfo` entries. Uses `lxml` for XML manipulation.
- **xsd_enrich_cli.py** — CLI entrypoint for `xsd-enrich` (registered as console script).

### Key Concepts

- **Object identity**: `id`/`ID` prefer XML `xmi:id` when present; `local_id` is a stable fallback within a single run.
- **Traversal**: Containment traversal uses `eAllContainments`; reference traversal uses `eAllReferences`.
- **Filter language**: Supports `is_class()`, `is_kind_of()`, attribute comparisons, `and`/`or`/`not`, and `in` for set membership. Variables available: `eclass`, `nsuri`, `id`, `ID`, `local_id`, `path`, `attrs`, plus direct attribute names.

## Dependencies

- Python ≥ 3.11
- `pyecore` ≥ 0.13 (EMF metamodel/instance handling)
- `lxml` ≥ 4.9 (XML/XSD processing)

## Test Data

Tests in `tests/` use inline fixtures or small `.ecore` files. The full ISO 20022 eRepository files are external (typically at `/var/software/input/`), not committed to the repo.
