from json_codegen.astlib import python as ast
from json_codegen.types import SchemaType, PropertyType


PYTHON_ANNOTATION_MAP = {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}


def make_annotation(
    json_schema: SchemaType, property_: PropertyType, is_required: bool = False
) -> ast.AST:
    annotation = resolve_annotation(json_schema, property_)

    # Make annotation optional if no default value
    if not is_required and "default" not in property_:
        annotation = ast.Subscript(
            value=ast.Name(id="Optional"), slice=ast.Index(value=annotation)
        )

    # Return
    return annotation


def resolve_annotation(json_schema: SchemaType, property_: PropertyType) -> ast.AST:
    # Map property type to annotation
    property_type = property_["type"]

    # ...map object
    if property_type == "object":
        if "oneOf" in property_:
            ref = json_schema.definitions[property_["oneOf"][0]["$ref"]]

            if json_schema.definition_is_primitive_alias(ref):
                annotation = resolve_annotation(ref)
            else:
                annotation = ast.Name(id=ref["title"])
        elif "additionalProperties" in property_:
            object_name = json_schema.definitions[property_["additionalProperties"]["$ref"]][
                "title"
            ]

            annotation = ast.Subscript(
                value=ast.Name(id="Dict"),
                slice=ast.Index(
                    value=ast.Tuple(elts=[ast.Name(id="str"), ast.Name(id=object_name)])
                ),
            )
        else:
            annotation = ast.Name(id="Dict")

    # ... map array
    elif property_type == "array":
        items = property_.get("items")

        if isinstance(items, dict):

            item_annotation = resolve_annotation(items)
        elif isinstance(items, list):
            raise NotImplementedError("Tuple for 'array' is not supported: {}".format(property_))
        else:
            item_annotation = ast.Name(id="Any")

        annotation = ast.Subscript(
            value=ast.Name(id="List"), slice=ast.Index(value=item_annotation)
        )

    # ... map scalar
    else:
        python_type = PYTHON_ANNOTATION_MAP[property_["type"]]

        annotation = ast.Name(id=python_type)

    # Return
    return annotation
