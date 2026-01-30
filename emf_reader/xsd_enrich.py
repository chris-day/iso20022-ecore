from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from lxml import etree

from .export import build_object_graph
from .loader import _all_features
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
    "CodeSet",
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
        "CodeSet",
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


def _is_allowed(obj: object) -> bool:
    if obj.eClass.name in ALLOWED_ECLASSES:
        return True
    for sup in obj.eClass.eAllSuperTypes():
        if sup.name in {"DataType", "CodeSet"}:
            return True
    return False


def _iter_ref_targets(value: object) -> list[object]:
    if value is None:
        return []
    if hasattr(value, "eClass"):
        return [value]
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
        try:
            return [v for v in value if hasattr(v, "eClass")]
        except Exception:  # noqa: BLE001
            return []
    return []


def _collect_objects_with_references(roots: Iterable[object]) -> list[object]:
    seen: set[object] = set()
    queue = list(roots)
    while queue:
        obj = queue.pop()
        if obj in seen:
            continue
        seen.add(obj)
        for ref in _all_features(obj, "eAllReferences"):
            try:
                value = obj.eGet(ref)
            except Exception:  # noqa: BLE001
                continue
            for target in _iter_ref_targets(value):
                if target not in seen:
                    queue.append(target)
    return list(seen)

def _index_model_objects(objects: Iterable[object]) -> Dict[str, List[object]]:
    index: Dict[str, List[object]] = {}
    for obj in objects:
        if not _is_allowed(obj):
            continue
        name = getattr(obj, "name", None)
        if not isinstance(name, str) or not name:
            continue
        index.setdefault(name, []).append(obj)
        xml_tag = getattr(obj, "xmlTag", None)
        if isinstance(xml_tag, str) and xml_tag:
            index.setdefault(xml_tag, []).append(obj)
    return index


def _find_parent_complex_type(elem: etree._Element) -> str | None:
    current = elem.getparent()
    while current is not None:
        if current.tag == f"{{{XSD_NS}}}complexType":
            return current.get("name")
        current = current.getparent()
    return None


def _children_by_xml_tag(parent_obj: object, xml_tag: str) -> list[object]:
    matches: list[object] = []
    for ref in _all_features(parent_obj, "eAllContainments"):
        value = parent_obj.eGet(ref)
        if value is None:
            continue
        items = list(value) if ref.many else [value]
        for child in items:
            if child.eClass.name not in {"MessageElement", "MessageAttribute"}:
                continue
            tag = getattr(child, "xmlTag", None)
            if isinstance(tag, str) and tag == xml_tag:
                matches.append(child)
    return matches


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


def _message_definition_identifier(obj: object) -> str | None:
    if obj.eClass.name != "MessageDefinitionIdentifier":
        return None
    business_area = getattr(obj, "businessArea", None)
    message_functionality = getattr(obj, "messageFunctionality", None)
    flavour = getattr(obj, "flavour", None)
    version = getattr(obj, "version", None)
    parts = [business_area, message_functionality, flavour, version]
    if all(isinstance(p, str) and p for p in parts):
        return ".".join(parts)
    return None


