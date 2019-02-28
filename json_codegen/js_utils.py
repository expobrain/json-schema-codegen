from json_codegen.astlib import javascript as ast


def get_object_type_annotation(definitions, property_):
    additionalProperties = property_.get("additionalProperties")

    if additionalProperties:
        return ast.ObjectTypeAnnotation(
            properties=[],
            indexers=[
                ast.ObjectTypeIndexer(
                    id_=ast.Identifier("key"),
                    key=ast.StringTypeAnnotation(),
                    value=get_type_annotation(definitions, additionalProperties, required=True),
                )
            ],
        )

    return ast.GenericTypeAnnotation(ast.Identifier("Object"))


def get_single_type_annotation(definitions, property_):
    # Parse type
    type_name = property_.get("type")
    ref_key = property_.get("$ref")

    if type_name is None and ref_key is None:
        return ast.AnyTypeAnnotation()
    elif type_name in ("integer", "number"):
        return ast.NumberTypeAnnotation()
    elif type_name == "string":
        return ast.StringTypeAnnotation()
    elif type_name == "boolean":
        return ast.BooleanTypeAnnotation()
    elif type_name == "object":
        return get_object_type_annotation(definitions, property_)
    elif type_name == "array":
        parameters = get_union_type_annotation(definitions, property_.get("items", []))

        if len(parameters) == 0:
            parameters = [ast.ExistsTypeAnnotation()]

        return ast.GenericTypeAnnotation(
            ast.Identifier("Array"), type_parameters=ast.TypeParameterInstantiation(parameters)
        )
    elif ref_key is not None:
        definition = definitions[ref_key]

        return ast.GenericTypeAnnotation(ast.Identifier(definition["title"]))

    # Nothing matches
    raise NotImplementedError("{}: {}".format(definitions, property_))


def get_union_type_annotation(definitions, types):
    return [get_single_type_annotation(definitions, t) for t in types]


def get_type_annotation(definitions, property_, required=False):
    # Check for oneOf
    if "oneOf" in property_:
        annotations = get_union_type_annotation(definitions, property_["oneOf"])

        if len(annotations) == 1:
            annotation = annotations[0]
        elif len(annotations) > 1:
            annotation = ast.UnionTypeAnnotation(annotations)
    else:
        annotation = get_single_type_annotation(definitions, property_)

    if not required:
        annotation = ast.NullableTypeAnnotation(annotation)

    return annotation
