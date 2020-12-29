"""test_syntax_analyzer

The purpose of this file is to ensure that syntax errors are properly
identified; it is complementary to the use of catch_syntax_error.py
which imports various individual files, each having a separate syntax error and
triggering the entire exception analysis code of friendly-traceback, which
is more akin to an integration test.

By contrast, the current file does not trigger any exceptions, and focused
on testing a single module.  The goal is to ensure that any syntactically
invalid code is properly identified, and that no false positive is
generated by the analysis.


You may want to have a look at analyze_syntax.py and confirm that the following
is still accurate.

The analysis of SyntaxErrors is done via analyze_syntax.find_likely_cause()
which calls analyze_syntax._find_likely_cause(). The latter is called with
the following arguments:
    _find_likely_cause(source_lines, linenumber, message, offset)

Given that a SyntaxError exception will include something like

    SyntaxError: invalid syntax
    or
    SyntaxError: a more specific "message"


_find_likely_cause() will proceed in three steps:

1. It will try to make use of the message included. Since the message can
   differ (sometimes just slightly) between Python versions, some tests
   below are done to confirm that messages are properly analyzed.
   This is done with a call to a series of specific functions which
   are given the "message", the line of code identified as problematic
   by Python and its corresponding linenumber. [The offset is ignored.]

2. Next, it will try to look at the content of the line flagged by Python as
   the last line it could analyze, going through a series of individual
   tests.  Here, only the last line of code is passed, which is broken
   down into a series of tokens prior to be sent to individual analyzers.
   [The message, linenumber and offset arguments are not used.]

3. Finally, it will look at the entire content, mostly focusing on checking
   if (), [], and {}, are properly matched and closed. In doing so, it might
   identify other errors along the way.
"""
import sys
from friendly_traceback import set_lang
from friendly_traceback.syntax_errors import analyze_syntax


def find(lines=[" "], linenumber=1, message="invalid syntax", offset=1):
    return analyze_syntax._find_likely_cause(
        source_lines=lines, linenumber=linenumber, message=message, offset=offset
    )[0]


multiline_def = """def f(x,
y):
    pass
"""


def test_no_false_positive():
    # The following tests use valid syntax.
    # They should never have raised a Syntax error, and thus
    # we should not be able to find a likely cause of a problem.
    set_lang("en")
    no_cause = "I cannot guess the likely cause of this error"

    assert no_cause in find(["def test(arg1, arg2):"])
    assert no_cause in find(["def test(arg1, arg2=None):"])
    assert no_cause in find(["def test(arg1=(None, 1)):"])
    assert no_cause in find(["def test(arg1=(1, None)):"])
    assert no_cause in find(["def test(arg1=[1, None]):"])
    assert no_cause in find(["def test(arg1={1, None}):"])
    # assert no_cause in find(multiline_def.split("\n"))

    assert no_cause in find(["for i in range(3):"])
    assert no_cause in find(["while True:"])
    assert no_cause in find(["pass"])
    assert no_cause in find(["else:"])

    walrus_test = ["a := 1"]
    if sys.version_info >= (3, 8):
        assert no_cause in find(walrus_test, offset=3)
    else:
        assert "walrus operator" in find(walrus_test, offset=3)


def test_assign_to_literal():
    # two different messages possible, depending on Python version
    literal = "is or includes an actual object"

    case_1 = find(["1=a"], message="can't assign to literal")
    assert literal in case_1
    assert "a = 1" in case_1

    case_2 = find(["'a' = a"], message="cannot assign to literal")
    assert literal in case_2
    assert "a = 'a'" in case_2


def test_assign_to_function_call():
    assert "a function call and" in find(
        lines=["a() = 1"], message="cannot assign to function call"
    )
    assert "a function call and" in find(
        lines=["a() = 1"], message="can't assign to function call"
    )


def test_eol_while_scanning_string_literal():
    assert "You starting writing a string" in find(
        message="EOL while scanning string literal"
    )


def test_assign_to_keyword():
    assert "`None` is a constant in Python; you cannot assign it a value" in find(
        message="can't assign to keyword", lines=["None = 1"]
    )
    assert "assign a value to the Python keyword `def`" in find(lines=["def = 1"])


def test_confused_elif():
    assert "wrote `else if` instead" in find(lines=["    else if"])
    assert "wrote `else if` instead" in find(lines=["else if whatever:"])
    assert "wrote `elseif` instead" in find(lines=["    elseif"])
    assert "wrote `elseif` instead" in find(lines=["elseif True:"])


def test_import_from():
    assert "from A import B" in find(lines=["import B from A"])


def test_missing_colon():
    result = "forgot to add a colon `:` at the end"
    assert result in find(lines=["class True"])
    assert result in find(lines=["if True"])
    assert result in find(lines=["elif True"])
    assert result in find(lines=["else True"])
    assert result in find(lines=["for True"])
    assert result in find(lines=["while True"])
    assert result in find(lines=["try True"])
    assert result in find(lines=["except True"])
    assert result in find(lines=["finally True"])


def test_malformed_def():
    assert "tried to define a function or method" in find(lines=["def () :"])
    assert "tried to define a function or method" in find(lines=["def name  :"])
    assert "tried to define a function or method" in find(lines=["def (arg) :"])
    assert "tried to define a function or method" in find(lines=["def :"])


def test_look_for_missing_bracket():
    assert "The opening" in find(lines=["a =[1, 2, 3, 4)"], linenumber=1, offset=10)
    assert "The opening" in find(lines=["a =(1, 2 "], linenumber=1, offset=10)
    assert "The closing" in find(lines=["a =1, 2)"], linenumber=1, offset=10)


def test_keyword_as_attribute():
    assert "cannot use the Python keyword `True` as" in find(lines=["obj.True = 1"])


def test_misplaced_quote():
    assert "trying to use a quote inside a string" in find(lines=["info = 'don't"])


def test_missing_comma():
    # inside look_for_missing_bracket
    assert "a =[1, 2, 3, 4]" in find(lines=["a =[1, 2 3, 4]"], linenumber=1, offset=10)
    assert "a =(1, 2, 3, 4)" in find(lines=["a =(1, 2 3, 4)"], linenumber=1, offset=10)
    assert "def fn(a, b):" in find(
        lines=["def fn(a b):", "pass"], linenumber=1, offset=10
    )


def test_equal_sign_instead_of_colon():
    # inside look_for_missing_bracket
    assert "used an equal sign `=` instead of a colon `:`" in find(
        lines=["a = {'a' = 1}"], linenumber=1, offset=8
    )


if __name__ == "__main__":
    import copy

    known = copy.copy(locals())
    count = 0
    for var in known:
        if var.startswith("test_") and callable(known[var]):
            try:
                count += 1
                known[var]()
            except AssertionError:
                print(f"{var} failed")
                print("Suggestion: try python -m pytest")
                count -= 1
    print(f"{count} tests ran successfully.")
