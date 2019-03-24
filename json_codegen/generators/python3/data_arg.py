from json_codegen.astlib import python as ast
from json_codegen.types import DefinitionType, SchemaType, PropertyType


def get_value_from_data_arg(
    json_schema: SchemaType, key: str, property_: PropertyType, is_required: bool = False
) -> ast.AST:
    # Check additionalProperty
    additional_properties = property_.get("additionalProperties")

    if additional_properties is not None:
        if "$ref" not in additional_properties:
            raise NotImplementedError("Scalar types for additionalProperties not supported yet")

        return make_dict_comprehension(key, property_)

    # Check default or required
    if "default" in property_:
        value = make_default(key, property_)
    elif is_required:
        value = make_slice_key(key)
    else:
        value = make_get_key(key)

    # Wrap call to nested object
    property_type = property_["type"]

    if property_type == "array":
        # Wrap in list comprehension if array
        value = make_map(json_schema, property_, value)
    elif property_type == "object":
        value = make_coerce_to_obj(json_schema, property_, value)

    # Return value
    return value


def make_coerce_to_obj(
    json_schema: SchemaType, property_: PropertyType, value: ast.AST
) -> ast.AST:
    if "oneOf" in property_:
        ref = property_["oneOf"][0].get("$ref")

        if ref is not None:
            # Don't wrap if type is a primitive
            ref = json_schema.definitions[ref]

            if not json_schema.definition_is_primitive_alias(ref):
                ref_title = ref["title"]

                value = ast.IfExp(
                    test=ast.Compare(
                        left=value, ops=[ast.Is()], comparators=[ast.NameConstant(value=None)]
                    ),
                    body=ast.NameConstant(value=None),
                    orelse=ast.Call(func=ast.Name(id=ref_title), args=[value], keywords=[]),
                )

    return value


def make_map(json_schema: SchemaType, property_: PropertyType, value: ast.AST) -> ast.ListComp:
    """
    If array has `items` as 'object' type with `$ref`
    wrap it into a list comprehension and map array's elements
    """
    # Exit early if doesn't needs to wrap
    items = property_.get("items")

    if isinstance(items, dict):
        one_of = items.get("oneOf")
        ref = one_of[0]["$ref"] if one_of else None
    elif isinstance(items, list):
        raise NotImplementedError("Tuple for 'array' non supported: {}".format(property_))
    else:
        ref = None

    if property_.get("type") != "array" or ref is None:
        return value

    # Don't wrap if type is a primitive
    ref = json_schema.definitions[ref]

    if json_schema.definition_is_primitive_alias(ref):
        return value

    # Wrap value
    ref_title = ref["title"]

    return ast.ListComp(
        elt=ast.Call(
            func=ast.Name(id=ref_title),
            args=[ast.Name(id="v")],
            keywords=[],
            starargs=None,
            kwargs=None,
        ),
        generators=[ast.comprehension(target=ast.Name(id="v"), iter=value, ifs=[], is_async=0)],
    )


def make_slice_key(key: str) -> ast.Subscript:
    return ast.Subscript(value=ast.Name(id="data"), slice=ast.Index(value=ast.Str(s=key)))


def make_dict_comprehension(key: str, property_: PropertyType) -> ast.DictComp:
    # key, value
    comp_key = ast.Name(id="k")
    comp_value = ast.Call(
        func=ast.Name(id="Value"), args=[ast.Name(id="v")], keywords=[], starargs=None, kwargs=None
    )

    # Generator
    generator = ast.comprehension(
        target=ast.Tuple(elts=[ast.Name(id="k"), ast.Name(id="v")]),
        iter=ast.Call(
            func=ast.Attribute(value=make_default(key, property_), attr="iteritems"),
            args=[],
            keywords=[],
            starargs=None,
            kwargs=None,
        ),
        ifs=[],
        is_async=0,
    )

    # Dit comprehension
    dict_comp = ast.DictComp(key=comp_key, value=comp_value, generators=[generator])

    # Return node
    return dict_comp


def make_default(name: str, definition: DefinitionType) -> ast.IfExp:
    def ast_from_dict(d):
        keys = []
        values = []

        for k, v in d.items():
            keys.append(ast.Str(s=k))
            values.append(ast.Num(n=v))

        return ast.Dict(keys=keys, values=values)

    # Get compare's body
    type_ = definition.get("type")

    if type_ == "integer":
        body = ast.Num(n=definition["default"])
    elif type_ == "array":
        body = ast.List(elts=[ast.Num(n=n) for n in definition["default"]])
    elif type_ == "boolean":
        body = ast.NameConstant(value=definition["default"])
    elif type_ == "string":
        body = ast.Str(s=definition["default"])
    elif type_ == "object":
        body = ast_from_dict(definition["default"])
    else:
        raise NotImplementedError("{} => {}".format(name, definition))

    # Return ternary expression
    test = ast.Compare(
        left=make_get_key(name), ops=[ast.Is()], comparators=[ast.NameConstant(value=None)]
    )
    orelse = make_get_key(name)

    return ast.IfExp(test=test, body=body, orelse=orelse)


def make_get_key(key: str) -> ast.Call:
    return ast.Call(
        func=ast.Attribute(value=ast.Name(id="data"), attr="get"),
        args=[ast.Str(s=key)],
        keywords=[],
        starargs=None,
        kwargs=None,
    )
