from __future__ import annotations

import argparse
import logging
import sys

from .export import export_edges, export_json, export_paths
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
    parser.add_argument("--export-paths", help="Export expansion paths to text")
    parser.add_argument("--filter-expr", help="Filter expression for exported objects")
    parser.add_argument(
        "--expand-from",
        help="Expansion start expression (adds reachable objects via references)",
    )
    parser.add_argument(
        "--expand-depth",
        type=int,
        help="Expansion depth (0=start only, -1=unbounded). Default: 1",
        default=1,
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)
    logging.info("Args: %s", vars(args))

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
        expand_depth = args.expand_depth if args.expand_from else None
        if args.export_json:
            try:
                entries, metrics = export_json(
                    roots,
                    args.export_json,
                    filter_expr=args.filter_expr,
                    expand_expr=args.expand_from,
                    expand_depth=expand_depth,
                )
            except ValueError as exc:
                logging.error("Invalid filter expression: %s", exc)
                return 2
            logging.info("Wrote JSON: %s (objects=%s)", args.export_json, len(entries))
            if metrics:
                logging.info(
                    "Expansion metrics: start_nodes=%s nodes_seen=%s edges_traversed=%s loops_detected=%s max_depth=%s",
                    metrics["start_nodes"],
                    metrics["nodes_seen"],
                    metrics["edges_traversed"],
                    metrics["loops_detected"],
                    metrics["max_depth"],
                )
        if args.export_edges:
            try:
                edges, metrics = export_edges(
                    roots,
                    args.export_edges,
                    filter_expr=args.filter_expr,
                    expand_expr=args.expand_from,
                    expand_depth=expand_depth,
                )
            except ValueError as exc:
                logging.error("Invalid filter expression: %s", exc)
                return 2
            logging.info("Wrote edges: %s (edges=%s)", args.export_edges, len(edges))
            if metrics:
                logging.info(
                    "Expansion metrics: start_nodes=%s nodes_seen=%s edges_traversed=%s loops_detected=%s max_depth=%s",
                    metrics["start_nodes"],
                    metrics["nodes_seen"],
                    metrics["edges_traversed"],
                    metrics["loops_detected"],
                    metrics["max_depth"],
                )
        if args.export_paths:
            if not args.expand_from:
                logging.error("export-paths requires --expand-from")
                return 2
            try:
                paths, metrics = export_paths(
                    roots,
                    args.export_paths,
                    filter_expr=args.filter_expr,
                    expand_expr=args.expand_from,
                    expand_depth=expand_depth,
                )
            except ValueError as exc:
                logging.error("Invalid filter expression: %s", exc)
                return 2
            logging.info("Wrote paths: %s (paths=%s)", args.export_paths, len(paths))
            if metrics:
                logging.info(
                    "Expansion metrics: start_nodes=%s nodes_seen=%s edges_traversed=%s loops_detected=%s max_depth=%s",
                    metrics["start_nodes"],
                    metrics["nodes_seen"],
                    metrics["edges_traversed"],
                    metrics["loops_detected"],
                    metrics["max_depth"],
                )

    return 0


if __name__ == "__main__":
    sys.exit(main())
