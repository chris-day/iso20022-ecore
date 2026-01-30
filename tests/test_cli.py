import os
from pathlib import Path

import pytest

from emf_reader import cli as emf_cli
from emf_reader import xsd_enrich_cli

ECORE = "/var/software/input/ISO20022.ecore"
INSTANCE = "/var/software/input/20250424_ISO20022_2013_eRepository.iso20022"
XSD = "auth.016.001.03.xsd"


def _skip_if_missing(*paths: str):
    missing = [p for p in paths if not Path(p).exists()]
    if missing:
        pytest.skip(f"missing required files: {missing}")


def test_cli_dump_metamodel_json(tmp_path):
    _skip_if_missing(ECORE)
    out = tmp_path / "metamodel.json"
    code = emf_cli.main([
        "--ecore",
        ECORE,
        "--dump-metamodel-json",
        str(out),
    ])
    assert code == 0
    assert out.exists()
    assert out.stat().st_size > 0


def test_cli_dump_model_json(tmp_path):
    _skip_if_missing(ECORE, INSTANCE)
    out = tmp_path / "model.json"
    code = emf_cli.main([
        "--ecore",
        ECORE,
        "--instance",
        INSTANCE,
        "--dump-model-json",
        str(out),
    ])
    assert code == 0
    assert out.exists()
    assert out.stat().st_size > 0


def test_xsd_enrich_trace(tmp_path):
    _skip_if_missing(ECORE, INSTANCE, XSD)
    out = tmp_path / "enriched.xsd"
    code = xsd_enrich_cli.main([
        "--ecore",
        ECORE,
        "--instance",
        INSTANCE,
        "--xsd",
        XSD,
        "--output",
        str(out),
        "--trace-name",
        "UnderlyingIdentification2Choice",
    ])
    assert code == 0
    assert out.exists()
    assert out.stat().st_size > 0
