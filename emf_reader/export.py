from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from pyecore.ecore import EObject
from pyecore.resources import URI
from pyecore.resources.xmi import XMIResource

from .query import build_context, build_predicate
from .loader import _configure_resource_set


@dataclass
class ObjectInfo:
    obj: EObject
    obj_id: str
    path: str


def _all_features(obj: EObject, name: str):
    attr = getattr(obj.eClass, name, [])
    return attr() if callable(attr) else list(attr)

def _containment_features(obj: EObject):
    return [ref for ref in _all_features(obj, "eAllReferences") if getattr(ref, "containment", False)]

def _json_safe(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    name = getattr(value, "name", None)
    if name is not None:
        return name
    return str(value)


def build_object_graph(roots: Iterable[EObject]) -> Tuple[List[ObjectInfo], List[Dict[str, str | bool]]]:
    seen: Dict[EObject, ObjectInfo] = {}
    edges: List[Dict[str, str | bool]] = []

    def ensure(obj: EObject, path: str) -> ObjectInfo:
        if obj in seen:
            return seen[obj]
        obj_id = f"o{len(seen) + 1}"
        info = ObjectInfo(obj=obj, obj_id=obj_id, path=path)
        seen[obj] = info
        return info

    def visit(obj: EObject, path: str) -> None:
        info = ensure(obj, path)
        for ref in _containment_features(obj):
            value = obj.eGet(ref)
            if value is None:
                continue
            if ref.many:
                for idx, child in enumerate(list(value)):
                    if child is None:
                        continue
                    child_path = f"{info.path}/{ref.name}[{idx}]"
                    child_info = ensure(child, child_path)
                    edges.append(
                        {
                            "src_id": info.obj_id,
                            "src_class": obj.eClass.name,
                            "feature": ref.name,
                            "dst_id": child_info.obj_id,
                            "dst_class": child.eClass.name,
                            "containment": True,
                        }
                    )
                    visit(child, child_path)
            else:
                child = value
                if child is None:
                    continue
                child_path = f"{info.path}/{ref.name}[0]"
                child_info = ensure(child, child_path)
                edges.append(
                    {
                        "src_id": info.obj_id,
                        "src_class": obj.eClass.name,
                        "feature": ref.name,
                        "dst_id": child_info.obj_id,
                        "dst_class": child.eClass.name,
                        "containment": True,
                    }
                )
                visit(child, child_path)

    for idx, root in enumerate(roots):
        visit(root, f"/{root.eClass.name}[{idx}]")

    objects = list(seen.values())
    return objects, edges


def _iter_values(value: object) -> List[EObject]:
    if value is None:
        return []
    if isinstance(value, EObject):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return [v for v in value if isinstance(v, EObject)]
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
        try:
            return [v for v in value if isinstance(v, EObject)]
        except Exception:  # noqa: BLE001
            return []
    return []


def _reference_ids(obj: EObject, ref, id_map: Dict[EObject, str]) -> List[str]:
    value = obj.eGet(ref)
    values = _iter_values(value)
    return [id_map[v] for v in values if v in id_map]


def _node_label(obj: EObject) -> str:
    name = getattr(obj, "name", None)
    if isinstance(name, str) and name:
        return name
    return ""

def _id_label(obj: EObject, fallback: str) -> str:
    value = getattr(obj, "_internal_id", None)
    if isinstance(value, str) and value:
        return value
    return fallback


def _preferred_id(obj: EObject, fallback: str) -> str:
    return _id_label(obj, fallback)


def _xmi_id(obj: EObject) -> str | None:
    value = getattr(obj, "_internal_id", None)
    if isinstance(value, str) and value:
        return value
    return None


def _proxy_id(obj: EObject) -> str | None:
    proxy_uri = getattr(obj, "eProxyURI", None)
    if proxy_uri is None:
        return None
    fragment = getattr(proxy_uri, "fragment", None)
    if isinstance(fragment, str) and fragment:
        return fragment
    proxy_text = str(proxy_uri)
    if "#" in proxy_text:
        return proxy_text.split("#", 1)[1] or None
    return None


def _resolve_filtered_target(
    target: EObject, filtered_set: set[EObject], xmi_id_map: dict[str, EObject]
) -> EObject | None:
    if target in filtered_set:
        return target
    target_id = _xmi_id(target) or _proxy_id(target)
    if target_id and target_id in xmi_id_map:
        return xmi_id_map[target_id]
    return None


def _neighbor_expand(
    objects: List[ObjectInfo],
    seed_expr: str,
    hops: int,
    include_containment: bool = True,
    include_references: bool = True,
) -> tuple[List[ObjectInfo], dict[str, int]]:
    predicate = build_predicate(seed_expr)
    obj_map = {info.obj: info for info in objects}
    seeds: List[EObject] = []
    for info in objects:
        ctx = build_context(info.obj, info.obj_id, info.path)
        if predicate(ctx):
            seeds.append(info.obj)
    if not seeds:
        return [], {"seed_nodes": 0, "nodes_seen": 0, "edges_traversed": 0, "max_hops": 0}

    seen: set[EObject] = set(seeds)
    frontier: List[EObject] = list(seeds)
    edges_traversed = 0
    depth = 0
    while frontier and depth < hops:
        next_frontier: List[EObject] = []
        for obj in frontier:
            refs = []
            if include_references:
                refs.extend(_all_features(obj, "eAllReferences"))
            if include_containment:
                refs.extend(_containment_features(obj))
            for ref in refs:
                value = obj.eGet(ref)
                for target in _iter_values(value):
                    edges_traversed += 1
                    if target not in seen:
                        seen.add(target)
                        next_frontier.append(target)
        frontier = next_frontier
        depth += 1

    return (
        [obj_map[obj] for obj in seen if obj in obj_map],
        {
            "seed_nodes": len(seeds),
            "nodes_seen": len(seen),
            "edges_traversed": edges_traversed,
            "max_hops": depth,
        },
    )


def _expand_from(
    objects: List[ObjectInfo],
    expand_expr: str,
    expand_depth: int | None,
    expand_classes: set[str] | None,
) -> tuple[List[ObjectInfo], dict[str, int], dict[EObject, str], dict[EObject, str]]:
    predicate = build_predicate(expand_expr)
    obj_map = {info.obj: info for info in objects}
    id_map = {info.obj: info.obj_id for info in objects}
    start: List[EObject] = []
    for info in objects:
        if expand_classes and info.obj.eClass.name not in expand_classes:
            continue
        ctx = build_context(info.obj, info.obj_id, info.path)
        if predicate(ctx):
            start.append(info.obj)

    if not start:
        return (
            [],
            {
            "start_nodes": 0,
            "nodes_seen": 0,
            "edges_traversed": 0,
            "loops_detected": 0,
            "max_depth": 0,
            },
            {},
            {},
        )

    seen: set[EObject] = set(start)
    frontier: List[EObject] = list(start)
    path_map: dict[EObject, str] = {obj: f"/{_node_label(obj)}" for obj in start}
    id_path_map: dict[EObject, str] = {
        obj: f"/{_id_label(obj, id_map[obj])}" for obj in start if obj in id_map
    }
    depth = 0
    edges_traversed = 0
    loops_detected = 0
    while frontier and (expand_depth is None or expand_depth < 0 or depth < expand_depth):
        next_frontier: List[EObject] = []
        for obj in frontier:
            for ref in _all_features(obj, "eAllReferences"):
                value = obj.eGet(ref)
                if value is None:
                    continue
                if ref.many:
                    try:
                        items = list(value)
                    except Exception:  # noqa: BLE001
                        items = []
                    for idx, target in enumerate(items):
                        if not isinstance(target, EObject):
                            continue
                        edges_traversed += 1
                        if expand_classes and target.eClass.name not in expand_classes:
                            continue
                        if target not in seen:
                            seen.add(target)
                            next_frontier.append(target)
                            path_map[target] = f"{path_map[obj]}/{_node_label(target)}"
                            id_path_map[target] = (
                                f"{id_path_map.get(obj, '')}/{_id_label(target, id_map[target])}"
                            )
                        else:
                            loops_detected += 1
                else:
                    target = value if isinstance(value, EObject) else None
                    if target is None:
                        continue
                    if expand_classes and target.eClass.name not in expand_classes:
                        continue
                    edges_traversed += 1
                    if target not in seen:
                        seen.add(target)
                        next_frontier.append(target)
                        path_map[target] = f"{path_map[obj]}/{_node_label(target)}"
                        id_path_map[target] = (
                            f"{id_path_map.get(obj, '')}/{_id_label(target, id_map[target])}"
                        )
                    else:
                        loops_detected += 1
        frontier = next_frontier
        depth += 1

    return (
        [obj_map[obj] for obj in seen if obj in obj_map],
        {
            "start_nodes": len(start),
            "nodes_seen": len(seen),
            "edges_traversed": edges_traversed,
            "loops_detected": loops_detected,
            "max_depth": depth,
        },
        path_map,
        id_path_map,
    )


def _apply_filter(
    objects: List[ObjectInfo],
    filter_expr: str | None,
    expand_expr: str | None,
    expand_depth: int | None,
    expand_classes: set[str] | None,
    neighbor_expr: str | None = None,
    neighbor_hops: int | None = None,
) -> tuple[
    List[ObjectInfo],
    dict[str, int] | None,
    dict[EObject, str] | None,
    dict[EObject, str] | None,
]:
    neighbor_metrics = None
    if neighbor_expr and neighbor_hops is not None:
        objects, neighbor_metrics = _neighbor_expand(
            objects,
            neighbor_expr,
            neighbor_hops,
            include_containment=True,
            include_references=True,
        )
    if expand_expr:
        filtered, metrics, path_map, id_path_map = _expand_from(
            objects, expand_expr, expand_depth, expand_classes
        )
    else:
        filtered = objects
        metrics = None
        path_map = None
        id_path_map = None
    if not filter_expr:
        if neighbor_metrics and metrics:
            metrics = {**metrics, **neighbor_metrics}
        elif neighbor_metrics:
            metrics = neighbor_metrics
        return filtered, metrics, path_map, id_path_map
    predicate = build_predicate(filter_expr)
    result: List[ObjectInfo] = []
    for info in filtered:
        ctx = build_context(info.obj, info.obj_id, info.path)
        if predicate(ctx):
            result.append(info)
    if path_map is not None:
        path_map = {info.obj: path_map[info.obj] for info in result if info.obj in path_map}
    if id_path_map is not None:
        id_path_map = {
            info.obj: id_path_map[info.obj] for info in result if info.obj in id_path_map
        }
    if neighbor_metrics and metrics:
        metrics = {**metrics, **neighbor_metrics}
    elif neighbor_metrics:
        metrics = neighbor_metrics
    return result, metrics, path_map, id_path_map


def export_json(
    roots: Iterable[EObject],
    output_path: str,
    filter_expr: str | None = None,
    expand_expr: str | None = None,
    expand_depth: int | None = None,
    expand_classes: set[str] | None = None,
    neighbor_expr: str | None = None,
    neighbor_hops: int | None = None,
) -> tuple[List[Dict[str, object]], dict[str, int] | None]:
    objects, edges = build_object_graph(roots)
    objects, metrics, _, _ = _apply_filter(
        objects,
        filter_expr,
        expand_expr,
        expand_depth,
        expand_classes,
        neighbor_expr=neighbor_expr,
        neighbor_hops=neighbor_hops,
    )
    id_map = {info.obj: _preferred_id(info.obj, info.obj_id) for info in objects}

    entries: List[Dict[str, object]] = []

    for info in objects:
        obj = info.obj
        attributes: Dict[str, object] = {}
        for attr in _all_features(obj, "eAllAttributes"):
            value = obj.eGet(attr)
            if attr.many:
                attributes[attr.name] = _json_safe(list(value)) if value is not None else []
            else:
                attributes[attr.name] = _json_safe(value)

        containment_ids: List[str] = []
        for ref in _containment_features(obj):
            value = obj.eGet(ref)
            if value is None:
                continue
            if ref.many:
                for child in list(value):
                    if child in id_map:
                        containment_ids.append(id_map[child])
            else:
                if value in id_map:
                    containment_ids.append(id_map[value])

        references: Dict[str, List[str]] = {}
        for ref in _all_features(obj, "eAllReferences"):
            if ref.containment:
                continue
            references[ref.name] = _reference_ids(obj, ref, id_map)

        entries.append(
            {
                "id": _preferred_id(obj, info.obj_id),
                "local_id": info.obj_id,
                "ID": _id_label(obj, info.obj_id),
                "eClass": obj.eClass.name,
                "nsURI": obj.eClass.ePackage.nsURI if obj.eClass.ePackage else None,
                "attributes": attributes,
                "containment": containment_ids,
                "references": references,
                "path": info.path,
            }
        )

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(entries, handle, indent=2)

    return entries, metrics


def export_edges(
    roots: Iterable[EObject],
    output_path: str,
    filter_expr: str | None = None,
    expand_expr: str | None = None,
    expand_depth: int | None = None,
    expand_classes: set[str] | None = None,
    neighbor_expr: str | None = None,
    neighbor_hops: int | None = None,
) -> tuple[List[Dict[str, str | bool]], dict[str, int] | None]:
    objects, containment_edges = build_object_graph(roots)
    objects, metrics, _, _ = _apply_filter(
        objects,
        filter_expr,
        expand_expr,
        expand_depth,
        expand_classes,
        neighbor_expr=neighbor_expr,
        neighbor_hops=neighbor_hops,
    )
    id_map = {info.obj: _preferred_id(info.obj, info.obj_id) for info in objects}
    local_to_preferred = {info.obj_id: id_map[info.obj] for info in objects}
    edges: List[Dict[str, str | bool]] = list(containment_edges)
    remapped_edges: List[Dict[str, str | bool]] = []
    for edge in edges:
        src = local_to_preferred.get(edge["src_id"])
        dst = local_to_preferred.get(edge["dst_id"])
        if not src or not dst:
            continue
        remapped = dict(edge)
        remapped["src_id"] = src
        remapped["dst_id"] = dst
        remapped_edges.append(remapped)
    edges = remapped_edges

    for info in objects:
        obj = info.obj
        for ref in _all_features(obj, "eAllReferences"):
            if ref.containment:
                continue
            value = obj.eGet(ref)
            if value is None:
                continue
            for target in _iter_values(value):
                if target not in id_map:
                    continue
                edges.append(
                    {
                        "src_id": info.obj_id,
                        "src_class": obj.eClass.name,
                        "feature": ref.name,
                        "dst_id": id_map[target],
                        "dst_class": target.eClass.name,
                        "containment": False,
                    }
                )

    id_set = set(id_map.values())
    edges = [edge for edge in edges if edge["src_id"] in id_set and edge["dst_id"] in id_set]

    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["src_id", "src_class", "feature", "dst_id", "dst_class", "containment"],
        )
        writer.writeheader()
        writer.writerows(edges)

    return edges, metrics