def _target_namespace_identifier(target_namespace: str) -> str | None:
    prefix = "urn:iso:std:iso:20022:tech:xsd:"
    if target_namespace.startswith(prefix):
        return target_namespace[len(prefix) :]
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
    verbose: bool = False,
) -> Dict[str, int]:
    rset, _ = load_metamodel(ecore_path)
    instance_resource = load_instance(instance_path, rset)

    objects, _ = build_object_graph(instance_resource.contents)
    containment_objects = [info.obj for info in objects]
    model_objects = _collect_objects_with_references(containment_objects)
    id_index = { _get_xmi_id(obj): obj for obj in model_objects if _get_xmi_id(obj)}
    index = _index_model_objects(model_objects)

    prefs = dict(DEFAULT_KIND_PREFERENCES)
    if kind_preferences:
        prefs.update(kind_preferences)

    tree = etree.parse(xsd_path)
    root = tree.getroot()
    target_namespace = root.get("targetNamespace")

    matched_identifier = None
    identifier_obj = None
    if target_namespace:
        target_id = _target_namespace_identifier(target_namespace)
        if target_id:
            for obj in model_objects:
                ident = _message_definition_identifier(obj)
                if ident and ident == target_id:
                    matched_identifier = ident
                    identifier_obj = obj
                    break

    if matched_identifier and identifier_obj:
        _ensure_annotation(root, "messageDefinitionIdentifier", matched_identifier)
        _ensure_annotation(root, "businessArea", identifier_obj.businessArea)
        _ensure_annotation(root, "messageFunctionality", identifier_obj.messageFunctionality)
        _ensure_annotation(root, "flavour", identifier_obj.flavour)
        _ensure_annotation(root, "version", identifier_obj.version)
        md = getattr(identifier_obj, "eContainer", lambda: None)()
        if md is not None:
            md_id = _get_xmi_id(md)
            if md_id:
                _ensure_annotation(root, "messageDefinition", md_id)

    def _belongs_to_message_definition(obj: object) -> bool:
        if not matched_identifier:
            return True
        current = obj
        while current is not None:
            if current.eClass.name == "MessageDefinition":
                mdi = getattr(current, "messageDefinitionIdentifier", None)
                ident = _message_definition_identifier(mdi) if mdi is not None else None
                return ident == matched_identifier
            current = getattr(current, "eContainer", lambda: None)()
        return False

    def _scope_candidates(cands: list[object]) -> list[object]:
        scoped = []
        for c in cands:
            if c.eClass.name in {"MessageBuildingBlock", "MessageElement"}:
                if _belongs_to_message_definition(c):
                    scoped.append(c)
            else:
                scoped.append(c)
        return scoped

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
            candidates = []
            if kind == "element":
                parent_name = _find_parent_complex_type(elem)
                if parent_name:
                    parent_candidates = _scope_candidates(index.get(parent_name, []))
                    parent = _pick_candidate(parent_candidates, ["MessageComponent", "MessageComponentType", "ChoiceComponent"])
                    if parent is not None:
                        candidates = _children_by_xml_tag(parent, lookup_name)
            if not candidates:
                candidates = _scope_candidates(index.get(lookup_name, []))
            if not candidates and kind == "element":
                type_name = elem.get("type")
                if type_name:
                    if ":" in type_name:
                        type_name = type_name.split(":", 1)[1]
                    type_lookup = _normalize_xsd_name(type_name)
                    candidates = _scope_candidates(index.get(type_lookup, []))
            pref_list = prefs.get(kind, [])
            if lookup_name.endswith("Code"):
                pref_list = ["CodeSet"] + [p for p in pref_list if p != "CodeSet"]
            picked = _pick_candidate(candidates, pref_list)
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
                if verbose:
                    LOGGER.warning("xsd=%s kind=%s status=missing", lookup_name, kind)
                continue
            xmi_id = _get_xmi_id(picked)
            if not xmi_id:
                stats["missing"] += 1
                if verbose:
                    LOGGER.warning("xsd=%s kind=%s status=missing (no xmi:id)", lookup_name, kind)
                continue
            _ensure_annotation(elem, "xmi:id", xmi_id)
            definition = getattr(picked, "definition", None)
            if isinstance(definition, str) and definition:
                _ensure_annotation(elem, "definition", definition)
            if picked.eClass.name == "MessageElement":
                be_trace = getattr(picked, "businessElementTrace", None)
                bc_trace = getattr(picked, "businessComponentTrace", None)

                def _trace_name(trace_obj: object) -> str | None:
                    if trace_obj is None:
                        return None
                    if hasattr(trace_obj, "eClass"):
                        name = getattr(trace_obj, "name", None)
                        return name if isinstance(name, str) and name else None
                    if isinstance(trace_obj, str):
                        target = id_index.get(trace_obj)
                        if target is not None:
                            name = getattr(target, "name", None)
                            return name if isinstance(name, str) and name else None
                    return None

                def _trace_id(trace_obj: object) -> str | None:
                    if trace_obj is None:
                        return None
                    if hasattr(trace_obj, "eClass"):
                        return _get_xmi_id(trace_obj)
                    if isinstance(trace_obj, str):
                        target = id_index.get(trace_obj)
                        if target is not None:
                            return _get_xmi_id(target)
                    return None

                be_name = _trace_name(be_trace)
                if be_name:
                    _ensure_annotation(elem, "businessElementName", be_name)
                be_id = _trace_id(be_trace)
                if be_id:
                    _ensure_annotation(elem, "businessElementId", be_id)
                bc_name = _trace_name(bc_trace)
                if bc_name:
                    _ensure_annotation(elem, "businessComponentName", bc_name)
                bc_id = _trace_id(bc_trace)
                if bc_id:
                    _ensure_annotation(elem, "businessComponentId", bc_id)
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
            if verbose:
                LOGGER.info("xsd=%s kind=%s status=annotated", lookup_name, kind)

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
