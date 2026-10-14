"""Orchestration of all compiler phases."""

from __future__ import annotations

from dataclasses import dataclass, field

from .codegen import CodegenResult, generate_target
from .icg import ICGResult, generate
from .lexer import LexError, tokenize
from .optimizer import OptimizationResult, optimize
from .parser import SyntaxErrorInfo, parse
from .semantic import SemanticResult, analyze


@dataclass
class PhaseResult:
    status: str
    output: object = None
    errors: list[object] = field(default_factory=list)
    warnings: list[object] = field(default_factory=list)


@dataclass
class PipelineResult:
    phases: dict[str, PhaseResult]


def compile_source(source: str) -> PipelineResult:
    phases: dict[str, PhaseResult] = {}
    tokens, lex_errors = tokenize(source)
    phases["lexical"] = PhaseResult("failed" if lex_errors else "passed", tokens, lex_errors)
    if lex_errors:
        return _skip(phases, ["syntax", "semantic", "intermediate_code", "optimization", "target_code"])
    ast, syntax_errors = parse(source)
    phases["syntax"] = PhaseResult("failed" if syntax_errors else "passed", ast, syntax_errors)
    if syntax_errors or ast is None:
        return _skip(phases, ["semantic", "intermediate_code", "optimization", "target_code"])
    semantic = analyze(ast)
    phases["semantic"] = PhaseResult("failed" if semantic.errors else "passed", semantic, semantic.errors, semantic.warnings)
    if semantic.errors:
        return _skip(phases, ["intermediate_code", "optimization", "target_code"])
    icg = generate(ast)
    phases["intermediate_code"] = PhaseResult("passed", icg)
    optimized = optimize(icg.instructions)
    phases["optimization"] = PhaseResult("passed", optimized)
    target = generate_target(optimized.after)
    phases["target_code"] = PhaseResult("passed", target)
    return PipelineResult(phases)


def _skip(phases: dict[str, PhaseResult], names: list[str]) -> PipelineResult:
    for name in names:
        phases[name] = PhaseResult("skipped")
    return PipelineResult(phases)


run_pipeline = compile_source
