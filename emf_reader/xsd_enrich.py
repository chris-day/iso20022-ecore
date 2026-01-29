from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from lxml import etree

from .export import build_object_graph
from .loader import load_instance, load_metamodel

LOGGER = logging.getLogger(__name__)

XSD_NS = "http://www.w3.org/2001/XMLSchema"

ALLOWED_ECLASSES = {
    "MessageSet",
    "BusinessArea",
    "MessageDefinition",
    "ExternalSchema",
    "MessageBuildingBlock",
    "MessageComponent",
    "ChoiceComponent",
    "MessageComponentType",
    "MessageElement",
    "MessageAssociationEnd",
    "MessageAttribute",
    "DataType",
}

DEFAULT_KIND_PREFERENCES = {
    "complexType": [
        "MessageDefinition",
        "MessageComponent",
        "MessageComponentType",
        "ChoiceComponent",
    ],
    "simpleType": [
        "DataType",
    ],
    "element": [
        "MessageElement",
        "MessageBuildingBlock",
        "MessageAssociationEnd",
    ],
    "attribute": [
        "MessageAttribute",
    ],
}


def _normalize_xsd_name(name: str) -> str:
    if name.endswith("_SimpleType"):
        return name[: -len("_SimpleType")]
    return name


def _index_model_objects(objects: Iterable[object]) -> Dict[str, List[object]]:
    index: Dict[str, List[object]] = {}
    for obj in objects:
        if obj.eClass.name not in ALLOWED_ECLASSES:
            continue
        name = getattr(obj, "name", None)
        if not isinstance(name, str) or not name:
            continue
        index.setdefault(name, []).append(obj)
    return index


def _pick_candidate(candidates: List[object], preferences: List[str]) -> object | None:
    if not candidates:
        return None
    if not preferences:
        return candidates[0]
    for pref in preferences:
        for cand in candidates:
            if cand.eClass.name == pref:
                return cand
    return candidates[0]


def _get_xmi_id(obj: object) -> str | None:
    value = getattr(obj, "_internal_id", None)
    if isinstance(value, str) and value:
        return value
    return None


def _ensure_annotation(element: etree._Element, source: str, value: str) -> None:
    ann = element.find(f"{{{XSD_NS}}}annotation")
    if ann is None:
        ann = etree.SubElement(element, f"{{{XSD_NS}}}annotation")
    appinfo = None
    for child in ann.findall(f"{{{XSD_NS}}}appinfo"):
        if child.get("source") == source:
            appinfo = child
            break
    if appinfo is None:
        appinfo = etree.SubElement(ann, f"{{{XSD_NS}}}appinfo")
        appinfo.set("source", source)
    appinfo.text = value


def enrich_xsd(
    ecore_path: str,
    instance_path: str,
    xsd_path: str,
    output_path: str,
    kind_preferences: Dict[str, List[str]] | None = None,
    trace_name: str | None = None,
) -> Dict[str, int]:
    rset, _ = load_metamodel(ecore_path)
    instance_resource = load_instance(instance_path, rset)

    objects, _ = build_object_graph(instance_resource.contents)
    model_objects = [info.obj for info in objects]
    index = _index_model_objects(model_objects)

    prefs = dict(DEFAULT_KIND_PREFERENCES)
    if kind_preferences:
        prefs.update(kind_preferences)

    tree = etree.parse(xsd_path)
    root = tree.getroot()

    stats = {
        "annotated": 0,
        "missing": 0,
        "total": 0,
    }

    for kind in ("complexType", "simpleType", "element", "attribute"):
        for elem in root.findall(f".//xs:{kind}", namespaces={"xs": XSD_NS}):
            name = elem.get("name")
            if not name:
                continue
            stats["total"] += 1
            lookup_name = _normalize_xsd_name(name)
            candidates = index.get(lookup_name, [])
            if not candidates and kind == "element":
                type_name = elem.get("type")
                if type_name:
                    if ":" in type_name:
                        type_name = type_name.split(":", 1)[1]
                    type_lookup = _normalize_xsd_name(type_name)
                    candidates = index.get(type_lookup, [])
            picked = _pick_candidate(candidates, prefs.get(kind, []))
            if trace_name and lookup_name == trace_name:
                LOGGER.info(
                    "trace-name=%s kind=%s candidates=%s picked=%s",
                    trace_name,
                    kind,
                    [f"{c.eClass.name}:{getattr(c, 'name', None)}" for c in candidates],
                    f"{picked.eClass.name}:{getattr(picked, 'name', None)}" if picked else None,
                )
            if picked is None:
                stats["missing"] += 1
                continue
            xmi_id = _get_xmi_id(picked)
            if not xmi_id:
                stats["missing"] += 1
                continue
            _ensure_annotation(elem, "xmi:id", xmi_id)
            parent = getattr(picked, "eContainer", lambda: None)()
            if parent is not None:
                parent_id = _get_xmi_id(parent)
                if parent_id:
                    parent_value = parent_id
                else:
                    parent_name = getattr(parent, "name", None)
                    parent_value = parent_name if isinstance(parent_name, str) and parent_name else None
                if parent_value:
                    _ensure_annotation(elem, "parent", parent_value)
            stats["annotated"] += 1

    out_path = Path(output_path)
    out_path.write_bytes(
        etree.tostring(tree, xml_declaration=True, encoding="UTF-8", pretty_print=True)
    )

    return stats


def load_preferences(path: str | None) -> Dict[str, List[str]] | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
