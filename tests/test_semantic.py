from compiler.parser import parse
from compiler.semantic import analyze


def semantic(source):
    ast, parse_errors = parse(source)
    assert not parse_errors
    return analyze(ast)


def test_declaration_enters_symbol_table():
    result = semantic("int x;")
    assert result.symbol_table.lookup("x").type == "int"


def test_undeclared_variable_error():
    result = semantic("x = 1;")
    assert any("Undeclared" in error.message for error in result.errors)


def test_redeclaration_error():
    result = semantic("int x; float x;")
    assert any("Redeclaration" in error.message for error in result.errors)


def test_use_before_initialization_warning():
    result = semantic("int x; print(x);")
    assert any("before initialization" in warning.message for warning in result.warnings)


def test_float_to_int_warning():
    result = semantic("int x = 1.5;")
    assert any("float" in warning.message for warning in result.warnings)


def test_constant_zero_division_error():
    result = semantic("int x = 4 / 0;")
    assert any("zero" in error.message for error in result.errors)
