# emf_reader

Version: 0.1.78

Python library and CLI for loading Eclipse EMF `.ecore` metamodels and instance files (XMI/XML) using **pyecore**.

## Installation

```bash
python -m pip install -e .
```

## CLI

### Usage

```bash
emf-read --ecore <path> [--instance <path>] [--dump-metamodel] [--dump-metamodel-json <path>] \
  [--dump-instances] [--dump-instances-json <path>] [--dump-instances-filter <expr>] \
  [--dump-model] [--dump-model-json <path>] [--export-json <path>] \
  [--export-edges <path>] [--export-paths <path>] [--export-path-ids <path>] \
  [--export-mermaid <path>] [--export-plantuml <path>] [--export-gml <path>] \
  [--export-instance <path>] [--include-classes <list>] [--exclude-classes <list>] \
  [--neighbors-from <expr>] [--neighbors <n>] \
  [--filter-expr <expr>] [--expand-from <expr>] [--expand-depth <n>] \
  [--expand-classes <list>] [--verbose]

xsd-enrich --ecore <path> --instance <path> --xsd <path> --output <path> [--map <path>] [--trace-name <name>] [--verbose]
```

### Examples

Dump metamodel summary (no instance required):

```bash
emf-read --ecore /var/software/input/ISO20022.ecore --dump-metamodel
```

Dump metamodel to JSON:

```bash
emf-read --ecore /var/software/input/ISO20022.ecore --dump-metamodel-json /tmp/metamodel.json
```

Metamodel JSON includes package hierarchy (`subpackages`) and class references with target type, cardinality, and containment.

Load instance, dump summary, and export JSON/edges:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-instances \
  --export-json /tmp/iso20022.json \
  --export-edges /tmp/iso20022_edges.csv
```

Verbose logging:

```bash
emf-read --ecore /var/software/input/ISO20022.ecore --dump-metamodel --verbose
```

Filter exports with a tiny expression language:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent') and registrationStatus == 'REGISTERED'" \
  --export-json /tmp/business_components.json \
  --export-edges /tmp/business_components_edges.csv
```

Filter using helper functions (include all BusinessComponent subclasses plus BusinessAssociationEnd):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent') or is_class('BusinessAssociationEnd')" \
  --export-mermaid /tmp/business_components_with_assoc.mmd
```

Neighborhood expansion from a seed (6 hops, containment + references):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --neighbors-from "name == 'Account'" \
  --neighbors 6 \
  --export-mermaid /tmp/account_neighborhood.mmd
```

Neighborhood expansion with class filtering:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --neighbors-from "name == 'Account'" \
  --neighbors 6 \
  --filter-expr "is_kind_of('BusinessComponent') or is_class('BusinessAssociationEnd')" \
  --export-mermaid /tmp/account_neighborhood_filtered.mmd
```

Export a filtered instance resource (XMI):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --export-instance /tmp/filtered.iso20022 \
  --include-classes BusinessComponent,BusinessAssociationEnd \
  --exclude-classes BusinessProcess
```

Enrich an XSD with xmi:id annotations:

```bash
xsd-enrich \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --xsd auth.016.001.03.xsd \
  --output /tmp/auth.016.001.03.enriched.xsd
```

Use `--verbose` to log per-element annotation status (annotated/missing).

Trace a specific XSD name during mapping:

```bash
xsd-enrich \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --xsd auth.016.001.03.xsd \
  --output /tmp/auth.016.001.03.enriched.xsd \
  --trace-name UnderlyingIdentification2Choice
```

