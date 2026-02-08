# Filter Language

Filters are used in `--filter-expr`, `--expand-from`, `--dump-instances-filter`, and neighbor seeds.

## Supported context fields

- `eclass` (string)
- `name` (string)
- `id` (preferred ID: XML `xmi:id` if present, else internal)
- `ID` (same as `id`)
- `local_id` (stable internal id)
- `nsuri`

## Helper functions

- `is_class('ClassName')`
- `is_kind_of('SuperType')`

## Examples

```text
name == 'Account'

eclass == 'BusinessComponent' and name == 'Account'

is_kind_of('BusinessComponent') or is_class('BusinessAssociationEnd')

id == '_E1rHgsTGEeChad0JzLk7QA_-1068889728'
```