def export_paths(
    roots: Iterable[EObject],
    output_path: str,
    filter_expr: str | None = None,
    expand_expr: str | None = None,
    expand_depth: int | None = None,
    expand_classes: set[str] | None = None,
    neighbor_expr: str | None = None,
    neighbor_hops: int | None = None,
) -> tuple[List[str], dict[str, int] | None]:
    objects, _ = build_object_graph(roots)
    objects, metrics, path_map, _ = _apply_filter(
        objects,
        filter_expr,
        expand_expr,
        expand_depth,
        expand_classes,
        neighbor_expr=neighbor_expr,
        neighbor_hops=neighbor_hops,
    )
    with open(output_path, "w", encoding="utf-8") as handle:
        if path_map is None:
            return [], metrics
        paths = [path_map[info.obj] for info in objects if info.obj in path_map]
        paths = sorted(set(paths))
        for path in paths:
            handle.write(f"{path}\n")
    return paths, metrics


def export_path_ids(
    roots: Iterable[EObject],
    output_path: str,
    filter_expr: str | None = None,
    expand_expr: str | None = None,
    expand_depth: int | None = None,
    expand_classes: set[str] | None = None,
    neighbor_expr: str | None = None,
    neighbor_hops: int | None = None,
) -> tuple[List[tuple[str, str]], dict[str, int] | None]:
    objects, _ = build_object_graph(roots)
    objects, metrics, _, id_path_map = _apply_filter(
        objects,
        filter_expr,
        expand_expr,
        expand_depth,
        expand_classes,
        neighbor_expr=neighbor_expr,
        neighbor_hops=neighbor_hops,
    )
    with open(output_path, "w", encoding="utf-8") as handle:
        if id_path_map is None:
            return [], metrics
        pairs = [
            (info.obj_id, id_path_map[info.obj])
            for info in objects
            if info.obj in id_path_map
        ]
        pairs = sorted(set(pairs))
        for _, id_path in pairs:
            handle.write(f"{id_path}\n")
    return pairs, metrics


