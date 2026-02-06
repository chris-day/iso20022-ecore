from __future__ import annotations

import argparse
import json
import logging
import sys

from .export import (
    dump_instances_by_class,
    export_edges,
    export_filtered_instance,
    export_gml,
    export_json,
    export_metamodel_gml,
    export_metamodel_mermaid,
    export_metamodel_plantuml,
    export_mermaid,
    export_path_ids,
    export_paths,
    export_plantuml,
    preview_prune_metamodel,
    model_dump,
    summarize_model,
)
from .loader import (
    count_metamodel_classes,
    instance_stats,
    load_instance,
    load_metamodel,
    metamodel_dump,
    metamodel_stats,
    summarize_instances,
    summarize_metamodel,
)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _log_prune_summary(stats: dict[str, object]) -> None:
    logging.info(
        "Prune dry-run: scope=%s total=%s selected=%s pruned=%s roots=%s",
        stats.get("scope", "instance"),
        stats.get("total_objects", stats.get("total_classes")),
        stats.get("selected_objects", len(stats.get("selected_classes", {}))),
        stats.get("pruned_objects", len(stats.get("pruned_classes", {}))),
        stats.get("roots", "n/a"),
    )
    logging.info(
        "Pruned containment edges=%s references=%s",
        stats.get("pruned_containment_edges"),
        stats.get("pruned_reference_edges"),
    )
    pruned_classes = stats.get("pruned_classes", {})
    if isinstance(pruned_classes, dict) and pruned_classes:
        logging.info("Pruned classes:")
        for name in sorted(pruned_classes):
            logging.info("  %s: %s", name, pruned_classes[name])
    pruned_names = stats.get("pruned_class_names", [])
    if isinstance(pruned_names, list) and pruned_names:
        logging.info("Pruned class names:")
        for name in pruned_names:
            logging.info("  %s", name)
    pruned_containment = stats.get("pruned_containment_features", {})
    if isinstance(pruned_containment, dict) and pruned_containment:
        logging.info("Pruned containment by feature: %s", pruned_containment)
    pruned_refs = stats.get("pruned_reference_features", {})
    if isinstance(pruned_refs, dict) and pruned_refs:
        logging.info("Pruned references by feature: %s", pruned_refs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read EMF .ecore metamodels and instance files.")
    parser.add_argument("--ecore", required=True, help="Path to .ecore file")
    parser.add_argument("--instance", help="Path to instance file (.xmi/.xml/.iso20022)")
    parser.add_argument("--dump-metamodel", action="store_true", help="Print metamodel summary")
    parser.add_argument("--dump-metamodel-json", help="Write metamodel summary to JSON")
    parser.add_argument("--export-metamodel-mermaid", help="Export metamodel graph to Mermaid")
    parser.add_argument("--export-metamodel-plantuml", help="Export metamodel graph to PlantUML")
    parser.add_argument("--export-metamodel-gml", help="Export metamodel graph to GML")
    parser.add_argument(
        "--metamodel-include-references",
        action="store_true",
        help="Include non-containment references in metamodel graphs",
    )
    parser.add_argument("--dump-model", action="store_true", help="Print model summary")
    parser.add_argument("--dump-model-json", help="Write model summary to JSON")
    parser.add_argument("--dump-instances", action="store_true", help="Print instance summary")
    parser.add_argument("--dump-instances-json", help="Write instances grouped by class to JSON")
    parser.add_argument("--dump-instances-filter", help="Filter expression for instance JSON dump")
    parser.add_argument("--export-mermaid", help="Export filtered instance graph to Mermaid")
    parser.add_argument("--export-plantuml", help="Export filtered instance graph to PlantUML")
    parser.add_argument("--export-gml", help="Export filtered instance graph to GML")
    parser.add_argument("--export-instance", help="Export filtered instance resource to XMI")
    parser.add_argument("--include-classes", help="Comma-separated EClass names to include")
    parser.add_argument("--exclude-classes", help="Comma-separated EClass names to exclude")
    parser.add_argument(
        "--prune-strip-refs",
        action="store_true",
        help="Remove references to pruned classes in exported instance",
    )
    parser.add_argument(
        "--prune-dry-run",
        action="store_true",
        help="Preview pruning results without writing an instance file",
    )
    parser.add_argument(
        "--prune-dry-run-json",
        help="Write pruning dry-run summary to JSON",
    )
    parser.add_argument("--neighbors-from", help="Seed filter expression for neighborhood expansion")
    parser.add_argument("--neighbors", type=int, help="Neighborhood hops for expansion")
    parser.add_argument("--export-json", help="Export loaded objects to JSON")
    parser.add_argument("--export-edges", help="Export edges to CSV")
    parser.add_argument("--export-paths", help="Export expansion paths to text")
    parser.add_argument("--export-path-ids", help="Export expansion path IDs to text")
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
    parser.add_argument(
        "--expand-classes",
        help="Comma-separated EClass names allowed during expansion",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        _configure_logging(args.verbose)
        logging.info("Parameters:")
        for name, value in vars(args).items():
            logging.info("%s: %s", name, value)

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
        if args.dump_metamodel_json:
            payload = metamodel_dump(packages)
            with open(args.dump_metamodel_json, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
            logging.info("Wrote metamodel JSON: %s", args.dump_metamodel_json)
        if args.export_metamodel_mermaid:
            stats = export_metamodel_mermaid(
                packages,
                args.export_metamodel_mermaid,
                include_references=args.metamodel_include_references,
            )
            logging.info(
                "Wrote metamodel Mermaid: %s (nodes=%s edges=%s)",
                args.export_metamodel_mermaid,
                stats["nodes"],
                stats["edges"],
            )
        if args.export_metamodel_plantuml:
            stats = export_metamodel_plantuml(
                packages,
                args.export_metamodel_plantuml,
                include_references=args.metamodel_include_references,
            )
            logging.info(
                "Wrote metamodel PlantUML: %s (nodes=%s edges=%s)",
                args.export_metamodel_plantuml,
                stats["nodes"],
                stats["edges"],
            )
        if args.export_metamodel_gml:
            stats = export_metamodel_gml(
                packages,
                args.export_metamodel_gml,
                include_references=args.metamodel_include_references,
            )
            logging.info(
                "Wrote metamodel GML: %s (nodes=%s edges=%s)",
                args.export_metamodel_gml,
                stats["nodes"],
                stats["edges"],
            )

        needs_instance = (
            args.dump_instances
            or args.dump_model
            or args.dump_model_json
            or args.dump_instances_json
            or args.export_json
            or args.export_edges
            or args.export_paths
            or args.export_path_ids
            or args.export_mermaid
            or args.export_plantuml
            or args.export_gml
            or args.export_instance
        )
        if needs_instance or args.prune_dry_run or args.prune_dry_run_json:
            if not args.instance and needs_instance:
                logging.error("Instance file required for instance operations")
                return 2
            try:
                instance_resource = load_instance(args.instance, rset) if args.instance else None
            except Exception as exc:  # noqa: BLE001
                logging.error("Failed to load instance: %s", exc)
                return 2
            if instance_resource is not None:
                instats = instance_stats([instance_resource])
                logging.info("Instance stats: roots=%s", instats["roots"])
                roots = list(instance_resource.contents)
            else:
                roots = []
            if args.dump_instances:
                print(summarize_instances([instance_resource]))
            if args.dump_model:
                print(summarize_model(roots))
            if args.dump_model_json:
                payload = model_dump(roots)
                with open(args.dump_model_json, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, indent=2)
                logging.info("Wrote model JSON: %s", args.dump_model_json)
            if args.dump_instances_json:
                try:
                    payload = dump_instances_by_class(roots, filter_expr=args.dump_instances_filter)
                except ValueError as exc:
                    logging.error("Invalid filter expression: %s", exc)
                    return 2
                with open(args.dump_instances_json, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, indent=2)
                logging.info("Wrote instances JSON: %s", args.dump_instances_json)
            expand_depth = args.expand_depth if args.expand_from else None
            expand_classes = None
            if args.expand_classes:
                expand_classes = {name.strip() for name in args.expand_classes.split(",") if name.strip()}
            neighbor_expr = args.neighbors_from
            neighbor_hops = args.neighbors if args.neighbors is not None else None
            include_classes = None
            exclude_classes = None
            if args.include_classes:
                include_classes = {name.strip() for name in args.include_classes.split(",") if name.strip()}
            if args.exclude_classes:
                exclude_classes = {name.strip() for name in args.exclude_classes.split(",") if name.strip()}
            if args.prune_dry_run or args.prune_dry_run_json:
                if instance_resource is None:
                    stats = preview_prune_metamodel(
                        packages,
                        include_classes=include_classes,
                        exclude_classes=exclude_classes,
                    )
                else:
                    stats = export_filtered_instance(
                        instance_resource,
                        args.export_instance or "",
                        include_classes=include_classes,
                        exclude_classes=exclude_classes,
                        dry_run=True,
                    )
                _log_prune_summary(stats)
                if args.prune_dry_run_json:
                    with open(args.prune_dry_run_json, "w", encoding="utf-8") as handle:
                        json.dump(stats, handle, indent=2)
                    logging.info("Wrote prune dry-run JSON: %s", args.prune_dry_run_json)
            if args.export_mermaid:
                try:
                    stats = export_mermaid(
                        roots,
                        args.export_mermaid,
                        filter_expr=args.filter_expr,
                        neighbor_expr=neighbor_expr,
                        neighbor_hops=neighbor_hops,
                    )
                except ValueError as exc:
                    logging.error("Invalid filter expression: %s", exc)
                    return 2
                logging.info(
                    "Wrote Mermaid: %s (nodes=%s edges=%s)",
                    args.export_mermaid,
                    stats["nodes"],
                    stats["edges"],
                )
                if "seed_nodes" in stats:
                    logging.info(
                        "Neighbor metrics: seed_nodes=%s nodes_seen=%s edges_traversed=%s max_hops=%s",
                        stats["seed_nodes"],
                        stats["nodes_seen"],
                        stats["edges_traversed"],
                        stats["max_hops"],
                    )
            if args.export_instance:
                stats = export_filtered_instance(
                    instance_resource,
                    args.export_instance,
                    include_classes=include_classes,
                    exclude_classes=exclude_classes,
                    strip_pruned_references=args.prune_strip_refs,
                )
                logging.info(
                    "Wrote instance XMI: %s (selected=%s roots=%s)",
                    args.export_instance,
                    stats["selected"],
                    stats["roots"],
                )
            if args.export_plantuml:
                try:
                    stats = export_plantuml(
                        roots,
                        args.export_plantuml,
                        filter_expr=args.filter_expr,
                        neighbor_expr=neighbor_expr,
                        neighbor_hops=neighbor_hops,
                    )
                except ValueError as exc:
                    logging.error("Invalid filter expression: %s", exc)
                    return 2
                logging.info(
                    "Wrote PlantUML: %s (nodes=%s edges=%s)",
                    args.export_plantuml,
                    stats["nodes"],
                    stats["edges"],
                )
                if "seed_nodes" in stats:
                    logging.info(
                        "Neighbor metrics: seed_nodes=%s nodes_seen=%s edges_traversed=%s max_hops=%s",
                        stats["seed_nodes"],
                        stats["nodes_seen"],
                        stats["edges_traversed"],
                        stats["max_hops"],
                    )
            if args.export_gml:
                try:
                    stats = export_gml(
                        roots,
                        args.export_gml,
                        filter_expr=args.filter_expr,
                        neighbor_expr=neighbor_expr,
                        neighbor_hops=neighbor_hops,
                    )
                except ValueError as exc:
                    logging.error("Invalid filter expression: %s", exc)
                    return 2
                logging.info(
                    "Wrote GML: %s (nodes=%s edges=%s)",
                    args.export_gml,
                    stats["nodes"],
                    stats["edges"],
                )
                if "seed_nodes" in stats:
                    logging.info(
                        "Neighbor metrics: seed_nodes=%s nodes_seen=%s edges_traversed=%s max_hops=%s",
                        stats["seed_nodes"],
                        stats["nodes_seen"],
                        stats["edges_traversed"],
                        stats["max_hops"],
                    )
            if args.export_json:
                try:
                    entries, metrics = export_json(
                        roots,
                        args.export_json,
                        filter_expr=args.filter_expr,
                        expand_expr=args.expand_from,
                        expand_depth=expand_depth,
                        expand_classes=expand_classes,
                        neighbor_expr=neighbor_expr,
                        neighbor_hops=neighbor_hops,
                    )
                except ValueError as exc:
                    logging.error("Invalid filter expression: %s", exc)
                    return 2
                logging.info("Wrote JSON: %s (objects=%s)", args.export_json, len(entries))
                if metrics:
                    if "seed_nodes" in metrics:
                        logging.info(
                            "Neighbor metrics: seed_nodes=%s nodes_seen=%s edges_traversed=%s max_hops=%s",
                            metrics["seed_nodes"],
                            metrics["nodes_seen"],
                            metrics["edges_traversed"],
                            metrics["max_hops"],
                        )
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
                        expand_classes=expand_classes,
                        neighbor_expr=neighbor_expr,
                        neighbor_hops=neighbor_hops,
                    )
                except ValueError as exc:
                    logging.error("Invalid filter expression: %s", exc)
                    return 2
                logging.info("Wrote edges: %s (edges=%s)", args.export_edges, len(edges))
                if metrics:
                    if "seed_nodes" in metrics:
                        logging.info(
                            "Neighbor metrics: seed_nodes=%s nodes_seen=%s edges_traversed=%s max_hops=%s",
                            metrics["seed_nodes"],
                            metrics["nodes_seen"],
                            metrics["edges_traversed"],
                            metrics["max_hops"],
                        )
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
                        expand_classes=expand_classes,
                        neighbor_expr=neighbor_expr,
                        neighbor_hops=neighbor_hops,
                    )
                except ValueError as exc:
                    logging.error("Invalid filter expression: %s", exc)
                    return 2
                logging.info("Wrote paths: %s (paths=%s)", args.export_paths, len(paths))
                if paths:
                    preview = ", ".join(paths[:10])
                    logging.info("Expansion paths preview (max 10): %s", preview)
                if metrics:
                    if "seed_nodes" in metrics:
                        logging.info(
                            "Neighbor metrics: seed_nodes=%s nodes_seen=%s edges_traversed=%s max_hops=%s",
                            metrics["seed_nodes"],
                            metrics["nodes_seen"],
                            metrics["edges_traversed"],
                            metrics["max_hops"],
                        )
                    logging.info(
                        "Expansion metrics: start_nodes=%s nodes_seen=%s edges_traversed=%s loops_detected=%s max_depth=%s",
                        metrics["start_nodes"],
                        metrics["nodes_seen"],
                        metrics["edges_traversed"],
                        metrics["loops_detected"],
                        metrics["max_depth"],
                    )
                    if metrics["start_nodes"] == 0:
                        logging.warning("No expansion start nodes matched the expression")
            if args.export_path_ids:
                if not args.expand_from:
                    logging.error("export-path-ids requires --expand-from")
                    return 2
                try:
                    pairs, metrics = export_path_ids(
                        roots,
                        args.export_path_ids,
                        filter_expr=args.filter_expr,
                        expand_expr=args.expand_from,
                        expand_depth=expand_depth,
                        expand_classes=expand_classes,
                        neighbor_expr=neighbor_expr,
                        neighbor_hops=neighbor_hops,
                    )
                except ValueError as exc:
                    logging.error("Invalid filter expression: %s", exc)
                    return 2
                logging.info("Wrote path IDs: %s (rows=%s)", args.export_path_ids, len(pairs))
                if pairs:
                    preview = ", ".join([path for _, path in pairs[:10]])
                    logging.info("Path IDs preview (max 10): %s", preview)
                if metrics:
                    if "seed_nodes" in metrics:
                        logging.info(
                            "Neighbor metrics: seed_nodes=%s nodes_seen=%s edges_traversed=%s max_hops=%s",
                            metrics["seed_nodes"],
                            metrics["nodes_seen"],
                            metrics["edges_traversed"],
                            metrics["max_hops"],
                        )
                    logging.info(
                        "Expansion metrics: start_nodes=%s nodes_seen=%s edges_traversed=%s loops_detected=%s max_depth=%s",
                        metrics["start_nodes"],
                        metrics["nodes_seen"],
                        metrics["edges_traversed"],
                        metrics["loops_detected"],
                        metrics["max_depth"],
                    )
                    if metrics["start_nodes"] == 0:
                        logging.warning("No expansion start nodes matched the expression")

        return 0
    except KeyboardInterrupt:
        print("Stopped by user.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
