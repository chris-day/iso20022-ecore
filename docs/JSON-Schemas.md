# JSON Schemas

These are output structure examples, not formal JSON Schema validation documents.
They are generated from a small illustrative model (`urn:example`), not the full ISO 20022 metamodel.

## Metamodel JSON (`--dump-metamodel-json`)

```json
{
  "packages": [
    {
      "name": "example",
      "nsURI": "urn:example",
      "classes": [
        {
          "name": "BusinessComponent",
          "attributes": [
            {
              "name": "name",
              "type": "EString",
              "many": false
            }
          ],
          "references": []
        }
      ],
      "subpackages": []
    }
  ],
  "total_classes": 1
}
```

## Model JSON (`--dump-model-json`)

```json
{
  "total_objects": 1,
  "classes": [
    {
      "name": "BusinessComponent",
      "count": 1,
      "attributes": [
        "name"
      ],
      "references": []
    }
  ]
}
```

## Instance JSON (`--export-json`)

```json
[
  {
    "id": "account-id",
    "local_id": "o1",
    "ID": "account-id",
    "eClass": "BusinessComponent",
    "nsURI": "urn:example",
    "attributes": {
      "name": "Account"
    },
    "containment": [],
    "references": {},
    "path": "/BusinessComponent[0]"
  }
]
```

## Instances by class (`--dump-instances-json`)

```json
{
  "total_objects": 1,
  "classes": {
    "BusinessComponent": [
      {
        "id": "account-id",
        "local_id": "o1",
        "ID": "account-id",
        "eClass": "BusinessComponent",
        "nsURI": "urn:example",
        "path": "/BusinessComponent[0]",
        "attributes": {
          "name": "Account"
        },
        "containment": [],
        "references": {}
      }
    ]
  }
}
```

## Field semantics

Metamodel attributes are metadata objects with `name`, `type`, and `many`;
references also have `containment`. Packages include `subpackages`; the top level
includes `total_classes`. Exact cardinality bounds are not exported.

Model JSON summarizes counts and feature **names**, with `total_objects` at the root.
Grouped instance output wraps class lists under `classes` and includes `total_objects`
for the traversed graph before filtering. Each entry has the same full shape as
an object export; `name` is under `attributes`, not at the entry root.

`id` and `ID` prefer the loaded `_internal_id`; `local_id` is traversal-local.
Containment and reference arrays use the same preferred ID scheme. Scalar attributes
can be null; multi-valued attributes are lists. Enum conversion currently uses the
enum name when available (for example `REGISTERED`), not necessarily its XML literal.
References to objects outside a filtered JSON export are omitted. Grouped exports
build their ID map before filtering, so references may identify entries not included
in the selected groups. Paths are containment feature paths, not the name-only
expansion paths described in [Path exports](Path-Exports.md).

## Edges CSV (`--export-edges`)

The header is `src_id,src_class,feature,dst_id,dst_class,containment`.
Python's CSV writer emits booleans as `True` and `False`. Treat IDs as strings.