def summarize_model(roots: Iterable[EObject]) -> str:
    objects, _ = build_object_graph(roots)
    class_counts: dict[str, int] = {}
    class_attrs: dict[str, list[dict[str, object]]] = {}
    class_refs: dict[str, list[dict[str, object]]] = {}
    for info in objects:
        name = info.obj.eClass.name
        class_counts[name] = class_counts.get(name, 0) + 1
        if name not in class_attrs:
            attrs: list[dict[str, object]] = []
            for attr in _all_features(info.obj, "eAllAttributes"):
                attr_type = attr.eType.name if getattr(attr, "eType", None) else None
                attrs.append({"name": attr.name, "type": attr_type, "many": bool(attr.many)})
            refs: list[dict[str, object]] = []
            for ref in _all_features(info.obj, "eAllReferences"):
                ref_type = ref.eType.name if getattr(ref, "eType", None) else None
                refs.append(
                    {
                        "name": ref.name,
                        "type": ref_type,
                        "many": bool(ref.many),
                        "containment": bool(ref.containment),
                    }
                )
            class_attrs[name] = attrs
            class_refs[name] = refs
    lines = [f"Total objects: {len(objects)}", "Classes:"]
    for name in sorted(class_counts):
        lines.append(f"  {name}: {class_counts[name]}")
        attrs = class_attrs.get(name, [])
        refs = class_refs.get(name, [])
        if attrs:
            lines.append(f"    Attributes: {', '.join(attrs)}")
        if refs:
            lines.append(f"    References: {', '.join(refs)}")
    return "\n".join(lines)


