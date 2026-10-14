from compiler.lexer import tokenize


def test_keywords_and_identifiers():
    tokens, errors = tokenize("int value = 2; print(value);")
    assert not errors
    assert [token[0] for token in tokens] == ["INT", "IDENTIFIER", "ASSIGN", "INTEGER", "SEMICOLON", "PRINT", "LPAREN", "IDENTIFIER", "RPAREN", "SEMICOLON"]


def test_comments_and_lines():
    tokens, errors = tokenize("// comment\nfloat x = 1.5;")
    assert not errors
    assert tokens[0] == ("FLOAT", "float", 2)


def test_illegal_character_has_line():
    _, errors = tokenize("int x = 1;\n@")
    assert errors[0].line == 2
    assert "Illegal character" in errors[0].message


def test_numeric_values():
    tokens, _ = tokenize("1 2.5 .75 3e2")
    assert [token[1] for token in tokens] == ["1", "2.5", "0.75", "300.0"]
