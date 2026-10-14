"""Semantic checks and type annotation for the mini compiler AST."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .ast_nodes import Assignment, BinaryOp, Expression, Identifier, Literal, PrintStmt, Program, UnaryOp, VarDecl
from .symbol_table import SymbolTable


@dataclass(frozen=True)
class Diagnostic:
    message: str
    line: int


@dataclass
class SemanticResult:
    symbol_table: SymbolTable
    errors: list[Diagnostic]
    warnings: list[Diagnostic]
    ast: Program


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.symbol_table = SymbolTable()
        self.errors: list[Diagnostic] = []
        self.warnings: list[Diagnostic] = []

    def analyze(self, ast: Program) -> SemanticResult:
        for statement in ast.statements:
            if isinstance(statement, VarDecl):
                self._declaration(statement)
            elif isinstance(statement, Assignment):
                self._assignment(statement)
            elif isinstance(statement, PrintStmt):
                self._expression(statement.expression)
        return SemanticResult(self.symbol_table, self.errors, self.warnings, ast)

    def _declaration(self, node: VarDecl) -> None:
        if node.name in self.symbol_table:
            self.errors.append(Diagnostic(f"Redeclaration of variable '{node.name}'", node.line))
            if node.initializer is not None:
                self._expression(node.initializer)
            return
        initialized = node.initializer is not None
        self.symbol_table.declare(node.name, node.var_type, node.line, initialized)
        if node.initializer is not None:
            expression_type = self._expression(node.initializer)
            self._check_assignment_type(node.var_type, expression_type, node.line)

    def _assignment(self, node: Assignment) -> None:
        expression_type = self._expression(node.expression)
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            self.errors.append(Diagnostic(f"Undeclared variable '{node.name}'", node.line))
            return
        self._check_assignment_type(symbol.type, expression_type, node.line)
        symbol.initialized = True

    def _check_assignment_type(self, target: str, actual: Optional[str], line: int) -> None:
        if target == "int" and actual == "float":
            self.warnings.append(Diagnostic("Assigning float value to int variable", line))

    def _expression(self, node: Expression | None) -> Optional[str]:
        if node is None:
            return None
        if isinstance(node, Literal):
            node.inferred_type = node.literal_type
            return node.inferred_type
        if isinstance(node, Identifier):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                self.errors.append(Diagnostic(f"Undeclared variable '{node.name}'", node.line))
                return None
            if not symbol.initialized:
                self.warnings.append(Diagnostic(f"Variable '{node.name}' used before initialization", node.line))
            node.inferred_type = symbol.type
            return node.inferred_type
        if isinstance(node, UnaryOp):
            node.inferred_type = self._expression(node.operand)
            return node.inferred_type
        if isinstance(node, BinaryOp):
            left_type = self._expression(node.left)
            right_type = self._expression(node.right)
            if node.operator == "/" and self._constant_value(node.right) == 0:
                self.errors.append(Diagnostic("Division by constant zero", node.line))
            node.inferred_type = "float" if "float" in (left_type, right_type) else "int"
            return node.inferred_type
        return None

    def _constant_value(self, node: Expression | None) -> int | float | None:
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, UnaryOp):
            value = self._constant_value(node.operand)
            return -value if value is not None and node.operator == "-" else None
        if isinstance(node, BinaryOp):
            left = self._constant_value(node.left)
            right = self._constant_value(node.right)
            if left is None or right is None:
                return None
            if node.operator == "+":
                return left + right
            if node.operator == "-":
                return left - right
            if node.operator == "*":
                return left * right
            if node.operator == "/" and right != 0:
                return left / right
        return None


def analyze(ast: Program) -> SemanticResult:
    return SemanticAnalyzer().analyze(ast)
