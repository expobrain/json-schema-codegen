from __future__ import unicode_literals, print_function, division

import json


def File(program=None, comments=[]):
    return {"type": "File", "program": program, "comments": comments or []}


def Program(source_type="module", body=None, directives=None):
    return {
        "type": "Program",
        "sourceType": source_type,
        "body": body or [],
        "directives": directives or [],
    }


def ExportNamedDeclaration(specifiers=None, source=None, declaration=None, export_kind="value"):
    return {
        "type": "ExportNamedDeclaration",
        "specifiers": specifiers or [],
        "source": source,
        "declaration": declaration,
        "exportKind": export_kind,
    }


def ClassDeclaration(id_=None, super_class=None, body=None):
    return {"type": "ClassDeclaration", "id": id_, "superClass": super_class, "body": body}


def Identifier(name, type_annotation=None):
    node = {"type": "Identifier", "name": name}

    if type_annotation is not None:
        node["typeAnnotation"] = type_annotation

    return node


def ClassBody(body=None):
    return {"type": "ClassBody", "body": body or []}


def BlockStatement(body=None, directives=None):
    return {"type": "BlockStatement", "body": body or [], "directives": directives or []}


def ClassMethod(
    static=False,
    key=None,
    computed=False,
    kind="method",
    id_=None,
    generator=False,
    async_=False,
    params=None,
    body=None,
):
    return {
        "type": "ClassMethod",
        "static": static,
        "key": key,
        "computed": computed,
        "kind": kind,
        "id": id_,
        "generator": generator,
        "async": async_,
        "params": params or [],
        "body": body or [],
    }


def ClassProperty(
    static=False, key=None, computed=False, variance=None, typeAnnotation=None, value=None
):
    return {
        "type": "ClassProperty",
        "static": static,
        "key": key,
        "computed": computed,
        "variance": variance,
        "typeAnnotation": typeAnnotation,
        "value": value,
    }


def TypeAnnotation(type_annotation):
    return {"type": "TypeAnnotation", "typeAnnotation": type_annotation}


def NumberTypeAnnotation():
    return {"type": "NumberTypeAnnotation"}


def AnyTypeAnnotation():
    return {"type": "AnyTypeAnnotation"}


def StringTypeAnnotation():
    return {"type": "StringTypeAnnotation"}


def NullableTypeAnnotation(type_annotation):
    return {"type": "NullableTypeAnnotation", "typeAnnotation": type_annotation}


def GenericTypeAnnotation(id_, type_parameters=None):
    return {"type": "GenericTypeAnnotation", "id": id_, "typeParameters": type_parameters}


def AssignmentPattern(left, right):
    return {"type": "AssignmentPattern", "left": left, "right": right}


def ObjectExpression(properties=None):
    return {"type": "ObjectExpression", "properties": properties or []}


def ExpressionStatement(expression):
    return {"type": "ExpressionStatement", "expression": expression}


def AssignmentExpression(left, right, operator="="):
    return {"type": "AssignmentExpression", "operator": operator, "left": left, "right": right}


def MemberExpression(object_, property_, computed=False):
    return {
        "type": "MemberExpression",
        "object": object_,
        "property": property_,
        "computed": computed,
    }


def ThisExpression():
    return {"type": "ThisExpression"}


def ConditionalExpression(test, consequent, alternate):
    return {
        "type": "ConditionalExpression",
        "test": test,
        "consequent": consequent,
        "alternate": alternate,
    }


def NumericLiteral(value):
    return {
        "type": "NumericLiteral",
        "value": value,
        "extra": {"rawValue": value, "raw": json.dumps(value)},
    }


def CallExpression(callee, arguments):
    return {"type": "CallExpression", "callee": callee, "arguments": arguments}


def TypeParameterInstantiation(params):
    return {"type": "TypeParameterInstantiation", "params": params}


def ExistsTypeAnnotation():
    return {"type": "ExistsTypeAnnotation"}


def BooleanTypeAnnotation():
    return {"type": "BooleanTypeAnnotation"}


def ArrayExpression(elements=None):
    return {"type": "ArrayExpression", "elements": elements or []}


def BinaryExpression(left, right, operator="==="):
    return {"type": "BinaryExpression", "left": left, "right": right, "operator": operator}


def UnaryExpression(operator=None, prefix=True, argument=None, extra=None):
    return {
        "type": "UnaryExpression",
        "operator": operator,
        "prefix": prefix,
        "argument": argument,
        "extra": dict({"parenthesizedArgument": False}, **(extra or {})),
    }


def StringLiteral(value):
    return {
        "type": "StringLiteral",
        "value": value,
        "extra": {"rawValue": value, "raw": json.dumps(value)},
    }


def BooleanLiteral(value):
    return {"type": "BooleanLiteral", "value": value}


def LogicalExpression(left, right, operator="&&"):
    return {"type": "LogicalExpression", "left": left, "right": right, "operator": operator}


def NullLiteral():
    return {"type": "NullLiteral"}


def ObjectProperty(key, value, method=False, computed=False, shorthand=False):
    return {
        "type": "ObjectProperty",
        "key": key,
        "value": value,
        "method": method,
        "computed": computed,
        "shorthand": shorthand,
    }


def ArrowFunctionExpression(params=None, body=None, id=None, generator=False, async=False):
    return {
        "type": "ArrowFunctionExpression",
        "params": params or [],
        "body": body or [],
        "id": id,
        "generator": generator,
        "async": async,
    }


def DeclareTypeAlias(id_, right, type_parameters=None):
    return {
        "type": "DeclareTypeAlias",
        "id": id_,
        "right": right,
        "typeParameters": type_parameters,
    }


def ObjectTypeAnnotation(properties, call_properties=None, indexers=None, exact=False):
    return {
        "type": "ObjectTypeAnnotation",
        "properties": properties,
        "callProperties": call_properties or [],
        "indexers": indexers or [],
        "exact": exact,
    }


def ObjectTypeProperty(
    key,
    value,
    static=False,
    kind="init",
    method=False,
    variance=None,
    optional=False,
    force_variance=False,
):
    node = {
        "type": "ObjectTypeProperty",
        "key": key,
        "value": value,
        "static": static,
        "kind": kind,
        "method": method,
        "optional": optional,
    }

    # This is necessary because the generated AST from babylon
    # includes the `variance` key only in some cases
    if force_variance or variance:
        node["variance"] = variance

    return node


def FunctionTypeAnnotation(params=None, rest=None, type_parameters=None, return_type=None):
    return {
        "type": "FunctionTypeAnnotation",
        "params": params or [],
        "rest": rest,
        "typeParameters": type_parameters,
        "returnType": return_type,
    }


def FunctionTypeParam(name, optional=False, type_annotation=None):
    return {
        "type": "FunctionTypeParam",
        "name": name,
        "optional": optional,
        "typeAnnotation": type_annotation,
    }


def VoidTypeAnnotation():
    return {"type": "VoidTypeAnnotation"}


def UnionTypeAnnotation(types):
    return {"type": "UnionTypeAnnotation", "types": types}
