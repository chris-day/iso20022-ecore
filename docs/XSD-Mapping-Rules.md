# XSD Mapping Rules

This is a simplified summary of the rules implemented by `xsd-enrich`.

## Target namespace mapping

- Parse `xs:schema/@targetNamespace`.
- If it begins with `urn:iso:std:iso:20022:tech:xsd:` then the suffix
  is interpreted as a MessageDefinitionIdentifier: `businessArea.messageFunctionality.flavour.version`.
- This identifier is used to find the MessageDefinition and scope MessageBuildingBlocks and MessageElements.

## Object lookup rules

- `xs:complexType` → `MessageComponent`, `MessageComponentType`, `ChoiceComponent`, `MessageDefinition` (by name)
- `xs:simpleType` → `DataType` or `CodeSet` (by name; if name ends with `Code`, prefer `CodeSet`)
- `xs:element` → `MessageElement` or `MessageAttribute`
  - Resolve parent complexType → MessageComponent/MessageComponentType/ChoiceComponent
  - Match child by `xmlTag` equals the XSD element name
- `xs:attribute` → `MessageAttribute`

## Annotations added

- `xmi:id`, `definition`, `parent`
- `businessElementName`, `businessComponentName`
- `businessElementId`, `businessComponentId`

## Trace mode

`--trace-name` logs candidate matches for the given name and the selected match.
