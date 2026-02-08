# emf-read CLI

`emf-read` loads an `.ecore` metamodel and optionally an instance resource, then exports summaries and graphs.

## Usage

```bash
emf-read --ecore <path> [--instance <path>] [--dump-metamodel] [--dump-metamodel-json <path>] \
  [--export-metamodel-mermaid <path>] [--export-metamodel-plantuml <path>] [--export-metamodel-gml <path>] \
  [--metamodel-include-references] \
  [--dump-instances] [--dump-instances-json <path>] [--dump-instances-filter <expr>] \
  [--dump-model] [--dump-model-json <path>] [--export-json <path>] \
  [--export-edges <path>] [--export-paths <path>] [--export-path-ids <path>] \
  [--export-mermaid <path>] [--export-plantuml <path>] [--export-gml <path>] \
  [--export-instance <path>] [--include-classes <list>] [--exclude-classes <list>] [--prune-include-supertypes] [--prune-strip-refs] [--prune-serialize-defaults] [--prune-no-containers] \
  [--prune-dry-run] [--prune-dry-run-json <path>] [--neighbors-from <expr>] [--neighbors <n>] \
  [--filter-expr <expr>] [--expand-from <expr>] [--expand-depth <n>] \
  [--expand-classes <list>] [--verbose]
```

## Common use-cases

- **Inspect metamodel classes and features**
- **Summarize instance objects**
- **Export JSON and edges for analysis**
- **Generate Mermaid/PlantUML/GML diagrams**
- **Filter and expand subgraphs**
- **Prune instances by class**

## Examples

Dump metamodel summary:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --dump-metamodel
```

Export metamodel graph (inheritance + containment references):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --export-metamodel-mermaid /tmp/iso20022_metamodel.mmd
```

Dump model JSON:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-model-json /tmp/model.json
```

Export edges for BusinessComponent neighborhood:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --neighbors-from "name == 'Account'" \
  --neighbors 4 \
  --filter-expr "is_kind_of('BusinessComponent') or is_class('BusinessAssociationEnd')" \
  --export-edges /tmp/account_edges.csv
```

Export instance XMI filtered by classes:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --export-instance /tmp/filtered.iso20022 \
  --include-classes BusinessComponent,BusinessAssociationEnd \
  --exclude-classes BusinessProcess \
  --prune-strip-refs \
  --prune-serialize-defaults
```

## Related

- [Filter Language](Filter-Language)
- [Exports & Formats](Exports-and-Formats)
- [Pruning & Dry-Run](Pruning-and-Dry-Run)
- [Conceptual Pruning Example](Pruning-and-Dry-Run#example-conceptual-pruning)
