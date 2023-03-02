import ast
import os
import warnings
from pathlib import Path

import astor
import pytest

from json_codegen import load_schema
from json_codegen.generators.python3_marshmallow import Python3MarshmallowGenerator

SCHEMAS_DIR = Path(__file__).parent / "fixtures" / "schemas"
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "python3_marshmallow"

expected_init_py = astor.dump_tree(ast.Module(body=[]))

test_params = sorted(pytest.param(f, id=f.name) for f in SCHEMAS_DIR.glob("*.schema.json"))


def load_fixture(name):
    filename = FIXTURES_DIR / (name + ".py")

    return astor.parse_file(filename)


@pytest.mark.parametrize("schema_filename", (test_params))
def test_generate(schema_filename):
    fixture_filename = FIXTURES_DIR / (schema_filename.name.split(".")[0] + ".py")

    schema = load_schema(schema_filename.read_text())

    try:
        fixture = astor.parse_file(fixture_filename)
    except FileNotFoundError:
        warnings.warn(
            f"Fixture not implemented yet: {os.path.basename(fixture_filename)}", stacklevel=2
        )
        return

    generator = Python3MarshmallowGenerator(schema)
    result = generator.generate().as_ast()

    result_ast = astor.dump_tree(result)
    expected = astor.dump_tree(fixture)

    print(astor.to_source(result))

    assert result_ast == expected
