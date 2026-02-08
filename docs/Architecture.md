# Architecture

## Key modules

- `emf_reader/loader.py`: loads `.ecore` into `ResourceSet` and registers metamodel.
- `emf_reader/export.py`: builds graphs, exports JSON/CSV/graphs/paths, filtering.
- `emf_reader/query.py`: filter language parsing and helpers.
- `emf_reader/cli.py`: CLI entrypoint for `emf-read`.
- `emf_reader/xsd_enrich.py`: mapping rules and annotation injection for XSD.
- `emf_reader/xsd_enrich_cli.py`: CLI entrypoint for `xsd-enrich`.

## Object identity

- `id` and `ID` prefer XML `xmi:id` if present.
- If missing, `local_id` is a stable internal ID within the run.

## Traversal strategy

- Containment traversal uses `eAllContainments` (via `eAllReferences` with `containment=True`).
- Reference traversal uses `eAllReferences`.
