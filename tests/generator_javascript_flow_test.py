import json
from pathlib import Path

import astor
import pytest

from json_codegen import load_schema
from json_codegen.generators.javascript_flow import JavaScriptFlowGenerator

SCHEMAS_DIR = Path(__file__).parent / "fixtures" / "schemas"
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "javascript_flow"

test_params = sorted(pytest.param(f, id=f.name) for f in SCHEMAS_DIR.glob("*.schema.json"))


def load_fixture(name):
    filename = FIXTURES_DIR / (name + ".ast.json")

    return astor.parse_file(filename)


@pytest.mark.parametrize("schema_filename", (test_params))
def test_generate(schema_filename):
    fixture_filename = FIXTURES_DIR / (schema_filename.name.split(".")[0] + ".ast.json")

    schema = load_schema(schema_filename.read_text())

    generator = JavaScriptFlowGenerator(schema)
    result = generator.generate().as_ast()

    expected = json.loads(fixture_filename.read_text())

    assert result == expected
