from compiler.icg import generate
from compiler.parser import parse


def test_temporary_generation():
    ast, errors = parse("print(1 + 2 * 3);")
    result = generate(ast)
    assert not errors
    assert [item.result for item in result.instructions[:2]] == ["t1", "t2"]


def test_assignment_and_print():
    ast, _ = parse("int x = 2; print(x);")
    result = generate(ast)
    assert result.instructions[-1].op == "print"
    assert "print x" in result.text
