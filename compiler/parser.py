"""PLY parser that builds the mini compiler AST."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import ply.yacc as yacc

from .ast_nodes import (
    Assignment,
    BinaryOp,
    Identifier,
    Literal,
    PrintStmt,
    Program,
    UnaryOp,
    VarDecl,
)
from .lexer import MiniLexer, build_lexer


@dataclass(frozen=True)
class SyntaxErrorInfo:
    message: str
    line: int


class MiniParser:
    tokens = MiniLexer.tokens
    precedence = (
        ("left", "PLUS", "MINUS"),
        ("left", "TIMES", "DIVIDE"),
        ("right", "UMINUS"),
    )

    def p_program(self, p):
        """program : statements"""
        p[0] = Program(line=1, statements=p[1])

    def p_statements_many(self, p):
        """statements : statements statement"""
        p[0] = p[1] + [p[2]]

    def p_statements_one(self, p):
        """statements : statement"""
        p[0] = [p[1]]

    def p_statement_decl(self, p):
        """statement : type_spec IDENTIFIER SEMICOLON
                     | type_spec IDENTIFIER ASSIGN expression SEMICOLON"""
        initializer = p[4] if len(p) == 6 else None
        p[0] = VarDecl(line=p.lineno(2), name=p[2], var_type=p[1], initializer=initializer)

    def p_type_spec(self, p):
        """type_spec : INT
                     | FLOAT"""
        p[0] = p[1]

    def p_statement_assignment(self, p):
        """statement : IDENTIFIER ASSIGN expression SEMICOLON"""
        p[0] = Assignment(line=p.lineno(1), name=p[1], expression=p[3])

    def p_statement_print(self, p):
        """statement : PRINT LPAREN expression RPAREN SEMICOLON"""
        p[0] = PrintStmt(line=p.lineno(1), expression=p[3])

    def p_expression_binary(self, p):
        """expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression"""
        p[0] = BinaryOp(line=p.lineno(2), operator=p[2], left=p[1], right=p[3])

    def p_expression_group(self, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = p[2]

    def p_expression_unary(self, p):
        """expression : MINUS expression %prec UMINUS"""
        p[0] = UnaryOp(line=p.lineno(1), operator="-", operand=p[2])

    def p_expression_integer(self, p):
        """expression : INTEGER"""
        p[0] = Literal(line=p.lineno(1), value=p[1], literal_type="int")

    def p_expression_float(self, p):
        """expression : FLOATING"""
        p[0] = Literal(line=p.lineno(1), value=p[1], literal_type="float")

    def p_expression_identifier(self, p):
        """expression : IDENTIFIER"""
        p[0] = Identifier(line=p.lineno(1), name=p[1])

    def p_error(self, token):
        errors = getattr(self, "errors", [])
        if token is None:
            errors.append(SyntaxErrorInfo("Syntax error: unexpected end of input", self._last_line))
        else:
            errors.append(
                SyntaxErrorInfo(
                    f"Syntax error near {token.value!r}; expected a valid statement or expression",
                    token.lineno,
                )
            )
        self.errors = errors


def build_parser() -> yacc.LRParser:
    """Build a fresh parser with no generated table files."""
    parser_object = MiniParser()
    parser = yacc.yacc(
        module=parser_object,
        write_tables=False,
        debug=False,
        errorlog=yacc.NullLogger(),
    )
    parser._mini_parser = parser_object
    return parser


def parse(source: str) -> tuple[Optional[Program], list[SyntaxErrorInfo]]:
    """Parse source and return an AST plus recoverable syntax diagnostics."""
    lexer = build_lexer()
    parser = build_parser()
    parser_object = parser._mini_parser
    parser_object.errors = []
    parser_object._last_line = source.count("\n") + 1
    ast = parser.parse(source, lexer=lexer, tracking=True)
    errors = list(parser_object.errors)
    if errors:
        return None, errors
    return ast, errors


def parse_source(source: str) -> tuple[Optional[Program], list[SyntaxErrorInfo]]:
    return parse(source)
