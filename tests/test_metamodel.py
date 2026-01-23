from emf_reader.loader import count_metamodel_classes, load_metamodel, summarize_metamodel


ECORE_PATH = "/var/software/input/ISO20022.ecore"


def test_load_metamodel():
    rset, packages = load_metamodel(ECORE_PATH)
    assert packages
    assert rset.metamodel_registry


def test_metamodel_summary_has_classes():
    _, packages = load_metamodel(ECORE_PATH)
    count = count_metamodel_classes(packages)
    assert count > 10


def test_dump_metamodel_without_instance():
    _, packages = load_metamodel(ECORE_PATH)
    summary = summarize_metamodel(packages)
    assert "Package:" in summary
    assert "Total classes" in summary
