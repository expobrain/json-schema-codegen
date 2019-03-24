from json_codegen.astlib import python as ast


def make_imports() -> ast.ImportFrom:
    return [
        ast.ImportFrom(
            module="typing",
            names=[
                ast.alias(name="Dict", asname=None),
                ast.alias(name="Optional", asname=None),
                ast.alias(name="List", asname=None),
                ast.alias(name="Any", asname=None),
            ],
            level=0,
        )
    ]
