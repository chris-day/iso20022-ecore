# FAQ

## Do I need the instance file for metamodel operations?

No. `--dump-metamodel` and `--dump-metamodel-json` only require `.ecore`.

## Does dry-run require the instance file?

No. Dry-run is metamodel-based when no instance is supplied.

## How do IDs work?

If an object has `xmi:id`, it is used as `id`/`ID`. Otherwise a stable internal id is used.
