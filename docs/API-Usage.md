# API Usage

`emf_reader` exposes Python APIs for loading metamodels and instances, building object graphs, and exporting JSON/edges.

## Load metamodel and instance

```python
from emf_reader.loader import load_metamodel, load_instance

rset, packages = load_metamodel("/var/software/input/ISO20022.ecore")
resource = load_instance("/var/software/input/20250424_ISO20022_2013_eRepository.iso20022", rset)
roots = list(resource.contents)
```

## Summarize metamodel

```python
from emf_reader.loader import summarize_metamodel, metamodel_stats

print(summarize_metamodel(packages))
print(metamodel_stats(packages))
```

## Build object graph

```python
from emf_reader.export import build_object_graph

objects, edges = build_object_graph(roots)
```

## Export JSON and edges

```python
from emf_reader.export import export_json, export_edges

export_json(roots, "/tmp/iso20022.json")
export_edges(roots, "/tmp/iso20022_edges.csv")
```

## Filtered exports

```python
from emf_reader.export import export_mermaid

export_mermaid(
    roots,
    "/tmp/business_components.mmd",
    filter_expr="is_kind_of('BusinessComponent')"
)
```

## Instance grouping

```python
from emf_reader.export import dump_instances_by_class

payload = dump_instances_by_class(roots, filter_expr="eclass == 'BusinessComponent'")
```

## Prune preview

```python
from emf_reader.export import preview_prune_metamodel

summary = preview_prune_metamodel(
    packages,
    include_classes={"BusinessComponent"},
    exclude_classes={"BusinessProcess"},
)
```
