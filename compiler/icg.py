"""Three-address code generation."""

from __future__ import annotations

from dataclasses import dataclass

from .ast_nodes import Assignment, BinaryOp, Identifier, Literal, PrintStmt, Program, UnaryOp, VarDecl


@dataclass(frozen=True)
class TACInstruction:
    op: str
    arg1: str | None = None
    arg2: str | None = None
    result: str | None = None

    def text(self) -> str:
        if self.op == "assign":
            return f"{self.result} = {self.arg1}"
        if self.op == "print":
            return f"print {self.arg1}"
        if self.op == "uminus":
            return f"{self.result} = -{self.arg1}"
        return f"{self.result} = {self.arg1} {self.op} {self.arg2}"


@dataclass
class ICGResult:
    instructions: list[TACInstruction]
    text: str


class ThreeAddressGenerator:
    def __init__(self) -> None:
        self.instructions: list[TACInstruction] = []
        self.temp_index = 0

    def generate(self, program: Program) -> ICGResult:
        for statement in program.statements:
            if isinstance(statement, VarDecl):
                if statement.initializer is not None:
                    self.instructions.append(TACInstruction("assign", self._expression(statement.initializer), None, statement.name))
            elif isinstance(statement, Assignment):
                self.instructions.append(TACInstruction("assign", self._expression(statement.expression), None, statement.name))
            elif isinstance(statement, PrintStmt):
                self.instructions.append(TACInstruction("print", self._expression(statement.expression)))
        return ICGResult(self.instructions, "\n".join(item.text() for item in self.instructions))

    def _temp(self) -> str:
        self.temp_index += 1
        return f"t{self.temp_index}"

    def _expression(self, node) -> str:
        if isinstance(node, Literal):
            return str(node.value)
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, UnaryOp):
            result = self._temp()
            self.instructions.append(TACInstruction("uminus", self._expression(node.operand), None, result))
            return result
        if isinstance(node, BinaryOp):
            left = self._expression(node.left)
            right = self._expression(node.right)
            result = self._temp()
            self.instructions.append(TACInstruction(node.operator, left, right, result))
            return result
        raise TypeError(f"Unsupported AST node: {type(node).__name__}")


def generate(program: Program) -> ICGResult:
    return ThreeAddressGenerator().generate(program)
