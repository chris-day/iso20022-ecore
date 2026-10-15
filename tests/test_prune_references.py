import pytest
from lxml import etree
from pyecore.ecore import EClass, EPackage, EReference
from pyecore.resources import ResourceSet, URI
from pyecore.resources.xmi import XMIResource

from emf_reader.export import export_filtered_instance, _omit_export_references
from emf_reader.cli import build_parser


@pytest.mark.parametrize("defaults", [False, True])
def test_drop_reference_preserves_opposite_and_objects(tmp_path, defaults):
    component = EClass("BusinessComponent")
    end = EClass("BusinessAssociationEnd")
    package = EPackage("test", nsURI="urn:test", nsPrefix="test")
    package.eClassifiers.extend([component, end])
    domain = EReference("associationDomain", end, upper=-1)
    target = EReference("type", component, eOpposite=domain)
    component.eStructuralFeatures.append(domain)
    end.eStructuralFeatures.append(target)
    owner, association = component(), end()
    owner._internal_id, association._internal_id = "component-id", "end-id"
    association.type = owner
    rset = ResourceSet()
    rset.resource_factory["xmi"] = XMIResource
    source = rset.create_resource(URI(str(tmp_path / "source.xmi")))
    source.extend([owner, association])
    output = tmp_path / "pruned.xmi"
    export_filtered_instance(source, str(output), serialize_defaults=defaults,
                             drop_references={"associationDomain"})
    tree = etree.parse(str(output))
    assert not tree.xpath("//@associationDomain | //associationDomain")
    assert tree.xpath("//@type") == ["component-id"]
    assert len(tree.xpath("//@xmi:id", namespaces={"xmi": "http://www.omg.org/XMI"})) == 2
    assert association.type is owner
    assert association in owner.associationDomain
    assert domain in owner._isset


def test_suppression_restores_state_on_failure():
    cls = EClass("Node")
    ref = EReference("link", cls)
    cls.eStructuralFeatures.append(ref)
    obj = cls()
    obj.link = cls()
    original = obj._isset
    with pytest.raises(RuntimeError):
        with _omit_export_references([obj], {"link"}):
            assert ref not in obj._isset
            raise RuntimeError("save failed")
    assert obj._isset is original
    assert ref in obj._isset


def test_drop_refs_cli():
    args = build_parser().parse_args(["--ecore", "model.ecore", "--prune-drop-refs", "associationDomain"])
    assert args.prune_drop_refs == "associationDomain"
