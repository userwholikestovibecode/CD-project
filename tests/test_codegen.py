from compiler.codegen import generate_target
from compiler.icg import TACInstruction


def test_codegen_emits_load_and_add():
    result = generate_target([TACInstruction("+", "a", "2", "t1"), TACInstruction("print", "t1")])
    assert any(line.startswith("ADD ") for line in result.instructions)
    assert any(line.startswith("PRINT ") for line in result.instructions)


def test_codegen_emits_store():
    result = generate_target([TACInstruction("assign", "5", None, "x")])
    assert any(line.startswith("STORE x") for line in result.instructions)
