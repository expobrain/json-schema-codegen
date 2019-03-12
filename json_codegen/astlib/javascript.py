from typing import List, Optional, Any, Dict
import dataclasses
import json

import strcase


def as_dict(obj):
    def camel_case_dict(items):
        return {strcase.to_lower_camel(k): v for k, v in items}

    return dataclasses.asdict(obj, dict_factory=camel_case_dict)


@dataclasses.dataclass(frozen=True, init=False, eq=False, repr=False)
class AST:
    """
    Base class to derive all other AST nodes.

    Used only for typing.
    """

    pass


@dataclasses.dataclass
class File(AST):
    type: str = dataclasses.field(init=False, default="File")
    program: AST = None
    comments: List[AST] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Program(AST):
    type: str = dataclasses.field(init=False, default="Program")
    source_type: str = "module"
    body: List[AST] = dataclasses.field(default_factory=list)
    directives: List[AST] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ExportNamedDeclaration(AST):
    type: str = dataclasses.field(init=False, default="ExportNamedDeclaration")
    specifiers: List[AST] = dataclasses.field(default_factory=list)
    source: Optional[AST] = None
    declaration: Optional[AST] = None
    export_kind: str = "value"


@dataclasses.dataclass
class ClassDeclaration(AST):
    type: str = dataclasses.field(init=False, default="ClassDeclaration")
    id: Optional[AST] = None
    super_class: Optional[AST] = None
    body: Optional[AST] = None


@dataclasses.dataclass
class Identifier(AST):
    type: str = dataclasses.field(init=False, default="Identifier")
    name: Optional[AST] = None
    type_annotation_value: dataclasses.InitVar[Optional[AST]] = None

    def __post_init__(self, type_annotation_value):
        if type_annotation_value:
            self.type_annotation = type_annotation_value

    def as_dict(self):
        d = super().as_dict()

        if hasattr(self, "type_annotation"):
            type_annotation = self.type_annotation
            d["typeAnnotation"] = type_annotation.as_dict() if type_annotation else None

        return d


@dataclasses.dataclass
class ClassBody(AST):
    type: str = dataclasses.field(init=False, default="ClassBody")
    body: List[AST] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class BlockStatement(AST):
    type: str = dataclasses.field(init=False, default="BlockStatement")
    body: List[AST] = dataclasses.field(default_factory=list)
    directives: List[AST] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ClassMethod(AST):
    type: str = dataclasses.field(init=False, default="ClassMethod")
    static: Optional[AST] = None
    key: Optional[AST] = None
    computed: bool = False
    kind: str = "method"
    generator: bool = False
    async_: bool = False
    params: List[AST] = dataclasses.field(default_factory=list)
    body: List[AST] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ClassProperty(AST):
    type: str = dataclasses.field(init=False, default="ClassProperty")
    static: Optional[AST] = None
    key: Optional[AST] = None
    computed: bool = False
    variance: Optional[AST] = None
    type_annotation: Optional[AST] = None
    value: Optional[AST] = None


@dataclasses.dataclass
class TypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="TypeAnnotation")
    type_annotation: Optional[AST] = None


@dataclasses.dataclass
class NumberTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="NumberTypeAnnotation")


@dataclasses.dataclass
class AnyTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="AnyTypeAnnotation")


@dataclasses.dataclass
class StringTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="StringTypeAnnotation")


@dataclasses.dataclass
class NullableTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="NullableTypeAnnotation")
    type_annotation: AST


@dataclasses.dataclass
class GenericTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="GenericTypeAnnotation")
    id: Optional[AST] = None
    type_parameters: Optional[AST] = None


@dataclasses.dataclass
class AssignmentPattern(AST):
    type: str = dataclasses.field(init=False, default="AssignmentPattern")
    left: AST
    right: AST


