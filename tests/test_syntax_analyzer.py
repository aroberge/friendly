"""test_syntax_analyzer"""

from friendly_traceback.analyze_syntax import analyze_last_line as last
from friendly_traceback.analyze_syntax import assign_to_literal as assign
from friendly_traceback.analyze_syntax import find_likely_cause as find


def test_no_false_positive():
    # The following tests use valid syntax. We should not be able to
    # find a likely cause.
    # find_likely_cause(source, linenumber, message, offset)
    assert find(["def test(arg1, arg2):"], 1, "irrelevant", 1) == "No cause found"
    assert find(["for i in range(3):"], 1, "irrelevant", 1) == "No cause found"
    assert find(["while True:"], 1, "irrelevant", 1) == "No cause found"


def test_assign_to_literal():
    assert assign("can't assign to literal", "1 = a") == "can't assign to literal 1"
    assert assign("can't assign to literal", "'a' = a") == "can't assign to literal 'a'"


def test_assign_to_keyword():
    assert last("pass = 1") == "Assigning to Python keyword"


def test_confused_elif():
    assert last("else if") == "elif not else if"
    assert last("else if whatever:") == "elif not else if"
    assert last("elseif ") == "elif not elseif"
    assert last("elseif True:") == "elif not elseif"


def test_missing_colon():
    assert last("class True") == "class missing colon"
    assert last("if True") == "if missing colon"
    assert last("elif True") == "elif missing colon"
    assert last("else True") == "else missing colon"
    assert last("for True") == "for missing colon"
    assert last("while True") == "while missing colon"
    assert last("try True") == "try missing colon"
    assert last("except True") == "except missing colon"
    assert last("finally True") == "finally missing colon"


def test_malformed_def():
    assert last("def () :") == "malformed def"
    assert last("def name  :") == "malformed def"
    assert last("def (arg) :") == "malformed def"
    assert last("def :") == "malformed def"


if __name__ == "__main__":
    test_assign_to_keyword()
    test_confused_elif()
    test_missing_colon()
    test_malformed_def()
    print("Tests ran successfully")
