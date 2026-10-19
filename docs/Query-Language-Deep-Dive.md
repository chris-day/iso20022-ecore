# Query Language Deep Dive

This section describes the expression language used by:

- `--filter-expr`
- `--expand-from`
- `--dump-instances-filter`
- `--neighbors-from`

## Execution model

Expressions are evaluated against a per-object context. The same syntax is used for filtering and for choosing seed nodes.

## Available context fields

- `eclass`: EClass name (string)
- `name`: object name if present (string)
- `id`: preferred ID (XML `xmi:id` if present, else internal)
- `ID`: alias for `id`
- `local_id`: stable internal ID for the run
- `nsuri`: namespace URI of the EPackage
- `path`: containment path
- `attrs`: dictionary of attribute values; for example `attrs["name"]`

## Helper functions

- `is_class('ClassName')`
- `is_kind_of('SuperType')`

## Operators

- `==`, `!=`, `<`, `<=`, `>`, `>=`
- `and`, `or`, `not`
- `in`, `not in` (lists, tuples, sets, and dictionary keys)

## Examples

Exact class match:

```text
eclass == 'BusinessComponent'
```

Class + name:

```text
eclass == 'BusinessComponent' and name == 'Account'
```

Check for supertype:

```text
is_kind_of('BusinessComponent')
```

Multi-class filter:

```text
is_kind_of('BusinessComponent') or is_class('BusinessAssociationEnd')
```

ID filter:

```text
id == '_E1rHgsTGEeChad0JzLk7QA_-1068889728'
```

Neighbors seed:

```text
name == 'Account'
```

## Tips

- Strings may use either Python quote style; shell quoting must preserve the expression.
- Keep expressions simple when troubleshooting.
- For ID filters, prefer `id` so XML `xmi:id` is used when present.

## Limits

Only `is_class` and `is_kind_of` calls are accepted. Attribute access, arbitrary Python calls and arithmetic are rejected. Missing feature names can raise an evaluation error; `name` is supplied as `None` when absent. Guard nullable values before ordered comparisons. Enum values in the query context use their model names, such as `REGISTERED`, rather than their XML literals. Direct attribute names can override context fields of the same name.