def model_dump(roots: Iterable[EObject]) -> dict[str, object]:
    objects, _ = build_object_graph(roots)
    class_counts: dict[str, int] = {}
    class_attrs: dict[str, list[str]] = {}
    class_refs: dict[str, list[str]] = {}
    for info in objects:
        name = info.obj.eClass.name
        class_counts[name] = class_counts.get(name, 0) + 1
        if name not in class_attrs:
            attrs = [a.name for a in _all_features(info.obj, "eAllAttributes")]
            refs = [r.name for r in _all_features(info.obj, "eAllReferences")]
            class_attrs[name] = attrs
            class_refs[name] = refs
    classes = []
    for name in sorted(class_counts):
        classes.append(
            {
                "name": name,
                "count": class_counts[name],
                "attributes": class_attrs.get(name, []),
                "references": class_refs.get(name, []),
            }
        )
    return {
        "total_objects": len(objects),
        "classes": classes,
    }


def dump_instances_by_class(
    roots: Iterable[EObject], filter_expr: str | None = None
) -> dict[str, object]:
    objects, _ = build_object_graph(roots)
    id_map = {info.obj: _preferred_id(info.obj, info.obj_id) for info in objects}
    classes: dict[str, list[dict[str, object]]] = {}
    predicate = build_predicate(filter_expr) if filter_expr else None
    for info in objects:
        if predicate:
            ctx = build_context(info.obj, info.obj_id, info.path)
            if not predicate(ctx):
                continue
        obj = info.obj
        cls_name = obj.eClass.name
        entry: dict[str, object] = {
            "id": _preferred_id(obj, info.obj_id),
            "local_id": info.obj_id,
            "ID": _id_label(obj, info.obj_id),
            "eClass": cls_name,
            "nsURI": obj.eClass.ePackage.nsURI if obj.eClass.ePackage else None,
            "path": info.path,
            "attributes": {},
            "containment": [],
            "references": {},
        }
        for attr in _all_features(obj, "eAllAttributes"):
            value = obj.eGet(attr)
            if attr.many:
                entry["attributes"][attr.name] = _json_safe(list(value)) if value is not None else []
            else:
                entry["attributes"][attr.name] = _json_safe(value)
        for ref in _containment_features(obj):
            value = obj.eGet(ref)
            if value is None:
                continue
            if ref.many:
                for child in list(value):
                    if child in id_map:
                        entry["containment"].append(id_map[child])
            else:
                if value in id_map:
                    entry["containment"].append(id_map[value])
        for ref in _all_features(obj, "eAllReferences"):
            if ref.containment:
                continue
            entry["references"][ref.name] = _reference_ids(obj, ref, id_map)
        classes.setdefault(cls_name, []).append(entry)
    return {
        "total_objects": len(objects),
        "classes": classes,
    }


