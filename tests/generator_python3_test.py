from pathlib import Path

import pytest
import astor

from json_codegen import load_schema
from json_codegen.astlib import python as ast
from json_codegen.generators.python3 import Python3Generator


SCHEMAS_DIR = Path(__file__).parent / "fixtures" / "schemas"
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "python3"


test_params = sorted(pytest.param(f, id=f.name) for f in SCHEMAS_DIR.glob("*.schema.json"))


@pytest.mark.parametrize("schema_filename", test_params)
@pytest.mark.parametrize("code_getter", [lambda g: g.as_ast(), lambda g: ast.parse(g.as_code())])
def test_generate(schema_filename, code_getter):
    fixture_filename = FIXTURES_DIR / (schema_filename.name.split(".")[0] + ".py")

    schema = load_schema(schema_filename.read_text())
    fixture = astor.parse_file(fixture_filename)

    generator = Python3Generator(schema)
    result = code_getter(generator)

    result_ast = astor.dump_tree(result)
    expected = astor.dump_tree(fixture)

    print(astor.to_source(result))

    assert result_ast == expected
