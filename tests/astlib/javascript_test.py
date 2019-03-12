import pytest

from json_codegen.astlib.javascript import (
    Identifier,
    CommentLine,
    AnyTypeAnnotation,
    ObjectTypeProperty,
    TypeCastExpression,
    UnaryExpression,
    NumericLiteral,
    StringLiteral,
)


@pytest.mark.parametrize(
    "name, type_annotation_value, expected",
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
def test_Identifier(name, type_annotation_value, expected):
    result = Identifier(name, type_annotation_value=type_annotation_value)

    assert result.as_dict() == expected


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

    assert result.as_dict() == expected


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

    assert result.as_dict() == expected


@pytest.mark.parametrize(
    "expression, type_annotation, extra_value, expected",
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
def test_TypeCastExpression(expression, type_annotation, extra_value, expected):
    result = TypeCastExpression(expression, type_annotation, extra_value=extra_value)

    assert result.as_dict() == expected


@pytest.mark.parametrize(
    "extra_value, expected",
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
def test_UnaryExpression(extra_value, expected):
    result = UnaryExpression(extra_value=extra_value)

    assert result.as_dict() == expected


@pytest.mark.parametrize(
    "value, expected",
    [[42, {"type": "NumericLiteral", "value": 42, "extra": {"rawValue": 42, "raw": "42"}}]],
)
def test_NumericLiteral(value, expected):
    result = NumericLiteral(value)

    assert result.as_dict() == expected


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

    assert result.as_dict() == expected