def export_mermaid(
    roots: Iterable[EObject],
    output_path: str,
    filter_expr: str | None = None,
    neighbor_expr: str | None = None,
    neighbor_hops: int | None = None,
) -> dict[str, int]:
    objects, _ = build_object_graph(roots)
    filtered, metrics, _, _ = _apply_filter(
        objects,
        filter_expr,
        expand_expr=None,
        expand_depth=None,
        expand_classes=None,
        neighbor_expr=neighbor_expr,
        neighbor_hops=neighbor_hops,
    )

    lines = ["graph TD"]
    id_map = {info.obj: _preferred_id(info.obj, info.obj_id) for info in filtered}
    node_count = 0
    edge_count = 0
    filtered_objs = {info.obj for info in filtered}
    xmi_id_map = { _xmi_id(info.obj): info.obj for info in filtered if _xmi_id(info.obj)}

    def node_label(obj: EObject) -> str:
        name = getattr(obj, "name", None)
        return name if isinstance(name, str) and name else obj.eClass.name

    for info in filtered:
        node_id = id_map[info.obj].replace("-", "_")
        label = node_label(info.obj).replace("\"", "'")
        lines.append(f"  {node_id}[\"{label}\"]")
        node_count += 1

    for info in filtered:
        src_id = id_map[info.obj].replace("-", "_")
        for ref in _all_features(info.obj, "eAllReferences"):
            value = info.obj.eGet(ref)
            for target in _iter_values(value):
                resolved = _resolve_filtered_target(target, filtered_objs, xmi_id_map)
                if resolved is None:
                    continue
                dst_id = id_map[resolved].replace("-", "_")
                lines.append(f"  {src_id} --> {dst_id}")
                edge_count += 1

    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")

    result = {"nodes": node_count, "edges": edge_count}
    if metrics:
        result.update(metrics)
    return result


