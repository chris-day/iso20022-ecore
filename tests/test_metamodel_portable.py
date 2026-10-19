"""Metamodel checks that do not require external ISO 20022 input files."""
import json

from emf_reader.cli import main
from emf_reader.loader import count_metamodel_classes, load_metamodel, summarize_metamodel


def test_generated_metamodel_and_cli(tmp_path, capsys):
    path = tmp_path / "example.ecore"
    classes = "".join(
        f'<eClassifiers xsi:type="ecore:EClass" name="Example{i}"/>'
        for i in range(12)
    )
    path.write_text(
        '<ecore:EPackage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:ecore="http://www.eclipse.org/emf/2002/Ecore" '
        'name="example" nsURI="urn:example:test" nsPrefix="example">'
        + classes + '</ecore:EPackage>',
        encoding="utf-8",
    )
    rset, packages = load_metamodel(str(path))
    assert rset.metamodel_registry["urn:example:test"] is packages[0]
    assert count_metamodel_classes(packages) == 12
    assert "Total classes" in summarize_metamodel(packages)

    out = tmp_path / "metamodel.json"
    assert main([
        "--ecore", str(path), "--dump-metamodel", "--dump-metamodel-json", str(out)
    ]) == 0
    assert "Package:" in capsys.readouterr().out
    assert json.loads(out.read_text())["total_classes"] == 12
