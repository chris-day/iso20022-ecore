"""EMF metamodel/instance reader using pyecore."""

__version__ = "0.1.47"

from .loader import (
    load_metamodel,
    load_instance,
    count_metamodel_classes,
    metamodel_stats,
    metamodel_dump,
    summarize_metamodel,
    summarize_instances,
    instance_stats,
)
from .export import export_json, export_edges, build_object_graph, model_dump

__all__ = [
    "load_metamodel",
    "load_instance",
    "count_metamodel_classes",
    "metamodel_stats",
    "metamodel_dump",
    "summarize_metamodel",
    "summarize_instances",
    "instance_stats",
    "build_object_graph",
    "export_json",
    "export_edges",
    "model_dump",
]
