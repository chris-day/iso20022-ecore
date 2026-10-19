# Troubleshooting

## "ModuleNotFoundError: pyecore"

Activate the venv before running tests or the CLI:

```bash
source .venv/bin/activate
pytest
```

## No output files generated

Check that `--instance` is supplied for instance operations, and confirm output directory permissions.

## Filter expressions failing

Use simple expressions first and ensure you quote strings properly:

```text
name == 'Account'
```

## Known implementation limitations

`--dump-model` currently tries to join feature dictionaries as text and can raise `TypeError`; use `--dump-model-json`. Pruning and metamodel graphs have limitations documented in [Pruning and dry-run](Pruning-and-Dry-Run.md) and [Graph exports](Graph-Exports.md). Python API calls can mutate the input resource during pruning; reload it before another independent export.
