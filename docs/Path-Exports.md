# Path Exports

## Name paths

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --expand-from "eclass == 'BusinessComponent' and name == 'Account'" \
  --expand-depth 2 \
  --export-paths /tmp/account_paths.txt
```

## ID paths

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --expand-from "eclass == 'BusinessComponent' and name == 'Account'" \
  --expand-depth 2 \
  --export-path-ids /tmp/account_path_ids.txt
```
