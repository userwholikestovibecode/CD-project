from compiler.icg import TACInstruction
from compiler.optimizer import optimize


def test_constant_folding():
    result = optimize([TACInstruction("*", "2", "3", "t1"), TACInstruction("print", "t1")])
    assert any(item.arg1 == "6" for item in result.after)


def test_constant_propagation():
    result = optimize([TACInstruction("assign", "4", None, "x"), TACInstruction("+", "x", "2", "t1"), TACInstruction("print", "t1")])
    assert any(item.arg1 == "6" for item in result.after)


def test_algebraic_simplification():
    result = optimize([TACInstruction("*", "x", "1", "t1"), TACInstruction("print", "t1")])
    assert result.after[0].arg1 == "x"


def test_dead_temporary_elimination():
    result = optimize([TACInstruction("+", "1", "2", "t1"), TACInstruction("assign", "3", None, "x"), TACInstruction("print", "x")])
    assert all(item.result != "t1" for item in result.after)


def test_stats_and_logs():
    result = optimize([TACInstruction("+", "1", "2", "t1"), TACInstruction("print", "t1")])
    assert result.before_count == 2
    assert result.logs
