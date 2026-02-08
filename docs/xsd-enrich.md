# xsd-enrich CLI

`xsd-enrich` annotates ISO 20022 XSDs using EMF model data. It adds `xs:annotation/xs:appinfo` entries for model IDs, definitions, and trace links.

## Usage

```bash
xsd-enrich --ecore <path> --instance <path> --xsd <path> --output <path> [--map <path>] [--trace-name <name>] [--verbose]
```

## Example

```bash
xsd-enrich \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --xsd auth.016.001.03.xsd \
  --output /tmp/auth.016.001.03.enriched.xsd
```

## What gets annotated

- `xmi:id`
- `definition`
- `parent` (xmi:id if present, otherwise name)
- `businessElementName` / `businessComponentName`
- `businessElementId` / `businessComponentId`

## Trace mode

Use `--trace-name` to log candidate matches for a particular XSD name.

```bash
xsd-enrich \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --xsd auth.016.001.03.xsd \
  --output /tmp/auth.016.001.03.enriched.xsd \
  --trace-name UnderlyingIdentification2Choice
```

## Mapping rules

See [XSD Mapping Rules](XSD-Mapping-Rules).
