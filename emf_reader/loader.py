from __future__ import annotations

import logging
from typing import Iterable, List, Tuple

from pyecore.ecore import EPackage
from pyecore.resources import ResourceSet, URI
from pyecore.resources.xmi import XMIResource

LOGGER = logging.getLogger(__name__)


def _configure_resource_set() -> ResourceSet:
    rset = ResourceSet()
    rset.resource_factory["ecore"] = XMIResource
    rset.resource_factory["xmi"] = XMIResource
    rset.resource_factory["xml"] = XMIResource
    rset.resource_factory["iso20022"] = XMIResource
    rset.resource_factory[None] = XMIResource
    return rset


def _iter_packages(pkgs: Iterable[EPackage]) -> Iterable[EPackage]:
    for pkg in pkgs:
        yield pkg
        for sub in pkg.eSubpackages:
            yield from _iter_packages([sub])


def load_metamodel(ecore_path: str, rset: ResourceSet | None = None) -> Tuple[ResourceSet, List[EPackage]]:
    if rset is None:
        rset = _configure_resource_set()
    LOGGER.info("Loading metamodel: %s", ecore_path)
    resource = rset.get_resource(URI(ecore_path))
    packages = [obj for obj in resource.contents if isinstance(obj, EPackage)]
    if not packages:
        raise ValueError(f"No EPackage found in metamodel: {ecore_path}")
    for pkg in _iter_packages(packages):
        if pkg.nsURI:
            rset.metamodel_registry[pkg.nsURI] = pkg
    return rset, packages


def load_instance(instance_path: str, rset: ResourceSet) -> XMIResource:
    LOGGER.info("Loading instance: %s", instance_path)
    resource = rset.get_resource(URI(instance_path))
    return resource


def _all_classifiers(pkg: EPackage):
    return list(pkg.eClassifiers)


def _all_features(cls, name: str):
    attr = getattr(cls, name, [])
    return attr() if callable(attr) else list(attr)


def count_metamodel_classes(packages: Iterable[EPackage]) -> int:
    total_classes = 0
    for pkg in packages:
        for cls in _all_classifiers(pkg):
            if cls.eClass.name == "EClass":
                total_classes += 1
    return total_classes


def metamodel_stats(packages: Iterable[EPackage]) -> dict[str, int]:
    class_count = 0
    attr_count = 0
    ref_count = 0
    pkg_count = 0
    for pkg in packages:
        pkg_count += 1
        for cls in _all_classifiers(pkg):
            if cls.eClass.name != "EClass":
                continue
            class_count += 1
            attr_count += len(_all_features(cls, "eAllAttributes"))
            ref_count += len(_all_features(cls, "eAllReferences"))
    return {
        "packages": pkg_count,
        "classes": class_count,
        "attributes": attr_count,
        "references": ref_count,
    }


def summarize_metamodel(packages: Iterable[EPackage]) -> str:
    lines: List[str] = []
    total_classes = 0
    for pkg in packages:
        lines.append(f"Package: {pkg.name} nsURI={pkg.nsURI}")
        for cls in _all_classifiers(pkg):
            if cls.eClass.name != "EClass":
                continue
            total_classes += 1
            attrs = [a.name for a in _all_features(cls, "eAllAttributes")]
            refs = [r.name for r in _all_features(cls, "eAllReferences")]
            lines.append(f"  Class: {cls.name} attrs={len(attrs)} refs={len(refs)}")
    lines.append(f"Total classes: {total_classes}")
    return "\n".join(lines)


def summarize_instances(resources: Iterable[XMIResource]) -> str:
    roots = [obj for res in resources for obj in res.contents]
    lines = [f"Root objects: {len(roots)}"]
    for idx, obj in enumerate(roots):
        lines.append(f"  [{idx}] {obj.eClass.name}")
    return "\n".join(lines)


def instance_stats(resources: Iterable[XMIResource]) -> dict[str, int]:
    roots = [obj for res in resources for obj in res.contents]
    return {"roots": len(roots)}
