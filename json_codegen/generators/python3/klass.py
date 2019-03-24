from json_codegen.astlib import python as ast
from json_codegen.types import DefinitionType, SchemaType, PropertiesType, RequiredType
from json_codegen.generators.python3.annotations import make_annotation
from json_codegen.generators.python3.data_arg import get_value_from_data_arg


def make_klass(json_schema: SchemaType, definition: DefinitionType) -> ast.ClassDef:
    # Build class properties
    class_body = []
    properties = definition.get("properties")

    if properties:
        required = definition.get("required", [])

        class_body.append(make_klass_constructor(json_schema, properties, required))
    else:
        class_body.append(ast.Pass())

    # Create class definition
    class_def = ast.ClassDef(
        name=definition["title"], bases=[], body=class_body, decorator_list=[], keywords=[]
    )

    # Add to module's body
    return class_def


def make_klass_constructor(
    json_schema: SchemaType, properties: PropertiesType, required: RequiredType
) -> ast.FunctionDef:
    # Prepare body
    body = []

    # Default value for `data` argument
    if len(properties) > 0:
        body.append(
            ast.Assign(
                targets=[ast.Name(id="data")],
                value=ast.BoolOp(
                    op=ast.Or(), values=[ast.Name(id="data"), ast.Dict(keys=[], values=[])]
                ),
            )
        )

    for key in sorted(properties.keys()):
        # Get default value
        is_required = key in required
        property_ = properties[key]

        annotation = make_annotation(json_schema, property_, is_required=is_required)
        value = get_value_from_data_arg(json_schema, key, property_, is_required=is_required)

        # Build assign expression
        attribute = ast.AnnAssign(
            target=ast.Attribute(value=ast.Name(id="self"), attr=key),
            annotation=annotation,
            value=value,
            simple=0,
        )

        # Add to body
        body.append(attribute)

    # Bundle function arguments and keywords
    fn_arguments = ast.arguments(
        args=[
            ast.arg(arg="self", annotation=None),
            ast.arg(
                arg="data",
                annotation=ast.Subscript(
                    value=ast.Name(id="Optional"), slice=ast.Index(value=ast.Name(id="Dict"))
                ),
            ),
        ],
        vararg=None,
        kwarg=None,
        kwonlyargs=[],
        kw_defaults=[],
        defaults=[ast.NameConstant(value=None)],
    )

    # Generate class constructor
    fn_init = ast.FunctionDef(
        name="__init__", args=fn_arguments, body=body, decorator_list=[], returns=None
    )

    # Return constructor
    return fn_init