@dataclasses.dataclass
class ObjectExpression(AST):
    type: str = dataclasses.field(init=False, default="ObjectExpression")
    properties: str = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ExpressionStatement(AST):
    type: str = dataclasses.field(init=False, default="ExpressionStatement")
    expression: AST


@dataclasses.dataclass
class AssignmentExpression(AST):
    type: str = dataclasses.field(init=False, default="AssignmentExpression")
    left: AST
    right: AST
    operator: str = "="


@dataclasses.dataclass
class MemberExpression(AST):
    type: str = dataclasses.field(init=False, default="MemberExpression")
    object_: AST
    property_: AST
    computed: bool = False


@dataclasses.dataclass
class ThisExpression(AST):
    type: str = dataclasses.field(init=False, default="ThisExpression")


@dataclasses.dataclass
class ConditionalExpression(AST):
    type: str = dataclasses.field(init=False, default="ConditionalExpression")
    test: AST
    consequent: AST
    alternate: AST


@dataclasses.dataclass
class NumericLiteral(AST):
    type: str = dataclasses.field(init=False, default="NumericLiteral")
    value: Any
    extra: Dict = dataclasses.field(init=False)

    def __post_init__(self):
        self.extra = {"rawValue": self.value, "raw": json.dumps(self.value)}

    # def __call__(self, value):
    #     return {
    #         "type": "NumericLiteral",
    #         "value": value,
    #         "extra": {"rawValue": value, "raw": json.dumps(value)},
    #     }


@dataclasses.dataclass
class CallExpression(AST):
    type: str = dataclasses.field(init=False, default="CallExpression")
    callee: AST
    arguments: List[AST]


@dataclasses.dataclass
class TypeParameterInstantiation(AST):

    type: str = dataclasses.field(init=False, default="TypeParameterInstantiation")
    params: List[AST]


@dataclasses.dataclass
class ExistsTypeAnnotation(AST):

    type: str = dataclasses.field(init=False, default="ExistsTypeAnnotation")


@dataclasses.dataclass
class BooleanTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="BooleanTypeAnnotation")


@dataclasses.dataclass
class ArrayExpression(AST):
    type: str = dataclasses.field(init=False, default="ArrayExpression")
    elements: List[AST] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class BinaryExpression(AST):
    type: str = dataclasses.field(init=False, default="BinaryExpression")
    left: AST
    right: AST
    operator: str = "==="


@dataclasses.dataclass
class UnaryExpression(AST):
    type: str = dataclasses.field(init=False, default="UnaryExpression")
    operator: Optional[AST] = None
    prefix: bool = True
    argument: Optional[AST] = None
    extra: Dict = dataclasses.field(init=False)
    extra_value: dataclasses.InitVar[Optional[Dict]] = None

    def __post_init__(self, extra_value):
        self.extra = dict({"parenthesizedArgument": False}, **(extra_value or {}))


@dataclasses.dataclass
class StringLiteral(AST):
    type: str = dataclasses.field(init=False, default="StringLiteral")
    value: str
    extra: Dict = dataclasses.field(init=False)

    def __post_init__(self):
        self.extra = {"rawValue": self.value, "raw": json.dumps(self.value)}


@dataclasses.dataclass
class BooleanLiteral(AST):
    type: str = dataclasses.field(init=False, default="BooleanLiteral")
    value: bool


@dataclasses.dataclass
class LogicalExpression(AST):
    type: str = dataclasses.field(init=False, default="LogicalExpression")
    left: AST
    right: AST
    operator: str = "&&"


@dataclasses.dataclass
class NullLiteral(AST):
    type: str = dataclasses.field(init=False, default="NullLiteral")


@dataclasses.dataclass
class ObjectProperty(AST):
    type: str = dataclasses.field(init=False, default="ObjectProperty")
    key: AST
    value: AST
    method: bool = False
    computed: bool = False
    shorthand: bool = False


