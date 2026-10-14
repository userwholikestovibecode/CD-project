"""Abstract syntax tree nodes for the mini compiler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class ASTNode:
    line: int
    inferred_type: Optional[str] = field(default=None, init=False)


@dataclass
class Program(ASTNode):
    statements: list[Statement] = field(default_factory=list)


@dataclass
class VarDecl(ASTNode):
    name: str = ""
    var_type: str = "int"
    initializer: Optional[Expression] = None


@dataclass
class Assignment(ASTNode):
    name: str = ""
    expression: Expression | None = None


@dataclass
class PrintStmt(ASTNode):
    expression: Expression | None = None


@dataclass
class BinaryOp(ASTNode):
    operator: str = ""
    left: Expression | None = None
    right: Expression | None = None


@dataclass
class UnaryOp(ASTNode):
    operator: str = ""
    operand: Expression | None = None


@dataclass
class Literal(ASTNode):
    value: Union[int, float] = 0
    literal_type: str = "int"


@dataclass
class Identifier(ASTNode):
    name: str = ""


Statement = Union[VarDecl, Assignment, PrintStmt]
Expression = Union[BinaryOp, UnaryOp, Literal, Identifier]