The enrichment adds `xs:annotation/xs:appinfo` entries for `xmi:id`, `definition`, and, when a parent exists, `parent` (the parent object's XMI id, or its name if the id is missing). It also annotates `xs:schema` with the `messageDefinitionIdentifier` and its parts when the targetNamespace matches.

Optional mapping file (`--map`) can specify preferred EClass matches by XSD kind:

```json
{
  "complexType": ["MessageDefinition", "MessageComponent", "MessageComponentType", "ChoiceComponent"],
  "simpleType": ["DataType"],
  "element": ["MessageElement", "MessageBuildingBlock", "MessageAssociationEnd"],
  "attribute": ["MessageAttribute"]
}
```

Expand the graph from a matching start node (depth 2):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --expand-from "eclass == 'BusinessComponent' and name == 'Account'" \
  --expand-depth 2 \
  --export-json /tmp/account_graph.json \
  --export-edges /tmp/account_graph_edges.csv
```

Write expansion paths (XPath-like, name-only) to a text file:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --expand-from "eclass == 'BusinessComponent' and name == 'Account'" \
  --expand-depth 2 \
  --export-paths /tmp/account_paths.txt
```

Write expansion path IDs (id-only paths that mirror expansion):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --expand-from "eclass == 'BusinessComponent' and name == 'Account'" \
  --expand-depth 2 \
  --export-path-ids /tmp/account_path_ids.txt
```

Restrict expansion to specific classes:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --expand-from "eclass == 'BusinessComponent' and name == 'Account'" \
  --expand-depth 4 \
  --expand-classes BusinessAssociationEnd,BusinessAttribute,BusinessComponent \
  --export-paths /tmp/account_paths_limited.txt
```

Dump model summary (object counts by class):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-model
```

Dump model summary to JSON:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-model-json /tmp/model.json
```

Dump instances grouped by class to JSON:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-instances-json /tmp/instances_by_class.json
```

Dump filtered instances grouped by class to JSON:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-instances-json /tmp/account_instances.json \
  --dump-instances-filter "eclass == 'BusinessComponent' and name == 'Account'"
```

Export a Mermaid diagram for BusinessComponent instances (labelled by name):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent')" \
  --export-mermaid /tmp/business_components.mmd
```

Export a PlantUML class diagram for BusinessComponent instances (labelled by name):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent')" \
  --export-plantuml /tmp/business_components.puml
```

Export a GML graph for BusinessComponent instances (labelled by name):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent')" \
  --export-gml /tmp/business_components.gml
```

Model JSON includes per-class attribute/reference definitions with target type, cardinality, and containment.

Combine filter and expansion (expand first, then filter results):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --expand-from "eclass == 'BusinessComponent' and name == 'Account'" \
  --expand-depth 3 \
  --filter-expr "eclass == 'BusinessRole'" \
  --export-json /tmp/account_roles.json
```

Unbounded expansion (use with care on large models):

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --expand-from "eclass == 'BusinessComponent' and name == 'Account'" \
  --expand-depth -1 \
  --export-edges /tmp/account_all_edges.csv
```

Filter expression variables:

- `eclass`, `nsuri`, `id`, `ID`, `local_id`, `path`
- `attrs` (dict of attribute values)
- attribute names as direct variables (e.g., `name`, `registrationStatus`)
- helpers: `is_class('Foo')`, `is_kind_of('BusinessComponent')`

### Filter language
Patterns you can use in `--filter-expr`:

- Exact class match: `is_class('BusinessAssociationEnd')`
- Subclass match: `is_kind_of('BusinessComponent')`
- Attribute equality: `registrationStatus == 'REGISTERED'`
- Combined conditions: `is_kind_of('BusinessComponent') and name == 'Account'`
- Set membership: `eclass in ('BusinessComponent', 'BusinessAssociationEnd')`

## Output formats

### JSON export
A list of objects with:

- `id`: XMI id if present, otherwise stable id per run (based on traversal order)
- `local_id`: stable id per run (always present)
- `ID`: XMI id if present, otherwise `local_id`
- `eClass`: class name
- `nsURI`: package nsURI
- `attributes`: scalar or list attribute values
- `containment`: list of child ids (containment references)
- `references`: dict of non-containment reference name -> list of target ids
- `path`: containment path (e.g., `/Repository[0]/messages[12]`)

### Edge CSV export
Columns:

- `src_id`, `src_class`
- `feature`
- `dst_id`, `dst_class`
- `containment` (true/false)

## Library usage

```python
from emf_reader.loader import load_metamodel, load_instance
from emf_reader.export import export_json

rset, packages = load_metamodel("/var/software/input/ISO20022.ecore")
resource = load_instance("/var/software/input/20250424_ISO20022_2013_eRepository.iso20022", rset)
export_json(resource.contents, "/tmp/iso20022.json")
```
