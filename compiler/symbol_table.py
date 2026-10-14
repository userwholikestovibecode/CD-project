"""Shared symbol table for semantic analysis and later compiler phases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Symbol:
    name: str
    type: str
    line_declared: int
    initialized: bool = False


class SymbolTable:
    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}

    def declare(self, name: str, type: str, line_declared: int, initialized: bool = False) -> Symbol:
        symbol = Symbol(name, type, line_declared, initialized)
        self._symbols[name] = symbol
        return symbol

    def lookup(self, name: str) -> Symbol | None:
        return self._symbols.get(name)

    def symbols(self) -> list[Symbol]:
        return list(self._symbols.values())

    def __contains__(self, name: str) -> bool:
        return name in self._symbols
