# Graph Exports

## Metamodel graph

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --export-metamodel-mermaid /tmp/iso20022_metamodel.mmd
```

Add non-containment references:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --export-metamodel-mermaid /tmp/iso20022_metamodel.mmd \
  --metamodel-include-references
```

## Mermaid

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent')" \
  --export-mermaid /tmp/business_components.mmd
```

## PlantUML

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent')" \
  --export-plantuml /tmp/business_components.pml
```

## GML

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent')" \
  --export-gml /tmp/business_components.gml
```
