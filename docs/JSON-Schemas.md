# JSON Schemas

This page describes the JSON output formats produced by `emf-read`.

## Metamodel JSON (`--dump-metamodel-json`)

Top-level object:

```json
{
  "packages": [
    {
      "name": "ISO20022",
      "nsURI": "...",
      "classes": [
        {
          "name": "BusinessComponent",
          "attributes": ["name", "definition", "registrationStatus"],
          "references": ["associationDomain", "derivation", "subType", "superType"]
        }
      ]
    }
  ]
}
```

Notes:

- Packages include class names and their attribute/reference names.
- `attributes` and `references` are metadata (not instance values).

## Model JSON (`--dump-model-json`)

Top-level object:

```json
{
  "classes": [
    {
      "name": "BusinessComponent",
      "count": 123,
      "attributes": ["name", "definition"],
      "references": ["associationDomain", "derivation"]
    }
  ]
}
```

Notes:

- This summarizes instance counts per class, plus attribute/reference names.

## Instance JSON (`--export-json`)

Top-level is a list of objects:

```json
[
  {
    "id": "_E1rHgsTGEeChad0JzLk7QA_-1068889728",
    "ID": "_E1rHgsTGEeChad0JzLk7QA_-1068889728",
    "local_id": "o42",
    "eClass": "BusinessComponent",
    "nsURI": "...",
    "attributes": {
      "name": "Account",
      "definition": "...",
      "registrationStatus": "Registered"
    },
    "containment": ["o43", "o44"],
    "references": {
      "subType": ["o120"],
      "superType": ["o7"]
    },
    "path": "/Repository[0]/businessComponent[12]"
  }
]
```

Notes:

- `id`/`ID` prefer XML `xmi:id` if present, else `local_id`.
- `containment` is a list of child IDs.
- `references` maps reference names to target IDs.

## Edges CSV (`--export-edges`)

Columns:

- `src_id`
- `src_class`
- `feature`
- `dst_id`
- `dst_class`
- `containment` (true/false)

## Instances by class (`--dump-instances-json`)

Top-level object:

```json
{
  "BusinessComponent": [
    {"id": "...", "name": "Account"}
  ],
  "MessageComponent": [
    {"id": "...", "name": "AmountAndDirection61"}
  ]
}
```

Notes:

- Values are lightweight dictionaries used for inspection and filtering.
