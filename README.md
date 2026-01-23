# emf_reader

Version: 0.1.4

Python library and CLI for loading Eclipse EMF `.ecore` metamodels and instance files (XMI/XML) using **pyecore**.

## Installation

```bash
python -m pip install -e .
```

## CLI

### Usage

```bash
emf-read --ecore <path> [--instance <path>] [--dump-metamodel] [--dump-instances] \
  [--export-json <path>] [--export-edges <path>] [--verbose]
```

### Examples

Dump metamodel summary (no instance required):

```bash
emf-read --ecore /var/software/input/ISO20022.ecore --dump-metamodel
```

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

## Output formats

### JSON export
A list of objects with:

- `id`: stable id per run (based on traversal order)
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
