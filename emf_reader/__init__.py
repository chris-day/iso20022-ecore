"""EMF metamodel/instance reader using pyecore."""

__version__ = "0.1.16"

from .loader import (
    load_metamodel,
    load_instance,
    count_metamodel_classes,
    metamodel_stats,
    summarize_metamodel,
    summarize_instances,
    instance_stats,
)
from .export import export_json, export_edges, build_object_graph

__all__ = [
    "load_metamodel",
    "load_instance",
    "count_metamodel_classes",
    "metamodel_stats",
    "summarize_metamodel",
    "summarize_instances",
    "instance_stats",
    "build_object_graph",
    "export_json",
    "export_edges",
]
