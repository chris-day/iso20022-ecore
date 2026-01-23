from __future__ import annotations

import argparse
import logging
import sys

from .export import export_edges, export_json
from .loader import (
    count_metamodel_classes,
    instance_stats,
    load_instance,
    load_metamodel,
    metamodel_stats,
    summarize_instances,
    summarize_metamodel,
)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read EMF .ecore metamodels and instance files.")
    parser.add_argument("--ecore", required=True, help="Path to .ecore file")
    parser.add_argument("--instance", help="Path to instance file (.xmi/.xml/.iso20022)")
    parser.add_argument("--dump-metamodel", action="store_true", help="Print metamodel summary")
    parser.add_argument("--dump-instances", action="store_true", help="Print instance summary")
    parser.add_argument("--export-json", help="Export loaded objects to JSON")
    parser.add_argument("--export-edges", help="Export edges to CSV")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    try:
        rset, packages = load_metamodel(args.ecore)
    except Exception as exc:  # noqa: BLE001
        logging.error("Failed to load metamodel: %s", exc)
        return 2
    stats = metamodel_stats(packages)
    logging.info(
        "Metamodel stats: packages=%s classes=%s attributes=%s references=%s",
        stats["packages"],
        stats["classes"],
        stats["attributes"],
        stats["references"],
    )

    if args.dump_metamodel:
        summary = summarize_metamodel(packages)
        logging.info("Metamodel classes: %s", count_metamodel_classes(packages))
        print(summary)

    if args.dump_instances or args.export_json or args.export_edges:
        if not args.instance:
            logging.error("Instance file required for instance operations")
            return 2
        try:
            instance_resource = load_instance(args.instance, rset)
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to load instance: %s", exc)
            return 2
        instats = instance_stats([instance_resource])
        logging.info("Instance stats: roots=%s", instats["roots"])

        if args.dump_instances:
            print(summarize_instances([instance_resource]))

        roots = list(instance_resource.contents)
        if args.export_json:
            export_json(roots, args.export_json)
            logging.info("Wrote JSON: %s", args.export_json)
        if args.export_edges:
            export_edges(roots, args.export_edges)
            logging.info("Wrote edges: %s", args.export_edges)

    return 0


if __name__ == "__main__":
    sys.exit(main())
