# Exports & Formats

## JSON export

`--export-json <path>` writes a list of objects with:

- `id`, `ID`, `local_id`
- `eClass`, `nsURI`
- `attributes` (scalar values)
- `containment` (list of child IDs)
- `references` (dict name -> list of IDs)
- `path` (containment path)

## Edges (CSV)

`--export-edges <path>` writes:

- `src_id`, `src_class`, `feature`, `dst_id`, `dst_class`, `containment`

## Dump instances grouped by class

`--dump-instances-json <path>` groups instances by class name.
