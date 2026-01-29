#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys

from .xsd_enrich import enrich_xsd, load_preferences


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enrich ISO 20022 XSD with xmi:id annotations.")
    parser.add_argument("--ecore", required=True, help="Path to .ecore file")
    parser.add_argument("--instance", required=True, help="Path to instance file (.xmi/.xml/.iso20022)")
    parser.add_argument("--xsd", required=True, help="Path to input XSD")
    parser.add_argument("--output", required=True, help="Path to output XSD")
    parser.add_argument("--map", dest="prefs", help="JSON file with kind->EClass preferences")
    parser.add_argument("--trace-name", help="Trace mapping for a specific XSD name")
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

        prefs = load_preferences(args.prefs)
        stats = enrich_xsd(
            ecore_path=args.ecore,
            instance_path=args.instance,
            xsd_path=args.xsd,
            output_path=args.output,
            kind_preferences=prefs,
            trace_name=args.trace_name,
        )
        logging.info(
            "XSD enrichment complete: annotated=%s missing=%s total=%s",
            stats["annotated"],
            stats["missing"],
            stats["total"],
        )
        return 0
    except KeyboardInterrupt:
        print("Stopped by user.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
