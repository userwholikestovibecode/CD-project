from compiler.pipeline import compile_source


def test_pipeline_success():
    result = compile_source("int x = 2 + 3; print(x);")
    assert all(phase.status == "passed" for phase in result.phases.values())


def test_pipeline_stops_on_lexical_error():
    result = compile_source("int x = @;")
    assert result.phases["lexical"].status == "failed"
    assert result.phases["syntax"].status == "skipped"


def test_pipeline_stops_on_syntax_error():
    result = compile_source("int x = ;")
    assert result.phases["syntax"].status == "failed"
    assert result.phases["semantic"].status == "skipped"


def test_pipeline_stops_on_semantic_error():
    result = compile_source("x = 1;")
    assert result.phases["semantic"].status == "failed"
    assert result.phases["intermediate_code"].status == "skipped"