def export_plantuml(
    roots: Iterable[EObject],
    output_path: str,
    filter_expr: str | None = None,
    neighbor_expr: str | None = None,
    neighbor_hops: int | None = None,
) -> dict[str, int]:
    objects, _ = build_object_graph(roots)
    filtered, metrics, _, _ = _apply_filter(
        objects,
        filter_expr,
        expand_expr=None,
        expand_depth=None,
        expand_classes=None,
        neighbor_expr=neighbor_expr,
        neighbor_hops=neighbor_hops,
    )

    lines = ["@startuml"]
    id_map = {info.obj: _preferred_id(info.obj, info.obj_id) for info in filtered}
    node_count = 0
    edge_count = 0
    filtered_objs = {info.obj for info in filtered}
    xmi_id_map = { _xmi_id(info.obj): info.obj for info in filtered if _xmi_id(info.obj)}

    def node_label(obj: EObject) -> str:
        name = getattr(obj, "name", None)
        return name if isinstance(name, str) and name else obj.eClass.name

    for info in filtered:
        node_id = id_map[info.obj].replace("-", "_")
        label = node_label(info.obj).replace("\"", "'")
        lines.append(f'class "{label}" as {node_id}')
        node_count += 1

    for info in filtered:
        src_id = id_map[info.obj].replace("-", "_")
        for ref in _all_features(info.obj, "eAllReferences"):
            value = info.obj.eGet(ref)
            for target in _iter_values(value):
                resolved = _resolve_filtered_target(target, filtered_objs, xmi_id_map)
                if resolved is None:
                    continue
                dst_id = id_map[resolved].replace("-", "_")
                lines.append(f"{src_id} --> {dst_id}")
                edge_count += 1

    lines.append("@enduml")
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")

    result = {"nodes": node_count, "edges": edge_count}
    if metrics:
        result.update(metrics)
    return result


