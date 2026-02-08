# ISO 20022 EMF Tools

Welcome to the ISO 20022 EMF tools wiki. This repository provides:

- `emf-read`: a CLI and Python library for loading ISO 20022 EMF `.ecore` metamodels and instance resources, exporting JSON/CSV/graph/paths, and filtering/expanding the object graph.
- `xsd-enrich`: a CLI tool that enriches ISO 20022 XSDs with EMF `xmi:id`, model definitions, and related annotations.

If you're new, start with:

- [Quick Start](Quick-Start.md)
- [emf-read](emf-read.md)
- [xsd-enrich](xsd-enrich.md)

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

- [Quick Start](Quick-Start.md)
- [emf-read CLI](emf-read.md)
- [xsd-enrich CLI](xsd-enrich.md)
- [Filter Language](Filter-Language.md)
- [Query Language Deep Dive](Query-Language-Deep-Dive.md)
- [JSON Schemas](JSON-Schemas.md)
- [API Usage](API-Usage.md)
- [Exports & Formats](Exports-and-Formats.md)
- [Graph Exports](Graph-Exports.md)
- [Path Exports](Path-Exports.md)
- [Pruning & Dry-Run](Pruning-and-Dry-Run.md)
- [Conceptual Pruning Example](Pruning-and-Dry-Run.md#example-conceptual-pruning)
- [Instance Grouping](Instance-Grouping.md)
- [Architecture](Architecture.md)
- [Troubleshooting](Troubleshooting.md)
- [FAQ](FAQ.md)