@dataclasses.dataclass
class ArrowFunctionExpression(AST):
    type: str = dataclasses.field(init=False, default="ArrowFunctionExpression")
    params: List[AST] = dataclasses.field(default_factory=list)
    body: List[AST] = dataclasses.field(default_factory=list)
    id: Optional[AST] = None
    generator: bool = False
    async_: bool = False


@dataclasses.dataclass
class DeclareTypeAlias(AST):
    type: str = dataclasses.field(init=False, default="DeclareTypeAlias")
    id: AST
    right: AST
    type_parameters: Optional[AST] = None
    # leadingComments: List[AST] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ObjectTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="ObjectTypeAnnotation")
    properties: List[AST]
    call_properties: List[AST] = dataclasses.field(default_factory=list)
    indexers: List[AST] = dataclasses.field(default_factory=list)
    exact: bool = False


@dataclasses.dataclass
class ObjectTypeProperty(AST):
    type: str = dataclasses.field(init=False, default="ObjectTypeProperty")
    key: AST
    value: AST
    static: bool = False
    kind: str = "init"
    method: bool = False
    optional: bool = False
    variance_value: dataclasses.InitVar[Optional[AST]] = None
    force_variance: dataclasses.InitVar[bool] = False

    def __post_init__(self, variance_value, force_variance):
        if variance_value or force_variance:
            self.variance = variance_value

    def as_dict(self):
        d = super().as_dict()

        if hasattr(self, "variance"):
            variance = self.variance
            d["variance"] = variance.as_dict() if variance else None

        return d


@dataclasses.dataclass
class FunctionTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="FunctionTypeAnnotation")
    params: List[AST] = dataclasses.field(default_factory=list)
    rest: Optional[AST] = None
    type_parameters: Optional[AST] = None
    return_type: Optional[AST] = None


@dataclasses.dataclass
class FunctionTypeParam(AST):
    type: str = dataclasses.field(init=False, default="FunctionTypeParam")
    name: AST
    optional: bool = False
    type_annotation: Optional[AST] = None


@dataclasses.dataclass
class VoidTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="VoidTypeAnnotation")


@dataclasses.dataclass
class UnionTypeAnnotation(AST):
    type: str = dataclasses.field(init=False, default="UnionTypeAnnotation")
    types: AST


@dataclasses.dataclass
class CommentLine(AST):
    type: str = dataclasses.field(init=False, default="CommentLine")
    value: str

    def __post_init__(self):
        self.value = " " + str(self.value).strip()


@dataclasses.dataclass
class ObjectTypeIndexer(AST):
    type: str = dataclasses.field(init=False, default="ObjectTypeIndexer")
    id: AST
    key: AST
    value: AST
    static: bool = False
    variance: Optional[AST] = None


@dataclasses.dataclass
class VariableDeclaration(AST):
    type: str = dataclasses.field(init=False, default="VariableDeclaration")
    declarations: List[AST]
    kind: str = "const"


@dataclasses.dataclass
class VariableDeclarator(AST):
    type: str = dataclasses.field(init=False, default="VariableDeclarator")
    id: AST
    init: Optional[AST] = None


@dataclasses.dataclass
class ArrayPattern(AST):
    type: str = dataclasses.field(init=False, default="ArrayPattern")
    elements: List[AST]


@dataclasses.dataclass
class TypeCastExpression(AST):
    type: str = dataclasses.field(init=False, default="TypeCastExpression")
    expression: AST
    type_annotation: AST
    extra: Dict = dataclasses.field(init=False)
    extra_value: dataclasses.InitVar[Dict] = None

    def __post_init__(self, extra_value):
        self.extra = dict({"parenthesized": True}, **(extra_value or {}))


@dataclasses.dataclass
class NewExpression(AST):
    type: str = dataclasses.field(init=False, default="NewExpression")
    calle: AST
    arguments: List[AST] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ReturnStatement(AST):
    type: str = dataclasses.field(init=False, default="ReturnStatement")
    argument: AST
