import pytest

from json_codegen.astlib.javascript import (
    AnyTypeAnnotation,
    CommentLine,
    Identifier,
    NumericLiteral,
    ObjectTypeProperty,
    StringLiteral,
    TypeCastExpression,
    UnaryExpression,
)


@pytest.mark.parametrize(
    "name, type_annotation, expected",
    [
        ["test", None, {"type": "Identifier", "name": "test"}],
        [
            "test",
            AnyTypeAnnotation(),
            {
                "type": "Identifier",
                "name": "test",
                "typeAnnotation": {"type": "AnyTypeAnnotation"},
            },
        ],
    ],
)
def test_Identifier(name, type_annotation, expected):
    result = Identifier(name, type_annotation=type_annotation)

    assert result == expected


@pytest.mark.parametrize(
    "key, value, force_variance, expected",
    [
        [
            Identifier("test"),
            AnyTypeAnnotation(),
            False,
            {
                "type": "ObjectTypeProperty",
                "key": {"type": "Identifier", "name": "test"},
                "value": {"type": "AnyTypeAnnotation"},
                "static": False,
                "kind": "init",
                "method": False,
                "optional": False,
            },
        ],
        [
            Identifier("test"),
            AnyTypeAnnotation(),
            True,
            {
                "type": "ObjectTypeProperty",
                "key": {"type": "Identifier", "name": "test"},
                "value": {"type": "AnyTypeAnnotation"},
                "static": False,
                "kind": "init",
                "method": False,
                "optional": False,
                "variance": None,
            },
        ],
    ],
)
def test_ObjectTypeProperty(key, value, force_variance, expected):
    result = ObjectTypeProperty(key, value, force_variance=force_variance)

    assert result == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ["my_comment", {"type": "CommentLine", "value": " my_comment"}],
        ["  my_comment", {"type": "CommentLine", "value": " my_comment"}],
        ["my_comment  ", {"type": "CommentLine", "value": " my_comment"}],
    ],
)
def test_CommentLine(value, expected):
    result = CommentLine(value)

    assert result == expected


@pytest.mark.parametrize(
    "expression, type_annotation, extra, expected",
    [
        [
            Identifier("test"),
            AnyTypeAnnotation(),
            None,
            {
                "type": "TypeCastExpression",
                "expression": {"type": "Identifier", "name": "test"},
                "typeAnnotation": {"type": "AnyTypeAnnotation"},
                "extra": {"parenthesized": True},
            },
        ]
    ],
)
def test_TypeCastExpression(expression, type_annotation, extra, expected):
    result = TypeCastExpression(expression, type_annotation, extra=extra)

    assert result == expected


@pytest.mark.parametrize(
    "extra, expected",
    [
        [
            None,
            {
                "type": "UnaryExpression",
                "operator": None,
                "prefix": True,
                "argument": None,
                "extra": {"parenthesizedArgument": False},
            },
        ]
    ],
)
def test_UnaryExpression(extra, expected):
    result = UnaryExpression(extra=extra)

    assert result == expected


@pytest.mark.parametrize(
    "value, expected",
    [[42, {"type": "NumericLiteral", "value": 42, "extra": {"rawValue": 42, "raw": "42"}}]],
)
def test_NumericLiteral(value, expected):
    result = NumericLiteral(value)

    assert result == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        [
            "test",
            {
                "type": "StringLiteral",
                "value": "test",
                "extra": {"rawValue": "test", "raw": '"test"'},
            },
        ]
    ],
)
def test_StringLiteral(value, expected):
    result = StringLiteral(value)

    assert result == expected
