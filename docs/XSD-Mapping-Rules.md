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

## Fallbacks and limitations

Names ending in `_SimpleType` are normalized by removing that suffix. For an
`xs:element`, the implementation searches the parent component's children by
`xmlTag`, then falls back to the element name globally, and finally its type name.
The `--map` file changes candidate preferences, not the allowed model-class list.
Concrete subclasses of `DataType` and `CodeSet` are discovered through supertypes.

The trace annotation block currently checks the exact EClass name `MessageElement`.
It does not automatically cover concrete `MessageAttribute` and
`MessageAssociationEnd` instances. Treat missing business trace annotations on these
classes as an implementation limitation, not evidence that no trace exists in the
source. Enrichment reports are mapping summaries, not XML Schema validity proofs.
