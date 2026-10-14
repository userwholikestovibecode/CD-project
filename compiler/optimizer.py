"""Fixed-point optimizations for three-address code."""

from __future__ import annotations

from dataclasses import dataclass

from .icg import TACInstruction


@dataclass(frozen=True)
class OptimizationLog:
    instruction: int
    rule: str
    reason: str


@dataclass
class OptimizationResult:
    before: list[TACInstruction]
    after: list[TACInstruction]
    logs: list[OptimizationLog]
    before_count: int
    after_count: int


def _number(value: str | None):
    if value is None:
        return None
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return None


def _fmt(value) -> str:
    return str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)


def optimize(instructions: list[TACInstruction]) -> OptimizationResult:
    before = list(instructions)
    current = list(instructions)
    logs: list[OptimizationLog] = []
    changed = True
    while changed:
        changed = False
        constants: dict[str, str] = {}
        new: list[TACInstruction] = []
        for index, instruction in enumerate(current, 1):
            a, b = instruction.arg1, instruction.arg2
            if a in constants:
                a = constants[a]
            if b in constants:
                b = constants[b]
            replacement = None
            if instruction.op in {"+", "-", "*", "/"}:
                left, right = _number(a), _number(b)
                if left is not None and right is not None and not (instruction.op == "/" and right == 0):
                    if instruction.op == "+":
                        value = left + right
                    elif instruction.op == "-":
                        value = left - right
                    elif instruction.op == "*":
                        value = left * right
                    else:
                        value = left / right
                    replacement = TACInstruction("assign", _fmt(value), None, instruction.result)
                    logs.append(OptimizationLog(index, "constant folding", "both operands are constants"))
                elif instruction.op == "*" and (a == "0" or b == "0"):
                    replacement = TACInstruction("assign", "0", None, instruction.result)
                    logs.append(OptimizationLog(index, "algebraic simplification", "x * 0 is always zero"))
                elif instruction.op == "*" and a == "1":
                    replacement = TACInstruction("assign", b, None, instruction.result)
                    logs.append(OptimizationLog(index, "algebraic simplification", "1 * x equals x"))
                elif instruction.op == "*" and b == "1":
                    replacement = TACInstruction("assign", a, None, instruction.result)
                    logs.append(OptimizationLog(index, "algebraic simplification", "x * 1 equals x"))
                elif instruction.op == "+" and a == "0":
                    replacement = TACInstruction("assign", b, None, instruction.result)
                    logs.append(OptimizationLog(index, "algebraic simplification", "0 + x equals x"))
                elif instruction.op == "+" and b == "0":
                    replacement = TACInstruction("assign", a, None, instruction.result)
                    logs.append(OptimizationLog(index, "algebraic simplification", "x + 0 equals x"))
            if replacement is None:
                replacement = TACInstruction(instruction.op, a, b, instruction.result)
            if replacement.op == "assign" and _number(replacement.arg1) is not None and replacement.result:
                constants[replacement.result] = replacement.arg1
            elif replacement.result and replacement.result in constants:
                constants.pop(replacement.result, None)
            if replacement != instruction:
                changed = True
            new.append(replacement)
        current = new
        needed: set[str] = set()
        filtered_reversed: list[TACInstruction] = []
        for index in range(len(current) - 1, -1, -1):
            instruction = current[index]
            keep = instruction.op == "print" or instruction.result is None or instruction.result in needed
            if keep:
                filtered_reversed.append(instruction)
                if instruction.result:
                    needed.discard(instruction.result)
                for arg in (instruction.arg1, instruction.arg2):
                    if arg:
                        needed.add(arg)
            elif instruction.result:
                logs.append(OptimizationLog(index + 1, "dead-code elimination", "result is never used"))
                changed = True
        current = list(reversed(filtered_reversed))
    return OptimizationResult(before, current, logs, len(before), len(current))
