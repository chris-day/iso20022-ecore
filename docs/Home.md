# ISO 20022 EMF Tools

Welcome to the ISO 20022 EMF tools wiki. This repository provides:

- `emf-read`: a CLI and Python library for loading ISO 20022 EMF `.ecore` metamodels and instance resources, exporting JSON/CSV/graph/paths, and filtering/expanding the object graph.
- `xsd-enrich`: a CLI tool that enriches ISO 20022 XSDs with EMF `xmi:id`, model definitions, and related annotations.

If you're new, start with:

- [Quick Start](Quick-Start)
- [emf-read](emf-read)
- [xsd-enrich](xsd-enrich)

## What this repo is for

- Inspect and summarize ISO 20022 EMF metamodels and instance resources.
- Export object graphs to JSON/CSV/graph formats.
- Filter and expand graphs with a small expression language.
- Produce XSDs annotated with model IDs, definitions, and trace links.

## Core artifacts

- `ISO20022.ecore` (metamodel)
- instance files, such as `20250424_ISO20022_2013_eRepository.iso20022`
- ISO 20022 XSDs (e.g., `auth.016.001.03.xsd`)

## Index

- [Quick Start](Quick-Start)
- [emf-read CLI](emf-read)
- [xsd-enrich CLI](xsd-enrich)
- [Filter Language](Filter-Language)
- [Query Language Deep Dive](Query-Language-Deep-Dive)
- [JSON Schemas](JSON-Schemas)
- [API Usage](API-Usage)
- [Exports & Formats](Exports-and-Formats)
- [Graph Exports](Graph-Exports)
- [Path Exports](Path-Exports)
- [Pruning & Dry-Run](Pruning-and-Dry-Run)
- [Conceptual Pruning Example](Pruning-and-Dry-Run#example-conceptual-pruning)
- [Instance Grouping](Instance-Grouping)
- [Architecture](Architecture)
- [Troubleshooting](Troubleshooting)
- [FAQ](FAQ)
