# Instance Grouping

Use `--dump-instances-json` to export instances grouped by class.

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-instances-json /tmp/instances_by_class.json
```

Optionally filter:

```bash
emf-read \
  --ecore /var/software/input/ISO20022.ecore \
  --instance /var/software/input/20250424_ISO20022_2013_eRepository.iso20022 \
  --dump-instances-json /tmp/instances_by_class.json \
  --dump-instances-filter "eclass == 'BusinessComponent'"
```
