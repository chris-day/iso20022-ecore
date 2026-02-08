# Quick Start

## Install

```bash
python -m pip install -e .
```

## Inspect metamodel

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --dump-metamodel
```

## Dump metamodel to JSON

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --dump-metamodel-json /tmp/metamodel.json
```

## Load instance and dump model

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-model
```

## Export graph

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --filter-expr "is_kind_of('BusinessComponent')" \
  --export-mermaid /tmp/business_components.mmd
```

## Enrich XSD with model annotations

```bash
xsd-enrich \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --xsd auth.016.001.03.xsd \
  --output /tmp/auth.016.001.03.enriched.xsd
```
