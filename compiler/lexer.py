"""PLY lexer for the mini compiler source language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import ply.lex as lex


@dataclass(frozen=True)
class LexError:
    message: str
    line: int
    character: str


class MiniLexer:
    tokens = (
        "INT",
        "FLOAT",
        "IDENTIFIER",
        "INTEGER",
        "FLOATING",
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "ASSIGN",
        "LPAREN",
        "RPAREN",
        "SEMICOLON",
    )
    reserved = {"int": "INT", "float": "FLOAT", "print": "PRINT"}
    tokens = tokens + ("PRINT",)

    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"
    t_ASSIGN = r"="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_SEMICOLON = r";"
    t_ignore = " \t\r"

    def t_COMMENT(self, token):
        r"//[^\n]*"
        return None

    def t_FLOATING(self, token):
        r"((\d+\.\d*)|(\.\d+))([eE][+-]?\d+)?|(\d+[eE][+-]?\d+)"
        token.value = float(token.value)
        return token

    def t_INTEGER(self, token):
        r"\d+"
        token.value = int(token.value)
        return token

    def t_IDENTIFIER(self, token):
        r"[A-Za-z_][A-Za-z0-9_]*"
        token.type = self.reserved.get(token.value, "IDENTIFIER")
        return token

    def t_newline(self, token):
        r"\n+"
        token.lexer.lineno += len(token.value)

    def t_error(self, token):
        errors = getattr(token.lexer, "errors", None)
        if errors is not None:
            errors.append(
                LexError(
                    f"Illegal character {token.value[0]!r}",
                    token.lineno,
                    token.value[0],
                )
            )
        token.lexer.skip(1)


def build_lexer() -> lex.Lexer:
    """Build a fresh lexer, safe to call on every Streamlit rerun."""
    scanner = MiniLexer()
    lexer = lex.lex(module=scanner, debug=False)
    lexer.errors = []
    return lexer


def tokenize(source: str) -> tuple[list[tuple[str, str, int]], list[LexError]]:
    """Return a structured token table and all lexical errors."""
    lexer = build_lexer()
    lexer.input(source)
    rows: list[tuple[str, str, int]] = []
    while True:
        token = lexer.token()
        if token is None:
            break
        lexeme = str(token.value)
        if token.type == "INTEGER":
            lexeme = str(token.value)
        rows.append((token.type, lexeme, token.lineno))
    return rows, list(lexer.errors)


def lex_source(source: str) -> tuple[list[tuple[str, str, int]], list[LexError]]:
    """Alias for :func:`tokenize` used by the UI and tests."""
    return tokenize(source)
