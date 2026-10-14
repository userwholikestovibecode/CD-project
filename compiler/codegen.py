"""Educational pseudo-assembly generator."""

from __future__ import annotations

from dataclasses import dataclass

from .icg import TACInstruction


@dataclass
class CodegenResult:
    instructions: list[str]
    text: str


def generate_target(instructions: list[TACInstruction]) -> CodegenResult:
    lines: list[str] = []
    registers: dict[str, str] = {}
    next_register = 1

    def load(value: str | None) -> str:
        nonlocal next_register
        if value is None:
            return "R0"
        if value not in registers:
            registers[value] = f"R{next_register}"
            next_register += 1
            lines.append(f"LOAD {registers[value]}, {value}")
        return registers[value]

    for item in instructions:
        if item.op == "print":
            lines.append(f"PRINT {load(item.arg1)}")
        elif item.op == "assign":
            source = load(item.arg1)
            destination = registers.setdefault(item.result or "", f"R{next_register}")
            if destination == f"R{next_register}":
                next_register += 1
            lines.append(f"MOV {destination}, {source}")
            if item.result:
                lines.append(f"STORE {item.result}, {destination}")
        elif item.op == "uminus":
            source = load(item.arg1)
            destination = registers.setdefault(item.result or "", f"R{next_register}")
            if destination == f"R{next_register}":
                next_register += 1
            lines.extend([f"MOV {destination}, 0", f"SUB {destination}, {source}", f"STORE {item.result}, {destination}"])
        else:
            left, right = load(item.arg1), load(item.arg2)
            destination = registers.setdefault(item.result or "", f"R{next_register}")
            if destination == f"R{next_register}":
                next_register += 1
            operation = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV"}[item.op]
            lines.extend([f"{operation} {destination}, {left}, {right}", f"STORE {item.result}, {destination}"])
    return CodegenResult(lines, "\n".join(lines))


def generate(instructions: list[TACInstruction]) -> CodegenResult:
    return generate_target(instructions)
