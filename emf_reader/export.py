from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from pyecore.ecore import EObject


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


def export_json(roots: Iterable[EObject], output_path: str) -> List[Dict[str, object]]:
    objects, edges = build_object_graph(roots)
    id_map = {info.obj: info.obj_id for info in objects}

    entries: List[Dict[str, object]] = []
    for info in objects:
        obj = info.obj
        attributes: Dict[str, object] = {}
        for attr in _all_features(obj, "eAllAttributes"):
            value = obj.eGet(attr)
            if attr.many:
                attributes[attr.name] = list(value) if value is not None else []
            else:
                attributes[attr.name] = value

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
                "id": info.obj_id,
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

    return entries


def export_edges(roots: Iterable[EObject], output_path: str) -> List[Dict[str, str | bool]]:
    objects, containment_edges = build_object_graph(roots)
    id_map = {info.obj: info.obj_id for info in objects}
    edges: List[Dict[str, str | bool]] = list(containment_edges)

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

    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["src_id", "src_class", "feature", "dst_id", "dst_class", "containment"],
        )
        writer.writeheader()
        writer.writerows(edges)

    return edges
