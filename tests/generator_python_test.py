from __future__ import unicode_literals, print_function, division

import ast

from pathlib2 import Path
import pytest
import astor
import json


from generators import load_schema
from generators.python import PythonGenerator


SCHEMAS_DIR = Path(__file__).parent / "fixtures" / "schemas"
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "python"

expected_init_py = astor.dump_tree(ast.Module(body=[]))

test_params = sorted(pytest.param(f, id=f.name) for f in SCHEMAS_DIR.glob("*.schema.json"))


def load_fixture(name):
    filename = FIXTURES_DIR / (name + ".py")

    return astor.parse_file(str(filename))


@pytest.mark.parametrize("schema_filename", (test_params))
def test_generate(schema_filename):
    fixture_filename = FIXTURES_DIR / (schema_filename.name.split(".")[0] + ".py")

    schema = load_schema(schema_filename.read_text())
    fixture = astor.parse_file(str(fixture_filename))

    generator = PythonGenerator(schema)
    result = generator.generate().as_ast()

    result_ast = astor.dump_tree(result)
    expected = astor.dump_tree(fixture)

    print(result_ast)

    assert result_ast == expected
