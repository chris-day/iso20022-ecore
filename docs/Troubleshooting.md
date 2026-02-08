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