def export_gml(
    roots: Iterable[EObject],
    output_path: str,
    filter_expr: str | None = None,
    neighbor_expr: str | None = None,
    neighbor_hops: int | None = None,
) -> dict[str, int]:
    objects, _ = build_object_graph(roots)
    filtered, metrics, _, _ = _apply_filter(
        objects,
        filter_expr,
        expand_expr=None,
        expand_depth=None,
        expand_classes=None,
        neighbor_expr=neighbor_expr,
        neighbor_hops=neighbor_hops,
    )

    filtered_objs = [info.obj for info in filtered]
    obj_to_idx = {obj: idx for idx, obj in enumerate(filtered_objs)}
    filtered_set = set(filtered_objs)
    xmi_id_map = { _xmi_id(obj): obj for obj in filtered_objs if _xmi_id(obj)}

    def node_label(obj: EObject) -> str:
        name = getattr(obj, "name", None)
        return name if isinstance(name, str) and name else obj.eClass.name

    lines = ["graph [", "  directed 1"]
    node_count = 0
    edge_count = 0

    for obj in filtered_objs:
        idx = obj_to_idx[obj]
        label = node_label(obj).replace("\"", "'")
        lines.append("  node [")
        lines.append(f"    id {idx}")
        lines.append(f"    label \"{label}\"")
        lines.append("  ]")
        node_count += 1

    filtered_set = set(filtered_objs)
    for src in filtered_objs:
        for ref in _all_features(src, "eAllReferences"):
            value = src.eGet(ref)
            for target in _iter_values(value):
                resolved = _resolve_filtered_target(target, filtered_set, xmi_id_map)
                if resolved is None:
                    continue
                lines.append("  edge [")
                lines.append(f"    source {obj_to_idx[src]}")
                lines.append(f"    target {obj_to_idx[resolved]}")
                lines.append("  ]")
                edge_count += 1

    lines.append("]")
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")

    result = {"nodes": node_count, "edges": edge_count}
    if metrics:
        result.update(metrics)
    return result


def export_filtered_instance(
    instance_resource: XMIResource,
    output_path: str,
    include_classes: set[str] | None = None,
    exclude_classes: set[str] | None = None,
) -> dict[str, int]:
    objects, _ = build_object_graph(instance_resource.contents)
    include_classes = include_classes or set()
    exclude_classes = exclude_classes or set()
    selected: set[EObject] = set()
    for info in objects:
        cls_name = info.obj.eClass.name
        if include_classes and cls_name not in include_classes:
            continue
        if exclude_classes and cls_name in exclude_classes:
            continue
        selected.add(info.obj)

    rset = instance_resource.resource_set
    if rset is None:
        rset = _configure_resource_set()
    rset.resource_factory["xmi"] = XMIResource
    rset.resource_factory["xml"] = XMIResource
    rset.resource_factory[None] = XMIResource
    out_res = rset.create_resource(URI(output_path))

    roots = [obj for obj in selected if obj.eContainer() not in selected]
    for obj in roots:
        out_res.append(obj)

    out_res.save()

    return {"selected": len(selected), "roots": len(roots)}
