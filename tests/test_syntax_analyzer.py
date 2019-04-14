"""test_syntax_analyzer"""

from friendly_traceback.analyze_syntax import analyze_last_line as last


def test_assign_to_keyword():
    assert last("pass = 1") == "Assigning to Python keyword"


def test_confused_elif():
    assert last("else if") == "elif not else if"
    assert last("else if whatever:") == "elif not else if"
    assert last("elseif ") == "elif not elseif"
    assert last("elseif whatever:") == "elif not elseif"


def test_missing_colon():
    assert last("class True") == "class missing colon"
    assert last("def True") == "def missing colon"
    assert last("if True") == "if missing colon"
    assert last("elif True") == "elif missing colon"
    assert last("else True") == "else missing colon"
    assert last("for True") == "for missing colon"
    assert last("while True") == "while missing colon"
    assert last("try True") == "try missing colon"
    assert last("except True") == "except missing colon"
    assert last("finally True") == "finally missing colon"


if __name__ == '__main__':
    test_missing_colon()
    print("Tests ran successfully")
