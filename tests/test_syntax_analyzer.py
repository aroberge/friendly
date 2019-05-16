"""test_syntax_analyzer"""

from friendly_traceback import analyze_syntax, set_lang


set_lang("en")


def test_no_false_positive():
    # The following tests use valid syntax.
    # They should never have raised a Syntax error, and thus
    # we should not be able to find a likely cause of a problem.
    find = analyze_syntax._find_likely_cause
    no_cause = "we cannot guess the likely cause of this error"

    # _find_likely_cause(source, linenumber, message, offset)
    assert no_cause in find(["def test(arg1, arg2):"], 1, "irrelevant", 1)
    assert no_cause in find(["for i in range(3):"], 1, "irrelevant", 1)
    assert no_cause in find(["while True:"], 1, "irrelevant", 1)
    assert no_cause in find(["pass"], 1, "irrelevant", 1)
    assert no_cause in find(["else:"], 1, "irrelevant", 1)


def test_assign_to_literal():
    assign = analyze_syntax.assign_to_literal
    literal = "what Python calls a 'literal'"

    case_1 = assign(message="can't assign to literal", line="1 = a")
    assert literal in case_1
    assert "a = 1" in case_1

    case_2 = assign(message="cannot assign to literal", line="'a' = a")
    assert literal in case_2
    assert "a = 'a'" in case_2

    assert not assign(message="other")


def test_eol_while_scanning_string_literal():
    eol = analyze_syntax.eol_while_scanning_string_literal

    assert eol(message="EOL while scanning string literal")
    assert not eol(message="other")


def test_assign_to_keyword():
    last_line = analyze_syntax.analyze_last_line
    assert "assign a value to the Python keyword 'pass'" in last_line("pass = 1")


def test_confused_elif():
    last_line = analyze_syntax.analyze_last_line
    assert "wrote 'else if' instead" in last_line("    else if")
    assert "wrote 'else if' instead" in last_line("else if whatever:")
    assert "wrote 'elseif' instead" in last_line("    elseif")
    assert "wrote 'elseif' instead" in last_line("elseif True:")


def test_import_from():
    last_line = analyze_syntax.analyze_last_line
    assert "from A import B" in last_line("import B from A")


def test_missing_colon():
    result = "forgot to add a colon ':' at the end"
    last_line = analyze_syntax.analyze_last_line
    assert result in last_line("class True")
    assert result in last_line("if True")
    assert result in last_line("elif True")
    assert result in last_line("else True")
    assert result in last_line("for True")
    assert result in last_line("while True")
    assert result in last_line("try True")
    assert result in last_line("except True")
    assert result in last_line("finally True")


def test_malformed_def():
    last_line = analyze_syntax.analyze_last_line
    assert "tried to define a function or method" in last_line("def () :")
    assert "tried to define a function or method" in last_line("def name  :")
    assert "tried to define a function or method" in last_line("def (arg) :")
    assert "tried to define a function or method" in last_line("def :")


if __name__ == "__main__":
    test_assign_to_keyword()
    test_confused_elif()
    test_missing_colon()
    test_malformed_def()
    print("Tests ran successfully")
