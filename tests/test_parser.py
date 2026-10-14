from compiler.ast_nodes import BinaryOp, UnaryOp
from compiler.parser import parse


def test_declaration_and_assignment():
    ast, errors = parse("int a = 1; a = a + 2;")
    assert not errors and len(ast.statements) == 2


def test_precedence():
    ast, errors = parse("print(1 + 2 * 3);")
    expression = ast.statements[0].expression
    assert not errors and isinstance(expression, BinaryOp)
    assert expression.operator == "+"
    assert expression.right.operator == "*"


def test_unary_minus_precedence():
    ast, errors = parse("print(-2 * 3);")
    assert not errors
    assert isinstance(ast.statements[0].expression.left, UnaryOp)


def test_parentheses():
    ast, errors = parse("print((1 + 2) * 3);")
    assert not errors
    assert ast.statements[0].expression.operator == "*"


def test_syntax_error_is_recoverable():
    ast, errors = parse("int x = ;")
    assert ast is None
    assert errors and errors[0].line == 1
